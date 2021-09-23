import os
import configparser
import yaml
import pathlib
import dotenv
import json
import logging
import sys

logging.basicConfig(filename="app.log",
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

config_name = ''
file_extension = ''
supported_file_types = ['conf', 'cfg', 'ini', 'yaml']


def retry_with_default_stanza(method):
    """
    This method is used as a decorator to call the read_conf method with retry=1 param if section header not found in the conf file.
    """
    def wrapper(*args, **kwargs):
        try:
            ret_val = method(*args, **kwargs)
            return ret_val
        except configparser.MissingSectionHeaderError as e:
            ret_val = method(*args, retry=1)
            return ret_val
        except Exception as e:
            print("Error Occured: {}".format(e))
            logger.error("Error Occured: {}".format(e))
            sys.exit(0)
    return wrapper


def handle_exception(method):
    """
    This method is used as a decorator to handle the unexpected exceptions.
    """
    def wrapper(*args, **kwargs):
        try:
            ret_val = method(*args, **kwargs)
            return ret_val
        except configparser.MissingSectionHeaderError as e:
            print("Could not read the conf file.\nRetrying with adding default header.")
            logger.error("Error Occured: {}".format(e))
            raise e
        except Exception as e:
            close_msg = "Returning to the main menu"
            print("Error Occured: {}\n{}".format(e, close_msg))
            logger.error("Error Occured: {}\n{}".format(e, close_msg))
            sys.exit(0)

    return wrapper


def get_file_path():
    """
    This method is used to get the absolute path of config file from User. 
    """
    return input("Enter absolute file path:")


def flatten(init, lkey=''):
    ret = {}
    key = lkey
    if isinstance(init, list):
        for item in init:
            if isinstance(item, dict) or isinstance(item, list):
                ret.update(flatten(item, key+'_'))
            else:
                ret[key] = item
    elif isinstance(init, dict):

        for rkey, val in init.items():
            key = lkey+rkey

            if isinstance(val, dict) or isinstance(val, list):
                ret.update(flatten(val, key+'_'))
            else:
                ret[key] = val

    return ret


@handle_exception
def convert_to_dict(config):
    """
    Reads the config file and convert it to dict
    Params: 
        config = parsed config values from ConfigParser.read 
    Return Value= config values converted to dict (<dict>)
    """
    dictionary = {}
    for section in config.sections():
        prefix = section+"_"
        for option in config.options(section):
            dictionary[prefix+option] = config.get(section, option)
    return dictionary


@retry_with_default_stanza
@handle_exception
def read_conf(file_path, retry=0):
    """
    Reads the config files of type .conf, .cfg and .ini.
    Params: 
        file_path = Path to the file
        retry = 0 to read the conf file for first time
        retry = 1 to read again when there is no section header in config file
    Return value: config parsed(<dict>)
    """
    if retry == 0:
        if os.path.exists(file_path):
            logger.info("File Found")
            with open(file_path):
                config = configparser.ConfigParser(
                    interpolation=configparser.ExtendedInterpolation())
                config.read(file_path)
                return convert_to_dict(config)

        else:
            logger.error("Config file {} not found.".format(
                file_path.split("/")[-1]))
            print("Config file not found. Please try again!")
            sys.exit(0)
    elif retry == 1:
        config = {}
        logger.info("Trying with adding default header to file {}.".format(
            file_path.split("/")[-1]))
        with open(file_path) as fp:
            for line in fp.readlines():
                if line.startswith('#'):
                    continue
                print(line)
                key, val = line.strip().split('=')
                config["default_"+key.strip()] = val.strip()
        logger.info("Worked with adding default header to file {}.".format(
            file_path.split("/")[-1]))
        return config
    else:
        logger.info("Config file is faulty {}.".format(
            file_path.split("/")[-1]))
        sys.exit(0)
    return config


@handle_exception
def conf_to_env(config_dict):
    """
    Sets the environment variables from parsed config dict.
    Params: 
        config_dict = parsed config values as dict
    Return Value= None
    """
    op_path = input(
        "Enter the path to dir where to create .env or existing path to append configurations to .env file\nPress enter to keep it in current dir.\nPath: ")
    __location__ = os.path.realpath(os.path.join(
        os.getcwd(), os.path.dirname(__file__)))
    if not op_path:
        logger.info(".env file not given")
        logger.info("Creating .env file at {}/.env".format(__location__))
        op_path = "{}/.env".format(__location__)

    for key, val in config_dict.items():
        if isinstance(val, dict):
            for k, v in val.items():
                if v is None:
                    continue
                k = str(k).strip()
                v = str(v).strip()

                logger.info("Setting env variable {}={}".format(k, v))
                os.environ[k] = v
                dotenv.set_key(op_path, k, os.environ[k])
        else:
            if val is None:
                continue
            key = str(key).strip()
            val = str(val).strip()
            logger.info("Setting env variable {}={}".format(key, val))
            os.environ[key] = val
            dotenv.set_key(op_path, key, os.environ[key])
        print("Dumped into file {}.".format(op_path))


@handle_exception
def conf_to_json(config_dict):
    """
    Converts the parsed config dict to JSON and dumps into the json file
    Params: 
        config_dict = parsed config values as dict
    Return Value= None
    """
    op_path = input("Enter the path to dir where to create .json file or existing path to append configurations to json file\nPress enter to create new json in current dir.\nPath: ")
    if os.path.isfile(op_path):
        logger.info("JSON file {} found".format(op_path.split("/")[-1]))
        with open(op_path, "r") as result:
            logger.info("Reading json file {}".format(op_path.split("/")[-1]))
            json_object = json.load(result)
        json_object[config_name+"."+file_extension] = config_dict
        with open(op_path, "w") as jsonFile:
            logger.info("Writing configs to json file {}".format(
                op_path.split("/")[-1]))
            json.dump(json_object, jsonFile)
        logger.info("Writing configs to json file {} Completed".format(
            op_path.split("/")[-1]))
        print("Dumped into file {}.".format(op_path))
    else:
        op_path = ".env"
        __location__ = os.path.realpath(os.path.join(
            os.getcwd(), os.path.dirname(__file__)))
        logger.info("JSON file {} not found!".format(op_path.split("/")[-1]))
        logger.info("Creating new file in dir {}".format(__location__))
        print("File not found. Creating new file {}".format(__location__))
        json_object = {}
        json_object[config_name+"."+file_extension] = config_dict
        with open("result.json", "w+") as jsonFile:
            logger.info("Writing configs to json file {}".format(
                op_path.split("/")[-1]))
            json.dump(json_object, jsonFile)
        logger.info("Writing configs to json file {} Completed".format(
            op_path.split("/")[-1]))
        print("Dumped into file at {}/result.json.".format(__location__))


@handle_exception
def load_yaml(file_path):
    """
    Loads the .yaml type of config file
    Params: 
        file_path = path to .yaml type of config file(<str>)
    Return Value= Nothing
    """
    if os.path.exists(file_path):
        logger.info("Found yaml file {}".format(file_path.split("/")[-1]))
        with open(file_path) as f:
            logger.info("Reading configs from yaml file {}".format(
                file_path.split("/")[-1]))
            config = yaml.load(f, Loader=yaml.SafeLoader)
            return flatten(config)

    else:
        logger.warning("Yaml file {} not found".format(
            file_path.split("/")[-1]))
        print("Config file not found. Please try again!")
        sys.exit(1)


def menu_options(config):
    """
    Prints the menu on the terminal and call functions based on return value
    """
    if not isinstance(config, dict):
        config_dict = convert_to_dict(config)
    else:
        config_dict = config
    choice = input("Enter 1 to convert it to dict\nEnter 2 to convert put it in .env file and set it as environment variable\nEnter 3 to put it in .json file\nYour Choice:")
    if choice == "1":
        logger.info("User chose to convert config to dict")
        print(config_dict)
    elif choice == "2":
        conf_to_env(config_dict)
        logger.info(
            "User chose to put config in .env file and set it as environment variable")
    elif choice == "3":
        logger.info("User chose to put config in .json file")

        conf_to_json(config_dict)
    else:
        logger.warning("User entered invalid choice")
        print("Invalid Choice! Try Again!")


def main():
    """
    Main driver function
    """
    file_path = get_file_path()
    logger.info("Finfding File {}".format(file_path))
    config_name = (file_path.split("/")[-1]).split(".")[0]
    file_extension = pathlib.Path(file_path).suffix[1:]
    if file_extension in supported_file_types[:3]:
        config = read_conf(file_path)
    elif file_extension == "yaml":
        config = load_yaml(file_path)
    else:
        print("File is not a supported config file!")
        logger.info("File is not a supported config file")
        sys.exit(1)

    menu_options(config)


if __name__ == "__main__":
    main()
