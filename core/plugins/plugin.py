import abc

class BasePlugin(object):
    '''
    Base class for Plugin
    '''
    __metaclass__  = abc.ABCMeta

    def __init__(self, log):
        self.log = log
