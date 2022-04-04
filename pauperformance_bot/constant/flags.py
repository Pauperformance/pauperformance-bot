from pauperformance_bot.exceptions import UnsupportedLanguage


def get_language_flag(language_name):
    language_name = language_name.lower()
    if language_name == "ita" or language_name == "it":
        return "🇮🇹"
    elif language_name == "eng" or language_name == "en":
        return "🇬🇧"
    else:
        raise UnsupportedLanguage(f"Missing flag for language {language_name}")
