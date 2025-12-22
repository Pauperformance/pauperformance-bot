import os

import pytest

REQUIRED_SECRETS = [
    "DISCORD_BOT_TOKEN",
    "DROPBOX_APP_KEY",
    "DROPBOX_APP_SECRET",
    "DROPBOX_REFRESH_TOKEN",
    "MTGGOLDFISH_PAUPERFORMANCE_PASSWORD",
    "MTGGOLDFISH_PAUPERFORMANCE_USERNAME",
    "TWITCH_APP_CLIENT_ID",
    "TWITCH_APP_CLIENT_SECRET",
    "YOUTUBE_API_KEY",
]


def pytest_collection_modifyitems(config, items):
    missing = [s for s in REQUIRED_SECRETS if not os.getenv(s)]

    if not missing:
        return

    skip_marker = pytest.mark.skip(reason=f"Missing CI secrets: {', '.join(missing)}")

    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_marker)
