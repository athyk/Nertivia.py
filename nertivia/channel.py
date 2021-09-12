import nertivia
from nertivia import http
from nertivia import message

# Official Nertivia Server endpoints, Consider having the first part be variable and changeable from a central location
URL = "https://nertivia.net/api/messages/channels/"
URL_MSG = "https://nertivia.net/api/messages/"
URL_STA = "https://nertivia.net/api/settings/status"


class Channel(object):
    """
    Class defining a Channel, not expected to be manually instantiated
    """
    def __init__(self, channel, **kwargs):
        """
        Creates a new channel object, takes in a dictionary containing full Channel information
        """
        
        # Allow for user-specific HTTPClient object.
        if kwargs.get('http') and isinstance(kwargs['http'], http.HTTPClient):
            self.http = kwargs['http']
        else:
            # Set the channel http attribute to the http object to simplify sending or retrieving of messages
            self.http = http.HTTPClient()

        # Set all of the properties of the channel in a self.x blob, consider cleaning up if possible
        # If a Channel object is provided in the arguments, then just extract all of its information
        if "channel" in channel:
            self.id = channel["channel"]["channelID"]
            self.name = channel["channel"]["name"]
            self.status = channel["channel"]["status"]
            self.name = channel["channel"]["name"]
            self.server: nertivia.Server = self.http.get_server(channel["channel"]["server_id"])
            self.last_messaged = channel["channel"]["timestamp"]
            self._channel = channel["channel"]

        # If it is a new Channel object, then we have less information to set and use what was provided
        else:
            self.id = channel["channelID"]
            self.name = channel["name"]
            self.server = self.http.get_server(channel["server_id"])
            if "timestamp" in channel:
                self.last_messaged = channel["timestamp"]
            self._channel = channel

    def __repr__(self):
        """
        Allow for channel to be used in strings
        """
        # Self.server removed .__repr__ as repr will be returned when used in this context
        return f"<id={self.id} name='{self.name}' server=<{self.server}>>"

    async def send(self, message_content):
        """
        Asynchronously send a message in a channel
        """
        # Throw it to the http object

        return_message = await self.http.send_message(self.id, message_content)
        message_json = await return_message.json()
        return message.Message({"message": message_json["messageCreated"]})

    async def get_message(self, message_id):
        """
        Asynchronously retrieve a message from a channel using its id
        """
        # Throw it to the http object
        return await self.http.get_message(message_id, self.id)
