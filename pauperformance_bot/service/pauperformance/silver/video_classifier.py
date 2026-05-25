import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor

from pauperformance_bot.constant.pauperformance.silver import (
    BREW_CLASSIFICATION_THRESHOLD,
    VIDEO_CLASSIFICATION_THREADS,
)
from pauperformance_bot.service.mtg.downloader.service import DeckDownloaderService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class VideoClassifier:
    def __init__(self, pauperformance, decklassifier):
        self.pauperformance = pauperformance
        self.storage = pauperformance.storage
        self.archetypes = pauperformance.config_reader.list_archetypes()
        self.decklassifier = decklassifier

    def classify_videos(self):
        storage = self.pauperformance.storage
        folder = storage.get_folder(storage.youtube_video_path)
        videos = {name.split("/")[-1]: content for name, content in folder.items()}
        myr_fs = self.pauperformance.config_reader.myr_file_system
        with open(myr_fs.VIDEO_ARCHETYPES, newline="") as f:
            manual_labels = {row[0]: row[1] for row in csv.reader(f) if row}
        with open(myr_fs.VIDEO_BANNED_IDS) as f:
            banned_ids = {line.strip() for line in f if line.strip()}
        candidates = [
            (file, video_json)
            for file, video_json in videos.items()
            if video_json["content_video_id"] not in banned_ids
        ]
        missing_rows = []
        with ThreadPoolExecutor(max_workers=VIDEO_CLASSIFICATION_THREADS) as executor:
            for i in range(0, len(candidates), VIDEO_CLASSIFICATION_THREADS):
                batch = candidates[i : i + VIDEO_CLASSIFICATION_THREADS]
                futures = [
                    executor.submit(
                        self._classify_video, file, video_json, manual_labels
                    )
                    for file, video_json in batch
                ]
                missing_rows.extend(row for f in futures if (row := f.result()))
        missing_rows.sort(key=lambda row: row[0])
        with open(myr_fs.MISSING_VIDEO_ARCHETYPES, "w", newline="") as out_f:
            csv.writer(out_f).writerows(missing_rows)

    def _classify_video(
        self,
        filename,
        video_json,
        manual_labels,
        brew_threshold=BREW_CLASSIFICATION_THRESHOLD,
    ):
        # check manual labels: these will override anything else
        video_id = video_json["content_video_id"]
        if video_id in manual_labels:
            logger.debug(
                f"Found manual label for {video_id}: {manual_labels[video_id]}."
            )
            self._update_video_archetype(filename, video_json, manual_labels[video_id])
            return None

        # leave unchanged any other previously classified video
        if video_json["archetype"] != "Brew":
            return None

        # check video description: try to download decks from linked URLs
        description = video_json.get("description", "")
        urls = self._extract_urls_from_description(description)
        logger.debug(f"Found {len(urls)} video urls.")
        deck_urls = [
            url
            for url in urls
            if any(domain in url for domain in DeckDownloaderService.known_domains())
        ]
        logger.debug(f"Found {len(deck_urls)} deck urls.")
        playable_decks = []
        for url in deck_urls:
            try:
                deck = DeckDownloaderService.from_url(url)
                if deck:
                    playable_decks.append(deck)
            except Exception:
                pass
        logger.debug(f"Parsed {len(playable_decks)} decks.")
        if len(playable_decks) == 1:
            logger.debug("Found unique deck URL in description: parsing it...")
            playable_deck = playable_decks[0]
            most_similar_archetype, highest_similarity = (
                self.decklassifier.classify_deck(playable_deck)
            )
            if highest_similarity >= brew_threshold:
                archetype = most_similar_archetype.name
                logger.debug(f"Classifying deck as {archetype}")
                self._update_video_archetype(filename, video_json, archetype)
                return None

        # check video title
        title = video_json["title"].lower()
        title = title.replace("brew", "").replace("brewing", "")
        archetype = next(
            (
                a.name
                for a in self.archetypes
                if a.name.lower() in title
                or any(alias.lower() in title for alias in a.aliases)
            ),
            None,
        )
        if archetype is not None:
            logger.debug(f"Found label for {video_id} in title: {archetype}.")
            self._update_video_archetype(filename, video_json, archetype)
            return None

        return [video_id, "Brew", video_json["url"], video_json["title"]]

    @staticmethod
    def _extract_urls_from_description(description):
        return re.findall(r"https?://\S+", description)

    def _update_video_archetype(self, filename, video_json, archetype):
        video_json["archetype"] = archetype
        path = (
            f"{self.storage.youtube_video_path}{self.storage._dir_separator}{filename}"
        )
        self.storage.update_file(path, json.dumps(video_json, indent=4))
        logger.info(f"Updated archetype for {filename} to '{archetype}'.")
