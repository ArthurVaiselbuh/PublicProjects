#!/usr/bin/python

import requests
import sys
from bs4 import BeautifulSoup as bs4

class LyricsFetcher(object):
    """
    This class handles getting lyrics from correct site, returning just the lyrics themselves.
    """

    def __init__(self):
        self.handlers = []
        self.handlers.append(_ChartLyrics())

    def get_lyrics(self, song, artist):
        #print "Getting song:{}, artist:{}".format(song, artist)
        for handler in self.handlers:
            try:
                return handler.get_lyrics(song, artist)
            except Exception as e:
                t = type(e)
                if t in [NotFoundError, requests.exceptions.RequestException]:
                    #Try next site.
                    continue
                #unknown issue, raise
                raise


class SiteHandler(object):
    def get_lyrics(self, song_name, artist):
        raise NotImplementedError

class _ChartLyrics(SiteHandler):
    def __init__(self):
        self._search_url = "http://api.chartlyrics.com/apiv1.asmx/SearchLyric"
    
    def get_lyrics(self, song, artist):
        song_url = self._search_for(song, artist)
        return self._get_lyrics(song_url)

    def _search_for(self, song, artist):
        sending_data = dict(artist=artist,
                        song=song
        )
        res = requests.get(self._search_url, params=sending_data)
        #print "*** Got response:", res.text
        print "From url:", res.url
        song_url = self._extract_song_url(res.text)
        print "song url:", song_url
        return song_url

    def _get_lyrics(self, url):
        page = requests.get(url)
        soup = bs4(page.text, "lxml")
        lyrics = soup.find("p").getText()
        return lyrics

    def _extract_song_url(self, data):
        soup = bs4(data, "lxml")
        tag = soup.find("songurl")
        return tag.getText()
    
class NotFoundError(Exception):
    pass

if __name__ == '__main__':
    fetcher = LyricsFetcher()
    print fetcher.get_lyrics(sys.argv[1], sys.argv[2])