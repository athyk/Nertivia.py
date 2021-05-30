# PNA - Python Nertivia API

This is a Python API Wrapper for the Nertiva chat platform.

## Installation
You can install `PNA` with pip using
`pip install PNA` or `pip3 install PNA`

## Example Bot

```py
import nertivia

token = "BOT TOKEN"

client = nertivia.Bot()


@client.event
async def on_ready(data: nertivia.User):
    print("Logged in as", data.username, "\nid:", data.id)


@client.event
async def on_quit():
    print("I'm disconnected!")


@client.event
async def on_message(message):
    if message.content.startswith("!ping"):
        await message.channel.send("pong")


client.login(token)
```
