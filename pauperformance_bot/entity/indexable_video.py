from pauperformance_bot.constant.myr import VIDEO_DECK_TAG
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class IndexableVideo:
    def __init__(self, description):
        self.description = description

    @property
    def deck_name(self):
        deck_name = None
        for line in self.description.split("\n"):
            line = line.strip()
            if line.lower().startswith(VIDEO_DECK_TAG.lower()):
                logger.debug(f"Extracting deck name from line:\n{line}")
                deck_name = line[len(VIDEO_DECK_TAG) :]
                logger.debug(f"Pairing video to deck {deck_name}")
                break
        return deck_name
