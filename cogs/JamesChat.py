import discord
import markovify
import asyncio
import random
from discord.ext import commands

# a bunch of avatars from Star Control II I like for theming this Cog
# I am assigning random avatars based on discord name for fun.
avatar_urls = ["http://www.star-control.com/hosted/happycamper/gifs/arilou-sitting.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/commander-talking.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/druuge-simple.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/dynarri-sitting.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/ilwrath-talking.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/korah-complex.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/melnorme-talking-purple.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/mycon-sitting.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/orz-sitting.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/pkunk-standing.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/shofixti-sitting.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/spathi.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/suppox-sitting.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/sylandro.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/syreen-laying.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/thraddash-sitting.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/umgah-sitting.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/urquan-complex.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/utwig-standing.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/vux-sitting.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/yehat-complex.gif",
               "http://www.star-control.com/hosted/happycamper/gifs/zoqfotpik-sitting.gif"]


# Created because a chat member needed space from the discord yet still wanted to interact. Odd.
class JamesChat(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.operating = False
        self.mode = 1

    @commands.Cog.listener()
    async def on_ready(self):
        print("JamesChat cog online.")

    # This checks for messages to send back to the caller.
    async def listenFor(self, ctx, channel):

        while self.operating:
            try:
                # Is the message in the correct channnel, not a bot and we are operating?
                def check2(m):
                    return m.channel == channel and m.author.bot is False and self.operating == True

                msg = await self.client.wait_for("message", check=check2)

                # Quit messaging to caller
                if msg.content == "Q":
                    await msg.add_reaction('📵')
                    exitEmbed = discord.Embed(title=f"{msg.author.name.upper()} has closed communication!", color=0xff0000)
                    random.seed(msg.author.name)
                    random.seed(msg.author.name)
                    seededURL = random.choice(avatar_urls)
                    exitEmbed.set_image(url=seededURL)
                    exitEmbed.set_thumbnail(url=msg.author.avatar_url)
                    self.operating = False
                    await channel.send(embed=exitEmbed)
                    await ctx.send(embed=exitEmbed)
                    break
                else:
                    # Send message to caller and consume original message for cleanliness
                    myContent = f"📨 " + msg.author.name.upper() + " ->📡 RECEIVED ↩️ " + ":" + "\n\t" + msg.content + "\n\n"
                    wrapper = "```fix\n" + myContent + "```"
                    myEmbed = discord.Embed(title=f"", color=0x33cc33,
                                            description=wrapper)
                    random.seed(msg.author.name)
                    seededURL = random.choice(avatar_urls)
                    myEmbed.set_image(url=seededURL)
                    userAvatar = msg.author.avatar_url
                    myEmbed.set_thumbnail(url=userAvatar)
                    #await msg.delete()
                    await ctx.send(embed=myEmbed)
            except discord.NotFound:
                print("a 404 not found happened.")
                pass
            except discord.HTTPException:
                await ctx.send("For some reason I didn't want to send that message, I prefer to send basic text.")
            except TypeError:
                pass

    # This sends messages to the selected channel
    async def sendTo(self, ctx, getch):
        myuser = ctx.message.author.name
        myavatar = ctx.message.author.avatar_url
        myEmbed = discord.Embed(title=f"INCOMING MESSAGE FROM {myuser.upper()}!", color=0x33cc33)
        chatEmbed = discord.Embed(title=f"CURRENT MESSAGE HISTORY WITH {myuser.upper()}!", color=0x33cc33)
        exitEmbed = discord.Embed(title=f"{myuser.upper()} has closed communication!", color=0xff0000)
        random.seed(myuser)
        seededURL = random.choice(avatar_urls)
        myEmbed.set_image(url=seededURL)
        myEmbed.set_thumbnail(url=myavatar)
        chatEmbed.set_image(url=seededURL)
        chatEmbed.set_thumbnail(url=myavatar)
        exitEmbed.set_image(url=seededURL)
        exitEmbed.set_thumbnail(url=myavatar)
        messageThreshold = 20
        currentMessages = 0
        totalMessages = 0
        myContent = ""
        myMsg = await getch.send(embed=myEmbed)
        if self.mode == 0:
            monitor = await ctx.send(embed=myEmbed)
        while self.operating:
            try:
                # By default, bot is listening to all channels it is in.
                # So checking if it is a PM message
                def check2(m):
                    return m.channel == ctx.channel

                msg = await self.client.wait_for("message", check=check2)

                # Quit sending
                if msg.content == "Q":
                    self.operating = False
                    await msg.add_reaction('📵')
                    await ctx.send(embed=exitEmbed)
                    await getch.send(embed=exitEmbed)
                    break
                # Keep sending
                else:
                    # Log messages others sent
                    if msg.author == self.client.user:
                        totalMessages += 1
                        print (msg.embeds[0].description)
                        size = len(msg.embeds[0].description)
                        myContent = myContent + msg.embeds[0].description[8:size-3]
                    # Log messages caller sent
                    else:
                        totalMessages += 1
                        myContent = myContent + f"📨 #{totalMessages} ↩️ " + ":" + "\n\t" + msg.content + "\n\n"
                        wrapper = "```fix\n" + myContent + "```"
                    wrapper = "```fix\n" + myContent + "```"
                    # Currently breaking the messages up if they get to a certain size
                    # await msg.delete()
                    if currentMessages < messageThreshold:
                        newEmbed = discord.Embed(title=f"📶 █▓▒░ TRANSMISSION FROM {myuser.upper()}!", color=0x33cc33,
                                                 description=wrapper)
                        newEmbed.add_field(name="azimuth:", value="342", inline=True)
                        newEmbed.add_field(name="orbit:", value="564/24o", inline=True)
                        newEmbed.add_field(name="apex:", value="214006¬Δ", inline=True)
                        newEmbed.add_field(name="zenith:", value="RCA", inline=True)
                        newEmbed.set_thumbnail(url=myavatar)
                        newEmbed.set_image(url=seededURL)
                        newEmbed.set_footer(text="CLOSE COMM LINK WITH: Q")
                        if self.mode == 1:
                            myMsg = await getch.send(embed=newEmbed)
                            #monitor = await ctx.send(embed=newEmbed)
                        else:
                            await myMsg.edit(embed=newEmbed)
                            await monitor.edit(embed=newEmbed)


                        currentMessages += 1
                    else:
                        myContent = msg.content
                        newEmbed = discord.Embed(title=f"CONTINUED TRANSMISSION FROM {myuser.upper()}!",
                                                 color=0x33cc33,
                                                 description=myContent)
                        newEmbed.add_field(name="azimuth:", value="342", inline=True)
                        newEmbed.add_field(name="orbit:", value="564/24o", inline=True)
                        newEmbed.add_field(name="apex:", value="214006¬Δ", inline=True)
                        newEmbed.add_field(name="zenith:", value="RCA", inline=True)
                        currentMessages = 0
                        newEmbed.set_thumbnail(url=myavatar)
                        newEmbed.set_image(url=seededURL)
                        newEmbed.set_footer(text="CLOSE COMM LINK WITH: Q")
                        myMsg = await getch.send(embed=newEmbed)
                        monitor = await ctx.send(embed=newEmbed)
                        currentMessages += 1
            except discord.NotFound:
                print("a 404 not found happened.")
                pass
            except discord.HTTPException:
                await ctx.send("For some reason I didn't want to send that message, I prefer to send basic text.")
            except TypeError:
                pass

    # Actual command in charge of running the two tasks, send and receive
    @commands.command(aliases=["transmit", "t"])
    async def transmitMessage(self, ctx):
        try:
            self.operating = True
            gl = []
            cl = []
            # Shell loop for operating call board
            em = discord.Embed(title="SELECT TRANSMISSION DESTINATION:", color=0x33cc33, description="Pick a discord server:")
            random.seed(ctx.author.name)
            seededURL = random.choice(avatar_urls)
            em.set_image(url=seededURL)
            userAvatar = ctx.author.avatar_url
            em.set_thumbnail(url=userAvatar)
            i = 0
            for guild in self.client.guilds:
                gl.append(guild)
                em.add_field(name=guild.name, value =f"Type: {i}")
                i += 1
            menu = await ctx.send(embed=em)

            def check(m):
                try:
                    j = int(m.content)
                except ValueError:
                    return False
                return j in range(0, len(gl))
            smsg = await self.client.wait_for("message", check=check, timeout=30)
            guild = gl[int(smsg.content)]
            i = 0
            nem = discord.Embed(title="SELECT CHANNEL PORT:", color=0x33cc33, description="Pick a discord channel:")
            random.seed(ctx.author.name)
            seededURL = random.choice(avatar_urls)
            nem.set_image(url=seededURL)
            userAvatar = ctx.author.avatar_url
            nem.set_thumbnail(url=userAvatar)
            for channel in guild.text_channels:
                if self.client.user in channel.members:
                    cl.append(channel)
                    nem.add_field(name=channel.name, value=f"Type: {i}")
                    i += 1
            await menu.edit(embed=nem)

            def chcheck(m):
                try:
                    j = int(m.content)
                except ValueError:
                    return False
                return j in range(0, len(cl))
            cmsg = await self.client.wait_for("message", check=chcheck, timeout=30)
            channel = cl[int(cmsg.content)]
            getch = discord.utils.get(guild.text_channels, id=channel.id)
            await ctx.send(f"Okay, now sending messages to {channel.name} in {guild.name}\nType Q to quit.")

            await asyncio.gather(self.listenFor(ctx, getch),self.sendTo(ctx, getch))

        except asyncio.TimeoutError:
            pass




def setup(client):
    client.add_cog(JamesChat(client))
