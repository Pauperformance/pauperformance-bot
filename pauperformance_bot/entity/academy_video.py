class AcademyVideo:
    def __init__(
        self,
        video_id,
        user_name,
        language,
        published_at,
        deck_name,
    ):
        self.video_id = video_id
        self.user_name = user_name
        self.language = language
        self.published_at = published_at
        self.deck_name = deck_name

    def __str__(self):
        return (
            f"video_id: {self.video_id}\n"
            f"user_login_name: {self.user_name}\n"
            f"language: {self.language}\n"
            f"published_at: {self.published_at}\n"
            f"duration: {self.deck_name}\n"
        )

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))
