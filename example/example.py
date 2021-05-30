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
