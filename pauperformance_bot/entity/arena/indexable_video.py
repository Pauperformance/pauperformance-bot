from pauperformance_bot.constant.pauperformance.myr import VIDEO_DECK_TAG
from pauperformance_bot.util.decorators import auto_repr, auto_str
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.naming import is_valid_p12e_deck_name

logger = get_application_logger()


@auto_repr
@auto_str
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
                maybe_deck_name = line[len(VIDEO_DECK_TAG) :]
                if is_valid_p12e_deck_name(maybe_deck_name):
                    deck_name = maybe_deck_name
                    logger.debug(f"Pairing video to deck {deck_name}")
                    break
        return deck_name

    @property
    def archetype(self):
        archetype = None
        for line in self.description.split("\n"):
            line = line.strip()
            if line.lower().startswith(VIDEO_DECK_TAG.lower()):
                logger.debug(f"Extracting archetype from line:\n{line}")
                archetype = line[len(VIDEO_DECK_TAG) :]
                if "." in archetype:  # need to drop deck name
                    archetype = archetype.split(".", maxsplit=1)[0].rsplit(
                        " ", maxsplit=1
                    )[0]
                logger.debug(f"Pairing video to archetype {archetype}")
                break
        return archetype
