import yumemi
import os
from time import sleep

from anidbsync.anidb.animemapping import ANIME
from anidbsync.config import AniDBConfig
from .groupmapping import GROUPS
from anidbsync.logger import get_logger
from anidbsync.auto import AutoRepr

logger = get_logger('anidb')

ANIDB_BANNED = 555

SLEEP_TIME = 7
SLEEP_TIME_BANNED = 1800


class MyListEntry(AutoRepr):
    def __init__(self, data):
        self.lid = data[0]
        self.fid = data[1]


class FileEntry(AutoRepr):
    UNWATCHED = None
    WATCHED = None

    def __init__(self, data):
        self.fid = data[0]
        try:
            self.watched = int(data[1]) > 0
        except ValueError:
            self.watched = False


FileEntry.UNWATCHED = FileEntry(['', '0'])
FileEntry.WATCHED = FileEntry(['', '1'])


class AnidbHelper:
    def __init__(self, username=None, password=None, api_key=None, config: AniDBConfig = None):
        self.client = yumemi.Client()
        if config is not None:
            self.config = config
        else:
            self.config = AniDBConfig(username=username, password=password, api_key=api_key)
        if self.config.username is None or self.config.password is None:
            raise AssertionError("Username and Password must be set")
        self.ensure_connection()

    def ensure_connection(self):
        try:
            self.client.auth(self.config.username, self.config.password)
            if self.config.api_key is not None:
                self.client.encrypt(self.config.api_key, self.config.username)
            if not self.client.ping():
                raise ConnectionError
        except yumemi.exceptions.ClientError as err:
            if err.response.code == ANIDB_BANNED:
                # Wait for half an hour
                logger.info("BANNED while logging in waiting 30min")
                sleep(SLEEP_TIME_BANNED)
                self.ensure_connection()
            else:
                raise

    def logout(self):
        self.client.logout()

    def __del__(self):
        self.logout()

    def load_episode_details(self, anime, group, epNo):
        if len(anime) == 0:
            return FileEntry.UNWATCHED
        if group in GROUPS:
            groups = GROUPS[group]
            for i in range(len(groups)):
                res = self._load_episode_details(anime, groups[i], epNo)
                if res is not None or i == len(groups):
                    return res
        return self._load_episode_details(anime, group, epNo)

    def _load_episode_details(self, anime, group, epNo):
        sleep(SLEEP_TIME)
        if anime in ANIME:
            anime = ANIME[anime]
        res = self.call('MYLIST ', {'aname': anime, 'gname': group, 'epno': epNo})
        if res.code == 312:
            logger.info("MULTI: " + anime + "[" + group + "]: " + str(epNo))
            return FileEntry(['', res.data[0][6]])
        if res.code == 221:
            sleep(SLEEP_TIME)
            ml_entry = MyListEntry(res.data[0])
            res = self.call('FILE', {'fid': ml_entry.fid, 'fmask': '0000000020', 'amask': '00000000'})
            if res.code == 220:
                return FileEntry(res.data[0])
        return None

    def mark_watched(self, file: FileEntry):
        sleep(SLEEP_TIME)
        if len(file.fid) > 0:
            res = self.call('MYLISTADD ', {'fid': file.fid, 'edit': '1', 'viewed': '1'})
            if res.code != 311:
                logger.info("Could not mark file as watched" + res.message)

    def call(self, name, args):
        try:
            return self.client.call(name, args)
        except yumemi.exceptions.ClientError as err:
            if err.response.code == ANIDB_BANNED:
                logger.info("BANNED while getting data waiting 30min")
                sleep(SLEEP_TIME_BANNED)
                self.ensure_connection()
                return self.client.call(name, args)
            else:
                raise


if __name__ == '__main__':
    anidb = AnidbHelper()
    ep = anidb.load_episode_details('One Piece', 'Kaizoku-Fansubs', '162')
    anidb.mark_watched(ep)
