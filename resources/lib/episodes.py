from kodipydent import Kodi
import re
import logging
from resources.lib.auto import AutoRepr
from resources.lib.anidb import AnidbHelper, FileEntry

from time import sleep

logger = logging.getLogger('episode_sync')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('episodes.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# TODO: Solve multiple entries problem
DONE = 14

class KodiTVShow(AutoRepr):
    def __init__(self, data):
        self.id = data['tvshowid']
        self.title = data['originaltitle'] if len(data['originaltitle']) > 0 else data['title']
        self.episode_count = data['episode']
        self.seasons = data['season']


class KodiEpisode(AutoRepr):
    def __init__(self, data):
        self.file = data['file']
        self.id = data['episodeid']
        self.episode = data['episode']
        self.show = data['showtitle']
        self.title = data['title']
        self.watched = data['playcount'] > 0


class KodiHelper:
    def __init__(self, url='localhost'):
        self.kodi = Kodi(url)

    def get_tvshows(self):
        return [KodiTVShow(show) for show in
                self.kodi.VideoLibrary.GetTVShows(properties=['title', 'season', 'episode', 'originaltitle'])['result']['tvshows'] if
                show['tvshowid'] > DONE]

    def get_episodes(self, tvshow: int, season: int, start=0, end=-1):
        result = self.kodi.VideoLibrary.GetEpisodes(tvshowid=tvshow, season=season, limits={'start': start, 'end': end},
                                                   properties=['file', 'episode', 'showtitle', 'title', 'playcount'])['result']
        if 'episodes' in result:
            return [KodiEpisode(e) for e in result['episodes']]
        return []

    def get_unwatched_episodes(self, tvshow: int, season: int, start=0, end=-1):
        return [e for e in self.get_episodes(tvshow, season, start, end) if not e.watched]

    def mark_as_watched(self, episode: KodiEpisode):
        self.kodi.VideoLibrary.SetEpisodeDetails(episodeid=episode.id, playcount=1)


kodi = KodiHelper('192.168.1.44')
anidb = AnidbHelper()

shows = kodi.get_tvshows()
for show in shows:
    for season in range(1, show.seasons + 1):
        unwatched = kodi.get_unwatched_episodes(show.id, season, end=show.episode_count)
        for ep in unwatched:
            print('Processing Episode', ep.episode, '[', ep.id, '] of ', show.title, '[', show.id, ']')
            group = re.search('\[(.+?)\]', ep.file).group(1)
            anidbFile = anidb.load_episode_details(show.title, group, ep.episode)
            if anidbFile is None:
                logger.info('AniDbError: show: ' + show.title + '[' + str(show.id) + ']:' + str(ep.episode) + '[' + str(ep.id) + ']')
                print("Could not find episode ", ep.episode, 'of', ep.show)
            if anidbFile.watched and not ep.watched:
                kodi.mark_as_watched(ep)
            # if not anidbFile.watched and ep.watched:
            #     anidb.mark_watched(anidbFile)
