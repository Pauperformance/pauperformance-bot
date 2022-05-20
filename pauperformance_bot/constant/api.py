from pauperformance_bot.constant.academy import ACADEMY_PATH
from pauperformance_bot.util.path import posix_path

DEFAULT_API_EXPORT_DIR = posix_path(ACADEMY_PATH, "assets", "data")

DEFAULT_PHD_SHEET_EXPORT_DIR = posix_path(DEFAULT_API_EXPORT_DIR, "phd")

