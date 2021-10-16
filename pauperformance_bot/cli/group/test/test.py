#!/usr/bin/env python3
from pauperformance_bot.cli.builder.group import CLIGroup
from pauperformance_bot.cli.group.test.command.hello import Hello
from pauperformance_bot.constant.cli import TEST_CLI_GROUP


class TestGroup(CLIGroup):

    _cli_commands = [Hello()]

    def __init__(self):
        super().__init__(TEST_CLI_GROUP, self._cli_commands)


if __name__ == "__main__":
    TestGroup().run()
