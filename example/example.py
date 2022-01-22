import nertivia

token = ""

# Change to True to enable viewing of events, information

client = nertivia.Bot(test=False)


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
