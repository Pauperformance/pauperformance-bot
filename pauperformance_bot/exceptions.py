class ClientException(Exception):
    pass


class DeckstatsException(ClientException):
    pass


class MTGGoldfishException(ClientException):
    pass


class WizardsException(ClientException):
    pass


class UnsupportedLanguage(Exception):
    pass


class StorageException(ClientException):
    pass


class StoredFileNotFound(StorageException):
    pass


class PauperformanceException(ClientException):
    pass


class ScryfallException(ClientException):
    pass


class CardNotFoundException(ScryfallException):
    pass
