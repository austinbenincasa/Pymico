import grpc
import time
import errno
import sys
import concurrent.futures
from subprocess import Popen, STDOUT, PIPE
from collections import defaultdict
from core.rpc import minionRPC_pb2
from core.rpc import minionRPC_pb2_grpc
from core.site_config import MinionConfig
from core.util.logging_util import LoggingUtil
from core.util.config_util import ConfigUtil
from core.util.loader_util import LoaderUtil
from core.util.os_util import OsUtil
from core.exceptions.util_exceptions import LoaderException, ConfigException



class Minion:
    '''
    '''
    def __init__(self):
        self.server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))

    def init(self, config_path):
        self._parse_config(config_path)
        self._start_logging()
        self._load_plugins()
        minionRPC_pb2_grpc.add_MinionRPCServicer_to_server(
            MinionRPC(
                self,
            ), 
            self.server
        )
        self._running = True

    def run(self):
        self.server.add_insecure_port('[::]:50051')
        self.server.start()
        try:
            if self._running:
                self.log.info("Minion node successfully started")
            while self._running:
                time.sleep(7)
            self.log.warn('Minion is shutting down...')
        except KeyboardInterrupt:
            self.log.warn('Minion is shutting down...')
            self.server.stop(0)

    def _start_logging(self):
        LoggingUtil(self._config)
        self.log = LoggingUtil.get_log()
        self.log.info("Starting minion node")

    def _load_plugins(self):
        self._plugins = defaultdict(dict)
        for plugin in self._config.plugins:
            try:
                obj = LoaderUtil.load_plugin(plugin)
                self._plugins[plugin] = obj(log=self.log)
                self.log.info("Successfully loaded plugin: %s", plugin)
            except LoaderException as e:
                self.log.warn("Could not load plugin: %s", str(e))
            except Exception as e:
                self.log.error("Could not load plugin: %s", str(e))
        if self._config.plugins is []:
            self.log.warn("No plugins were loaded into minion")
    
    def _parse_config(self, config_path):
        try:
            yaml = ConfigUtil.load_minion_config(config_path)
            self._config = MinionConfig(yaml)
        except ConfigException as e:
            self.log.error(str(e))
            self._running = False


class MinionRPC(minionRPC_pb2_grpc.MinionRPCServicer):
    '''
    '''
    def __init__(self, minion):
        self.log = minion.log
        self._plugins = minion._plugins
        self._minion = minion

    def shutdown(self, request, context):
        self._minion._running = False
        self.log.info(f"Received shutdown request")
        return minionRPC_pb2.shutdownResp(reply="okay")
    
    def restart(self, request, context):
        self.log.info(f"Received restart request")
        return minionRPC_pb2.restartResp(reply="okay")
    
    def checkAlive(self, request, context):
        self.log.info(f"Received alive check request")
        return minionRPC_pb2.aliveResp(reply="alive")

    def loadPlugin(self, request, context):
        return minionRPC_pb2.loadResp(reply="okay", error=0)

    def getPlugins(self, request, context):
        self.log.info(f"Received plugins request")
        ret = ''.join(self._plugins)
        return minionRPC_pb2.pluginsResp(reply=ret)

    def getPrompt(self, request, context):
        self.log.info(f"Received prompt request")
        return minionRPC_pb2.promptResp(
            prompt=OsUtil.get_prompt_path()
        )

    def runPluginFunction(self, request, context):
        param = f"{request.plugin}.{request.function}()"
        self.log.info(f"Received plugin function request: {param}")
        if request.plugin in self._plugins.keys():
            method = getattr(self._plugins[request.plugin], request.function)
            if method:
                return method()
            else:
                return minionRPC_pb2.functionResp(
                    data=f"{request.function} is not a function of plugin: {request.plugin}",
                    type="string",
                    error=1
                )
        else:
            return minionRPC_pb2.functionResp(
                data=f"{request.plugin} is not loaded into minion",
                type="string",
                error=1
            )

    def runShellCommand(self, request, context):
        #cmd = request.stdin + OsUtil.determine_cwd() 
        cmd = request.stdin
        try:
            proc = Popen(
                cmd,
                stdout=PIPE,
                stderr=STDOUT,
                shell=True,
                close_fds=True,
                cwd=request.cwd
            )
        except OSError as e:
            return minionRPC_pb2.commandResp(
                stdout=e.strerror,
                code=e.errno,
                cwd=""
            )
        for line in proc.stdout.readlines():
            line = minionRPC_pb2.commandResp(
                stdout=line.decode("utf-8"),
                code=0,
                cwd=""
            )
            yield line
