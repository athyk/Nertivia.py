import websocket
import _thread
import time
import json


def send_message(ws, message):
    ws.send(message)
    if message == "3":
        print("↑ WebSocket pong")
    else:
        print("↑ BCAST WebSocket message: " + message)


# Define WebSocket callback functions
def ws_message(ws, message):
    code = message[:2]
    if code == '40':
        print("↓ WebSocket connected")
        token = "TOKEN"
        send_message(ws,
                     '42["authentication", {"token": "{%s}"}]'.replace("{%s}", token))
        # Broadcast authentication
    elif code == "2":
        print("↓ WebSocket thread: ping")
        send_message(ws, "3")  # Send pong to ping
    elif code == "42":
        message = json.loads(message[2:])
        event = message[0]
        data = message[1]
        print("↓ WebSocket event: " + event, data)
    else:
        print("↓ WebSocket received: %s" % message)


def ws_open(ws):
    print("↓ WebSocket thread: opened")
    send_message(ws, "40")  # Send connection confirmation


def ws_error(ws, error):
    print("WebSocket error: %s" % error)


def ws_close(ws, code, reason):
    print("WebSocket thread: closed")
    print(code)
    print(reason)


def ws_thread(*args):
    ws = websocket.WebSocketApp('wss://nertivia.net/socket.io/?EIO=4&transport=websocket', on_open=ws_open,
                                on_message=ws_message, on_error=ws_error,
                                on_close=ws_close)
    ws.run_forever()


# Start a new thread for the WebSocket interface
_thread.start_new_thread(ws_thread, ())

# Continue other (non WebSocket) tasks in the main thread
while True:
    time.sleep(5)
