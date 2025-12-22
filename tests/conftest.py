import os

import pytest

REQUIRED_SECRETS = "RUN_TESTS_WITH_SECRETS"


def pytest_collection_modifyitems(config, items):
    if os.getenv(REQUIRED_SECRETS):
        return

    skip_marker = pytest.mark.skip(
        reason=f"Excluding tests with secrets (no : {REQUIRED_SECRETS} found)"
    )

    for item in items:
        if "secrets" in item.keywords:
            item.add_marker(skip_marker)
