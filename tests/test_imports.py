import ast
import pathlib
import unittest

import pauperformance_bot

_PACKAGE_ROOT = pathlib.Path(pauperformance_bot.__file__).parent

# Top-level subpackages and modules that belong to pauperformance_bot.
# Any import whose root matches one of these names must be prefixed with
# "pauperformance_bot." to avoid silent namespace collisions.
_INTERNAL_NAMES = {
    p.stem if p.is_file() else p.name
    for p in _PACKAGE_ROOT.iterdir()
    if (p.is_dir() and not p.name.startswith("_"))
    or (p.is_file() and p.suffix == ".py" and not p.name.startswith("_"))
}


class TestFullyQualifiedImports(unittest.TestCase):
    def test_all_internal_imports_are_fully_qualified(self):
        violations = []
        for py_file in sorted(_PACKAGE_ROOT.rglob("*.py")):
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
            except (OSError, SyntaxError):
                continue
            rel = py_file.relative_to(_PACKAGE_ROOT.parent)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.level != 0:
                        continue
                    module = node.module or ""
                    root = module.split(".")[0]
                    if root in _INTERNAL_NAMES:
                        violations.append(
                            f"{rel}:{node.lineno}: from {module} import ..."
                        )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        root = alias.name.split(".")[0]
                        if root in _INTERNAL_NAMES:
                            violations.append(
                                f"{rel}:{node.lineno}: import {alias.name}"
                            )
        self.assertEqual(
            [],
            violations,
            "Unqualified internal imports found:\n" + "\n".join(violations),
        )


if __name__ == "__main__":
    unittest.main()
