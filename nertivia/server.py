class Server(object):
    def __init__(self, server):
        self.id = server['server_id']
        self.name = server['name']
        self.default_channel = server['default_channel_id']
        self.created = server['created']

    @property
    def _id(self):
        return self.id

    @property
    def _name(self):
        return self.name
