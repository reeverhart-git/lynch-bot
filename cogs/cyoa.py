import discord
import random
import asyncio
import json
from discord.ext import commands

with open('cogs/cyoastories.json') as json_file:
    data = json.load(json_file)


async def displayStories():
    embed = discord.Embed(title="Pick a Story:", color=0xff5900)
    for i in range(0,len(data["stories"])):
        embed.add_field(name=data["stories"][i]["name"], value="Type " + str(i) + "!")
    return embed

async def choose(i, key, choice):
    j = 0
    for part in data["stories"][i]["events"]:
        if part['key'] == key:
            return data["stories"][i]["events"][j]["choices"][choice]["link"]
        j += 1
    return "END"

async def nextPart(i,key):
    j = 0
    for part in data["stories"][i]["events"]:
        if part['key'] == key:
            return data["stories"][i]["events"][j]
        j += 1
    return "END"


class ChooseYourOwnAdventure(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def getInput(self, ctx):
        await ctx.send("Choose an option, type the number: ")
        try:
            choice = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, \
                                                timeout=120)
            return choice.content
        except asyncio.TimeoutError:
            await ctx.send("Where'd you go? The book is closed!")
            return "END"

    @commands.Cog.listener()
    async def on_ready(self):
        print("CYOA cog online.")

    @commands.command(aliases=['str', 'cyoa'])
    async def story(self, ctx):
        reading = True
        embed = await displayStories()
        msg = await ctx.send(embed=embed)
        story = int(await self.getInput(ctx))
        next = await nextPart(story, "intro")
        stembed = discord.Embed(title=data["stories"][story]["name"], color=0xff5900)
        stembed.add_field(name=data["stories"][story]["events"][0]["key"].capitalize(), \
                          value=data["stories"][story]["events"][0]["text"], inline=False)
        for i in range(0, len(data["stories"][story]["events"][0]["choices"])):
            stembed.add_field(name=str(i), value=data["stories"][story]["events"][0]["choices"][i]["text"])
        await msg.edit(embed=stembed)
        choice = int(await self.getInput(ctx))
        key = await choose(story, data["stories"][story]["events"][0]["key"], choice)
        while reading:
            next = await nextPart(story, key)
            newembed=discord.Embed(title=next["title"], color=0xff5900)
            newembed.add_field(name=next["key"].capitalize(), value=next["text"], inline=False)
            for i in range(0, len(next["choices"])):
                newembed.add_field(name=str(i), value=next["choices"][i]["text"])
            msgl = await ctx.send(embed=newembed)
            choice = int(await self.getInput(ctx))
            key = await choose(story, next["key"], choice)
            if key == "GAMEOVER":
                reading = False
                newembed.set_footer(text="Thanks for playing!", icon_url=self.client.user.avatar_url)
                await msgl.edit(embed=newembed)








def setup(client):
    client.add_cog(ChooseYourOwnAdventure(client))
