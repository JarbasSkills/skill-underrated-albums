import random
from os.path import join, dirname

import requests
from json_database import JsonStorageXDG

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class UnderratedAlbumsSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.skill_icon = self.default_bg = join(dirname(__file__), "ui", "underratedalbums_icon.jpg")
        self.supported_media = [MediaType.MUSIC]
        self.n_mixes = 5
        self.archive = JsonStorageXDG("UnderratedAlbums", subfolder="OCP")
        super().__init__(*args, **kwargs)

    def initialize(self):
        self._sync_db()
        self.load_ocp_keywords()

    def _sync_db(self):
        bootstrap = "https://github.com/JarbasSkills/skill-underrated-albums/raw/dev/bootstrap.json"
        data = requests.get(bootstrap).json()
        self.archive.merge(data)
        self.schedule_event(self._sync_db, random.randint(3600, 24 * 3600))

    def load_ocp_keywords(self):
        albums = []
        artists = []
        songs = []

        for url, data in self.archive.items():
            t = data["title"].split("(")[0].split("|")[0].split("[")[0].strip() \
                .replace("–", "-").replace("—", "-")
            if "-" in t:
                artist, title = t.split("-")[:2]
                artists.append(artist.strip())
                if "album" in data["title"].lower():
                    albums.append(title.strip())
                else:
                    songs.append(title.strip())

        self.register_ocp_keyword(MediaType.MUSIC,
                                  "artist_name", artists)
        self.register_ocp_keyword(MediaType.MUSIC,
                                  "album_name", albums)
        self.register_ocp_keyword(MediaType.MUSIC,
                                  "song_name", songs)
        self.register_ocp_keyword(MediaType.MUSIC,
                                  "music_streaming_provider",
                                  ["Underrated Albums"])

    def match_skill(self, phrase, media_type):
        score = 0
        if self.voc_match(phrase, "music") or media_type == MediaType.MUSIC:
            score += 10
        if self.voc_match(phrase, "underrated_albums"):
            score += 80
        return score

    @ocp_search()
    def search_db(self, phrase, media_type):
        entities = self.ocp_voc_match(phrase)
        candidates = list(self.archive.values())
        artist = entities.get("artist_name")
        album = entities.get("album_name")
        song = entities.get("song_name")

        if "music_streaming_provider" in entities:  # asked for skill by name
            # random playlists from this skill
            pl = self.featured_media(-1)
            for i in range(self.n_mixes):
                random.shuffle(pl)
                yield {
                    "match_confidence": 90,
                    "media_type": MediaType.MUSIC,
                    "playlist": pl[:100],
                    "playback": PlaybackType.AUDIO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": self.skill_icon,
                    "bg_image": self.default_bg,
                    "title": f"Underrated Albums (Mix {i + 1})"
                }

        if artist or song or album:
            # filter valid results
            if album:
                candidates = [video for video in candidates
                              if album.lower() in video["title"].lower()]
            elif artist:
                candidates = [video for video in candidates
                              if artist.lower() in video["title"].lower()]
            elif song:
                candidates = [video for video in candidates
                              if song.lower() in video["title"].lower()]

            for video in candidates:
                yield {
                    "title": video["title"],
                    "author": artist or video["author"],
                    "album": album,
                    "match_confidence": 90,
                    "media_type": MediaType.MUSIC,
                    "uri": "youtube//" + video["url"],
                    "playback": PlaybackType.AUDIO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"],
                    "bg_image": self.default_bg
                }

    @ocp_featured_media()
    def featured_media(self, num_entries=25):
        return [
                   {
                       "match_confidence": 90,
                       "media_type": MediaType.MUSIC,
                       "uri": "youtube//" + entry["url"],
                       "playback": PlaybackType.AUDIO,
                       "image": entry["thumbnail"],
                       "bg_image": self.default_bg,
                       "skill_icon": self.skill_icon,
                       "skill_id": self.skill_id,
                       "title": entry["title"]
                   } for entry in self.archive.values()
               ][:num_entries]


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = UnderratedAlbumsSkill(bus=FakeBus(), skill_id="t.fake")
    #for r in s.search_db("Underrated Albums", MediaType.MUSIC):
    #    print(r)

    for r in s.search_db("Village Of The Snake God", MediaType.MUSIC):
        print(r)
