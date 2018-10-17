import argparse
from pypsi.core import Command, PypsiArgParser, CommandShortCircuit
from core.util.loader_util import LoaderUtil
from core.rpc import minionRPC_pb2

HelpTopic= "preform action on a minion. must first connect to a minion using `connect`"
MinionCmdUsage = "%(prog)s CMD [-h]"

class MinionCommand(Command):

    def __init__(self, topic='proxy', name='minion', brief=HelpTopic, **kwargs):
        self.parser = PypsiArgParser(
            prog=name,
            description=brief,
            usage=MinionCmdUsage
        )
        subcmd = self.parser.add_subparsers(prog='minion', dest='subcmd', metavar='subcmd')
        subcmd.required = True
        shutdown = subcmd.add_parser(
            'shutdown', help='shutdown the connected minion'
        )
        restart = subcmd.add_parser(
            'restart', help='restart the connected minion'
        )
        load = subcmd.add_parser(
            'load', help='loads a plugin into minion'
        )
        load.add_argument(
            'plugin', metavar='PLUGIN', help='name of plugin to load into minion'
        )
        log = subcmd.add_parser(
            'log', help='print the log of a minion'
        )
        log.add_argument(
            'lines', metavar='LINES', help='range of line number to print <start:finish>'
        )

        super(MinionCommand, self).__init__(
            name=name, usage=self.parser.format_help(), topic=topic,
            brief=brief, **kwargs
        )

    def run(self, shell, args):
        if not self.check_connected(shell):
            self.error("shell", "Not currently connected to minion")
            return 0
        try:
            ns = self.parser.parse_args(args)
        except CommandShortCircuit as e:
            return e.code
        if ns.subcmd == 'shutdown':
            self.shutdown_minion(shell)
        elif ns.subcmd == 'restart':
            self.restart_minion(shell)
        elif ns.subcmd == 'load':
            self.load_plugin(shell, ns.plugin)        

    def complete(self, shell, args, prefix):
        cmds = ['shutdown', 'restart', 'load','log']
        if len(args) == 1:
            return sorted(
                [cmd for cmd in cmds if cmd.startswith(prefix)]
            )

    def check_connected(self, shell):
        minion = shell.connect
        if minion is not None:
            return True
        else:
            False
    
    def shutdown_minion(self, shell):
        params = minionRPC_pb2.Empty()
        rpc = shell.minions[shell.connect]['rpc']
        try:
            ret = rpc.shutdown(params)
        except Exception as e:
            shell.log.error(str(e))
            self.error('shell', f"Failed to shutdown minion: {shell.connect}")
        if ret.reply == "okay":
            print(f'Shutting down minion: {shell.connect}')
        else:
            self.error('shell', f"Failed to shutdown minion: {shell.connect}")

    def restart_minion(self, shell):
        params = minionRPC_pb2.Empty()
        rpc = shell.minions[shell.connect]['rpc']
        try:
            ret = rpc.runPluginFunction(params)
        except Exception as e:
            shell.log.error(str(e))
            self.error('shell', f"Failed to restart minion: {shell.connect}")
        if ret.reply == "okay":
            print(f'Restarting minion: {shell.connect}')
        else:
            self.error('shell', f"Failed to restart minion: {shell.connect}")

    
    def load_plugin(self, shell, plugin):
        try:
            plg = LoaderUtil.load_plugin(plugin)
        except:
            self.error('shell', f"Plugin: {plugin} is not in the available plugin list")
        params = minionRPC_pb2.loadReq(plugin=plugin)
        rpc = shell.minions[shell.connect]['rpc']
        try:
            ret = rpc.loadPlugin(params)
        except Exception as e:
            shell.log.error(str(e))
        if ret.error < 1:
            print(f'Loaded plugin: {plugin} into minion: {shell.connect}')
        else:
            shell.log.error(ret.reply)
            self.error('shell', f"Failed to load plugin: { plugin } in {shell.connect}")


