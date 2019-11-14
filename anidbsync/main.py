from anidbsync.anidb.anidb import AnidbHelper, FileEntry
from anidbsync.config import KodiConfig, AniDBConfig, get_anidb_config, get_kodi_config
from anidbsync.kodi.kodi import KodiHelper
import re
import operator
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


def get_unwatched_optimized_order(unwatched, episode_count):
    # Make sure to only reorder if we actually have the full series to work with
    if len(unwatched) < 2 or not unwatched[0].episode == 1:
        return unwatched
    # Make sure the last episode in the list is not a special
    if unwatched[-1].episode == episode_count:
        episode_check_order = [0, 1, len(unwatched) - 1] + [i + 2 for i in range(len(unwatched) - 3)]
        return [unwatched[i] for i in episode_check_order]
    else:
        # Ignore the special
        return get_unwatched_optimized_order(unwatched[:-1], episode_count - 1) + [unwatched[-1]]


def sync_anime(kodi_config: KodiConfig, anidb_config: AniDBConfig, start_at=0):
    kodi = KodiHelper(config=kodi_config, start_at=start_at)
    anidb = AnidbHelper(config=anidb_config)
    shows = kodi.get_tvshows()
    for show in shows:
        print('Processing show ' + show.title)
        seasons = kodi.get_seasons(show.id)
        seasons.sort(key=operator.attrgetter('num'), reverse=True)
        some_watched = False
        for season in seasons: # Start with s1 instead of s0 (= specials / openings / endings etc)
            unwatched = kodi.get_unwatched_episodes(show.id, season.num, end=season.episode_count)
            if len(unwatched) == 0:
                break
            optimized_order = get_unwatched_optimized_order(unwatched, season.episode_count)
            first_n_unwatched = optimized_order[0].episode == 1
            last_ep = optimized_order[2].episode if len(optimized_order) > 2 else optimized_order[-1].episode
            all_watched = False
            for ep in optimized_order:
                print('Processing Episode', ep.episode, '[', ep.id, '] of ', season.name, ' of ', show.title, '[', show.id, ']')
                group = re.search("\\[(.+?)\\]", ep.file).group(1)

                #
                if 'Specials' in season.name and ('Opening' in ep.file or 'Ending' in ep.file):
                    if some_watched:
                        kodi.mark_as_watched(ep)
                    continue
                anidb_file = anidb.load_episode_details(show.title, group, ep.episode)
                if anidb_file is None:
                    logger.info(
                        'AniDbError: show: ' + show.title + '[' + str(show.id) + ']:' + str(ep.episode) + '[' + str(
                            ep.id) + ']')
                    anidb_file = FileEntry.UNWATCHED
                first_n_unwatched = first_n_unwatched and not anidb_file.watched
                all_watched = all_watched and anidb_file.watched

                if anidb_file.watched:
                    some_watched = True

                if anidb_file.watched and not ep.watched:
                    if ep.episode == last_ep:
                        # Assume all are watched
                        all_watched = True
                        break
                    kodi.mark_as_watched(ep)
                elif first_n_unwatched and not anidb_file.watched and ep.episode >= 2:
                    print('First 2 episodes of ' + show.title + ' are unwatched. Assuming the series is unwatched')
                    break
                # if not anidb_file.watched and ep.watched:
                #     anidb.mark_watched(anidb_file)
            if all_watched:
                print('First, second and last episodes are watched. Assuming ' + show.title + ' is watched')
                for e in optimized_order:
                    kodi.mark_as_watched(e)
        set_starting_series(show.id)


if __name__ == '__main__':
    start = get_starting_series()
    sync_anime(get_kodi_config(), get_anidb_config(), start_at=start)
