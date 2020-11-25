import discord
import random
import json
from discord.ext import commands

with open('cogs/insults.json') as json_file:
    data = json.load(json_file)


# This is a "for fun" annoyance tool, can be misused be smart.
class AngryThoughtBees(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Print that this cog is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Angry Thought Bees are swarming.")

    @commands.command(aliases=['gethisass', 'swarm'])
    async def sendTheBees(self, ctx, victim: discord.User, rate=5):
        try:
            authorization = True
            max = 25
            i = 0
            for id in data['immunity']:
                #print(id)
                #print(id['id'])
                if str(victim.id) == id['id']:
                    authorization = False
                i += 1

            if authorization:
                if rate > max:
                    rate = max
                await ctx.send(f"😈 Sending a swarm of {rate} angry thought bees! 😈")
                for i in range(0, rate):
                    await victim.send(data['insult'][random.randrange(0, len(data['insult']))])
            else:
                if rate > max:
                    rate = max
                await ctx.send(f"😞 They are immune! \n😈 Reflecting  {rate} angry thought bees at you! 😈")
                for i in range(0, rate):
                    await ctx.author.send(data['insult'][random.randrange(0, len(data['insult']))])

        except AttributeError:
            await ctx.send("Nice try...")


    @commands.command(aliases=['saveme', 'protectme'])
    async def notTheBees(self, ctx):

        safe = '{ "id":' + '"' + str(ctx.author.id) + '"}'
        jsafe = json.loads(safe)
        data['immunity'].append(jsafe)
        with open('cogs/insults.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['getme'])
    async def yesTheBees(self, ctx):
        i = 0
        for id in data['immunity']:
            if str(ctx.author.id) == id['id']:
                del data['immunity'][i]
        i += 1
        with open('cogs/insults.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['addinsult'])
    async def addInsult(self, ctx, *, insult):
        data['insult'].append(insult)
        with open('cogs/insults.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['beehelp'])
    async def atbHelp(self, ctx):
        embed=discord.Embed(title='Angry Thought Bees Help: ', color=0xf1ef5e)
        embed.add_field(name=',swarm "@victim" "#"', value='Attack the user with # angry thought bees.')
        embed.add_field(name=',addinsult "insult"', value='Adds the insult to the list of things the bees say.')
        embed.add_field(name=',saveme', value='Give yourself immunity to bee attacks.')
        embed.add_field(name=',getme', value='Remove your immunity to bee attacks.')
        embed.set_footer(text="GET THEM!", icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url="https://i.postimg.cc/T3ZxFd3H/killerbee.png")
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(AngryThoughtBees(client))