import asyncio

import socketioN
from .http import HTTPClient

SOCKET_IP = "https://nertivia.net"
sio = socketioN.AsyncClient()

token = None


class Bot:
    global token

    def __init__(self, **args):
        global SOCKET_IP
        if args.get("test"):
            SOCKET_IP = "http://server.localtest.me"
        self._listeners = {}
        self.sio = sio
        self.http = HTTPClient(socket_ip=SOCKET_IP)
        self.headers = {'Accept': 'text/plain',
                        'authorization': token,
                        'Content-Type': 'application/json;charset=utf-8'}

    def _get_sio(self):
        return self.sio

    async def main(self, new_token):
        await self.sio.connect(SOCKET_IP, namespaces=['/'], transports=['websocket'])
        await sio.emit('authentication', {'token': new_token})

        @sio.event
        def auth_err(data):
            print("Invalid Token")
        await sio.wait()

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
            self.sio.handlers[namespace][event] = handler
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
