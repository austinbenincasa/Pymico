from pypsi.core import Command, PypsiArgParser, CommandShortCircuit
from pypsi.format import Table, Column, obj_str
from pypsi.ansi import AnsiCodes
import sys

HelpTopic= "displays infomation of minions currently configured with master"

ListCmdUsage = "%(prog)s [-h]"

class ListCommand(Command):

    def __init__(self, topic='proxy', brief=HelpTopic, name='list', **kwargs):
        self.parser = PypsiArgParser(
            prog=name,
            description=brief,
            usage=ListCmdUsage
        )
        super(ListCommand, self).__init__(
            name=name, usage=self.parser.format_help(), topic=topic,
            brief=brief, **kwargs
        )

    def run(self, shell, args):
        print("\nConfigured minions:\n")
        table = Table(
                    columns=(
                        Column('Name', Column.Shrink),
                        Column('IP Address', Column.Shrink),
                        Column('Plugins', Column.Grow)
                    ),
                    spacing=4
                )
        for name in shell.minions:
            table.append(name, shell.minions[name]['ip'], obj_str(shell.minions[name]['plugins']))
        table.write(sys.stdout)
        print()