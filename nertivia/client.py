import requests
from .user import *
import socketioN

SOCKET_IP = "https://nertivia.net/"
sio = socketioN.Client(engineio_logger=True, logger=True)


class Client:
    def __init__(self):
        self._listeners = {}
        self.token = None
        self.sio = sio
        self.headers = {'Accept': 'text/plain',
                        'authorization': self.token,
                        'Content-Type': 'application/json;charset=utf-8'}

    def _get_sio(self):
        return self.sio

    def login(self, token):
        print("Deprecated client! Please use nertivia.bot instead!")
        self.token = token.strip()
        self.sio.connect(SOCKET_IP, namespaces=['/'], transports=['websocket'])

        @self.sio.event
        def connect():
            sio.emit('authentication', {'token': token})

        return self.sio

    def get_user(self, userID):
        print("Deprecated client! Please use nertivia.bot instead!")
        headers = {'Accept': 'text/plain',
                   'authorization': self.token,
                   'Content-Type': 'application/json;charset=utf-8'}
        r1 = requests.get(url=f'https://nertivia.net/api/user/{userID}', headers=headers)
        user = r1.json()

        user = User(user)

        return user

    def event(self, *args):
        print("Deprecated client! Please use nertivia.bot instead!")
        if args[0].__name__ == "on_ready":
            return self.sio.on("success")(args[0])
        if args[0].__name__ == "on_message":
            return self.sio.on("success")(args[0])
        if args[0].__name__ == "on_quit":
            return self.sio.on("disconnect")(args[0])
