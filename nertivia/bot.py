import asyncio
import logging
import traceback

import socketioN
from .http import HTTPClient
from .user import User

default_logger = logging.getLogger('nertivia')

SOCKET_IP = "https://nertivia.net"

token = None
user = None


class Bot:
    """
    Bot class object, represents the interface which represents the bot user
    """
    global token, default_logger

    def __init__(self, **args) -> None:
        """
        :param args:
        Expects named arguments, wrapped in **args
        Possible arguments are :
            `test` for a local Nertivia Test Server
            `debug` to activate debug mode (increased information logging)
            None for regular operation
        """

        # Socket IP is a string representing the url to the Nertivia Server (By default the official Server,nertivia.net
        # user is a User class object from user.py, set to None but expected to be defined before the Bot class being
        # - Initiated
        global SOCKET_IP, user

        # Check if a local server is being used to test Nertivia features (Address hardcoded to be the default one)
        if args.get("test"):
            # noinspection HttpUrlsUsage
            SOCKET_IP = "http://server.localtest.me"

        # Check if the library user desires mass information logging for debug purposes, if so initialises the client
        # Accordingly
        if args.get("debug"):
            self.sio = socketioN.AsyncClient(logger="True", engineio_logger="True")
        # Otherwise the bot is started normally
        else:
            self.sio = socketioN.AsyncClient()

        # Set self.http to the HTTP client connection object for future use
        self.http = HTTPClient(socket_ip=SOCKET_IP)

        # Note : Consider moving around, if i forgot to remove this check feasibility to move this upwards
        import nertivia.cache_nertivia_data
        self.user: User = nertivia.cache_nertivia_data.user
        self.headers = {'Accept': 'text/plain',
                        'authorization': token,
                        'Content-Type': 'application/json;charset=utf-8'}

    def _get_sio(self):
        """
        :return:
        Synchronous function returning the AsyncClient object from socketioN
        """
        return self.sio

    async def main(self, new_token: str) -> None:
        """
        :param new_token:
        :return None:

        Asynchronous function initiating a (new) connection to Nertivia using the Token (str) passed as an argument
        """

        # Start connection to SOCKET_IP, then send authentication header
        await self.sio.connect(SOCKET_IP, transports=['websocket'])
        await self.sio.emit('authentication', {'token': new_token})
        self.sio.on('update_bot_user', self.update_bot_user)
        a_sio = self.sio

        # Wait for a response, if an authentication error has occurred auth_err() is called
        @a_sio.event
        def auth_err(data):
            print("Invalid Token")

        @a_sio.event
        async def connect():
            print("reconnected to server!")
            await self.sio.emit('authentication', {'token': new_token})
        await a_sio.wait()

    def update_bot_user(self, data):
        """
        :param data:
        :return:

        Update the Bot User: replace it by a new/updated `bot` Instance
        """
        global user
        self.user = data

    def login(self, new_token: str):
        """
        :param new_token:
        :return:

        Have the script login into an account using a provided Token
        """

        # Set global token to the provided token, before then setting the token globally to the http connection object
        # After which, call `main` method using asyncio.run as it is an asynchronous function
        global token
        token = new_token
        self.http.set_token(token)
        asyncio.run(self.main(new_token))

        return self.sio

    async def get_user(self, userID):
        """
        :param userID:
        :return:

        Obtain a user object from user.py from cache preferably, but if not cached then fetch it
        """
        return await self.http.get_user(userID)

    def on(self, event, handler=None, namespace=None):
        """
        :param event:
        :param handler:
        :param namespace:
        :return:

        Event Handler, creates Handlers if non existent
        """

        # Exceptions may happen
        try:
            namespace = namespace or '/'

            # Set a Handler to an event, handlers are set in the dictionary mess inside of sio.handlers
            # noinspection PyShadowingNames
            def set_handler(handler):
                # If namespace doesn't exist in the handlers dictionary, we create a dictionary for it before moving on
                if namespace not in self.sio.handlers:
                    self.sio.handlers[namespace] = {}

                # If the event doesn't exist inside of the handler, inside of the namespace then we create a list for it
                if event not in self.sio.handlers[namespace]:
                    self.sio.handlers[namespace][event] = []

                # Finally we append the handler to the correct list
                self.sio.handlers[namespace][event].append(handler)

                return handler

            # If the event handler isn't set then we return the function that links a handler to an event once
            # The handler is created (so that it may be passed as an argument)
            if handler is None:
                return set_handler

            # Otherwise, we just call set_handler
            set_handler(handler)

        # In case something unexpected happened, we catch it and print the error
        except Exception:
            # noinspection PyArgumentList
            traceback.print_exc()

    def event(self, *args):
        """
        :param args:
        :return:

        Handler for all event.x decorators
        Also this is a nice if wall
        """
        HandledEvents = {"on_ready": "on_ready", "on_message": "receiveMessage", "on_quit": "disconnect",
                         "on_status_change": "member:custom_status_change", "on_message_delete": "delete_message",
                         "on_message_edit": "update_message"}

        for Key, Value in HandledEvents.items():
            if args[0].__name__ == Key:
                return self.on(Value)(args[0])
