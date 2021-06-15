import asyncio

import nertivia
import nertivia.bot
from nertivia import http

URL = "https://nertivia.net/api/messages/channels/"
URL_MSG = "https://nertivia.net/api/messages/"
URL_STA = "https://nertivia.net/api/settings/status"


class Message:
    # __slots__ = ('id', 'content', 'author')

    def __init__(self, message):
        self.id: int = message['message']['messageID']
        self.content: str = message['message']['message']
        self.channel: nertivia.Channel = http.HTTPClient().get_channel(message["message"]["channelID"])
        self.server: nertivia.Server = self.channel.server
        self.author: str = message['message']['creator']['username'] + '@' + message['message']['creator']['tag']
        self.http = nertivia.bot.HTTPClient()

    @property
    def _id(self):
        return self.id

    @property
    def _author(self):
        return self.author

    async def edit(self, channel, content):
        await self.http.edit_message(self.id, channel, content)

    async def delete(self):
        await self.http.delete_message(self.id, self.channel.id)
