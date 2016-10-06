import threading

class ReturnThread(threading.Thread):
    def __init__(self, target, args=(), kwargs={}):
        assert callable(target)
        super(ReturnThread, self).__init__()
        self._return_val = None
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._return_val = self._target(*self._args, **self._kwargs)

    def join(self, timeout=None):
        super(ReturnThread, self).join(timeout)
        return self._return_val

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs