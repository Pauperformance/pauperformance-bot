from pauperformance_bot.util.time import pretty_str


class DeckstatsDeck:
    def __init__(
            self,
            owner_id,
            owner_name,
            saved_id,
            folder_id,
            name,
            added,
            updated,
            url,
    ):
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.saved_id = saved_id
        self.folder_id = folder_id
        self.name = name
        self.added = added
        self.updated = updated
        self.url = url

    @property
    def archetype(self):
        return self.name.rsplit(' ', maxsplit=1)[0]

    def __str__(self):
        return f"owner_id: {self.owner_id}; " \
               f"owner_name: {self.name}; " \
               f"saved_id: {self.saved_id}; " \
               f"folder_id: {self.folder_id}; " \
               f"name: {self.name}; " \
               f"added: {pretty_str(self.added)}; " \
               f"updated: {pretty_str(self.updated)}; " \
               f"url: {self.url}"


