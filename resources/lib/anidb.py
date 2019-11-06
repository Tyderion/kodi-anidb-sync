import yumemi
import os
import logging
from time import sleep

logger = logging.getLogger('anidb_connect')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('anidb.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

class MyListEntry:
    def __init__(self, data):
        self.lid = data[0]
        self.fid = data[1]


class FileEntry:
    def __init__(self, data):
        self.fid = data[0]
        self.watched = data[1] == '1'


class AnidbHelper:
    def __init__(self):
        self.client = yumemi.Client()
        self.client.auth(os.environ['USERNAME'], os.environ['PASSWORD'])
        if not self.client.ping():
            raise ConnectionError

    def __del__(self):
        self.client.logout()

    def load_episode_details(self, anime, group, epNo):
        if len(anime) == 0:
            return FileEntry(['', '0'])
        res = self.client.call('MYLIST ', {'aname': anime, 'gname': group, 'epno': epNo})
        if res.code == 312:
            logger.info("MULTI: " + anime + "[" + group + "]: " + str(epNo))
            return FileEntry(['', int(res.data[0][6]) > 0])
        if res.code == 221:
            sleep(5)
            ml_entry = MyListEntry(res.data[0])
            res = self.client.call('FILE', {'fid': ml_entry.fid, 'fmask': '0000000020', 'amask': '00000000'})
            if res.code == 220:
                f_entry = FileEntry(res.data[0])
                return f_entry
        elif group == 'K-F':
            sleep(5)
            return self.load_episode_details(anime, 'Kaizoku-Fansubs', epNo)
        elif group == 'Kaizoku-Fansubs':
            sleep(5)
            return self.load_episode_details(anime, 'Kikkai-Fansub', epNo)

    def mark_watched(self, file):
        if len(file.fid) > 0:
            res = self.client.call('MYLISTADD ', {'fid': file.fid, 'edit': '1', 'viewed': '1'})
            print(res.message)

    def end(self):
        self.client.logout()

if __name__ == '__main__':
    anidb = AnidbHelper()
    ep = anidb.load_episode_details('One Piece', 'Kaizoku-Fansubs', '162')
    anidb.mark_watched(ep)
