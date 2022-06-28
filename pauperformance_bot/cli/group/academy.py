#!/usr/bin/env python3
from pauperformance_bot.cli.builder.command import CLICommand
from pauperformance_bot.cli.builder.group import CLIGroup
from pauperformance_bot.cli.builder.options import FlagCLIOption
from pauperformance_bot.constant.cli import (
    ACADEMY_CLI_GROUP,
    UPDATE2_ACADEMY_CMD,
    UPDATE_ACADEMY_CMD,
)
from pauperformance_bot.task.academy import main as main_v1
from pauperformance_bot.task.academy import (
    run_coroutine_in_event_loop,
    async_import_players_videos_from_twitch,
    async_import_players_videos_from_youtube,
    async_import_decks_from_deckstats,
    async_import_decks_from_discord
)
from pauperformance_bot.task.academy2 import main as main_v2
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger(ACADEMY_CLI_GROUP)


class TwitchCLIOption(FlagCLIOption):
    def __init__(self):
        super().__init__("twitch", "Import players' videos from Twitch.")


class YouTubeCLIOption(FlagCLIOption):
    def __init__(self):
        super().__init__("youtube", "Import players' videos from YouTube.")


class DeckstatsCLIOption(FlagCLIOption):
    def __init__(self):
        super().__init__("deckstats", "Import decks from DeckStats.")


class DiscordCLIOption(FlagCLIOption):
    def __init__(self):
        super().__init__("discord", "Import decks from Discord.")


class UpdateCommand(CLICommand):
    def __init__(self):
        super().__init__(
            UPDATE_ACADEMY_CMD,
            "Update Academy web site (old version).",
            [
                TwitchCLIOption(),
                YouTubeCLIOption(),
                DeckstatsCLIOption(),
                DiscordCLIOption()
            ],
        )

    def dispatch_cmd(self, *args, **kwargs):
        super().dispatch_cmd(*args, **kwargs)
        default = True
        if kwargs.pop(TwitchCLIOption().dest_var, False):
            default = False
            run_coroutine_in_event_loop(
                async_import_players_videos_from_twitch,
                send_notification=True,
                update_dev=False
            )
        if kwargs.pop(YouTubeCLIOption().dest_var, False):
            default = False
            run_coroutine_in_event_loop(
                async_import_players_videos_from_youtube,
                send_notification=True,
                update_dev=False
            )
        if kwargs.pop(DeckstatsCLIOption().dest_var, False):
            default = False
            run_coroutine_in_event_loop(
                async_import_decks_from_deckstats,
                send_notification=True,
                update_dev=False
            )
        if kwargs.pop(DiscordCLIOption().dest_var, False):
            default = False
            run_coroutine_in_event_loop(
                async_import_decks_from_discord,
                send_notification=True,
                update_dev=False
            )
        if default:
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
