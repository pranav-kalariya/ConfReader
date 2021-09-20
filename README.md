# ConfReader

This python-based project provides functionality to parse config file and convert it to Dict and dump to env variable or JSON file.

## Steps to set up the environment

1. Create a virtual environment and activate it. follow link: [Virtual Env](https://www.geeksforgeeks.org/python-virtual-environment/)(optional)
2. Clone the package from <link> or download it from <link>
3. Copy package to virualenv(if created).
4. Open terminal in the main folder ConfReader and Hit command `pip install -r requirements.txt`

**Now you are ready to go!**

## Steps to Use:

1. Go to ConfReader directory and run command `python main.py`
2. Enter the absolute path to config file._Supported file types are .conf, .cfg, .yaml._
3. If the config file does not have section header, you might see the message `Could not read the conf file. Retrying with adding default header.`. If the config file is not faulty it will be parsed.
4. You will see 3 options to choose from.

   - Enter 1 to convert the config to Dict format and print it on the terminal
   - Enter 2 to put the configurations in the .env file and set them in environment.

     - Once you select choice 2, you can choose to enter the path of .env file. Enter the path to .env file and it will be written in the path you entered. If there are any variables with the same name already existing then it will be overwritten as with values.

     - If you don't provide the path to .env file then new .env file will be created under the current directory and if it already exist then it will be overwritten.

   - Enter 3 if you want to convert configurations to JSON and dump them to JSON file.

     - Once you select choice 3, you can choose to enter the path of JSON file. Enter the path to JSON file and it will be written in the path you entered with the new key named configs name. For example: if you are reading abc.conf then JSON will be added with `"abc":{<config in json format>}`
     - If you don't provide the path to JSON file then new file will be created under the current directory with name of result.json and if it already exist then it will be appended with the new key as mentioned above.

## TroubleShooting

1. Logs are added in `ConfReader/app.log` file. You can always check the logs.
2. If the section header is not found then you will see logs as below
   `ERROR - Error Occured: File contains no section headers. file: '/home/pranav/Desktop/python_codes/assignments/ConfReader/ConfReader/<configname>'`
   Though you don't need to do anything yet as script will automatically handle this case by adding [default] and you will see logs like this
   `Trying with adding default header to file <config name>.`
   ` INFO - Worked with adding default header to file pyvenv.cfg`. Though if this does not work it means config file is faulty. Please check the config file in this case.
