import main
import unittest
import mock
from mock import patch

class TestMain(unittest.TestCase):
    """
    Test main file
    """
    @patch("builtins.input")
    def test_get_file_path(self, mock_input):
        mock_input.return_value = "test"
        return_value = main.get_file_path()
        self.assertEqual(return_value, "test")

    @patch("builtins.open")
    @patch("main.configparser.ConfigParser")
    @patch("main.logger")
    @patch("main.os")
    def test_read_conf_with_first_try_with_file_exist(self,mock_os,mock_logger, mock_conf_parser, mock_open):
        mock_os.path.exists.return_value = True
        instance = mock_conf_parser.return_value 
        main.read_conf("test_path")
        mock_os.path.exists.assert_called_with("test_path")
        mock_logger.info.assert_called_once()
        mock_conf_parser.assert_called_once()
        instance.read.assert_called_once()
        mock_open.assert_called_once()
    
    @patch("main.print")
    @patch("main.logger")
    @patch("main.os")
    def test_read_conf_with_first_try_with_file_not_exist(self,mock_os,mock_logger, mock_print):
        mock_os.path.exists.return_value = False
        main.read_conf("test_path")
        mock_os.path.exists.assert_called_with("test_path")
        mock_logger.error.assert_called_with("Config file test_path not found.")
        mock_print.assert_called_with("Config file not found. Please try again!")


    @patch("builtins.open", new_callable=mock.mock_open, read_data="test=test")
    @patch("main.logger")
    def test_read_conf_with_second_try(self, mock_logger, mock_open):
        return_val = main.read_conf("test_path", retry=1)
        self.assertEqual(mock_logger.info.call_count, 2)
        mock_open.assert_called_once()
        self.assertEqual(return_val, {'test': 'test'})

    @patch("builtins.open", new_callable=mock.mock_open, read_data="#test")
    @patch("main.logger")
    def test_read_conf_with_second_try_with_comment(self, mock_logger, mock_open):
        return_val = main.read_conf("test_path", retry=1)
        self.assertEqual(mock_logger.info.call_count, 2)
        mock_open.assert_called_once()
        self.assertEqual(return_val, {})
    

    @patch("main.logger")
    def test_read_conf_with_last_try(self, mock_logger):
        with self.assertRaises(SystemExit):
            return_val = main.read_conf("test_path", retry=3)
        self.assertEqual(mock_logger.info.call_count, 1)

        
    def test_convert_to_dict(self):
        mock_obj = mock.MagicMock()
        mock_obj.sections.return_value = ["test"]
        mock_obj.options.return_value = ["test"]
        mock_obj.get.return_value = ["test"]
        return_value = main.convert_to_dict(mock_obj)
        self.assertEqual(return_value, {'test': {'test': ['test']}})

    @patch("main.print")
    @patch("main.dotenv")
    @patch("main.logger")
    @patch("builtins.input")
    @patch("main.os")
    def test_conf_to_env(self, mock_os, mock_inp, mock_logger, mock_dotenv, mock_print):
        mock_inp.return_value = None
        mock_os.path.realpath.return_value=None
        config_dict = {"1":{"1":"2","2":None},"2":"2","3":None}
        main.conf_to_env(config_dict)
        self.assertEqual(mock_logger.info.call_count,4)
    
    @patch("main.print")
    @patch("builtins.open", new_callable=mock.mock_open, read_data='{"1":"1"}')
    @patch("main.logger")
    @patch("builtins.input")
    @patch("main.os")
    def test_conf_to_json(self, mock_os, mock_inp, mock_logger, mock_file, mock_print):
        config_name="abc"
        file_extension = "conf"
        mock_inp.return_value = "abc/abc.json"
        main.conf_to_json({"2":"2"})
        mock_file.assert_called_with("abc/abc.json", 'w')
        mock_os.path.isfile.return_value = True            
        self.assertEqual( mock_logger.info.call_count, 4)
        mock_print.assert_called_once()

    @patch("main.print")
    @patch("builtins.open", new_callable=mock.mock_open, read_data='{"1":"1"}')
    @patch("main.logger")
    @patch("builtins.input")
    @patch("main.os")
    def test_conf_to_json_without_output_path(self, mock_os, mock_inp, mock_logger, mock_file, mock_print):
        config_name="abc"
        file_extension = "conf"
        mock_os.path.isfile.return_value = False
        main.conf_to_json({"2":"2"})
        mock_file.assert_called_with("result.json", 'w+')            
        self.assertEqual( mock_logger.info.call_count, 4)
        self.assertEqual(mock_print.call_count, 2)

    @patch("main.sys.exit")
    @patch("main.print")
    @patch("main.logger.warning")
    @patch("main.os")
    def test_load_yaml_else_condition(self, mock_os, mock_logger, mock_print, mock_exit):
        mock_os.path.exists.return_value = False
        main.load_yaml("test_path")
        mock_os.path.exists.assert_called_with("test_path")
        mock_logger.assert_called_once()
        mock_print.assert_called_once()
        mock_exit.assert_called_once()

    @patch("builtins.open")
    @patch("main.yaml.load")
    @patch("main.logger")
    @patch("main.os")
    def test_load_yaml_with_if_condition(self, mock_os, mock_logger, mock_yaml, mock_open):
        mock_os.path.exists.return_value = True
        main.load_yaml("test_path")
        mock_os.path.exists.assert_called_with("test_path")
        mock_logger.info.assert_called_with("Reading configs from yaml file test_path")
        mock_yaml.assert_called_once()
        mock_open.assert_called_with("test_path")

    @patch("main.convert_to_dict")
    @patch("builtins.input")
    @patch("main.print")
    @patch("main.logger")
    def test_menu_options_with_choice_1(self, mock_logger, mock_print, mock_inp, mock_ctd):
        mock_inp.return_value = "1"
        main.menu_options("test=test")
        mock_logger.info.assert_called_once()
        mock_print.assert_called_once()

    @patch("main.conf_to_env")
    @patch("main.convert_to_dict")
    @patch("builtins.input")
    @patch("main.logger")
    def test_menu_options_with_choice_2(self, mock_logger, mock_inp, mock_ctd, mock_cte):
        mock_ctd.return_value = {"1":"1"}
        mock_inp.return_value = "2"
        main.menu_options("test=test")
        mock_logger.info.assert_called_once()       

    @patch("main.conf_to_json")
    @patch("builtins.input")
    @patch("main.logger")
    def test_menu_options_with_choice_3(self, mock_logger, mock_inp, mock_cte):
        mock_inp.return_value = "3"
        main.menu_options({"test":"test"})
        mock_logger.info.assert_called_once() 
        mock_cte.assert_called_once()    

    @patch("builtins.input")
    @patch("main.print")
    @patch("main.logger")
    def test_menu_options_with_choice_4(self, mock_logger, mock_print, mock_inp):
        mock_inp.return_value = "4"
        main.menu_options({"test":"test"})
        mock_logger.warning.assert_called_once() 
        mock_print.assert_called_once() 

    @patch("main.menu_options")
    @patch("main.read_conf")
    @patch("main.get_file_path")
    @patch("main.logger")    
    def test_main(self, mock_logger, mock_gfp, mock_read_conf, mock_menu_options):
        
        mock_gfp.return_value = "abc/abc.conf"
        main.main()
        mock_logger.info.assert_called_once()
        mock_gfp.assert_called_once()
        mock_read_conf.assert_called_once()
        mock_menu_options.assert_called_once()

    @patch("main.menu_options")
    @patch("main.load_yaml")
    @patch("main.get_file_path")
    @patch("main.logger")    
    def test_main_with_yaml(self, mock_logger, mock_gfp, mock_load_yaml, mock_menu_options):
        
        mock_gfp.return_value = "abc/abc.yaml"
        main.main()
        mock_logger.info.assert_called_once()
        mock_gfp.assert_called_once()
        mock_load_yaml.assert_called_once()
        mock_menu_options.assert_called_once()



if __name__ == "__main__":
     unittest.main()
