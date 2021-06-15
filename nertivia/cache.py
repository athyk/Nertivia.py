import gc

import nertivia


class Cache:
    def __init__(self, guilds, users, channels):
        self.guilds = guilds
        self.users = users
        self.channels = channels

    @property
    def servers(self):
        return list(self.guilds.values())

    def get_server(self, server_id):
        return self.guilds.get(str(server_id))

    def get_channel(self, channel_id):
        value = self.get(channel_id)
        return value
