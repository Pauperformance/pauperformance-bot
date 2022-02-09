from pauperformance_bot.exceptions import UnsupportedLanguage


def get_language_flag(language_name):
    if language_name == "ITA":
        return "🇮🇹"
    elif language_name == "ENG":
        return "🇬🇧"
    else:
        raise UnsupportedLanguage(f"Missing flag for language {language_name}")
