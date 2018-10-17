# Pymico
Python Multisystem Interface Controller

## What is Pymico?
Pymico or Python Multisystem Interface Controller is a system management and orchestration tool developed in Python utilizing gPRC.
Pymico provides a single interface for managing systems and their services across a network or cloud infastructure.

## What is a Minion?
A minion is a system endpoint service that is configured on every system to be managed by Pymico. Minions handle the processing and execution of RPC calls that are issued from the Master. A Minion is configured with plugins which contain the functionality for interacting with a system and it services. These plugins and their functions are what is excuted by a Minion given the corresponding RPC call from the master. For example, if a administrator wanted to update the configuration file of a NGINX server the administrator would configure the Minion on the system to load the NGINX plugin that would provide the functionality for easily updating the configuration file. A Minion can be configured with multiple plugins and plugins can be created and added into any Minion by an administrator. 

## What is a Master?

A master is system service that issues RPC calls to configured Minions across a network. The service provides a interactive CLI for interfacing with the various Minions. Current features of the CLI include:

- Determing avaliable Minions
- Determing currently loaded plugins on a Minion
- Executing a plugin function on a Minion 
- Starting a interactive shell session on a Minion
- Interactive CLI Help

## Purpose of Plugins

The purpose of a plugin is to dynamically give functionallity to a 
minion and thus a master to interact with programs and services that
are installed on a minion. Instead of using configuration files like `Chef`, `Puppet` or `Salt`. Configuration of a system is managed through defining python functions in a plugin class. A plugin to manage a Web Server could look like the following.

```python 
class WebServerPlugin(BasePlugin):
    '''
    Plugin to manage my webserver
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "SystemPlugin"

    @staticmethod
    def list_functions():
        return [
            WebServerPlugin.start,
        ]

    @staticmethod
    def list_functions_names():
        return ['start', 'stop']

    def start(self):
      # todo
    
    def stop(self):
      # todo

```

## Purpose of Controllers

The purpose of a plugin is to dynamically give functionallity to a 
Master to interact with programs or services that are installed on the master.
