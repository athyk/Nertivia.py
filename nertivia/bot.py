import json
import logging
import nertivia.events
import websockets

import asyncio


class Bot(object):
    def __init__(self,
                 logger: logging.Logger = False,
                 request_timeout=5,
                 max_retries=3,
                 max_messages=600,
                 max_reactions=100,
                 max_channels=100,
                 max_members=100,
                 max_roles=100,
                 max_emojis=100,
                 max_invites=-1,
                 test=False
                 ):
        self.url = 'wss://nertivia.net/socket.io/?EIO=4&transport=websocket'  # Server to connect to

        self.token = None  # Token to use for any http or websocket requests

        self.logger = logging.getLogger('nertivia.bot')  # Set up logger, allows use for own logger
        if logger:
            self.logger = logger

        self.logger.setLevel(logging.ERROR)
        if test:
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(logging.StreamHandler())

        self.handlers = {}  # Stores events

        self.request_timeout = request_timeout
        self.max_retries = max_retries
        # Cache options
        self.max_messages = max_messages
        self.max_reactions = max_reactions
        self.max_channels = max_channels
        self.max_members = max_members
        self.max_roles = max_roles
        self.max_emojis = max_emojis
        self.max_invites = max_invites

    def on(self, event, handler=None):

        # noinspection PyShadowingNames
        def set_handler(handler):
            self.handlers[event] = handler
            return handler

        if handler is None:
            return set_handler

        set_handler(handler)

    def event(self, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # the decorator was invoked without arguments
            # args[0] is the decorated function
            return self.on(args[0].__name__)(args[0])

        # the decorator was invoked with arguments

        def set_handler(handler):
            return self.on(handler.__name__, *args, **kwargs)(handler)

        return set_handler

    async def call_event(self, event, data):
        self.logger.info("Calling event: " + event)
        renamed_event = nertivia.events.events[event]
        if renamed_event in self.handlers:
            await self.handlers[renamed_event](data)

    def login(self, token, url=None):
        self.token = token

        if url:
            self.url = url
        asyncio.get_event_loop().run_until_complete(asyncio.ensure_future(self.run()))

    async def send_ws_message(self, ws, message):
        await ws.send(message)
        if message == "3":
            self.logger.info("↑ WebSocket pong")
        else:
            self.logger.info("↑ BCAST WebSocket message: " + message)

    async def handle_message(self, ws, message):
        self.logger.info("↓ WebSocket received: %s" % message)
        code = message[:2].replace("{", "").replace("}", "").replace(":", "")
        if code == "0":
            await self.send_ws_message(ws, "40")
        elif code == '40':
            self.logger.info("↓ WebSocket connected")
            # Broadcast authentication to prevent being kicked
            await self.send_ws_message(ws,
                                       '42["authentication", {"token": "{%s}"}]'.replace("{%s}", self.token))
        elif code == "2":
            self.logger.info("↓ WebSocket thread: ping")
            await self.send_ws_message(ws, "3")  # Send pong to ping
        elif code == "42":
            message = json.loads(message[2:])
            event = message[0]
            data = message[1]
            self.logger.info("↓ WebSocket event: " + event, data)
            await self.call_event(event, data)

    async def ws_close(self, ws):
        self.logger.info("WebSocket thread: closed")
        await self.call_event("disconnected", {})
        await ws.close()

    async def run(self):
        self.logger.info('Starting bot')
        async with websockets.connect(self.url) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    await self.handle_message(websocket, message)
                except websockets.ConnectionClosed:
                    await self.ws_close(websocket)
                    break
                except websockets.ConnectionClosed:
                    self.logger.info('ConnectionClosed')
                    is_alive = False
                    break
