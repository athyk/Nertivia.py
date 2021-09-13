import nertivia
import nertivia.bot
from nertivia import http

# asyncio and nertivia.http unused ?

# Set the different endpoints that'll be used
URL = "https://nertivia.net/api/messages/channels/"
URL_MSG = "https://nertivia.net/api/messages/"
URL_STA = "https://nertivia.net/api/settings/status"


class Message:
    """
    Object class used to store a Messages information
    """
    def __init__(self, message, **kwargs):
        """
        Set different variables that'll be used later on for ease of access
        """
        # If a message object is passed then use its information to create this Message object
        # Otherwise create a new one from nothing
        if kwargs.get('http') and isinstance(kwargs['http'], http.HTTPClient):
            self.http = kwargs['http']
        else:
            self.http = http.HTTPClient()
        if "message" in message:
            self.id: int = message['message']['messageID']
            if "message" in message['message']:
                self.content: str = message['message']['message']
            else:
                self.content: str = ""
            if "files" in message['message']:
                self.files = message["message"]["files"]
            self.channel: nertivia.Channel = self.http.get_channel(message["message"]["channelID"])
            self.author: str = message['message']['creator']['username'] + '@' + message['message']['creator']['tag']

        else:
            self.id: int = message['messageID']
            self.content: str = message['message']
            self.channel: nertivia.Channel = self.http.get_channel(message["channelID"])
            self.author: str = message['creator']['username'] + '@' + message['creator']['tag']

        self.server: nertivia.Server = self.channel.server

    def __repr__(self):
        """
        Return a representation of the class Instance
        """
        return f"<id={self.id} content='{self.content}' channel={self.channel.__repr__()} " \
               f"server={self.server.__repr__()} author='{self.author}'>"

    @property
    def _id(self):
        """
        Return the ID of the message
        """
        return self.id

    @property
    def _author(self) -> nertivia.user:
        """
        Return the author of the message
        """
        return self.author

    async def edit(self, content):
        """
        Asynchronous function to edit a message, takes a channel object and a message content
        """
        await self.http.edit_message(self.id, self.channel.id, content)

    async def send(self, message):
        """
        Send a new message using a message
        Do not call manually
        """
        message = await self.http.send_message(self.channel.id, message)
        message_json = await message.json()
        return Message({"message": message_json["messageCreated"]})

    async def delete(self):
        """
        Asynchronously delete the message
        """
        await self.http.delete_message(self.id, self.channel.id)
