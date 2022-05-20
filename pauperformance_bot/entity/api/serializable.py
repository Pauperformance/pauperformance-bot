import json
import os
from abc import ABC, abstractmethod

from pauperformance_bot.util.path import posix_path


class Serializable(ABC):
    @property
    @abstractmethod
    def path(self) -> str:
        pass

    @property
    @abstractmethod
    def key(self) -> str:
        pass

    def dump_to_file(self):
        os.makedirs(self.path, exist_ok=True)
        with open(posix_path(self.path, self.key), 'w') as out_f:
            json.dump(self.__dict__, out_f)
