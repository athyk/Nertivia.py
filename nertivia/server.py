import nertivia
from nertivia import http


class Server(object):
    """
    Object representing a server
    """
    def __init__(self, server, **kwargs):
        """
        Set basic variables for ease of use
        """
        self.http = http.HTTPClient()
        if server is not None:
            self.id = server['server_id']
            self.name = server['name']
            self.default_channel: nertivia.Channel = server['default_channel_id']

    def __repr__(self):
        """
        Returns a representation of the class
        """
        return f"<id={self.id} name='{self.name}' default_channel=<{self.default_channel}>>"

    @property
    def _id(self):
        """
        Returns the server id
        """
        return self.id

    @property
    def _name(self):
        """
        Returns the server name
        """
        return self.name
