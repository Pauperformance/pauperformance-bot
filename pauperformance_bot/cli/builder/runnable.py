from abc import abstractmethod
from argparse import ArgumentParser, Namespace
from typing import Any


class CLIRunnable:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def get_cli_parser(self) -> ArgumentParser:
        pass

    @abstractmethod
    def dispatch_cmd(self, *args: Any, **kwargs: Any) -> None:
        pass

    def run(self) -> None:
        args: Namespace = self.get_cli_parser().parse_args()
        # CLI params may contain '-', an invalid character for python variables
        # identifiers: replace it with '_'
        params: dict[str, Any] = {k.replace("-", "_"): v for k, v in vars(args).items()}
        self.dispatch_cmd(**params)
