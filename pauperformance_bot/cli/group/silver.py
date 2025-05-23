#!/usr/bin/env python3
from pauperformance_bot.cli.builder.command import CLICommand
from pauperformance_bot.cli.builder.group import CLIGroup
from pauperformance_bot.cli.builder.options import (
    InputFileCLIOption,
    OutputFileCLIOption,
)
from pauperformance_bot.constant.cli import DPL_META_SILVER_CMD, SILVER_CLI_GROUP
from pauperformance_bot.task.silver import main
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger(SILVER_CLI_GROUP)


class DPLMetaCommand(CLICommand):
    def __init__(self):
        super().__init__(
            DPL_META_SILVER_CMD,
            "Generate meta for a Dutch Pauper League tournament.",
            [
                InputFileCLIOption(required=True),
                OutputFileCLIOption(required=True),
            ],
        )

    def dispatch_cmd(self, input_file, output_file, *args, **kwargs):
        super().dispatch_cmd(*args, **kwargs)
        main(input_file, output_file)


class SilverGroup(CLIGroup):
    _cli_commands = [DPLMetaCommand()]

    def __init__(self):
        super().__init__(SILVER_CLI_GROUP, self._cli_commands)


if __name__ == "__main__":
    SilverGroup().run()
