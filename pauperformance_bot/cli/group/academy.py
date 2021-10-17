#!/usr/bin/env python3
from pauperformance_bot.cli.builder.command import CLICommand
from pauperformance_bot.cli.builder.group import CLIGroup
from pauperformance_bot.constant.cli import (
    ACADEMY_CLI_GROUP,
    UPDATE_ACADEMY_CMD,
)
from pauperformance_bot.service.mtg.archive.mtggoldfish import MTGGoldfish
from pauperformance_bot.service.pauperformance import Pauperformance
from pauperformance_bot.service.storage.dropbox_ import Dropbox
from pauperformance_bot.task.academy import academy_update
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger(ACADEMY_CLI_GROUP)


class Update(CLICommand):
    def __init__(self):
        super().__init__(
            UPDATE_ACADEMY_CMD,
            "Update Pauperformance web site.",
            [],
        )

    def dispatch_cmd(self, *args, **kwargs):
        super().dispatch_cmd(*args, **kwargs)
        storage = Dropbox()
        mtggoldfish = MTGGoldfish(storage)
        academy_update(Pauperformance(storage, mtggoldfish))


class AcademyGroup(CLIGroup):

    _cli_commands = [Update()]

    def __init__(self):
        super().__init__(ACADEMY_CLI_GROUP, self._cli_commands)


if __name__ == "__main__":
    AcademyGroup().run()
