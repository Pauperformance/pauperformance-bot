import os
from importlib import import_module

from pauperformance_bot.constant.myr import SECRETS_UNTRACKED_FILE


def _get_credential_from_secrets(credential_key):
    try:  # will succeed locally if secret.py file is available
        secret_module = import_module(SECRETS_UNTRACKED_FILE.rstrip(".py"))
        return getattr(secret_module, credential_key)
    except ModuleNotFoundError:  # will fail on Heroku after deployments
        return None


def get_credential(credential_key):
    return os.environ.get(
        credential_key, _get_credential_from_secrets(credential_key)
    )


DROPBOX_ACCESS_TOKEN = get_credential("DROPBOX_ACCESS_TOKEN")
DROPBOX_APP_KEY = get_credential("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = get_credential("DROPBOX_APP_SECRET")

MTGGOLDFISH_PAUPERFORMANCE_USERNAME = get_credential(
    "MTGGOLDFISH_PAUPERFORMANCE_USERNAME"
)
MTGGOLDFISH_PAUPERFORMANCE_PASSWORD = get_credential(
    "MTGGOLDFISH_PAUPERFORMANCE_PASSWORD"
)
MTGGOLDFISH_SHIKA93_USERNAME = get_credential("MTGGOLDFISH_SHIKA93_USERNAME")
MTGGOLDFISH_SHIKA93_PASSWORD = get_credential("MTGGOLDFISH_SHIKA93_PASSWORD")

TELEGRAM_MYR_API_TOKEN = get_credential("TELEGRAM_MYR_API_TOKEN")
TELEGRAM_PAUPERFORMANCE_ID = get_credential("TELEGRAM_PAUPERFORMANCE_ID")
TELEGRAM_SHIKA93_ID = get_credential("TELEGRAM_SHIKA93_ID")
TELEGRAM_MREVILEYE_ID = get_credential("TELEGRAM_MREVILEYE_ID")
TELEGRAM_MIKEOSCAR_ID = get_credential("TELEGRAM_MIKEOSCAR_ID")
TELEGRAM_THRABEN27_ID = get_credential("TELEGRAM_THRABEN27_ID")
TELEGRAM_RIKXVIS_ID = get_credential("TELEGRAM_RIKXVIS_ID")
TELEGRAM_CHUMPBLOCCKAMI_ID = get_credential("TELEGRAM_CHUMPBLOCCKAMI_ID")
TELEGRAM_TARMOGOYF_ITA_ID = get_credential("TELEGRAM_TARMOGOYF_ITA_ID")

TWITCH_APP_CLIENT_ID = get_credential("TWITCH_APP_CLIENT_ID")
TWITCH_APP_CLIENT_SECRET = get_credential("TWITCH_APP_CLIENT_SECRET")

YOUTUBE_API_KEY = get_credential("YOUTUBE_API_KEY")
