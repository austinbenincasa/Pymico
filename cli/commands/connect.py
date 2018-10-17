import argparse
from core.rpc import minionRPC_pb2
from pypsi.ansi import AnsiCodes
from pypsi.core import Command, PypsiArgParser, CommandShortCircuit

HelpTopic= "connects to a minion for interactive management"

ConnectCmdUsage = "%(prog)s NAME [-h]"

class ConnectCommand(Command):

    def __init__(self, topic='proxy', name='connect', brief=HelpTopic, **kwargs):
        self.parser = PypsiArgParser(
            prog=name,
            description=brief,
            usage=ConnectCmdUsage
        )

        self.parser.add_argument(
            'name', help='name of minion',
            metavar="NAME", completer=self.complete_minions
        )

        super(ConnectCommand, self).__init__(
            name=name, usage=self.parser.format_help(), topic=topic,
            brief=brief, **kwargs
        )

    def run(self, shell, args):
        try:
            ns = self.parser.parse_args(args)
        except CommandShortCircuit as e:
            return e.code
        if shell.connect is not None:
            self.error(shell, f"could not connect to {ns.name}: currently connected to {shell.connect}")
        elif ns.name in shell.minions:
            if self.test_minion_connection(shell, ns.name): 
                shell.connect = ns.name
                shell.add_prompt_connect()
                print(f"Successfully connected to minion: {ns.name}")
            else:
                self.error(shell, f"could not connect to {ns.name}: failed alive check")
        else:
            self.error(shell, f"cannot connect to {ns.name}: not a configured minion")

    def complete(self, shell, args, prefix):
        if len(args) == 1:
            return self.complete_minions(shell, args, prefix)

    def complete_minions(self, shell, args, prefix):
        return sorted(
            [name for name in shell.minions if name.startswith(prefix)]
        )

    def test_minion_connection(self, shell, minion):
        try:
            rpc = shell.minions[minion]['rpc']
            msg = minionRPC_pb2.Empty()
            ret = rpc.checkAlive(msg)
            if ret.reply == 'alive':
                return True
            else:
                return False
        except Exception as e:
            shell.log.error(str(e))
            return False
