import discord
import random
import asyncio
import string
import json
from difflib import SequenceMatcher
from discord.ext import commands

with open('cogs/trickortreat.json') as json_file:
    data = json.load(json_file)

inuse = False
disposition = 50
similarity = .9
location = "Sentinel"
name = "Sentinel"
age = "999999"
death = "Sentinel"
victim = "Sentinel"
prompts = ['are you there',
           'where are you',
           'who did you kill',
           'who are you',
           'what are you doing',
           'how did you die',
           'how old are you',
           'what is your name',
           'are you friendly',
           'do you want us to leave',
           'what should we do',
           'why are you here']
deaths = ["accident",
          "murder",
          "suicide",
          "disease",
          "time"]
actions = ["run",
           "hide",
           "die",
           "leave",
           "get out",
           "join us",
           "kill self"]
gactions = ["hunting",
            "flying",
            "hanging",
            "watching",
            "stalking",
            "looking",
            "killing",
            "hurting",
            "eating"]
motives = ["revenge",
           "summoned",
           "evil",
           "mad",
           "restless",
           "warn",
           "help"]

def yesorno(disp):
    if disp >= 50:
        return "Yes"
    else:
        return "No"


def getlocation(loc):
    if loc == "Sentinel":
        house = random.randint(0, len(data["houses"])-1)
        global location
        location = data["houses"][house]
        return location
    else:
        return loc


def getage(a):
    if a == "999999":
        global age
        age = str(random.randint(1, 900))
        return age
    else:
        return a


def getdeath(d):
    if d == "Sentinel":
        global death
        death = random.choice(deaths)
        return death
    else:
        return d


def getactions():
    return random.choice(actions)


def getghostactions():
    return random.choice(gactions)

def getmotivation():
    return random.choice(motives)


class SpiritBoard(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Spirit Board cog online.")

    async def compareToPrompt(self, ctx, string):
        if string[0] == ',':
            return "no command"
        # Are you there?
        elif SequenceMatcher(None, prompts[0], string).ratio() > similarity:
            return getlocation(location)
        # Where are you?
        elif SequenceMatcher(None, prompts[1], string).ratio() > similarity:
            return getlocation(location)
        # Who did you kill?
        elif SequenceMatcher(None, prompts[2], string).ratio() > similarity:
            return await self.getvictim(ctx, victim)
        # Who are you?
        elif SequenceMatcher(None, prompts[3], string).ratio() > .95:
            return await self.givename(ctx, name)
        # What are you doing?
        elif SequenceMatcher(None, prompts[4], string).ratio() > similarity:
            return getghostactions()
        # How did you die?
        elif SequenceMatcher(None, prompts[5], string).ratio() > similarity:
            return getdeath(death)
        # How old are you?
        elif SequenceMatcher(None, prompts[6], string).ratio() > similarity:
            return getage(age)
        # What is your name?
        elif SequenceMatcher(None, prompts[7], string).ratio() > similarity:
            return await self.givename(ctx, name)
            # Are you friendly?
        elif SequenceMatcher(None, prompts[8], string).ratio() > similarity:
            return yesorno(disposition)
        # Do you want us to leave?
        elif SequenceMatcher(None, prompts[8], string).ratio() > similarity:
            return yesorno(disposition)
        # What should we do?
        elif SequenceMatcher(None, prompts[9], string).ratio() > similarity:
            return getactions()
        # Why are you here?
        elif SequenceMatcher(None, prompts[10], string).ratio() > similarity:
            return getmotivation()
        else:
            return "..."

    async def givename(self, ctx, n):
        if n == "Sentinel":
            server = ctx.guild
            randuser = random.choice(server.members).display_name
            global name
            name = randuser
            return name
        else:
            return n

    async def getvictim(self, ctx, v):
        if v == "Sentinel":
            server = ctx.guild
            randuser = random.choice(server.members).display_name
            global name
            if randuser is not name:
                global victim
                victim = randuser
                return victim
            else:
                victim = "you"
        else:
            return v

    async def spellmessage(self, ctx, msg: discord.Message, string):
        ghost = list(string)
        gmsg = ""
        membed = discord.Embed
        for c in ghost:
            embed = discord.Embed(title="The Spirit Speaks...")
            embed.set_thumbnail(url="https://i.postimg.cc/xCj01bSY/spiritboard.jpg")
            embed.clear_fields()
            gmsg += c + " "
            embed.add_field(name=gmsg.upper(),value="...")
            await msg.edit(embed=embed)
            membed = embed
            await asyncio.sleep(.2)
        return membed

    @commands.command(aliases=['ouiji', 'ouija', 'weegee', 'wege', 'spiritb', 'spirit'])
    async def sboard(self, ctx):
        random.seed()
        global inuse
        if inuse:
            pass
        else:
            inuse = True
            # Is the spirit vengeful or friendly?
            global disposition
            disposition = random.randint(0, 100)

            embed = discord.Embed(title="It is time to commune with the spirits...")
            embed.set_thumbnail(url="https://i.postimg.cc/xCj01bSY/spiritboard.jpg")
            embed.add_field(name="The spirits are restless...", value="Why don't you ask a question?")
            msg = await ctx.send(embed=embed)
            talking = True
            while talking:
                try:
                    responsemsg = await self.client.wait_for('message', timeout=60)
                    responsest = responsemsg.content
                    result = await self.compareToPrompt(ctx, responsest)
                    if result == "goodbye":
                        talking = False
                        inuse = False
                    embed = await self.spellmessage(ctx, msg, result)
                    embed.set_footer(text="Ask another question?", icon_url=self.client.user.avatar_url)

                except asyncio.TimeoutError:
                    inuse = False
                    talking = False
                    finembed = discord.Embed(title="The spirit has vacated...")
                    finembed.set_thumbnail(url="https://i.postimg.cc/xCj01bSY/spiritboard.jpg")
                    embed.add_field(name="There is no more response...", value="Try again at another time.")
                    await msg.edit(embed=finembed)



def setup(client):
    client.add_cog(SpiritBoard(client))