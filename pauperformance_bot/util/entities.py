def auto_repr(cls):
    def __repr__(self):
        fq_class_name = ".".join([type(self).__module__, type(self).__qualname__])
        class_attributes = ", ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"{fq_class_name}({class_attributes})"

    cls.__repr__ = __repr__
    return cls


def auto_str(cls):
    def __str__(self):
        class_name = type(self).__name__
        class_attributes = ", ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"{class_name}({class_attributes})"

    cls.__str__ = __str__
    return cls
