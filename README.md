# Nertivia.py

This is the official Python API Wrapper for the Nertiva chat platform.

Support Server: https://nertivia.net/i/npy

## Installation
You can install `nertivia.py` with pip using

`pip install nertivia.py` or `pip3 install nertivia.py` once completed make sure you import it to your Python file with `import nertivia`.

## Example Bot

```py
import nertivia

token = ""

client = nertivia.Bot(debug=False)  # Change to True to enable viewing of events, information


@client.event
async def on_ready():
    print("Logged in as", client.user.username)


@client.event
async def on_quit():
    print("I'm disconnected!")


@client.event
async def on_status_change(data):
    print(data)


@client.event
async def on_message(message):
    if message.content.startswith("!ping"):
        await message.channel.send("pong")


client.login(token)
```

### Planned changes to Nertivia.py

- Add support for commands for better organisation
- Sub folder for events and commands
- Write docs for Nertivia.py 


