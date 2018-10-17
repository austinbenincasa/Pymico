from core.util.logging_util import LoggingUtil
from core.util.os_util import OsUtil
from core.exceptions.util_exceptions import VersionException, ConfigException
from yaml import load, YAMLError
import yaml

class ConfigUtil:
    '''
    Provides functionality for interacting with a yaml configuation file
    '''
    @staticmethod
    def load_minion_config(path):
        '''
        Loads the config file into a dictonary
        '''
        if path is None or path == "":
            path = OsUtil.get_minion_config_path()
        try:
            config_data = open(path, 'r')
        except Exception as e:
            raise ConfigException(str("Could not open config file: {}").format(path))
        try:
            return load(config_data)
        except YAMLError as e:
            raise ConfigException(str("Could not parse config file: {}").format(str(e)))

    @staticmethod
    def load_master_config(path):
        '''
        Loads the config file into a dictonary
        '''
        if path is None or path == "":
            path = OsUtil.get_master_config_path()
        try:
            config_data = open(path, 'r')
        except Exception as e:
            raise ConfigException(str("Could not open config file: {}").format(path))
        try:
            return load(config_data)
        except YAMLError as e:
            raise ConfigException(str("Could not parse config file: {}").format(str(e)))
