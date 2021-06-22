import nertivia
from nertivia import http

URL = "https://nertivia.net/api/messages/channels/"
URL_MSG = "https://nertivia.net/api/messages/"
URL_STA = "https://nertivia.net/api/settings/status"


class Channel(object):
    def __init__(self, channel, **kwargs):
        self.http = http.HTTPClient()
        if "channel" in channel:
            self.id = channel["channel"]["channelID"]
            self.name = channel["channel"]["name"]
            self.status = channel["channel"]["status"]
            self.name = channel["channel"]["name"]
            self.server: nertivia.Server = self.http.get_server(channel["channel"]["server_id"])
            self.last_messaged = channel["channel"]["timestamp"]
            self._channel = channel["channel"]
        else:
            self.id = channel["channelID"]
            self.name = channel["name"]
            self.name = channel["name"]
            self.server = self.http.get_server(channel["server_id"])
            if "timestamp" in channel:
                self.last_messaged = channel["timestamp"]
            self._channel = channel

    async def send(self, message):
        await self.http.send_message(self.id, message)

    async def get_message(self, messageID):
        # mes = list(filter(lambda x: x['messageID'] == messageID, r.json()['messages']))
        return await self.http.get_message(messageID, self.id)
