import requests
from .user import User
import socketioN

# Nertivia server endpoint
SOCKET_IP = "https://nertivia.net/"
sio = socketioN.Client(engineio_logger=True, logger=True)


class Client:
    """
    Client object, ancestor of Bot object found in bot.py
    DEPRECATED -> USE bot.py
    """
    def __init__(self):
        """
        Initiate the Client, set variables for future uses
        """
        self._listeners = {}
        self.token = None
        self.sio = sio
        self.headers = {'Accept': 'text/plain',
                        'authorization': self.token,
                        'Content-Type': 'application/json;charset=utf-8'}

    def _get_sio(self):
        """
        Return sio (socketioN.Client)
        """
        return self.sio

    def login(self, token):
        """
        Log into Nertivia using the Token to access the bot account
        """
        print("Deprecated client! Please use nertivia.bot instead!")

        # Obtain the token from the provided string
        self.token = token.strip()
        # Connect to the Nertivia severs
        self.sio.connect(SOCKET_IP, namespaces=['/'], transports=['websocket'])

        # Event listener, when asked return the authentication header
        @self.sio.event
        def connect():
            sio.emit('authentication', {'token': token})

        return self.sio

    def get_user(self, userID):
        """
        Obtain a user from their id
        This is a direct API call and doesn't cache | Beware & use bot.py
        """
        print("Deprecated client! Please use nertivia.bot instead!")
        headers = {'Accept': 'text/plain',
                   'authorization': self.token,
                   'Content-Type': 'application/json;charset=utf-8'}
        r1 = requests.get(url=f'https://nertivia.net/api/user/{userID}', headers=headers)
        user = r1.json()

        user = User(user)

        return user

    def event(self, *args):
        """
        Handles event decorators
        Only basic events are available as this is deprecated -> use bot.py
        """
        print("Deprecated client! Please use nertivia.bot instead!")
        if args[0].__name__ == "on_ready":
            return self.sio.on("success")(args[0])
        if args[0].__name__ == "on_message":
            return self.sio.on("success")(args[0])
        if args[0].__name__ == "on_quit":
            return self.sio.on("disconnect")(args[0])
