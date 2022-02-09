class ClientException(Exception):
    pass


class DeckstatsException(ClientException):
    pass


class MTGGoldfishException(ClientException):
    pass


class UnsupportedLanguage(Exception):
    pass
