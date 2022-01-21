import asyncio

import websockets
import _thread
import time
import json


async def send_message(ws, message):
    await ws.send(message)
    if message == "3":
        print("↑ WebSocket pong")
    else:
        print("↑ BCAST WebSocket message: " + message)


# Define WebSocket callback functions
async def ws_message(ws, message):
    print("↓ WebSocket received: %s" % message)
    code = message[:2].replace("{", "").replace("}", "").replace(":", "")
    if code == "0":
        await send_message(ws, "40")
    elif code == '40':
        print("↓ WebSocket connected")
        token = "TOKEN"
        await send_message(ws,
                           '42["authentication", {"token": "{%s}"}]'.replace("{%s}", token))
        # Broadcast authentication
    elif code == "2":
        print("↓ WebSocket thread: ping")
        await send_message(ws, "3")  # Send pong to ping
    elif code == "42":
        message = json.loads(message[2:])
        event = message[0]
        data = message[1]
        print("↓ WebSocket event: " + event, data)


def ws_open(ws):
    print("↓ WebSocket thread: opened")
    send_message(ws, "40")  # Send connection confirmation


def ws_error(ws, error):
    print("WebSocket error: %s" % error)


async def ws_close(ws, code, reason):
    print("WebSocket thread: closed")
    await ws.close()
    print(code)
    print(reason)


async def setup_connection():
    async with websockets.connect('wss://nertivia.net/socket.io/?EIO=4&transport=websocket') as websocket:
        while True:
            try:
                message = await websocket.recv()
                await ws_message(websocket, message)
            except websockets.ConnectionClosed:
                await ws_close(websocket, None, None)
                break
            except websockets.ConnectionClosed:
                print('ConnectionClosed')
                is_alive = False
                break


asyncio.get_event_loop().run_until_complete(asyncio.ensure_future(setup_connection()))
