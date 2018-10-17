import os
from sys import platform


class OsUtil:
    '''
    Provides functionality for simplistic cross platform runtime
    '''
    @staticmethod
    def get_minion_config_path():
        '''
        Properly handles path for version file
        '''
        if platform == "linux" or platform == "linux2":
            return str(os.getcwd() + '/minion.yml')
        elif platform == "darwin":
            return str(os.getcwd() + '//minion.yml')            
        elif platform == "win32":
            return str(os.getcwd() + '\\minion.yml')
        else:
            return str(os.getcwd() + '\\minion.yml')

    @staticmethod
    def get_master_config_path():
        '''
        Properly handles path for version file
        '''
        if platform == "linux" or platform == "linux2":
            return str(os.getcwd() + '/master.yml')
        elif platform == "darwin":
            return str(os.getcwd() + '//master.yml')            
        elif platform == "win32":
            return str(os.getcwd() + '\\master.yml')
        else:
            return str(os.getcwd() + '\\master.yml')

    @staticmethod
    def get_master_log_path():
        '''
        Properly handles path for version file
        '''
        if platform == "linux" or platform == "linux2":
            return str(os.getcwd() + '/master.log')
        elif platform == "darwin":
            return str(os.getcwd() + '//master.log')            
        elif platform == "win32":
            return str(os.getcwd() + '\\master.log')
        else:
            return str(os.getcwd() + '\\master.log')

    @staticmethod
    def get_prompt_path():
        if platform == "linux" or platform == "linux2":
            return str(os.getcwd())
        elif platform == "darwin":
            return str(os.getcwd())            
        elif platform == "win32":
            return str(os.getcwd())
        else:
            return str(os.getcwd())

    @staticmethod
    def determine_cwd():
        if platform == "linux" or platform == "linux2":
            return " && pwd"
        elif platform == "darwin":
            return " "
        elif platform == "win32":
            return " && (Resolve-Path .\).Path"

