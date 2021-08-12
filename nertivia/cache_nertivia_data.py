from collections import OrderedDict

users = {}
members = {}
guilds = {}
user = {}

class LimitedCache(OrderedDict):
    def __init__(self, maxsize=500, /, *args, **kwds):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


messages = LimitedCache()
