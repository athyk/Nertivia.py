class User(object):
    def __init__(self, user, **kwargs):
        if "user" not in user:
            user = {"user": user}
        if "uniqueID" in user["user"]:
            self.id = user['user']['uniqueID']
        else:
            self.id = user['user']['id']
        self.username = user['user']['username']
        self.tag = user['user']['tag']
        if "bot" in user["user"]:
            self.bot = user['user']['bot']
        else:
            self.bot = False
        self.avatar_url = "https://nertivia.net/api/avatars/{}".format(user['user']['avatar'])
        self.user = "{}@{}".format(user['user']['username'], user['user']['tag'])

    def __repr__(self):
        return f"<id={self.id} username='{self.username}' tag='{self.tag}' avatar_url='{self.avatar_url}' user='{self.user}' bot={self.bot}>"

    @property
    def _id(self):
        return self.id

    @property
    def _name(self):
        return self.username

    @property
    def _avatar_url(self):
        return self.avatar_url

    @property
    def _user(self):
        return self.user
