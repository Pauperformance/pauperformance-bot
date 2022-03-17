class AcademyVideo:
    def __init__(
        self,
        video_id,
        user_name,
        language,
        published_at,
        deck_name,
        url,
        fa_icon,
    ):
        self.video_id = video_id
        self.user_name = user_name
        self.language = language
        self.published_at = published_at
        self.deck_name = deck_name
        self.url = url
        self.fa_icon = fa_icon

    def __str__(self):
        return (
            f"video_id: {self.video_id}\n"
            f"user_name: {self.user_name}\n"
            f"language: {self.language}\n"
            f"published_at: {self.published_at}\n"
            f"deck_name: {self.deck_name}\n"
            f"url: {self.url}\n"
            f"fa_icon: {self.fa_icon}\n"
        )

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))
