"""
    @author: jldupont
    @date: Aug 1, 2010
"""
__all__=["get_id3_params"]

from mutagen.easyid3 import EasyID3

def get_id3_params(path):
    """
    Retrieves the 'artist' and 'title' 
    for a given .mp3 file pointed to by 'path'
    """
    audio=EasyID3(path)
    try:    album=audio["album"][0]
    except: album=""
    return (audio["artist"][0], album, audio["title"][0])

