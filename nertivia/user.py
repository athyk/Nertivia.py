class User(object):
    def __init__(self, user):
        if "uniqueID" in user["user"]:
            self.id = user['user']['uniqueID']
        else:
            self.id = user['user']['id']
        self.username = user['user']['username']
        self.tag = user['user']['tag']
        self.bot = user['user']['bot']
        self.survey_completed = user['user']['survey_completed']
        self.banner = user['user']['banner']
        self.avatar_url = "https://nertivia.net/api/avatars/{}".format(user['user']['avatar'])
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
