import logging, sys

FORMAT = '%(asctime)s %(levelname)s %(message)s'

class LoggingUtil:

    __instance = None

    @staticmethod
    def get_log():
        '''
        Static access method
        '''
        return LoggingUtil.__instance.log

    def __init__(self, config):
        self.path = config.log.get('path','')
        self.level = config.log.get('level','')
        self.name = config.log.get('name', 'proxy')
        self._start_logging()
        LoggingUtil.__instance = self

    def _start_logging(self):
        '''
        Method for initializing the Argos logger
        '''
        self.log = logging.getLogger(self.name)

        if self.path == '':
            logger_handler = logging.StreamHandler(sys.stdout)
        else:
            logger_handler = logging.FileHandler(self.path)

        if self.level == 'debug':
            self.log.setLevel(logging.DEBUG)
            logger_handler.setLevel(logging.DEBUG)
        elif self.level == 'warn':
            self.log.setLevel(logging.WARN)
            logger_handler.setLevel(logging.WARN)
        elif self.level == 'error':
            self.log.setLevel(logging.ERROR)
            logger_handler.setLevel(logging.ERROR)
        elif self.level == 'info':
            self.log.setLevel(logging.INFO)
            logger_handler.setLevel(logging.INFO)
        else: 
            self.log.setLevel(logging.DEBUG)
            logger_handler.setLevel(logging.DEBUG)
            self.level = 'debug'

        logger_formatter = logging.Formatter(FORMAT)
        logger_handler.setFormatter(logger_formatter)

        self.log.addHandler(logger_handler)

        self.log.info("Logger successfully started...")
        self.log.info("Log level currently set to: %s", self.level)
