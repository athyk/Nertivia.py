import nertivia
from nertivia import http


class Server(object):
    def __init__(self, server, **kwargs):
        self.http = http.HTTPClient()
        self.id = server['server_id']
        self.name = server['name']
        self.default_channel: nertivia.Channel = server['default_channel_id']

    @property
    def _id(self):
        return self.id

    @property
    def _name(self):
        return self.name
