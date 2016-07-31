import logging

class Event(object):
    def __init__(self):
        self._callbacks = list()
    
    def emit(self, *args):
        """
        Call every callback with args if provided.
        Target function must accpet the argument.
        """
        for callback in self._callbacks:
            try:
                callback(*args)
            except Exception:
                logging.error("Error calling callback {} in event:{}".format(callback, self))

    def connect(self, callback):
        """
        Register callback to be called when event is emitted
        """
        self._callbacks.append(callback)

    def disconnect(self, callback):
        """
        Unregister an already connected callback
        """
        self._callbacks.remove(callback)
