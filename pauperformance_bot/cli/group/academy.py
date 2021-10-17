#!/usr/bin/env python3
from pauperformance_bot.cli.builder.command import CLICommand
from pauperformance_bot.cli.builder.group import CLIGroup
from pauperformance_bot.constant.cli import (
    ACADEMY_CLI_GROUP,
    UPDATE_ACADEMY_CMD,
)
from pauperformance_bot.service.archive.mtggoldfish import (
    MTGGoldfishArchiveService,
)
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.service.storage.dropbox_ import DropboxService
from pauperformance_bot.task.academy import academy_update
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger(ACADEMY_CLI_GROUP)


class UpdateCommand(CLICommand):
    def __init__(self):
        super().__init__(
            UPDATE_ACADEMY_CMD,
            "Update Pauperformance web site.",
            [],
        )

    def dispatch_cmd(self, *args, **kwargs):
        super().dispatch_cmd(*args, **kwargs)
        storage = DropboxService()
        mtggoldfish = MTGGoldfishArchiveService(storage)
        academy_update(PauperformanceService(storage, mtggoldfish))


class AcademyGroup(CLIGroup):

    _cli_commands = [UpdateCommand()]

    def __init__(self):
        super().__init__(ACADEMY_CLI_GROUP, self._cli_commands)


if __name__ == "__main__":
    AcademyGroup().run()
