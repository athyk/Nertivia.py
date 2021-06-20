class User(object):
    def __init__(self, user, **kwargs):
        self.cache = None
        if kwargs.get("cache"):
            self.cache = kwargs.get("cache")
        if "user" not in user:
            user = {"user": user}
        if "uniqueID" in user["user"]:
            self.id = user['user']['uniqueID']
        else:
            self.id = user['user']['id']
        if "username" in user["user"]:
            self.username = user['user']['username']
        if "tag" in user["user"]:
            self.tag = user['user']['tag']
        if "bot" in user["user"]:
            self.bot = user['user']['bot']
        #self.banner =  user['user']['banner']
        if "avatar" in user["user"]:
            self.avatar_url = "https://nertivia.net/api/avatars/{}".format(user['user']['avatar'])
        if "user" in user["user"] and "tag" in user["user"]:
            self.user = "{}@{}".format(user['user']['username'], user['user']['tag'])

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
