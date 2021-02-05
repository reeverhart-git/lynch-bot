import discord
import requests
import random
import asyncio
import youtube_search
import json
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv(dotenv_path="bot.env")

with open('cogs/theme.json') as json_file:
    data = json.load(json_file)

# These are for the Google API, they are tied to a google account and are under a limited "free" version.
API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ID")
SEARCH_PREFIX_REG = 'https://www.googleapis.com/customsearch/v1?key='
SEARCH_PREFIX_REST = 'https://www.googleapis.com/customsearch/v1/siterestrict?key='

# This is for a dumb joke
CDI_START = ['https://i.postimg.cc/qqZN2psw/linksearch.gif', 'https://i.postimg.cc/WbF3QL6R/morshusearch.gif',
             'https://i.postimg.cc/B6bmG95F/mariosearch.gif']
CDI_KING = 'https://i.postimg.cc/nLcd8H5H/kingsearch.gif'

# This is for xmas theme
# All sourced from https://www.fg-a.com/christmas.htm
XMAS_START = ["https://www.fg-a.com/christmas/santa-scooter.gif",
              "https://www.fg-a.com/christmas/4-animated-christmastree.gif",
              "https://www.fg-a.com/christmas/santa-animated-elf-1.gif",
              "https://www.fg-a.com/christmas/snowman-merry-christmas.gif",
              "https://www.fg-a.com/christmas/2018-santa-skating-animation.gif",
              "https://www.fg-a.com/christmas/christmas-fireplace-2018.gif",
              "https://www.fg-a.com/christmas/merry-christmas-elf.gif",
              "https://www.fg-a.com/christmas/santa-delivering-gifts-1.gif",
              "https://www.fg-a.com/christmas/2020-santa-dance-animation.gif"]


class QueryMessage:
    def __init__(self, message: discord.Message, count, imagelist, query, n, user):
        self.message = message
        self.count = count
        self.imagelist = imagelist
        self.query = query
        self.n = n
        self.user = user


def findInQList(attribute, qlist):
    for x in qlist:
        if x.message.id == attribute:
            return x
    return None


async def popImages(imglist, q, n, restrict):
    # This is the Google API custom search engine link that sends up to 10 json objects.
    # The free version has a cap of 100 queries a day, not for heavy server use.
    # In the event that the default search engine is out of queries, we use the site restricted version.
    if restrict:
        url = f"{SEARCH_PREFIX_REST}{API_KEY}&cx={SEARCH_ENGINE_ID}&q={q}&start={n}&searchType=image"
    else:
        url = f"{SEARCH_PREFIX_REG}{API_KEY}&cx={SEARCH_ENGINE_ID}&q={q}&start={n}&searchType=image"
    data = requests.get(url).json()
    search_items = data.get("items")
    for i, search_item in enumerate(search_items, start=1):
        # populate the imagelist list with image links
        imglist.append(search_item.get("link"))


class GoogleImageSearch(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.searchmsgs = []
        self.ytmsgs = []
        self.mode = data["themes"][0]["theme"]

    # Print that this cog is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Google/Youtube Search cog online.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        msg = reaction.message
        valid = False
        # Check if the message is a Query Message
        smsg = findInQList(msg.id, self.searchmsgs)
        ymsg = findInQList(msg.id, self.ytmsgs)
        if smsg is not None:
            valid = True
            # If the searcher adds a forward arrow:
            if reaction.emoji == '▶' and user == smsg.user and valid:
                smsg.count += 1
                if smsg.count % 10 == 0 and smsg.count != 0:
                    # search again for the next 10 images
                    smsg.n += 10
                    await popImages(smsg.imagelist, smsg.query, smsg.n, False)
                    newem = discord.Embed(title=f"Search for: {smsg.query}, {smsg.count}", color=0x00a33f)
                    newem.set_image(url=smsg.imagelist[smsg.count])
                    await smsg.message.edit(embed=newem)
                else:
                    # go to the next picture link
                    newem = discord.Embed(title=f"Search for: {smsg.query}, {smsg.count}", color=0x00a33f)
                    newem.set_image(url=smsg.imagelist[smsg.count])
                    await smsg.message.edit(embed=newem)
            # If the searcher adds a back arrow:
            if reaction.emoji == '◀' and user == smsg.user and valid:
                if smsg.count != 1:
                    # go back to the previous picture link, unless it was the first picture.
                    smsg.count -= 1
                    newem = discord.Embed(title=f"Search for: {smsg.query}, {smsg.count}", color=0x00a33f)
                    newem.set_image(url=smsg.imagelist[smsg.count])
                    await smsg.message.edit(embed=newem)
        elif ymsg is not None:
            valid = True
            if reaction.emoji == '▶' and user == ymsg.user and valid:
                if ymsg.count < 9:
                    # go to the video
                    ymsg.count += 1
                    await msg.edit(content=ymsg.imagelist[ymsg.count])
                else:
                    # loop back to first video
                    ymsg.count = 0
                    await msg.edit(content=ymsg.imagelist[ymsg.count])

            if reaction.emoji == '◀' and user == ymsg.user and valid:
                if ymsg.count != 0:
                    # go back a video unless we are at first video
                    ymsg.count -= 1
                    await msg.edit(content=ymsg.imagelist[ymsg.count])
        else:
            pass

    # For some reason, the on_reaction_remove was not cooperating, thus raw is used.
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # a raw event returns a payload object with specific attributes
        emoji = payload.emoji
        userid = payload.user_id
        msgid = payload.message_id
        valid = False
        # Check if the message is a Query Message
        smsg = findInQList(msgid, self.searchmsgs)
        ymsg = findInQList(msgid, self.ytmsgs)
        if smsg is not None:
            valid = True
            # If the searcher removes a forward arrow:
            if emoji.name == '▶' and userid == smsg.user.id and valid:
                smsg.count += 1
                if smsg.count % 10 == 0 and smsg.count != 0:
                    # search again for the next 10 images
                    smsg.n += 10
                    await popImages(smsg.imagelist, smsg.query, smsg.n, False)
                    newem = discord.Embed(title=f"Search for: {smsg.query}, {smsg.count}", color=0x00a33f)
                    newem.set_image(url=smsg.imagelist[smsg.count])
                    await smsg.message.edit(embed=newem)
                else:
                    # go to the next picture link
                    newem = discord.Embed(title=f"Search for: {smsg.query}, {smsg.count}", color=0x00a33f)
                    newem.set_image(url=smsg.imagelist[smsg.count])
                    await smsg.message.edit(embed=newem)
            # If the searcher removes a back arrow:
            if emoji.name == '◀' and userid == smsg.user.id and valid:
                if smsg.count != 1:
                    # go back to the previous picture link, unless it was the first picture.
                    smsg.count -= 1
                    newem = discord.Embed(title=f"Search for: {smsg.query}, {smsg.count}", color=0x00a33f)
                    newem.set_image(url=smsg.imagelist[smsg.count])
                    await smsg.message.edit(embed=newem)
        elif ymsg is not None:
            valid = True
            if emoji.name == '▶' and userid == ymsg.user.id and valid:
                if ymsg.count < 9:
                    # go to the video
                    ymsg.count += 1
                    await ymsg.message.edit(content=ymsg.imagelist[ymsg.count])
                else:
                    # loop back to first video
                    ymsg.count = 0
                    await ymsg.message.edit(content=ymsg.imagelist[ymsg.count])

            if emoji.name == '◀' and userid == ymsg.user.id and valid:
                if ymsg.count != 0:
                    # go back a video unless we are at first video
                    ymsg.count -= 1
                    await ymsg.message.edit(content=ymsg.imagelist[ymsg.count])
        else:
            pass

    # The image search command
    @commands.command(aliases=['image', 'google', 'img'])
    async def google_image_search(self, ctx, *, query):
        try:
            # Store the emojis
            nextarrow = '▶'
            backarrow = '◀'
            imagelist = []
            inc = 1
            n = 1
            await popImages(imagelist, query, n, False)

            # Here we set the embed to "link" from the google json api, as that displays the image from the search.
            em = discord.Embed(title=f"Search for: {query}", color=0x00a33f)
            if self.mode == "cdi":
                cdiurl = random.choice(CDI_START)
                delay = 1
                em.set_image(url=cdiurl)
                msg = await ctx.send(embed=em)
                if cdiurl == CDI_START[2]:
                    delay = 3.5
                await asyncio.sleep(delay)
                em.set_image(url=imagelist[inc])
                await msg.edit(embed=em)
            elif self.mode == "xmas":
                xmasurl = random.choice(XMAS_START)
                delay = 2
                em.set_image(url=xmasurl)
                msg = await ctx.send(embed=em)
                await asyncio.sleep(delay)
                em.set_image(url=imagelist[inc])
                await msg.edit(embed=em)
            else:
                em.set_image(url=imagelist[inc])
                msg = await ctx.send(embed=em)
            qmsg = QueryMessage(msg, inc, imagelist, query, n, ctx.author)
            self.searchmsgs.append(qmsg)
            # The bot will react to its own message with the arrow emojis
            await msg.add_reaction(backarrow)
            await msg.add_reaction(nextarrow)

        except TypeError:
            if self.mode == "cdi":
                nem = discord.Embed(title="Hmm... No images. Try again?", color=0x00a33f)
                nem.set_footer(text="Google API could be done for the day, try ,simg!",
                               icon_url=self.client.user.avatar_url)
                nem.set_image(url=CDI_KING)
                await ctx.send(embed=nem)
            else:
                await ctx.send("Search gave problems, if you think this is a Google issue, try ,simg")
        except discord.NotFound:
            pass

    # The image search command, backup
    @commands.command(aliases=['simg'])
    async def google_image_search_backup(self, ctx, *, query):
        try:
            # Store the emojis
            nextarrow = '▶'
            backarrow = '◀'
            imagelist = []
            inc = 1
            n = 1
            await popImages(imagelist, query, n, True)

            em = discord.Embed(title=f"Search for: {query}", color=0x00a33f)
            # Here we set the embed to "link" from the google json api, as that displays the image from the search.
            if self.mode == "cdi":
                cdiurl = random.choice(CDI_START)
                delay = 1
                em.set_image(url=cdiurl)
                msg = await ctx.send(embed=em)
                if cdiurl == CDI_START[2]:
                    delay = 3.5
                await asyncio.sleep(delay)
                em.set_image(url=imagelist[inc])
                await msg.edit(embed=em)
            if self.mode == "xmas":
                xmasurl = random.choice(XMAS_START)
                delay = 2
                em.set_image(url=xmasurl)
                msg = await ctx.send(embed=em)
                await asyncio.sleep(delay)
                em.set_image(url=imagelist[inc])
                await msg.edit(embed=em)
            else:
                em.set_image(url=imagelist[inc])
                msg = await ctx.send(embed=em)
            qmsg = QueryMessage(msg, inc, imagelist, query, n, ctx.author)
            self.searchmsgs.append(qmsg)
            # The bot will react to its own message with the arrow emojis
            await msg.add_reaction(backarrow)
            await msg.add_reaction(nextarrow)

        except TypeError:
            if self.mode == "cdi":
                nem = discord.Embed(title="Hmm... No images.", color=0x00a33f)
                nem.set_footer(text="Google API could be completely done.",
                               icon_url=self.client.user.avatar_url)
                nem.set_image(url=CDI_KING)
                await ctx.send(embed=nem)
            else:
                await ctx.send("Google API limit reached...")
        except discord.NotFound:
            pass

    # The youtube search command
    @commands.command(aliases=['yt', 'vid', 'video', 'youtube'])
    async def youtube_video_search(self, ctx, *, query):
        try:
            # Store the emojis
            nextarrow = '▶'
            backarrow = '◀'
            inc = 0
            await ctx.send(f"YouTube search for: {query}")
            # youtube search returns videos in a list of dictionary objects
            data = youtube_search.YoutubeSearch(query, max_results=10).to_dict()
            # list comprehension to make a list of only the youtube links
            links = [dic['url_suffix'] for dic in data]
            # further list comprehension, because youtube_search only gives the /watch urls.
            ytlinks = ['https://www.youtube.com' + link for link in links]

            # discord doesn't support video embeds through discord.py, we have to use raw urls.
            if len(ytlinks) > 0:
                if self.mode == "cdi":
                    cdiurl = random.choice(CDI_START)
                    delay = 1
                    msg = await ctx.send(cdiurl)
                    if cdiurl == CDI_START[2]:
                        delay = 3.5
                    await asyncio.sleep(delay)
                    await msg.edit(content=ytlinks[inc])
                if self.mode == "xmas":
                    xmasurl = random.choice(XMAS_START)
                    delay = 2
                    msg = await ctx.send(xmasurl)
                    await asyncio.sleep(delay)
                    await msg.edit(content=ytlinks[inc])
                else:
                    msg = await ctx.send(ytlinks[inc])
                ymsg = QueryMessage(msg, inc, ytlinks, query, 0, ctx.author)
                self.ytmsgs.append(ymsg)
                # The bot will react to its own message with the arrow emojis
                await msg.add_reaction(backarrow)
                await msg.add_reaction(nextarrow)
            else:
                if self.mode == "cdi":
                    nem = discord.Embed(title="Hmm... No videos. Try again?", color=0x00a33f)
                    nem.set_image(url=CDI_KING)
                    await ctx.send(embed=nem)
                else:
                    await ctx.send("Youtube search had no results.")

        except IndexError:
            if self.mode == "cdi":
                nem = discord.Embed(title="Hmm... No videos.", color=0x00a33f)
                nem.set_image(url=CDI_KING)
                await ctx.send(embed=nem)
            else:
                await ctx.send("Youtube search had an issue.")

    @commands.command(aliases=['mode'])
    async def set_mode(self, ctx, mode="default"):
        self.mode = mode
        newJson = {"themes": [{"theme": str(mode)}]}
        with open('cogs/theme.json', 'w') as outfile:
            json.dump(newJson, outfile)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['cdi', 'cdimode'])
    async def set_mode_cdi(self, ctx):
        self.mode = "cdi"
        newJson = {"themes": [{"theme": "cdi"}]}
        with open('cogs/theme.json', 'w') as outfile:
            json.dump(newJson, outfile)
        await ctx.message.add_reaction('👍')


def setup(client):
    client.add_cog(GoogleImageSearch(client))
