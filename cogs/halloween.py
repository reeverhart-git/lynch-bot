import asyncio
import discord
import random
import datetime
import json
from discord.ext import commands

with open('cogs/trickortreat.json') as json_file:
    data = json.load(json_file)

# relevant dates
today = datetime.datetime.now()
halloween = datetime.datetime(today.year, 10, 31)
delta = halloween - today


class Halloween(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Print that this cog is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Halloween cog online.")

    # How many days till halloween?
    @commands.command(aliases=['halloween', 'hw'])
    async def xmoredaystillhalloween(self, ctx):

        # await ctx.send(f"{delta.days +1} days 'til Halloween, Halloween, Halloween! ")
        # await ctx.send(file=discord.File('resource/silvershamrock.gif'))

        embed = discord.Embed(title=f"{delta.days +1} days 'til Halloween, Halloween, Halloween! ", color=0xff5900)
        embed.set_image(url="https://i.postimg.cc/L5YBGzTr/silvershamrock.gif")
        if delta.days + 1 < 8:
            embed.set_footer(text="It's almost time!", icon_url=self.client.user.avatar_url)
        else:
            embed.set_footer(text="Silver Shamrock!", icon_url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['trick', 'treat', 'trickortreat','tot'])
    async def trickOrTreat(self, ctx):
        random.seed()
        house = random.randint(0, len(data["houses"])-1)
        embed = discord.Embed(title="You trick or treat at: " + data["houses"][house] + "...", color=0xff5900)
        embed.set_thumbnail(url="https://i.postimg.cc/RZxhrkhL/house.png")
        embed.set_footer(text="What will you get?", icon_url=self.client.user.avatar_url)
        msg = await ctx.send(embed=embed)
        choice = random.randint(0, 1)
        if choice == 0:  # tricked
            newembed = discord.Embed(title="You trick or treat at: " + data["houses"][house] + "...", color=0xff5900)
            newembed.set_thumbnail(url="https://i.postimg.cc/RZxhrkhL/house.png")
            newembed.set_footer(text="AHHHH!", icon_url=self.client.user.avatar_url)
            pick = random.randint(0, len(data["trick"])-1)
            trick = data["trick"][pick]
            newembed.add_field(name='TRICKED!', value="You were tricked! " + trick)

            await asyncio.sleep(3)
            await msg.edit(embed=newembed)
        elif choice == 1:  # treated
            newembed = discord.Embed(title="You trick or treat at: " + data["houses"][house] + "...", color=0xff5900)
            newembed.set_thumbnail(url="https://i.postimg.cc/RZxhrkhL/house.png")
            newembed.set_footer(text="Sweet!", icon_url=self.client.user.avatar_url)
            pick = random.randint(0, len(data["treat"])-1)
            treat = data["treat"][pick]
            newembed.add_field(name='TREAT!', value="You got a: " + treat + "! What a treat!")

            await asyncio.sleep(3)
            await msg.edit(embed=newembed)

    @commands.command(aliases=['addtrick'])
    async def addTrick(self, ctx, *, trick):
        data['trick'].append(trick)
        with open('cogs/trickortreat.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['addtreat'])
    async def addTreat(self, ctx, *, treat):
        data['treat'].append(treat)
        with open('cogs/trickortreat.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['addhouse'])
    async def addHouse(self, ctx, *, house):
        data['houses'].append(house)
        with open('cogs/trickortreat.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['tothelp'])
    async def totHelp(self, ctx):
        embed = discord.Embed(title='Trick or Treating Help: ', color=0xff5900)
        embed.add_field(name=',tot', value='Trick or treat!')
        embed.add_field(name=',addtrick "trick"', value='Adds a new trick to the pile.')
        embed.add_field(name=',addtreat "treat"', value='Adds a new treat to the pile')
        embed.add_field(name=',addhouse "house"', value='Adds a new house to go to.')
        embed.set_footer(text="Are you guys going trick or treating?", icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url="https://i.postimg.cc/RZxhrkhL/house.png")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Halloween(client))
