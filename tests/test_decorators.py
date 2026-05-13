import unittest

from pauperformance_bot.util.decorators import auto_repr, auto_str


@auto_repr
class _ReprTarget:
    def __init__(self, x, y):
        self.x = x
        self.y = y


@auto_str
class _StrTarget:
    def __init__(self, name, value):
        self.name = name
        self.value = value


@auto_repr
@auto_str
class _Both:
    def __init__(self, label):
        self.label = label


class TestAutoRepr(unittest.TestCase):
    def test_repr_contains_qualified_class_name(self):
        obj = _ReprTarget(1, 2)
        self.assertIn("_ReprTarget", repr(obj))

    def test_repr_contains_attribute_names_and_values(self):
        obj = _ReprTarget(10, 20)
        self.assertIn("x=10", repr(obj))
        self.assertIn("y=20", repr(obj))

    def test_repr_string_values(self):
        obj = _ReprTarget("hello", "world")
        self.assertIn("x=hello", repr(obj))
        self.assertIn("y=world", repr(obj))


class TestAutoStr(unittest.TestCase):
    def test_str_contains_simple_class_name(self):
        obj = _StrTarget("test", 42)
        self.assertIn("_StrTarget", str(obj))

    def test_str_contains_attributes(self):
        obj = _StrTarget("hello", 99)
        self.assertIn("name=hello", str(obj))
        self.assertIn("value=99", str(obj))

    def test_str_does_not_contain_module(self):
        obj = _StrTarget("a", 1)
        # auto_str uses only the class name, not the fully-qualified name
        self.assertNotIn(".", str(obj).split("(")[0])


class TestBothDecorators(unittest.TestCase):
    def test_repr_and_str_both_work(self):
        obj = _Both("test-label")
        self.assertIn("label=test-label", repr(obj))
        self.assertIn("label=test-label", str(obj))


if __name__ == "__main__":
    unittest.main()
