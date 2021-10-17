#!/usr/bin/env python3
from pauperformance_bot.cli.builder.command import CLICommand
from pauperformance_bot.cli.builder.group import CLIGroup
from pauperformance_bot.constant.cli import HELLO_TEST_CMD, TEST_CLI_GROUP
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger(TEST_CLI_GROUP)


class HelloCommand(CLICommand):
    def __init__(self):
        super().__init__(
            HELLO_TEST_CMD,
            "Call Myr.",
            [],
        )

    def dispatch_cmd(self, *args, **kwargs):
        super().dispatch_cmd(*args, **kwargs)
        print("Myr ready to serve you, Milord!")


class TestGroup(CLIGroup):

    _cli_commands = [HelloCommand()]

    def __init__(self):
        super().__init__(TEST_CLI_GROUP, self._cli_commands)


if __name__ == "__main__":
    TestGroup().run()
