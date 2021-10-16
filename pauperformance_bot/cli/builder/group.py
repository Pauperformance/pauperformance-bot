from pauperformance_bot.cli.builder.hookable_parser import HookableParser
from pauperformance_bot.cli.builder.runnable import CLIRunnable
from pauperformance_bot.cli.builder.utils import (
    build_commands_sub_parser,
    get_default_parent_parser,
    handle_default_cli_options,
)


class CLIGroup(CLIRunnable):
    def __init__(self, name, cli_commands):
        super().__init__(name)
        self.cli_commands = cli_commands

    def add_parser_argument(self, tool_parser):
        build_commands_sub_parser(tool_parser, self.cli_commands)

    def get_cli_parser(self):
        parser = HookableParser(
            description="A collection of {}-related tools.".format(self.name),
            parents=[get_default_parent_parser()],
        )
        self.add_parser_argument(parser)
        return parser

    def dispatch_cmd(self, command, *args, **kwargs):
        handle_default_cli_options(*args, **kwargs)
        dispatcher = next(
            filter(lambda c: c.name == command, self.cli_commands)
        )
        dispatcher.dispatch_cmd(*args, **kwargs)
