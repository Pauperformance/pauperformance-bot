import argparse


class HookableParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hooks = []

    @property
    def hooks(self):
        return self._hooks

    def parse_args(self, args=..., namespace=...):
        fn_to_wrap = super().parse_args
        for hook in self._hooks:
            fn_to_wrap = hook(fn_to_wrap)
        return fn_to_wrap()

    def add_hooks(self, hook_fns):
        self._hooks += hook_fns
