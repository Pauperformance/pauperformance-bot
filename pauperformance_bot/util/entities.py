from typing import TypeVar

_C = TypeVar("_C")


def auto_repr(cls: type[_C]) -> type[_C]:
    def __repr__(self: _C) -> str:
        fq_class_name = ".".join([type(self).__module__, type(self).__qualname__])
        class_attributes = ", ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"{fq_class_name}({class_attributes})"

    cls.__repr__ = __repr__  # type: ignore[method-assign, assignment]
    return cls


def auto_str(cls: type[_C]) -> type[_C]:
    def __str__(self: _C) -> str:
        class_name = type(self).__name__
        class_attributes = ", ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"{class_name}({class_attributes})"

    cls.__str__ = __str__  # type: ignore[method-assign, assignment]
    return cls
