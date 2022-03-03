class TwitchVideo:
    def __init__(
        self,
        video_id,
        stream_id,
        user_id,
        user_login_name,
        user_display_name,
        title,
        description,
        created_at,
        published_at,
        url,
        viewable,
        language,
        duration,
    ):
        self.video_id = video_id
        self.stream_id = stream_id
        self.user_id = user_id
        self.user_login_name = user_login_name
        self.user_display_name = user_display_name
        self.title = title
        self.description = description
        self.created_at = created_at
        self.published_at = published_at
        self.url = url
        self.viewable = viewable
        self.language = language
        self.duration = duration

    def __str__(self):
        return (
            f"video_id: {self.video_id}\n"
            f"stream_id: {self.stream_id}\n"
            f"user_id: {self.user_id}\n"
            f"user_login_name: {self.user_login_name}\n"
            f"user_display_name: {self.user_display_name}\n"
            f"title: {self.title}\n"
            f"description: {self.description}\n"
            f"created_at: {self.created_at}\n"
            f"published_at: {self.published_at}\n"
            f"url: {self.url}\n"
            f"viewable: {self.viewable}\n"
            f"language: {self.language}\n"
            f"duration: {self.duration}\n"
        )

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))
