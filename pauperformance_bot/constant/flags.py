from pauperformance_bot.exceptions import UnsupportedLanguage


def get_language_flag(language_name):
    if language_name == "ITA" or language_name == "it":
        return "🇮🇹"
    elif language_name == "ENG" or language_name == "en":
        return "🇬🇧"
    else:
        raise UnsupportedLanguage(f"Missing flag for language {language_name}")
