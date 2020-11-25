import discord
import asyncio
import json
import datetime
from discord.ext import commands, tasks

with open('cogs/channelmaker.json') as json_file:
    data = json.load(json_file)

safe = data["channelmaker"][0]["protected"]

# Cog for user created temporary voice channels
class ChannelMaker(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Print that this cog is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Channel making cog online.")
        # This checks if there were any created voice channels from this bot
        # and attempts to re-monitor them for deletion.
        try:
            scan_for_channels.start(self)
        except RuntimeError:
            print("Task loop is still running.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(error)

    # Command that makes a voice room based on what the user names it, works for strings and roles.
    @commands.cooldown(rate=2, per=30, type=commands.BucketType.user)
    @commands.command(aliases=['vc', 'vcr'])
    async def createvoice(self, ctx, *, topic: str):
        server = ctx.guild
        # Check if the topic is actually a role id.
        try:
            roleid = int(topic[3:-1])
            role = server.get_role(role_id=roleid)
            if role is not None:
                # Role was found
                await ctx.send(f"Created voice room: {role.name}!")
                await discord.Guild.create_voice_channel(server, name=role.name)
            else:
                # Role not found, so probably wasn't a role.
                await ctx.send(f"Created voice room: {topic}!")
                await discord.Guild.create_voice_channel(server, name=topic)
        except ValueError:
            # Topic was a string
            if topic[:1] == '@':
                topic = topic[1:]
            elif topic[:1] == '<':
                topic = topic[2:]
            await ctx.send(f"Created voice room: {topic}!")
            await discord.Guild.create_voice_channel(server, name=topic)
        except TypeError:
            # For some reason a TypeError exists in which a NoneType is Awaited.
            pass

    # Delete a voice channel if the bot fails to clean up after itself.
    @commands.command(aliases=['vclean'])
    async def cleanupvoicechannel(self, ctx, *, channel: discord.VoiceChannel):
        # We typically only want to remove channels created with this command, so we check the age of the channel
        today = datetime.date.today()
        past = channel.created_at
        delta = today - past.date()
        usercount = len(channel.members)
        # This assumes that channels older than 2 days were most likely made deliberately.
        if delta.days < 2 and usercount == 0:
            await channel.delete()
            await ctx.send(f'Channel: {channel} deleted!')
        else:
            await ctx.send(f'Channel: {channel} is too old to vclean, or has users in it.')

    # Command for renaming a voice channel made with this cog.
    @commands.command(aliases=['vtopic', 'vcn'])
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def renamevoicechannel(self, ctx, *, topic):
        try:
            # Collect necessary information into variables.
            author = ctx.message.author
            server = ctx.guild
            channel = author.voice.channel
            today = datetime.date.today()
            past = channel.created_at
            delta = today - past.date()
            # If the channel is new, it was most likely made with this bot.
            if delta.days < 2 and channel is not None:
                # Check if the topic was actually a role.
                try:
                    roleid = int(topic[3:-1])
                    role = server.get_role(role_id=roleid)
                    if role is not None:
                        await channel.edit(name=role.name)
                except ValueError:
                    await channel.edit(name=topic)
                except TypeError:
                    # For some reason a TypeError exists in which a NoneType is Awaited.
                    pass

            else:
                print('Attempted to rename old channel.')

        except AttributeError:
            await ctx.send("You need to be in a bot-created voice channel to change the topic!")

    @commands.command(aliases=['savech'])
    async def saveChannel(self, ctx, *, id):
        data['channelmaker'][0]['protected'].append(int(id))
        with open('cogs/channelmaker.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')


# This task loop will check for created servers left behind and removes them.
@tasks.loop(seconds=60)
async def scan_for_channels(self):
    # This checks if there were any created voice channels from this bot
    # and attempts to re-monitor them for deletion.
    servers = self.client.guilds
    channels = []
    # Scan for all of the voice channels.
    for server in servers:
        channels.extend(server.voice_channels)
    # Organize channels into two categories, empty (which are deleted here) and occupied
    for channel in channels:
        today = datetime.date.today()
        past = channel.created_at
        delta = today - past.date()
        usercount = len(channel.members)
        global safe
        if delta.days < 2 and channel.id not in safe:
            print(f'Found Channel: {channel.name}')
            if usercount != 0:
                print("But it was occupied so I couldn't delete it!")
            elif usercount == 0:
                print(f'Deleted voice channel: {channel.name}')
                try:
                    await channel.delete()
                    # print("Temporarily disabled deleting channels.")
                    # pass
                except discord.NotFound:
                    print("Attempted to delete deleted channel")


def setup(client):
    client.add_cog(ChannelMaker(client))