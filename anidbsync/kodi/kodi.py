from kodipydent import Kodi
from anidbsync.auto import AutoRepr
import operator
import re
# TODO: Solve multiple entries problem
from anidbsync.config import KodiConfig

class KodiTVShow(AutoRepr):
    def __init__(self, data):
        self.id = data['tvshowid']
        self.title = data['originaltitle'] if len(data['originaltitle']) > 0 else data['title']
        self.episode_count = data['episode']
        self.seasons = data['season']

class KodiSeason(AutoRepr):
    def __init__(self, data):
        self.id = data['seasonid']
        self.num = data['season']
        self.episode_count = data['episode']
        self.name = data['label']

class KodiEpisode(AutoRepr):
    def __init__(self, data):
        self.file = data['file']
        self.id = data['episodeid']
        self.episode = data['episode']
        self.show = data['showtitle']
        self.title = data['title']
        self.watched = data['playcount'] > 0
        self.group = re.search("\\[(.+?)\\]", self.file).group(1)


class KodiHelper:
    def __init__(self, url='localhost', password=None, port=None, config: KodiConfig = None, start_at=0):
        self.start_at = start_at
        if config is not None:
            self.kodi = Kodi(config.url, config.password, config.port)
        else:
            self.kodi = Kodi(url, password, port)

    def get_tvshows(self):
        return [KodiTVShow(show) for show in
                self.kodi.VideoLibrary.GetTVShows(properties=['title', 'season', 'episode', 'originaltitle'])['result'][
                    'tvshows'] if
                show['tvshowid'] > self.start_at]

    def get_seasons(self, tvshowid: int):
        seasons =  [KodiSeason(season) for season in
                self.kodi.VideoLibrary.GetSeasons(tvshowid=tvshowid, properties=['season', 'episode'])['result']['seasons']]
        # Anime generally only have 1 season (s2 is normally a different show).
        # season 0 is always the specials, which contain endings and openings
        # which should be marked watched if any ep is watched
        seasons.sort(key=operator.attrgetter('num'), reverse=True)
        return seasons

    def get_episodes(self, tvshow: int, season: int, start=0, end=-1):
        result = self.kodi.VideoLibrary.GetEpisodes(tvshowid=tvshow, season=season, limits={'start': start, 'end': end},
                                                    properties=['file', 'episode', 'showtitle', 'title', 'playcount'])[
            'result']
        if 'episodes' in result:
            return [KodiEpisode(e) for e in result['episodes']]
        return []

    def get_unwatched_episodes(self, tvshow: int, season: int, start=0, end=-1):
        return [e for e in self.get_episodes(tvshow, season, start, end) if not e.watched]

    def mark_as_watched(self, episode: KodiEpisode):
        self.kodi.VideoLibrary.SetEpisodeDetails(episodeid=episode.id, playcount=1)