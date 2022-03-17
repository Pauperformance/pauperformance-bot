from pauperformance_bot.entity.indexable_video import IndexableVideo


class YouTubeVideo(IndexableVideo):
    def __init__(
        self,
        video_id,  # YouTube internals
        etag,
        content_video_id,  # as displayed in the URL
        published_at,
        channel_id,
        channel_title,
        description,
        playlist_id,
        position,
        created_at,
        title,
        privacy_status,
        url,
        language,
    ):
        super().__init__(description)
        self.video_id = video_id
        self.etag = etag
        self.content_video_id = content_video_id
        self.published_at = published_at
        self.channel_id = channel_id
        self.channel_title = channel_title
        self.playlist_id = playlist_id
        self.position = position
        self.created_at = created_at
        self.title = title
        self.privacy_status = privacy_status
        self.url = url
        self.language = language

    def __str__(self):
        return (
            f"video_id: {self.video_id}\n"
            f"etag: {self.etag}\n"
            f"content_video_id: {self.content_video_id}\n"
            f"published_at: {self.published_at}\n"
            f"channel_id: {self.channel_id}\n"
            f"channel_title: {self.channel_title}\n"
            f"description: {self.description}\n"
            f"playlist_id: {self.playlist_id}\n"
            f"position: {self.position}\n"
            f"created_at: {self.created_at}\n"
            f"title: {self.title}\n"
            f"privacy_status: {self.privacy_status}\n"
            f"url: {self.url}\n"
            f"language: {self.language}\n"
        )

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))
