import logging
import gateway
import asyncio

class Bot(object):
    def __init__(self,
                 logger=False,
                 request_timeout=5,
                 max_retries=3,
                 max_messages=600,
                 max_reactions=100,
                 max_channels=100,
                 max_members=100,
                 max_roles=100,
                 max_emojis=100,
                 max_invites=-1,
                 test=False,
                 ):
        if not logger:
            self.logger = logging.getLogger('nertivia.bot')
            self.logger.setLevel(logging.ERROR)
            if test:
                self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(logging.StreamHandler())
            self.logger.info('Bot initialized')
        else:
            self.logger = logger
        self.handlers = {}
        self.request_timeout = request_timeout
        self.max_retries = max_retries
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

    def login(self, token, url = None):
        self.token = token
        self.url = url
        asyncio.get_event_loop().run_until_complete(self.run())
