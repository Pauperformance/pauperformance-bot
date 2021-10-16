from pauperformance_bot.cli.builder.utils import (
    get_default_parent_parser,
    handle_default_cli_options,
)
from pauperformance_bot.cli.builder.cli_runnable import CLIRunnable
from pauperformance_bot.cli.builder.hookable_parser import HookableParser


class CLICommand(CLIRunnable):
    def __init__(self, name, description, options):
        # command name must be unique in the entire application (not only
        # within the same group) to allow proper wildcard expansion (hooks on
        # the parser are placed on its name)
        super().__init__(name)
        self.description = description
        self.options = options

    def add_parser_argument(self, tool_parser):
        for option in self.options:
            option.add_to_parser(tool_parser, self.name)

    def get_cli_parser(self):
        parser = HookableParser(
            description=self.description, parents=[get_default_parent_parser()]
        )
        self.add_parser_argument(parser)
        return parser

    def dispatch_cmd(self, *args, **kwargs):
        handle_default_cli_options(*args, **kwargs)
