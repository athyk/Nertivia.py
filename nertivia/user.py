class User(object):
    """
    Object representing a user
    """
    def __init__(self, user, **kwargs):
        """
        Instantiate variables to be used later on
        """
        # If the user is not cached
        if user is not None:
            if "user" not in user:
                user = {"user": user}

            # Check whether the user ID is stored under `uniquerID` or `id`
            if "uniqueID" in user["user"]:
                self.id = user['user']['uniqueID']
            else:
                self.id = user['user']['id']

            self.username = user['user']['username']
            self.tag = user['user']['tag']

            # Set it to false first in case it doesn't exist, same story as using an &&
            self.bot = False if "bot" not in user["user"] else user["user"]["bot"]

            self.avatar_url = "https://nertivia.net/api/avatars/{}".format(user['user']['avatar'])

            # Set the user representation as Username#Tag
            self.user = "{}@{}".format(user['user']['username'], user['user']['tag'])

    def __repr__(self):
        """
        Returns a representation of the object
        """
        return f"<id={self.id} username='{self.username}' tag='{self.tag}' " \
               f"avatar_url='{self.avatar_url}' user='{self.user}' bot={self.bot}>"

    @property
    def _id(self):
        """
        Returns the id of the User
        """
        return self.id

    @property
    def _name(self):
        """
        Returns the name of the user
        """
        return self.username

    @property
    def _avatar_url(self):
        """
        Returns the url of the avatar of the user
        """
        return self.avatar_url

    @property
    def _user(self):
        """
        Returns the representation of the users name
        """
        return self.user
