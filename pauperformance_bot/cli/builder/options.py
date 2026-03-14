from abc import abstractmethod
from argparse import ArgumentParser, _ActionsContainer
from functools import partial
from typing import Any


class CLIOption:
    def __init__(self, dest_var: str, help_msg: str) -> None:
        self.dest_var = dest_var
        self.help_msg = help_msg

    @abstractmethod
    def add_to_parser(self, arg_parser: ArgumentParser, command_name: str) -> None:
        pass


class FlagCLIOption(CLIOption):
    def add_to_parser(self, arg_parser: ArgumentParser, command_name: str) -> None:
        arg_parser.add_argument(
            "--" + self.dest_var, action="store_true", help=self.help_msg
        )


class ValuedCLIOption(CLIOption):
    def __init__(
        self,
        dest_var: str,
        choices: list[str] | None,
        default_value: str | None,
        required: bool,
        multiple_allowed: bool,
        help_msg: str,
    ) -> None:
        super().__init__(dest_var, help_msg)

        if default_value and required:
            raise ValueError(
                "Default value {} provided for required option {}".format(
                    default_value, dest_var
                )
            )
        self.choices = choices
        self.default_value: Any = default_value
        self.required = required
        self.multiple_allowed = multiple_allowed

    def add_to_parser(self, arg_parser: ArgumentParser, command_name: str) -> None:
        add_args_fn = arg_parser.add_argument

        if self.multiple_allowed:
            add_args_fn = partial(add_args_fn, nargs="+")
            self.default_value = [self.default_value]

        add_args_fn(
            "-" + self.dest_var,
            default=self.default_value,
            choices=self.choices,
            required=self.required,
            help=self.help_msg,
            dest=self.dest_var,
        )


class QuietCLIOption(FlagCLIOption):
    def __init__(self) -> None:
        super().__init__("quiet", "suppress non-error messages")


class VerboseCLIOption(FlagCLIOption):
    def __init__(self) -> None:
        super().__init__("verbose", "verbose logging")


class InputFileCLIOption(ValuedCLIOption):
    def __init__(
        self,
        choices: list[str] | None = None,
        default_value: str | None = None,
        required: bool = False,
        multiple_allowed: bool = False,
    ) -> None:
        super().__init__(
            "input-file",
            choices,
            default_value,
            required,
            multiple_allowed,
            "input file",
        )


class OutputFileCLIOption(ValuedCLIOption):
    def __init__(
        self,
        choices: list[str] | None = None,
        default_value: str | None = None,
        required: bool = False,
        multiple_allowed: bool = False,
    ) -> None:
        super().__init__(
            "output-file",
            choices,
            default_value,
            required,
            multiple_allowed,
            "output file",
        )
