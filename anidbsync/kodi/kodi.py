from kodipydent import Kodi
from anidbsync.auto import AutoRepr

# TODO: Solve multiple entries problem
from anidbsync.config import KodiConfig

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
    def __init__(self, url='localhost', password=None, port=None, config: KodiConfig = None):
        if config is not None:
            self.kodi = Kodi(config.url, config.password, config.port)
        else:
            self.kodi = Kodi(url, password, port)

    def get_tvshows(self):
        return [KodiTVShow(show) for show in
                self.kodi.VideoLibrary.GetTVShows(properties=['title', 'season', 'episode', 'originaltitle'])['result'][
                    'tvshows'] if
                show['tvshowid'] > DONE]

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