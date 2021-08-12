import asyncio

import nertivia
import nertivia.bot
from nertivia import http

URL = "https://nertivia.net/api/messages/channels/"
URL_MSG = "https://nertivia.net/api/messages/"
URL_STA = "https://nertivia.net/api/settings/status"


class Message:
    # __slots__ = ('id', 'content', 'author')

    def __init__(self, message, **kwargs):
        self.id: int = message['message']['messageID']
        self.content: str = message['message']['message']
        self.http = nertivia.bot.HTTPClient()
        self.channel: nertivia.Channel = self.http.get_channel(message["message"]["channelID"])
        self.server: nertivia.Server = self.channel.server
        self.author: str = message['message']['creator']['username'] + '@' + message['message']['creator']['tag']

    def __repr__(self):
        return f"<id={self.id} content={self.content} channel=<{self.channel.__repr__()}> server=<{self.server.__repr__()}> author={self.author}"


    @property
    def _id(self):
        return self.id

    @property
    def _author(self):
        return self.author

    async def edit(self, channel, content):
        await self.http.edit_message(self.id, channel, content)

    async def send(self, message):
        await self.http.send_message(self.channel.id, message)

    async def delete(self):
        await self.http.delete_message(self.id, self.channel.id)
