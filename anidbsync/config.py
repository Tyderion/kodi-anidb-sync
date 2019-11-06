import os


class KodiConfig:
    def __init__(self, url='localhost', password=None, port=None):
        self.url = url
        self.password = password
        self.port = port


class AniDBConfig:
    def __init__(self, username, password, api_key=None):
        self.username = username
        self.password = password
        self.api_key = api_key


def get_anidb_config():
    return AniDBConfig(username=os.environ.get('ANIDB.USERNAME'),
                       password=os.environ.get('ANIDB.PASSWORD'),
                       api_key=os.environ.get('ANIDB.API_KEY'))


def get_kodi_config():
    return KodiConfig(url=os.environ.get('KODI.URL'),
                      password=os.environ.get('KODI.PASSWORD'),
                      port=os.environ.get('KODI.PORT'))

