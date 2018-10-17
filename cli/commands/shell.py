import argparse
import sys
from pypsi.shell import Shell
from pypsi.core import Command
from core.rpc import minionRPC_pb2
from pypsi.ansi import AnsiCodes
from pypsi.commands.exit import ExitCommand
from pypsi.core import Command, PypsiArgParser, CommandShortCircuit

HelpTopic= "starts a interactive shell on the minion"

ShellCmdUsage = "%(prog)s [-h]"

class ShellCommand(Command):
    def __init__(self, topic='proxy', name='shell', brief=HelpTopic, **kwargs):
        self.parser = PypsiArgParser(
            prog=name,
            description=brief,
            usage=ShellCmdUsage
        )
        super(ShellCommand, self).__init__(
            name=name, usage=self.parser.format_help(), topic=topic,
            brief=brief, **kwargs
        )

    def run(self, shell, args):
        if not self.check_connected(shell):
            self.error("shell", "Not currently connected to minion")
            return 0
        print(f'Starting interactive shell with: {shell.connect}')
        minionshell = MinionShell(shell.connect, shell)
        minionshell.cmdloop()
        print(f'Closed interactive shell with: {shell.connect}')

    def check_connected(self, shell):
        minion = shell.connect
        if minion is not None:
            return True

class MinionShell(Shell):
    def __init__(self, minion, shell):
        self.master_shell = shell
        self.minion = minion
        self.log = shell.log
        self.dir = self.get_initial_prompt()
        super(MinionShell, self).__init__()
        self.prompt = "{green}[({p}{minion}{green}) in {blue}{dir}{green}]>{r} ".format(
            r=AnsiCodes.reset.prompt(), green=AnsiCodes.green.prompt(), 
            p=AnsiCodes.purple.prompt(), blue=AnsiCodes.blue.prompt(),
            minion=minion, dir=self.dir
        )
        self.fallback_cmd = None

    def on_cmdloop_begin(self):
        print(AnsiCodes.clear_screen)
    
    def get_initial_prompt(self):
        params = minionRPC_pb2.Empty()
        rpc = self.master_shell.minions[self.minion]['rpc']
        try:
            ret = rpc.getPrompt(params)
        except Exception as e:
            self.log.error(str(e))
            self.error(f"Failed to retrieve prompt from minion: {self.minion}")
            self.running = False
        if ret:
            return ret.prompt
        else:
            self.error(f"Failed to retrieve prompt from minion: {self.minion}")
            self.running = False

    def execute(self, raw):
        if 'exit' in raw:
            self.running = False
            return
        if '' == raw:
            return
        rpc = self.master_shell.minions[self.minion]['rpc']
        l_line = None
        try:
            stream = rpc.runShellCommand(
                minionRPC_pb2.commandReq(
                    stdin=raw,
                    cwd=self.dir
                )
            )
            for line in stream:
                #if l_line is not None:
                sys.stdout.write(line.stdout)
                #    l_line = line.stdout
                #else:
                #    l_line = line.stdout
            #self.dir = l_line.rstrip()
            #self.update_prompt()
        except Exception as e:
            self.log.error(str(e))
            self.error(f"Shell command: {raw} failed: {str(e)}")

    def update_prompt(self):
        self.prompt = "{green}[({p}{minion}{green}) in {blue}{dir}{green}]>{r} ".format(
            r=AnsiCodes.reset.prompt(), green=AnsiCodes.green.prompt(), 
            p=AnsiCodes.purple.prompt(), blue=AnsiCodes.blue.prompt(),
            minion=self.minion, dir=self.dir
        )
    
    def run_local(self, cmd):
        pass

    