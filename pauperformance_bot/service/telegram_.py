import telegram

from pauperformance_bot.credentials import TELEGRAM_MYR_API_TOKEN
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class TelegramService:
    def __init__(self, myr_api_token=TELEGRAM_MYR_API_TOKEN):
        self.telegram_bot = telegram.Bot(token=myr_api_token)

    def send_message(self, player, message, disable_web_page_preview=True):
        if not player.telegram_id:
            logger.info(
                f"Not sending message '{message}' to {player.name}: "
                f"missing Telegram id."
            )
            return
        logger.debug(f"Sending message '{message}' to {player.name}...")
        self.telegram_bot.send_message(
            chat_id=player.telegram_id,
            text=message,
            disable_web_page_preview=disable_web_page_preview,
        )
        logger.debug(f"Sent message '{message}' to {player.name}.")
