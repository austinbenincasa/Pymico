from pypsi.core import Command, PypsiArgParser, CommandShortCircuit
import argparse
from pypsi.ansi import AnsiCodes

HelpTopic= "disconnects from a minion's interactive management"

DisconnectCmdUsage = "%(prog)s NAME [-h]"

class DisconnectCommand(Command):

    def __init__(self, topic='proxy', name='disconnect', brief=HelpTopic, **kwargs):
        self.parser = PypsiArgParser(
            prog=name,
            description=brief,
            usage=DisconnectCmdUsage
        )

        self.parser.add_argument(
            'name', help='name of minion',
            metavar="NAME", completer=self.complete_minions
        )

        super(DisconnectCommand, self).__init__(
            name=name, usage=self.parser.format_help(), topic=topic,
            brief=brief, **kwargs
        )

    def run(self, shell, args):
        try:
            ns = self.parser.parse_args(args)
        except CommandShortCircuit as e:
            return e.code
        if not ns.name:
            pass
        elif ns.name == shell.connect:            
            shell.connect = None
            shell.remove_prompt_connect()
            print(f"Successfully disconnected from minion: {ns.name}")
        else:
            self.error(shell,f"master is not currently connect to {ns.name}")

    def complete(self, shell, args, prefix):
        if len(args) == 1:
            return self.complete_minions(shell, args, prefix)

    def complete_minions(self, shell, args, prefix):
        return sorted(
            [name for name in shell.minions if name.startswith(prefix)]
        )