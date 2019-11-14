from anidbsync.anidb.anidb import AnidbHelper, FileEntry
from anidbsync.auto import AutoRepr
from anidbsync.config import KodiConfig, AniDBConfig, get_anidb_config, get_kodi_config
from anidbsync.kodi.kodi import KodiHelper, KodiSeason, KodiEpisode, KodiTVShow
from anidbsync.logger import get_logger

logger = get_logger('anidbsync')

state_name = 'start.conf'


def get_starting_series():
    try:
        with open(state_name) as f:
            content = f.read()
            return int(content)
    except (FileNotFoundError, ValueError):
        return 0


def set_starting_series(start_at: int):
    with open(state_name, 'w') as f:
        f.write(str(start_at))


class Result(AutoRepr):
    def __init__(self):
        self.assume_unwatched = True
        self.assume_watched = True
        self.some_watched = False
        self.all_unwatched = False
        self.all_watched = False

    def update(self, anidb_file: FileEntry, season: KodiSeason, ep: KodiEpisode):
        self.update_assumed(anidb_file)
        if anidb_file.watched:
            if not season.num == 0:  # 0 = Specials (Openings, Endings etc)
                self.some_watched = True
            if self.assume_watched and ep.episode == season.episode_count:
                self.all_watched = True
        elif self.assume_unwatched and ep.episode == season.episode_count:
            self.all_unwatched = True

    def update_assumed(self, anidb_file: FileEntry):
        self.assume_unwatched = self.assume_unwatched and not anidb_file.watched
        self.assume_watched = self.assume_watched and anidb_file.watched


class AnimeSync:
    def __init__(self, kodi_config: KodiConfig, anidb_config: AniDBConfig, start_at=0):
        self.kodi = KodiHelper(config=kodi_config, start_at=start_at)
        self.anidb = AnidbHelper(config=anidb_config)
        self.shows = self.kodi.get_tvshows()
        self.current_result = Result()

    def sync(self):
        for show in self.shows:
            print('Processing show ' + show.title)
            seasons = self.kodi.get_seasons(show.id)
            self.current_result = Result()
            for season in seasons:
                unwatched = self.get_unwatched_optimized_order(season, show)
                for ep in unwatched:
                    if self.current_result.all_watched:
                        self.kodi.mark_as_watched(ep)
                        continue
                    if self.current_result.all_unwatched:
                        print('First 2 episodes of ' + show.title + ' are unwatched. Assuming the series is unwatched')
                        break
                    self.sync_episode(ep, season, show)
                if self.current_result.all_unwatched:
                    break
            set_starting_series(show.id)

    def sync_episode(self, ep: KodiEpisode, season: KodiSeason, show: KodiTVShow):
        episode_log_info = str(ep.episode) + "[" + str(ep.id) + "] of " + season.name + " of " + show.title + "[" + \
                           str(show.id) + "]"
        print("Processing episode " + episode_log_info)
        if 'Specials' in season.name and ('Opening' in ep.file or 'Ending' in ep.file):
            # Don't try to check anidb for watched status of ed/op
            if self.current_result.some_watched:
                self.kodi.mark_as_watched(ep)
            return
        anidb_file = self.anidb.load_episode_details(show.title, ep.group, ep.episode)
        if anidb_file is None:
            logger.info('Could not retrieve data for episode' + episode_log_info)
            anidb_file = FileEntry.UNWATCHED

        if anidb_file.watched:
            self.kodi.mark_as_watched(ep)
        self.current_result.update(anidb_file, season, ep)

    def get_unwatched_optimized_order(self, season: KodiSeason, show: KodiTVShow):
        unwatched = self.kodi.get_unwatched_episodes(show.id, season.num, end=season.episode_count)
        # Make sure to only reorder if we actually have the full series to work with
        if len(unwatched) < 2 or not unwatched[0].episode == 1 or not unwatched[-1].episode == season.episode_count:
            return unwatched
        episode_check_order = [0, 1, -1] + [i + 2 for i in range(len(unwatched) - 3)]
        return [unwatched[i] for i in episode_check_order]


if __name__ == '__main__':
    start = get_starting_series()
    anisync = AnimeSync(get_kodi_config(), get_anidb_config(), start_at=start)
    anisync.sync()
