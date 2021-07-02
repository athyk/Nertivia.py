import asyncio
import logging

import socketioN
from .http import HTTPClient

default_logger = logging.getLogger('nertivia')

SOCKET_IP = "https://nertivia.net"
#sio = socketioN.AsyncClient()  # logger=True, engineio_logger=True

token = None


class Bot:
    global token, default_logger

    def __init__(self, **args):
        global SOCKET_IP
        if args.get("test"):
            SOCKET_IP = "http://server.localtest.me"
        self._listeners = {}
        if args.get("debug"):
            self.sio = socketioN.AsyncClient(logger="True", engineio_logger="True")
        else:
            self.sio = socketioN.AsyncClient()
        self.http = HTTPClient(socket_ip=SOCKET_IP)
        self.headers = {'Accept': 'text/plain',
                        'authorization': token,
                        'Content-Type': 'application/json;charset=utf-8'}

    def _get_sio(self):
        return self.sio

    async def main(self, new_token):
        await self.sio.connect(SOCKET_IP, transports=['websocket'])
        await self.sio.emit('authentication', {'token': new_token})

        a_sio = self.sio

        @a_sio.event
        def auth_err(data):
            print("Invalid Token")

        await a_sio.wait()

    def login(self, new_token):
        global token
        token = new_token
        self.http.set_token(token)
        asyncio.run(self.main(new_token))

        return self.sio

    async def get_user(self, userID):
        return await self.http.get_user(userID)

    def on(self, event, handler=None, namespace=None):
        namespace = namespace or '/'

        def set_handler(handler):
            if namespace not in self.sio.handlers:
                self.sio.handlers[namespace] = {}
            if event not in self.sio.handlers[namespace]:
                self.sio.handlers[namespace][event] = []
            self.sio.handlers[namespace][event].append(handler)
            return handler

        if handler is None:
            return set_handler
        set_handler(handler)

    def event(self, *args):

        if args[0].__name__ == "on_ready":
            return self.on("success")(args[0])
        if args[0].__name__ == "on_message":
            return self.on("receiveMessage")(args[0])
        if args[0].__name__ == "on_quit":
            return self.on("disconnect")(args[0])
        if args[0].__name__ == "on_status_change":
            return self.on("member:custom_status_change")(args[0])
        if args[0].__name__ == "on_message_delete":
            return self.on("delete_message")(args[0])
