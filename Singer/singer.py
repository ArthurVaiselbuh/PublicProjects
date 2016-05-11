#!/usr/bin/python
import lyrics
import pyttsx
import sys
import time

lyric_api = lyrics.LyricsFetcher()

class Singer(object):
    def __init__(self):
        self.speech = pyttsx.init()
        self.speech.setProperty("rate", 150)
        self.speech.setProperty("voice", "english-us")
        self.lines = []
        self.speech.startLoop(False)

    def isBusy(self):
        return self.speech.isBusy()

    def sing(self, song_name, artist):
        print "Performing \"{}\", by {}".format(song_name, artist)
        lyrics = lyric_api.get_lyrics(song_name, artist)
        #self.speech.connect("finished-utterance")
        print "Sing along!"
        for line in lyrics.split("\n"):
            print line
            self.speech.say(line)
            self.speech.iterate()

    def say_next_line(self, param):
        print "param:{}".format(param)
        if not self.lines:
            return
        self.speech.say(self.lines[0])
        self.lines = self.lines[1:]

if __name__ == "__main__":
    song, artist = sys.argv[1], sys.argv[2]
    singer = Singer()
    singer.sing(song, artist)
    while singer.isBusy():
        time.sleep(0.1)