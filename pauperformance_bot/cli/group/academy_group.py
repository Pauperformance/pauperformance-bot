#!/usr/bin/env python3
from pauperformance_bot.cli.builder.group import CLIGroup
from pauperformance_bot.constant.cli import ACADEMY_CLI_GROUP
from pauperformance_bot.cli.group.academy_cmds.update_cmd import Update


class AcademyGroup(CLIGroup):

    _cli_commands = [Update()]

    def __init__(self):
        super().__init__(ACADEMY_CLI_GROUP, self._cli_commands)


if __name__ == "__main__":
    AcademyGroup().run()
