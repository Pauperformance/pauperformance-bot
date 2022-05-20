#!/usr/bin/env python3
from pauperformance_bot.cli.builder.command import CLICommand
from pauperformance_bot.cli.builder.group import CLIGroup
from pauperformance_bot.constant.cli import ACADEMY_CLI_GROUP, UPDATE_ACADEMY_CMD
from pauperformance_bot.task.academy import main
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger(ACADEMY_CLI_GROUP)


class UpdateCommand(CLICommand):
    def __init__(self):
        super().__init__(
            UPDATE_ACADEMY_CMD,
            "Update Academy web site.",
            [],
        )

    def dispatch_cmd(self, *args, **kwargs):
        super().dispatch_cmd(*args, **kwargs)
        main()


class AcademyGroup(CLIGroup):

    _cli_commands = [UpdateCommand()]

    def __init__(self):
        super().__init__(ACADEMY_CLI_GROUP, self._cli_commands)


if __name__ == "__main__":
    AcademyGroup().run()
