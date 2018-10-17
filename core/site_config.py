class MasterConfig(object):
    '''
    Object to hold configuration parameters
    '''
    def __init__(self, yaml):
        self.core = yaml['SiteConfig'].get('core', {})
        self.log = yaml['SiteConfig'].get('log', {})
        self.minions = yaml['SiteConfig'].get('minions', [])
        self.controllers = yaml['SiteConfig'].get('controllers', [])

class MinionConfig(object):
    '''
    Object to hold configuration parameters
    '''
    def __init__(self, yaml):
        self.core = yaml['SiteConfig'].get('core', {})
        self.log = yaml['SiteConfig'].get('log', {})
        self.plugins = yaml['SiteConfig'].get('plugins', {})
