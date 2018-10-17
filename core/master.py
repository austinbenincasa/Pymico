import grpc
import time
from core import VERSION as version
from collections import defaultdict
from cli.shell import MasterShell
from core.rpc import minionRPC_pb2
from core.rpc import minionRPC_pb2_grpc
from core.site_config import MasterConfig
from core.util.logging_util import LoggingUtil
from core.util.config_util import ConfigUtil
from core.util.loader_util import LoaderUtil
from core.exceptions.util_exceptions import LoaderException, ConfigException

class Master:
    '''
    '''
    def __init__(self, cli):
        self._cli = cli
        self._minions = defaultdict(lambda:defaultdict(dict))

    def init(self, config_path):
        self._parse_config(config_path)
        self._start_logging()
        self._load_controllers()
        self._register_minions()
        self._determine_minions_plugins()
        self.running = True

    def run(self):
        if self.running and self._cli:
            shell = MasterShell(
                master=self
            )
            shell.cmdloop()
        if self.running and not self._cli:
            #TODO run headless
            pass
        else:
            self.log.error("An error occured during startup, master not running")

    def _start_logging(self):
        LoggingUtil(self._config)
        self.log = LoggingUtil.get_log()
        self.log.info("Starting master node...")

    def reload_minions(self):
        self._register_minions()
        self._determine_minions_plugins()
    
    def reload_controller(self):
        self._load_controllers()

    def _register_minions(self):
        minions = self._config.minions
        if minions is not []:
            for minion in minions:
                address = minion['address']
                port = minion['port']
                channel = grpc.insecure_channel(f'{address}:{port}')
                self._minions[minion['name']] = {
                    'ip': address,
                    'channel': channel,
                    'plugins': [],
                    'rpc': minionRPC_pb2_grpc.MinionRPCStub(channel)
                }
        else:
            self.log.error("No minions have be defined in config file")
            self.running = False

    def _determine_minions_plugins(self):
        msg = minionRPC_pb2.Empty()
        for minion in self._minions:
            try:
                plugins = self._minions[minion]['rpc'].getPlugins(msg)
                self._minions[minion]['plugins'] = plugins.reply.split(" ")
            except Exception as e:
                self.log.error("Could not determine plugins for: %s", minion)

    def _load_controllers(self):
        self._controllers = defaultdict(dict)
        controllers = self._config.controllers
        for controller in controllers:
            try:
                obj = LoaderUtil.load_controller(controller)
                self._controllers[controller] = obj(log=self.log)
                self.log.info("Successfully loaded controller: %s", controller)
            except LoaderException as e:
                self.log.warn("Could not load controller: %s", str(e))
            except Exception as e:
                self.log.error("Could not load controller: %s", str(e))
        if len(controllers) < 1:
            self.log.warn("No controllers were loaded into master")

    def _parse_config(self, config_path):
        try:
            yaml = ConfigUtil.load_master_config(config_path)
            self._config = MasterConfig(yaml)
        except ConfigException as e:
            self.log.error(str(e))
            self.running = False
