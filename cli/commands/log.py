from pypsi.core import Command, PypsiArgParser, CommandShortCircuit
from core.util.os_util import OsUtil
from pypsi.ansi import AnsiCodes
import argparse
import sys

HelpTopic= "prints the master log to the terminal"
LogCmdUsage = "%(prog)s [-h]"

class LogCommand(Command):

    def __init__(self, topic='proxy', name='log', brief=HelpTopic, **kwargs):
        self.parser = PypsiArgParser(
            prog=name,
            description=brief,
            usage=LogCmdUsage
        )

        self.parser.add_argument(
            '-a', '--all', help="prints out the entire log file", action='store_true'
        )

        self.parser.add_argument(
            '-l','--lines', help='prints out a range of lines <start_line>:<end_line>', metavar="LINES"
        )

        super(LogCommand, self).__init__(
            name=name, usage=self.parser.format_help(), topic=topic,
            brief=brief, **kwargs
        )

    def run(self, shell, args):
        try:
            ns = self.parser.parse_args(args)
        except CommandShortCircuit as e:
            return e.code
        if ns.all and ns.lines:
            self.error('shell', "Cannot specify -l/--lines and -a/--all at the sametime")
            return 1
        elif ns.all:
            self.print_logfile(shell, 0, 0, True)
        elif ns.lines:
            lnum = ns.lines.split(":")
            if len(lnum) > 2 or len(lnum) < 2:
                self.error('shell', "improper format: expecting <start_line>:<end_line>")
                return 1
            else:
                self.print_logfile(shell, lnum[0], lnum[1], False)

    def print_logfile(self, shell, start, end, printall):
        path = shell.config.log.get('path','master.log')
        red=AnsiCodes.red
        r = AnsiCodes.reset
        yellow = AnsiCodes.yellow
        if path == 'master.log':
            path = OsUtil.get_master_log_path()
        try:
            fh = open(path, "r")
            count = 0
            if start == '':
                start = 0
            start = int(start)
            if end != '':
                end = int(end)
            for line in fh:
                if count >= start or printall:
                    if 'ERROR' in line or 'EXCEPTION' in line:
                        sys.stdout.write(f"{red}{line}{r}")
                    elif 'WARN' in line:
                        sys.stdout.write(f"{yellow}{line}{r}")
                    else:
                        sys.stdout.write(line)
                    if (end != '') and ((count + 1) > end) and not printall:
                        fh.close()
                        return 0
                count += 1
            fh.close()
        except Exception as e:
            self.error('shell', f"could not display logfile {path}")
