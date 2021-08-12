# PNA - Python Nertivia API

This is a Python API Wrapper for the Nertiva chat platform. The replaces the deprecated Nertivia.py api wrapper. 

Support Server: https://nertivia.net/i/pna

## Installation
You can install `PNA` with pip using
`pip install PNA` or `pip3 install PNA`

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

### Planned changes to Python Nertivia API

- Add support for commands for better organisation
- Sub folder for events and commands
- Write docs for PNA

### Why not to use Nertivia.py

At the time of writing, Nertivia.py is severely outdated and provides no use to any developers. 

Many changes are needed to make Nertivia.py up to date such as upgrading from
`nertivia.tk` to `nertivia.net`. 


