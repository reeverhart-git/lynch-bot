import discord
import os
from quart import Quart
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv(dotenv_path="bot.env")

app = Quart(__name__)

# client is used for bot commands, client is deprecated and I should be using 'bot'
client = commands.Bot(command_prefix=',')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LOCAL_IP = os.getenv('LOCAL_IP')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(" "))
    print("Bot is ready.")


@client.event
async def on_resumed():
    print("Bot has resumed connection with Discord.")


@client.event
async def on_disconnect():
    print("Bot has disconnected from Discord.")



# purge messages command, checks if the user is admin.
@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)


# cog loading and unloading
@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
        client.load_extension(f'cogs.{extension}')


@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
        client.unload_extension(f'cogs.{extension}')

# Automatically load all cogs in the cogs folder.
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# run the bot with the discord token, currently token is exposed, security issue
# client.loop.create_task(app.run_task(LOCAL_IP, 5000, debug=True))
client.run(DISCORD_TOKEN)

