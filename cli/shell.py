from pypsi.shell import Shell
from pypsi.plugins.cmd import CmdPlugin
from pypsi.plugins.block import BlockPlugin
from pypsi.plugins.hexcode import HexCodePlugin
from pypsi.commands.system import SystemCommand
from pypsi.plugins.multiline import MultilinePlugin
from pypsi.commands.xargs import XArgsCommand
from pypsi.commands.exit import ExitCommand
from pypsi.plugins.variable import VariablePlugin
from pypsi.plugins.history import HistoryPlugin
from pypsi.plugins.alias import AliasPlugin
from pypsi.commands.echo import EchoCommand
from pypsi.commands.include import IncludeCommand
from pypsi.commands.help import HelpCommand, Topic
from pypsi.commands.tail import TailCommand
from pypsi.plugins.comment import CommentPlugin
from pypsi.ansi import AnsiCodes
from pypsi import topics

from core import VERSION as version
from cli.commands.minion import MinionCommand
from cli.commands.list import ListCommand
from cli.commands.disconnect import DisconnectCommand
from cli.commands.connect import ConnectCommand
from cli.commands.plugin import PluginCommand
from cli.commands.log import LogCommand
from cli.commands.shell import ShellCommand


import socket
import sys


class MasterShell(Shell):
    '''
    Master CLI for interfacing with configred minion nodes
    '''
    minion_cmd = MinionCommand()
    list_cmd = ListCommand()
    con_cmd = ConnectCommand()
    dis_cmd = DisconnectCommand()
    plg_cmd = PluginCommand()
    log_cmd = LogCommand()
    shell_cmd = ShellCommand()    
    system_cmd = SystemCommand(use_shell=(sys.platform == 'win32'))
    ml_plugin = MultilinePlugin()
    xargs_cmd = XArgsCommand()
    exit_cmd = ExitCommand()
    history_plugin = HistoryPlugin()
    cmd_plugin = CmdPlugin(cmd_args=1)
    tail_cmd = TailCommand()
    help_cmd = HelpCommand()
    var_plugin = VariablePlugin(case_sensitive=False, env=False)

    def __init__(self, master=None):
        super(MasterShell, self).__init__()
        self.master = master
        self.minions = master._minions
        self.controller = master._controllers
        self.log = master.log
        self.connect = None
        self.version = version

        self.prompt = "{green}[({yel}Master@{ip}{green})]>{r} ".format(
            gray=AnsiCodes.gray.prompt(), r=AnsiCodes.reset.prompt(),
            cyan=AnsiCodes.cyan.prompt(), green=AnsiCodes.green.prompt(),
            ip=socket.gethostname(), yel=AnsiCodes.yellow
        )
        self.fallback_cmd = self.system_cmd

        self.help_cmd.add_topic(self, Topic("shell", "Builtin Shell Commands"))
        self.help_cmd.add_topic(self, Topic("proxy", "Proxy Commands"))
        self._sys_bins = None


    def on_cmdloop_begin(self):
        print(AnsiCodes.clear_screen)
        banner = (
            "{blue} __  __           _             ____ _     ___\n"
            "|  \/  | __ _ ___| |_ ___ _ __ / ___| |   |_ _|\n"
            "| |\/| |/ _` / __| __/ _ \ '__| |   | |    | |\n"
            "| |  | | (_| \__ \ ||  __/ |  | |___| |___ | |\n"
            "|_|  |_|\__,_|___/\__\___|_|   \____|_____|___|\n"
            "{green}Version: {version}{r}\n"
        ).format(green=AnsiCodes.green, blue=AnsiCodes.blue,
            r=AnsiCodes.reset, version=str(self.version)
        )
        print(banner)

    def add_prompt_connect(self):
        self.prompt = "{green}[({yel}Master@{ip}{green})->{p}{minion}{green}]>{r} ".format(
            gray=AnsiCodes.gray.prompt(), r=AnsiCodes.reset.prompt(),
            cyan=AnsiCodes.cyan.prompt(), green=AnsiCodes.green.prompt(),
            ip=socket.gethostname(), yel=AnsiCodes.yellow, p=AnsiCodes.purple.prompt(),
            minion=self.connect
        )
 
    def remove_prompt_connect(self):
        self.prompt = "{green}[({yel}Master@{ip}{green})]>{r} ".format(
            gray=AnsiCodes.gray.prompt(), r=AnsiCodes.reset.prompt(),
            cyan=AnsiCodes.cyan.prompt(), green=AnsiCodes.green.prompt(),
            ip=socket.gethostname(), yel=AnsiCodes.yellow.prompt()
        )

    def get_command_name_completions(self, prefix):
        return sorted(
            [name for name in self.commands if name.startswith(prefix)]
        )
