from core.rpc import minionRPC_pb2
from core.rpc import minionRPC_pb2_grpc
from core.plugins.plugin import BasePlugin
import psutil 
import socket
import json


class SystemPlugin(BasePlugin):
    '''
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "SystemPlugin"

    @staticmethod
    def list_functions():
        return [
            SystemPlugin.interfaces,
            SystemPlugin.system_information
        ]

    @staticmethod
    def list_functions_names():
        return ['interfaces', 'system_information']

    def system_information(self):
        '''
        Displays information about the minion system
        '''
        ret = {}
        ret['hostname'] = socket.gethostname()
        ret['cpu_usage'] = psutil.cpu_percent(interval=None)
        ret['cpus'] = psutil.cpu_count(logical=False)
        ret['mem_usage'] = psutil.virtual_memory().percent
        return minionRPC_pb2.functionResp(
            data=json.dumps(ret),
            type="json",
            error=0
        )

    def interfaces(self):
        '''
        Displays statistics about the System 
        '''
        return minionRPC_pb2.functionResp(
            data="Not yet implemented",
            type="text",
            error=0
        )
