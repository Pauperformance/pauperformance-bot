from pauperformance_bot.constant.pauperformance.myr import RESOURCES_DIR
from pauperformance_bot.util.path import posix_path

MAINBOARD_WEIGHT = 1
SIDEBOARD_WEIGHT = 0.25
BREW_CLASSIFICATION_THRESHOLD = 0.76

CLASSIFIER_SNAPSHOT_PATH = posix_path(
    RESOURCES_DIR, "silver", "classifier_snapshot.pkl"
)
