import abc

class BaseController(object):
    '''
    Base class for Controller
    '''
    __metaclass__  = abc.ABCMeta

    def __init__(self, log):
        self.log = log
    
    @abc.abstractmethod
    def stats(self):
        self.log.error("Stats function was called but has not been implemented in %s() class", self.name)

    @abc.abstractmethod
    def alive(self):
        self.log.error("Stats function was called but has not been implemented in %s() class", self.name)
