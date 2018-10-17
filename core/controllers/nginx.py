from core.rpc import minionRPC_pb2
from core.rpc import minionRPC_pb2_grpc
from core.controllers.controller import BaseController


class NginxController(BaseController):
    '''
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "NginxController"

    def stats(self):
        print('cool it works!')

    def alive(self):
        return minionRPC_pb2.functionResp(reply="good")