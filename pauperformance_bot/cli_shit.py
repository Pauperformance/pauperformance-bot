#!/usr/bin/env python3
from pauperformance_bot.cli.cli import (
    add_default_options,
    handle_default_cli_options,
)
from pauperformance_bot.cli.cli_runnable import CLIRunnable
from pauperformance_bot.cli.hookable_parser import HookableParser
from pauperformance_bot.constant.myr import APPLICATION_NAME
from pauperformance_bot.group import academy_group, test_group


class MyrCLI(CLIRunnable):

    _cli_tools = [
        academy_group.AcademyGroup(),
        test_group.TestGroup(),
    ]

    def __init__(self):
        super().__init__(APPLICATION_NAME)

    def get_cli_parser(self):
        parser = HookableParser(description="A collection of Myr tasks")
        add_default_options(parser)

        description = (
            "Type 'tool-name -h' to show its help message (e.g. "
            "'{} -h)'".format(next(iter(MyrCLI._cli_tools)).name)
        )
        tools_parser = parser.add_subparsers(
            dest="tool", description=description, parser_class=HookableParser
        )
        tools_parser.required = True

        for tool in MyrCLI._cli_tools:
            description = "A collection of {}-related tools".format(tool.name)
            sub_parser = tools_parser.add_parser(
                tool.name, help=description.lower(), description=description
            )
            tool.add_parser_argument(sub_parser)
            parser.add_hooks(sub_parser.hooks)
        return parser

    def dispatch_cmd(self, tool, *args, **kwargs):
        handle_default_cli_options(*args, **kwargs)
        dispatcher = next(filter(lambda t: t.name == tool, MyrCLI._cli_tools))
        dispatcher.dispatch_cmd(*args, **kwargs)


def main():
    MyrCLI().run()


if __name__ == "__main__":
    main()