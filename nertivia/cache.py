import gc

import nertivia

'''
DELETE -> DEPRECATED
'''

# Imports not used ? Worth checking for cleanup


class Cache:
    """
    | DEPRECATED USE cache_nertivia_data.py INSTEAD |
    Cache class, Instances of this object hold channel & server cache (Not user cache)
    """

    def __init__(self, guilds: dict, users: dict, channels: dict):
        """
        Cannot check -- Arguments should be dictionaries
        """
        self.guilds = guilds
        self.users = users
        self.channels = channels

    @property
    def servers(self):
        """
        Synchronously request a list of cached servers
        """
        return list(self.guilds.values())

    def get_server(self, server_id):
        """
        Synchronously retrieve from cache a server using its ID
        """
        return self.guilds.get(str(server_id))

    def get_channel(self, channel_id):
        """
        Synchronously obtain a channel from its id
        """
        return self.get(channel_id)
