from Xlib.display import Display
from Xlib import X
from Xlib.ext import record
from Xlib.protocol import rq
import time
from misc import keysym_map

disp = None

class KeyListener(object):
    def __init__(self):
        """Really simple implementation of a keylistener

        Simply define your keyevents by creating your keylistener obj,
        and then calling addKeyListener("keycombination", callable)

        Keycombinations are separated by plus signs:
        examples:

        >>> keylistener = KeyListener()
        >>> keylistener.addKeyListener("L_CTRL+L_SHIFT+y", callable)
        >>> keylistener.addKeyListener("b+a+u+L_CTRL", callable)
        >>> keylistener.addKeyListener("a", callable)

        ex:

        >>> keylistener = KeyListener()
        >>> def sayhi():
                print "hi!"
        >>> keylistener.addKeyListener("L_CTRL+a", sayhi)

        from this moment on, python will execute sayhi every time you press
        left ctrl and a at the same time.

        Keycodes can be found in the keysym map above.
        """
        self.pressed = set()
        self.listeners = {}

    def press(self, character):
        """"must be called whenever a key press event has occurred
        You'll have to combine this with release, otherwise
        keylistener won't do anything
        """
        self.pressed.add(character)
        action = self.listeners.get(tuple(sorted(self.pressed)), False)
        #print("current action: " + str(tuple(self.pressed)))
        if action:
            action()

    def release(self, character):
        """must be called whenever a key release event has occurred."""
        if character in self.pressed:
            self.pressed.remove(character)

    def addKeyListener(self, hotkeys, callable):
        keys = tuple(sorted(hotkeys.split("+")))
        #print("Added new keylistener for : " + str(keys))
        self.listeners[keys] = callable

keylistener = KeyListener()

def keysym_to_character(sym):
    if sym in keysym_map:
        return keysym_map[sym]
    else:
        return sym

def handler(reply):
    """ This function is called when a xlib event is fired """
    data = reply.data
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(data, disp.display, None, None)

        keycode = event.detail
        keysym = disp.keycode_to_keysym(event.detail, 0)

        if keysym in keysym_map:
            character = keysym_to_character(keysym)
            #print(character)
            if event.type == X.KeyPress:
                keylistener.press(character)
            elif event.type == X.KeyRelease:
                keylistener.release(character)

def start():
    global disp
    # get current display
    disp = Display()
    root = disp.screen().root

    # Monitor keypress and button press
    ctx = disp.record_create_context(
                0,
                [record.AllClients],
                [{
                        'core_requests': (0, 0),
                        'core_replies': (0, 0),
                        'ext_requests': (0, 0, 0, 0),
                        'ext_replies': (0, 0, 0, 0),
                        'delivered_events': (0, 0),
                        'device_events': (X.KeyReleaseMask, X.ButtonReleaseMask),
                        'errors': (0, 0),
                        'client_started': False,
                        'client_died': False,
                }])

    disp.record_enable_context(ctx, handler)
    disp.record_free_context(ctx)

    while True:
        time.sleep(.1)
        # Infinite wait, doesn't do anything as no events are grabbed
        event = root.display.next_event()
