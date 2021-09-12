import asyncio
import gc
import json
from nertivia import cache_nertivia_data
import aiohttp
import nest_asyncio
import requests

import nertivia.message

nest_asyncio.apply()

# Set API endpoints
MAIN_URL = "https://nertivia.net/"
URL = "https://nertivia.net/api/channels/"
URL_MSG = "https://nertivia.net/api/messages/"
URL_STA = "https://nertivia.net/api/settings/status"

headers = {}

loop = asyncio.get_event_loop()

session = aiohttp.ClientSession()


def get_sid(token):
    """
    Obtain the sid from a given token, returns None if failed connection or other error preventing success
    Do not use manually
    """
    r = requests.get(url=str(URL + "app"), headers={'Accept': 'text/plain',
                                                    'authorization': token,
                                                    'Content-Type': 'application/json;charset=utf-8'})
    cookie = r.headers.get('set-cookie')

    # If successful, then the cookie was set
    if cookie:
        return cookie.split("connect.sid=", 1)[1].strip("; Path=/; HttpOnly")
    return None


def generate_headers(token):
    """
    Generates a header using a provided token and sets it as a global variable
    Do not use manually
    """
    global headers
    headers = {'Accept': 'text/plain',
               'authorization': token,
               'Content-Type': 'application/json;charset=utf-8',
               'Cookie': f'connect.sid={get_sid(token)}'}


async def fetch_server(server_id):
    """
    Asynchronous function which perform an API call to retrieve a server from its ID
    """

    session = aiohttp.ClientSession()
    res = await session.get(url=str(f'{MAIN_URL}/api/servers/{server_id}'),
                            headers=headers)
    await session.close()

    # Reminder : 2XX is a success
    # If unsuccessful we return the error message
    if res.status != 200:
        return res.content

    # However, if succesful return the json data that was returned and transform it into its python equivalent
    return await res.json()


async def fetch_channel(channel_id):
    """
    Asynchronous function that will perform an API call to retrieve a channel from its ID
    """
    session = aiohttp.ClientSession()
    res = await session.get(url=str(f'{URL}{channel_id}'), headers=headers)
    await session.close()

    # Reminder : 2XX is a success
    # If unsuccessful we return the error message
    if res.status != 200:
        return res.content

    # However, if succesful return the json data that was returned and transform it into its python equivalent
    return await res.json()


async def fetch_user(user_id):
    """
    Asynchronous function which performs an API call to retrieve a user from their ID
    """
    session = aiohttp.ClientSession()
    res = await session.get(url=str(f'{MAIN_URL}/api/user/{user_id}'),
                            headers=headers)
    await session.close()

    # Reminder : 2XX is a success
    # If unsuccessful we return the error message
    if res.status != 200:
        return res.content

    # However, if successful return the json data that was returned and transform it into its python equivalent
    return await res.json()


class HTTPClient:
    """
    Object representing the HTTPClient, do not instantiate manually
    Handles the bridge between Nertivia.py and the Nertivia servers
    """
    def __init__(self, **kwargs):
        """
        Prepare the HTTPClient instance
        """
        self.token = None
        self.user = {}
        self._servers = {}
        self._users = {}

        # If a token was passed as a named argument then set it as a self value for ease of acces
        if kwargs.get("token"):
            self.token = kwargs.get("token")

        # If a socket ip was given, use it to ready all of the endpoints
        if kwargs.get("socket_ip"):
            global MAIN_URL, URL, URL_MSG, URL_STA
            socket_ip = kwargs.get("socket_ip")
            MAIN_URL = f"{socket_ip}"
            URL = f"{socket_ip}/api/channels/"
            URL_MSG = f"{socket_ip}/api/messages/"
            URL_STA = f"{socket_ip}/api/settings/status"

    def set_token(self, token):
        """
        Set the token to the one provided, regardless of whether or not one was already set
        After which, generate new headers to fit with the new token
        """
        self.token = token
        generate_headers(token)

    def clear(self):
        """
        Clean up the memory, reset the dictionary entries for users, servers and the bot itself
        """
        self.user = {}
        self._servers = {}
        self._users = {}

        gc.collect()  # make sure it's memory efficient

    @property
    def servers(self):
        """
        Synchronously returns a list of all cached servers
        """
        return list(self._servers.values())

    def _get_server(self, server_id):
        """
        Returns a cached server using its ID
        If the server isn't cached, then `None` is returned
        """
        return self._servers.get(server_id)

    def _add_server(self, server):
        """
        Add a server to the cache, using its ID as the dictionary key and the server object being the value
        """
        self._servers[server.id] = server

    def _remove_server(self, server):
        """
        Remove from the cache a server using its ID
        For some reason server object is expected and not id (Fix if no dependencies)
        """

        # Remove the server from cache, then delete the argument despite no apparent further reference (Useless line ?)
        self._servers.pop(server.id, None)
        del server
        gc.collect()

    async def delete_message(self, message_id, channel_id):
        """
        Asynchronously delete a message using its ID, and the channel ID in which it is located
        """
        res = await session.delete(url=str(URL_MSG + str(message_id) + '/channels/' + str(channel_id)),
                                   headers=headers)

        # Reminder : if 2XX then it is a success
        if res.status != 200:
            return res.content

    async def edit_message(self, message_id, channel_id, content: str):
        """
        Edit a message using its ID, and the channel ID in which it is located
        Third argument is the content to replace it with
        """
        res = await session.patch(url=str(URL_MSG + str(message_id) + '/channels/' + str(channel_id)),
                                  headers=headers,
                                  data=json.dumps({'message': content}))
        if res.status != 200:
            return res.content

    async def send_message(self, channel_id, content: str):
        """
        Send a message in a channel which is found by its ID
        Second argument is a string containing the message to send
        """
        res = await session.post(url=str(URL_MSG + '/channels/' + str(channel_id)),
                                 data=json.dumps({"message": content}),
                                 headers=headers)
        # Reminder : if 2XX then it is a success
        if res.status != 200:
            return res
        # If successful return...Success message ? Not sure
        return res

    async def get_message(self, message_id, channel_id):
        """
        Asynchronously retrieve a message using its ID and the ID of the channel in which it is located
        """
        res = await session.get(url=str(f'{MAIN_URL}/api/messages/{message_id}/channels/{channel_id}'),
                                headers=headers)

        # Reminder : if 2XX then it is a success
        if res.status != 200:
            # If the response is unsuccessful and has a content attribute then we return it
            # Needs doc reading but a content attribute should always be present to specify success/error message
            try:
                if "content" in res:
                    return res.content
            # Error shouldn't be possible unless res is None
            except Exception:
                pass
            return None

        # Return a message object for easy manipulation
        return nertivia.message.Message({'message': await res.json()})

    def get_channel(self, channel_id):
        """
        Synchronously fetch a channel using its ID with an API call
        Channels are not cached ?
        Returns a nertivia.Channel object
        """
        try:
            res = asyncio.run(fetch_channel(channel_id))
        except asyncio.TimeoutError:
            res = asyncio.run(fetch_channel(channel_id))
        return nertivia.Channel(res)

    def get_user(self, user_id, force_cache: bool = False):
        """
        Synchronously obtain a user from cache, if the user is not cached then perform an API call to retrieve them
        `force_cache` may be set to True to have the function return None rather than perform an API call
        """

        if str(user_id) in cache_nertivia_data.users:
            return cache_nertivia_data.users[str(user_id)]
        elif not force_cache:
            return nertivia.User(asyncio.run(fetch_user(user_id)))
        return None

    def get_server(self, server_id, force_cache: bool = False):
        """
        Synchronously obtain a server from cache, if the server is not cached then perform an API call to retrieve it
        `force_cache` may be set to True to have the function return None rather than perform an API call
        """

        if str(server_id) in cache_nertivia_data.guilds:
            return cache_nertivia_data.guilds[str(server_id)]
        elif not force_cache:
            return nertivia.Server(asyncio.run(fetch_server(server_id)))

        return None
