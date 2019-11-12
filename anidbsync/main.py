from anidbsync.anidb.anidb import AnidbHelper, FileEntry
from anidbsync.config import KodiConfig, AniDBConfig, get_anidb_config, get_kodi_config
from anidbsync.kodi.kodi import KodiHelper
import re

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


def sync_anime(kodi_config: KodiConfig, anidb_config: AniDBConfig, start_at=0):
    kodi = KodiHelper(config=kodi_config, start_at=start_at)
    anidb = AnidbHelper(config=anidb_config)

    shows = kodi.get_tvshows()
    for show in shows:
        for season in range(1, show.seasons + 1):
            unwatched = kodi.get_unwatched_episodes(show.id, season, end=show.episode_count)
            first_n_unwatched = unwatched[0].episode == 1
            for ep in unwatched:
                print('Processing Episode', ep.episode, '[', ep.id, '] of ', show.title, '[', show.id, ']')
                group = re.search("\\[(.+?)\\]", ep.file).group(1)
                anidb_file = anidb.load_episode_details(show.title, group, ep.episode)
                if anidb_file is None:
                    logger.info(
                        'AniDbError: show: ' + show.title + '[' + str(show.id) + ']:' + str(ep.episode) + '[' + str(
                            ep.id) + ']')
                    anidb_file = FileEntry.UNWATCHED
                first_n_unwatched = not anidb_file.watched
                if anidb_file.watched and not ep.watched:
                    kodi.mark_as_watched(ep)
                elif first_n_unwatched and not anidb_file.watched and ep.episode >= 2:
                    break
                # if not anidb_file.watched and ep.watched:
                #     anidb.mark_watched(anidb_file)
        set_starting_series(show.id)


if __name__ == '__main__':
    start = get_starting_series()
    sync_anime(get_kodi_config(), get_anidb_config(), start_at=start)
