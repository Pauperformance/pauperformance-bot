import argparse
import logging

from pauperformance_bot.cli.builder.hookable_parser import HookableParser
from pauperformance_bot.cli.builder.options import (
    QuietCLIOption,
    VerboseCLIOption,
)
from pauperformance_bot.constant.cli import GROUP_CLI_DEST_ID
from pauperformance_bot.util.log import get_application_logger


def get_default_parent_parser():
    arg_parser = argparse.ArgumentParser(add_help=False)
    add_default_options(arg_parser)
    return arg_parser


def add_default_options(arg_parser):
    QuietCLIOption().add_to_parser(arg_parser, "")
    VerboseCLIOption().add_to_parser(arg_parser, "")


def handle_default_cli_options(quiet, verbose, *args, **kwargs):
    logger = get_application_logger()
    if quiet and verbose:
        raise ValueError("Unable to set both quiet and verbose flags")
    if quiet:
        logger.setLevel(logging.ERROR)
    if verbose:
        logger.setLevel(logging.DEBUG)


def build_commands_sub_parser(tool_parser, cli_commands):
    description = (
        "Type 'command-name -h' to show its help message "
        "(e.g. '{} -h)'".format(next(iter(cli_commands)).name)
    )
    tools_sub_parser = tool_parser.add_subparsers(
        dest=GROUP_CLI_DEST_ID,
        description=description,
        parser_class=HookableParser,
    )
    tools_sub_parser.required = True

    for group_command in cli_commands:
        group_sub_parser = tools_sub_parser.add_parser(
            group_command.name,
            help=group_command.description.lower(),
            description=group_command.description,
        )
        group_command.add_parser_argument(group_sub_parser)
        tool_parser.add_hooks(group_sub_parser.hooks)
