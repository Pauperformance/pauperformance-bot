import os

import pytest

REQUIRED_SECRETS: str = "RUN_TESTS_WITH_SECRETS"


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if os.getenv(REQUIRED_SECRETS):
        return

    skip_marker = pytest.mark.skip(
        reason=f"Excluding tests with secrets (no : {REQUIRED_SECRETS} found)"
    )

    for item in items:
        if "secrets" in item.keywords:
            item.add_marker(skip_marker)
