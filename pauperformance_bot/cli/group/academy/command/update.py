#!/usr/bin/env python3
from pauperformance_bot.cli.builder.command import CLICommand
from pauperformance_bot.constant.cli import (
    ACADEMY_CLI_GROUP,
    UPDATE_ACADEMY_CMD,
)
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
        update()


def update():
    print("TODO.")


if __name__ == "__main__":
    Update().run()
