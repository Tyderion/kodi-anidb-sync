# Anidb-Kodi-Sync
Synchronizes the watched status of your anime list on [aniDB](https://anidb.net).

If your anime files are named in a way that the group is in the first `[]`, e.g. `One Piece - 01 [FansubGroup]` it should work.

I suggest using Scudlees [AniDB scraper](https://forum.kodi.tv/showthread.php?tid=142835) for Kodi. If you use his AniDB Renaming Tags list it should work.

## Install dependencies
`pip install -r requirements.txt`

## Configuration
Setup your environment variables as follows (or change values in config.py)
### Anidb
- `ANIDB.USERNAME` - Your AniDB Username
- `ANIDB.PASSWORD` - Your AniDB Password
- `ANIDB.API_KEY` - Optional: Your Anidb UDP Api Key (encrypts traffic, needs pycrypt installed)

### Kodi
- `KODI.URL` - Your Kodi instance url or ip
- `KODI.PASSWORD` - Optional: Your Kodi remote access password (omitting works for default Kodi config)
- `KODI.PORT` - Optional: Your Kodi remote access port (omitting works for default Kodi config)

## Synchronize
Run main.py to synchronize all watched files from aniDB to your Kodi instance.
Also supports reverse synchro (from Kodi to aniDB)

# TODO
Detect newly watched episodes and sync back to aniDB