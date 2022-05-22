#!/usr/bin/env python3
from pauperformance_bot.cli.builder.command import CLICommand
from pauperformance_bot.cli.builder.group import CLIGroup
from pauperformance_bot.constant.cli import (
    ACADEMY_CLI_GROUP,
    UPDATE2_ACADEMY_CMD,
    UPDATE_ACADEMY_CMD,
)
from pauperformance_bot.task.academy import main as main_v1
from pauperformance_bot.task.academy2 import main as main_v2
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger(ACADEMY_CLI_GROUP)


class UpdateCommand(CLICommand):
    def __init__(self):
        super().__init__(
            UPDATE_ACADEMY_CMD,
            "Update Academy web site (old version).",
            [],
        )

    def dispatch_cmd(self, *args, **kwargs):
        super().dispatch_cmd(*args, **kwargs)
        main_v1()


class UpdateCommand2(CLICommand):
    def __init__(self):
        super().__init__(
            UPDATE2_ACADEMY_CMD,
            "Update Academy web site (new version).",
            [],
        )

    def dispatch_cmd(self, *args, **kwargs):
        super().dispatch_cmd(*args, **kwargs)
        main_v2()


class AcademyGroup(CLIGroup):

    _cli_commands = [UpdateCommand(), UpdateCommand2()]

    def __init__(self):
        super().__init__(ACADEMY_CLI_GROUP, self._cli_commands)


if __name__ == "__main__":
    AcademyGroup().run()
