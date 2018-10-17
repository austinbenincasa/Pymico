from pypsi.core import Command, PypsiArgParser, CommandShortCircuit
import argparse
import sys
import grpc
from core.rpc import minionRPC_pb2
from core.util.loader_util import LoaderUtil
from core.util.print_util import PrintUtil
from pypsi.format import Table, Column

HelpTopic= "Runs a plugin function on currently connected minion. must first be connected to minion using `connect`"
PluginCmdUsage = """%(prog)s PLUGIN -r FUNC
    or: %(prog)s -l,--list
"""

class PluginCommand(Command):

    def __init__(self, topic='proxy', name='plugin', brief=HelpTopic, **kwargs):
        self.parser = PypsiArgParser(
            prog=name,
            description=brief
        )

        self.parser.add_argument(
            'plugin', help='name of plugin',
            metavar="NAME"
        )
        subcmd = self.parser.add_subparsers(prog='plugin', dest='subcmd', metavar='subcmd')
        subcmd.required = True

        lst = subcmd.add_parser(
            'list', help="list a plugin's functions"
        )

        exe = subcmd.add_parser(
            'exec', help="runs a plugin's function on a minion",
        )
        exe.add_argument(
            'func', metavar='FUNC', help="function to execute on minion"
        )

        super(PluginCommand, self).__init__(
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
        if ns.subcmd == 'list':
            self.list_plugin_functions(shell, ns.plugin)
        elif ns.subcmd == 'exec':
            self.run_plugin_function(shell, ns.plugin, ns.func)


    def check_connected(self, shell):
        minion = shell.connect
        if minion is not None:
            return True
        else:
            False

    def run_plugin_function(self, shell, plugin, function):
        if not plugin in shell.minions[shell.connect]['plugins']:
            self.error('shell', f"plugin {plugin} is not loaded into minion: {shell.connect}")
            return 1
        ret = None
        isfunc = False
        plg = LoaderUtil.load_plugin(plugin)
        for func in plg.list_functions():
            if func.__name__ == function:
                isfunc = True
        if not isfunc:
            self.error('shell', f"{function} is not a function of plugin: {plugin}")
            return 1
        params = minionRPC_pb2.functionReq(
            plugin=plugin,
            function=function
        )
        rpc = shell.minions[shell.connect]['rpc']
        try:
            ret = rpc.runPluginFunction(params)
        except Exception as e:
            shell.log.error(str(e))
            self.error('shell', f"Function: {function} failed: {str(e)}")
        if ret is not None:
            print(ret.data)

    def list_plugin_functions(self, shell, plugin):
        try:
            plg = LoaderUtil.load_plugin(plugin)
            funcs = plg.list_functions()
            self.print_function_list(shell, plugin, funcs)
        except Exception as e:
            shell.log.error(str(e))
            self.error(shell, f"Could not determine {plugin}'s available functions")

    def complete(self, shell, args, prefix):
        if len(args) == 1:
            return self.complete_plugins(shell, args, prefix)
        elif len(args) == 2:
            return self.complete_subcmds(shell, args, prefix)
        elif len(args) == 3 and args[3] != "list":
            return self.complete_functions(shell, args[0], prefix)

    def complete_plugins(self, shell, args, prefix):
        minion = shell.connect
        if minion is not None:
            return sorted(
                [plugin for plugin in shell.minions[minion]['plugins'] if plugin.startswith(prefix)]
            )
        else:
            return []
    
    def complete_subcmds(self, shell, args, prefix):
        cmds = ['list', 'exec']
        return sorted(
            [cmd for cmd in cmds if cmd.startswith(prefix)]
        )

    def complete_functions(self, shell, plugin, prefix):
        minion = shell.connect
        if minion is not None:
            try:
                plg = LoaderUtil.load_plugin(plugin)
                funcs = plg.list_functions_names()
                return sorted(
                    [func for func in funcs if func.startswith(prefix)]
                )
            except Exception as e:
                return []
        else:
            return []

    def print_function_list(self, shell, plugin, funcs):
        table = Table(
            columns=(
                Column('Function Name', Column.Shrink),
                Column('Description', Column.Grow),
            ),
            spacing=4
        )
        for func in funcs:
            doc = self.trim(func.__doc__)
            table.append(func.__name__, doc)
        print(f"\n{plugin} Functions:\n")
        table.write(sys.stdout)
        print()

    def trim(self, docstring):
        if not docstring:
            return ''
        # Convert tabs to spaces (following the normal Python rules)
        # and split into a list of lines:
        lines = docstring.expandtabs().splitlines()
        # Determine minimum indentation (first line doesn't count):
        indent = sys.maxsize
        for line in lines[1:]:
            stripped = line.lstrip()
            if stripped:
                indent = min(indent, len(line) - len(stripped))
        # Remove indentation (first line is special):
        trimmed = [lines[0].strip()]
        if indent < sys.maxsize:
            for line in lines[1:]:
                trimmed.append(line[indent:].rstrip())
        # Strip off trailing and leading blank lines:
        while trimmed and not trimmed[-1]:
            trimmed.pop()
        while trimmed and not trimmed[0]:
            trimmed.pop(0)
        # Return a single string:
        return '\n'.join(trimmed)
