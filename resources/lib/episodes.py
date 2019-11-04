
from kodipydent import Kodi
import re

from resources.lib.anidb import AnidbHelper


class KodiEpisode:
    def __init__(self, data):
        self.file = data['file']
        self.epno = data['episode']
        self.show = data['showtitle']
        self.watched = data['playcount'] > 0


class KodiHelper:
    def __init__(self, url='localhost'):
        self.kodi = Kodi(url)

    def get_episodes(self, tvshow, season):
        return [KodiEpisode(ep) for ep in self.kodi.VideoLibrary.GetEpisodes(tvshowid=tvshow, season=season, properties=['file', 'episode', 'showtitle', 'title', 'playcount'])['result']['episodes']]

    def mark_as_watched(self, episode):
        self.kodi.VideoLibrary.SetEpisodeDetails(episodeid=episode.epno, playcount=1)


kodi = KodiHelper()
anidb = AnidbHelper()
for ep in kodi.get_episodes(1, 1):
    group = re.search('\[(.+?)\]', ep.file).group(1)
    anidbFile = anidb.load_episode_details(ep.show, group, ep.epno)
    if anidbFile.watched and not ep.watched:
        kodi.mark_as_watched(ep)
    if not anidbFile.watched and ep.watched:
        anidb.mark_watched(anidbFile)
