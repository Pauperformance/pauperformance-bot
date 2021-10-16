from abc import abstractmethod


class CLIRunnable:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @abstractmethod
    def get_cli_parser(self):
        pass

    @abstractmethod
    def dispatch_cmd(self, *args, **kwargs):
        pass

    def run(self):
        args = self.get_cli_parser().parse_args()
        # CLI params may contain '-', an invalid character for python variables
        # identifiers: replace it with '_'
        params = {k.replace("-", "_"): v for k, v in vars(args).items()}
        self.dispatch_cmd(**params)
