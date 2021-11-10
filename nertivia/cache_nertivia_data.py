from collections import OrderedDict
from typing import Dict

# The following dictionaries hold all cached information relative to their name
from .user import User
from .server import Server


class LimitedCache(OrderedDict):
    """
    Holds limited amount of information, acts as a cache object for messages objects
    Size of it can be edited during initialisation
    """

    def __init__(self, maxsize=500, /, *args, **kwds):
        """
        MaxSize affects the maximum size of the cache (main use -> messages to reduce RAM usage)
        """
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    def __getitem__(self, key):
        """
        Synchronously obtain the requested item depending on the key
        """
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        """
        Synchronously set an item of the cache to a given value
        """
        super().__setitem__(key, value)
        # Bit of logic to max sure that the maxsize is respected
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


users: OrderedDict[str, User] = LimitedCache(maxsize=300)
members: OrderedDict[str, User] = LimitedCache(maxsize=800)
guilds: Dict[str, Server] = {"0": Server(None)}
user: User = User(None)

messages = LimitedCache(maxsize=1000)
