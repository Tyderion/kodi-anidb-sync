from anidbsync.anidb.anidb import AnidbHelper
from anidbsync.config import KodiConfig, AniDBConfig, get_anidb_config, get_kodi_config
from anidbsync.kodi.kodi import KodiHelper
import re

from anidbsync.logger import get_logger

logger = get_logger('anidbsync')


def sync_anime(kodi_config: KodiConfig, anidb_config: AniDBConfig):
    kodi = KodiHelper(kodi_config)
    anidb = AnidbHelper(anidb_config)

    shows = kodi.get_tvshows()
    for show in shows:
        for season in range(1, show.seasons + 1):
            unwatched = kodi.get_unwatched_episodes(show.id, season, end=show.episode_count)
            for ep in unwatched:
                print('Processing Episode', ep.episode, '[', ep.id, '] of ', show.title, '[', show.id, ']')
                group = re.search("\\[(.+?)\\]", ep.file).group(1)
                anidb_file = anidb.load_episode_details(show.title, group, ep.episode)
                if anidb_file is None:
                    logger.info(
                        'AniDbError: show: ' + show.title + '[' + str(show.id) + ']:' + str(ep.episode) + '[' + str(
                            ep.id) + ']')
                    print("Could not find episode ", ep.episode, 'of', ep.show)
                if anidb_file.watched and not ep.watched:
                    kodi.mark_as_watched(ep)
                # if not anidb_file.watched and ep.watched:
                #     anidb.mark_watched(anidb_file)


if __name__ == '__main__':
    sync_anime(get_kodi_config(), get_anidb_config())
