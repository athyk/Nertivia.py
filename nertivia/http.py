import asyncio
import gc
import json

import aiohttp
import nest_asyncio
import requests

import nertivia.message

nest_asyncio.apply()

MAIN_URL = "https://nertivia.net/"
URL = "https://nertivia.net/api/channels/"
URL_MSG = "https://nertivia.net/api/messages/"
URL_STA = "https://nertivia.net/api/settings/status"

headers = {}

loop = asyncio.get_event_loop()


def get_sid(token):
    r = requests.get(url=str(URL + "app"), headers={'Accept': 'text/plain',
                                                    'authorization': token,
                                                    'Content-Type': 'application/json;charset=utf-8'})
    cookie = r.headers.get('set-cookie')
    if cookie:
        return cookie.split("connect.sid=", 1)[1].strip("; Path=/; HttpOnly")
    return None


def generate_headers(token):
    global headers
    headers = {'Accept': 'text/plain',
               'authorization': token,
               'Content-Type': 'application/json;charset=utf-8',
               'Cookie': f'connect.sid={get_sid(token)}'}


async def fetch_server(server_id):
    session = aiohttp.ClientSession()
    res = await session.get(url=str(f'{MAIN_URL}/api/servers/{server_id}'),
                            headers=headers)
    await session.close()
    if res.status != 200:
        return res.content
    data = await res.json()
    return data


async def fetch_channel(channel_id):
    session = aiohttp.ClientSession()
    res = await session.get(url=str(f'{URL}{channel_id}'), headers=headers)
    await session.close()
    if res.status != 200:
        return res.content
    return await res.json()


async def fetch_user(user_id):
    session = aiohttp.ClientSession()
    res = await session.get(url=str(f'{MAIN_URL}/api/user/{user_id}'),
                            headers=headers)
    await session.close()
    if res.status != 200:
        return res.content
    return await res.json()


class HTTPClient:
    def __init__(self, **kwargs):
        if kwargs.get("token"):
            self.token = kwargs.get("token")
        if kwargs.get("socket_ip"):
            global MAIN_URL, URL, URL_MSG, URL_STA
            socket_ip = kwargs.get("socket_ip")
            MAIN_URL = f"{socket_ip}"
            URL = f"{socket_ip}/api/channels/"
            URL_MSG = f"{socket_ip}/api/messages/"
            URL_STA = f"{socket_ip}/api/settings/status"
        self.cache = None
        if kwargs.get("cache"):
            self.cache = kwargs.get("cache")
        self.token = None
        self.user = {}
        self._servers = {}
        self._users = {}

    def set_token(self, token):
        self.token = token
        generate_headers(token)

    def clear(self):
        self.user = {}
        self._servers = {}
        self._users = {}

        gc.collect()  # make sure it's memory efficient

    @property
    def servers(self):
        return list(self._servers.values())

    def _get_server(self, server_id):
        return self._servers.get(server_id)

    def _add_server(self, server):
        self._servers[server.id] = server

    def _remove_server(self, server):
        self._servers.pop(server.id, None)
        del server
        gc.collect()

    async def delete_message(self, message_id, channel_id):
        session = aiohttp.ClientSession()
        res = await session.delete(url=str(URL_MSG + str(message_id) + '/channels/' + str(channel_id)),
                                   headers=headers)
        await session.close()
        if res.status != 200:
            return res.content

    async def edit_message(self, message_id, channel_id, content):
        session = aiohttp.ClientSession()
        res = await session.patch(url=str(URL_MSG + str(message_id) + '/channels/' + str(channel_id)),
                                  headers=headers,
                                  data=json.dumps({'message': content}))
        await session.close()
        if res.status != 200:
            return res.content

    async def send_message(self, channel_id, content):
        session = aiohttp.ClientSession()
        res = await session.post(url=str(URL_MSG + '/channels/' + str(channel_id)),
                                 data=json.dumps({"message": content}),
                                 headers=headers)
        await session.close()
        if res.status != 200:
            return res.content
        return res.content

    async def get_message(self, message_id, channel_id):
        session = aiohttp.ClientSession()
        res = await session.get(url=str(f'{MAIN_URL}/api/messages/{message_id}/channels/{channel_id}'),
                                headers=headers)
        if res.status != 200:
            return res.content
        await session.close()
        return nertivia.message.Message({'message': await res.json()}, cache=self.cache)

    def get_channel(self, channel_id):
        res = asyncio.run(fetch_channel(channel_id))
        return nertivia.Channel(res, cache=self.cache)

    def get_user(self, user_id):
        res = asyncio.run(fetch_user(user_id))
        return nertivia.User(res, cache=self.cache)

    def get_server(self, server_id):
        res = None
        if str(server_id) in self.cache.guilds:
            res = self.cache.guilds[str(server_id)]
        else:
            res = nertivia.Server(asyncio.run(fetch_server(server_id)), cache=self.cache)

        return res

