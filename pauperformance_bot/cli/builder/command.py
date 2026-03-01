from argparse import ArgumentParser
from typing import Any

import argcomplete

from pauperformance_bot.cli.builder.options import CLIOption
from pauperformance_bot.cli.builder.runnable import CLIRunnable
from pauperformance_bot.cli.builder.utils import (
    get_default_parent_parser,
    handle_default_cli_options,
)


class CLICommand(CLIRunnable):
    def __init__(self, name: str, description: str, options: list[CLIOption]) -> None:
        super().__init__(name)
        self.description = description
        self.options = options

    def add_parser_argument(self, tool_parser: ArgumentParser) -> None:
        for option in self.options:
            option.add_to_parser(tool_parser, self.name)

    def get_cli_parser(self) -> ArgumentParser:
        parser = ArgumentParser(
            description=self.description, parents=[get_default_parent_parser()]
        )
        self.add_parser_argument(parser)
        argcomplete.autocomplete(parser)
        return parser

    def dispatch_cmd(self, *args: Any, **kwargs: Any) -> None:
        handle_default_cli_options(*args, **kwargs)
