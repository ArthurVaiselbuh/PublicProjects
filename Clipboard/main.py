#!/usr/bin/python3
from handler import keylistener, start as h_start
import copy_handler


class KeyboardHandler:
    def __init__(self):
        self.clips = ["" for i in range(10)]
        self.keylistener = keylistener
        self.cur_clip = 1
        for i in range(10):
            # This default assignment is necessary due to how python handles func definition
            def tmp(i=i):   
                self.change_clip(i)
            self.keylistener.addKeyListener("L_CTRL+L_ALT+{}".format(i), tmp)

    def change_clip(self, clip):
        """
        changes current clip to clip.
        """
        print("Changing clip to", clip)
        # first copy contents of current clip to the array
        data = copy_handler.paste()
        self.clips[self.cur_clip] = data
        print("Recoverd clip:", data)
        # now change to new one
        copy_handler.copy(self.clips[clip])
        self.cur_clip = clip

    def start(self):
        h_start()

if __name__ == "__main__":
    h = KeyboardHandler()
    h.start()