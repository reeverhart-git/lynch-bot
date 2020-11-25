import discord
import random
import asyncio
import json
from discord.ext import commands

with open('cogs/judgementboy.json') as json_file:
    data = json.load(json_file)


async def preamble(ctx):
    embed = discord.Embed(title="Judgement!", color=0xb30000)
    embed.set_thumbnail(url="https://i.postimg.cc/nrJ91PQT/jb1.jpg")
    embed.add_field(name='Do you know?', value='Who I am?', inline=False)
    msg = await ctx.send(embed=embed)
    await asyncio.sleep(2)
    embed.clear_fields()
    embed.set_thumbnail(url="https://i.postimg.cc/gcVZ0mf7/jb2.jpg")
    embed.add_field(name='They call me:', value='Judgement boy!', inline=False)
    await msg.edit(embed=embed)
    await asyncio.sleep(2)
    embed.clear_fields()
    embed.set_thumbnail(url="https://i.postimg.cc/qMpChWrv/jb3.jpg")
    embed.add_field(name='Do you know?', value='Who I am?', inline=False)
    await msg.edit(embed=embed)
    await asyncio.sleep(2)
    embed.clear_fields()
    embed.set_thumbnail(url="https://i.postimg.cc/hPMQ9M4b/jb4.jpg")
    embed.add_field(name='I AM:', value='JUDGEMENT BOY!', inline=False)
    embed.set_footer(text="JUUUUUUDGEMENT!")
    await msg.edit(embed=embed)
    await asyncio.sleep(3)
    return msg, embed


async def reversePerson(string):
    split = string.split()
    oldsplit = string.split()
    i = 0
    for s in split:
        if split[i] == oldsplit[i]:
            if split[i].lower() == 'you':
                split[i] = 'me'
            elif split[i].lower() == "i":
                split[i] = 'you'
            elif split[i].lower() == "i'll":
                split[i] = "you'll"
            elif split[i].lower() == "my":
                split[i] = "your"
            elif split[i].lower() == "your":
                split[i] = "my"
            elif split[i].lower() == "you'll":
                split[i] = "I'll"
        i += 1
    i = 0
    newstring = ""
    for s in split:
        newstring += split[i] + " "
        i += 1
    newstring = newstring[:-1].capitalize() + "..."
    return newstring


class JudgementBoy(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Judgement Boy cog online.")

    @commands.command(aliases=['Judge'])
    async def judge(self, ctx, victim: discord.User):
        random.seed()
        pick = data["judgements"][random.randint(0,len(data["judgements"])-1)]
        prompt = pick["prompt"]
        mention = "<@" + str(victim.id) + ">"
        vname = victim.display_name
        msg, embed = await preamble(ctx)
        embed.clear_fields()
        embed.set_footer(text=" ")
        embed.add_field(name=vname + "!", value=prompt, inline=False)
        embed.add_field(name="Now...", value="What will you do? (Enter a reply " + mention + ")", inline=False)
        await msg.edit(embed=embed)

        try:
            responsemsg = await self.client.wait_for('message', check=lambda message: message.author == victim,\
                                                     timeout=120)
            responsest = responsemsg.content
            responsest = await reversePerson(responsest)
            embed.clear_fields()
            embed.add_field(name="YOU SAY YOU WILL:", value=responsest, inline=False)
            embed.add_field(name="WELL I SAY", value="WE CONSULT THE BALANCE OF TRUTH!", inline=False)
            embed.set_thumbnail(url="https://i.postimg.cc/RFhYGgwr/judgement.gif")
            msg2 = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            choice = random.randint(0,1)
            if choice == 0: # Money
                embed.add_field(name="💰:", value=pick["money"], inline=False)
            elif choice == 1: # Love
                embed.add_field(name="❤️:", value=pick["love"], inline=False)

            embed.add_field(name="It was your choice,", value="and you have to live with it.", inline=False)
            embed.set_thumbnail(url="https://i.postimg.cc/rzXYVc3c/jb5.jpg")
            await msg2.edit(embed=embed)

        except asyncio.TimeoutError:
            embed.clear_fields()
            embed.add_field(name=vname.upper() + " HAS RUN AWAY FROM THE TRUTH", \
                            value="AND WILL RECEIVE THE WORST POSSIBLE PUNISHMENT!", inline=False)
            await msg.edit(embed=embed)

    @commands.command(aliases=['addjudge'])
    async def addJudge(self, ctx, prompt, money, love):
        data['judgements'].append({'prompt': prompt, 'money': money, 'love': love})
        with open('cogs/judgementboy.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['judgehelp'])
    async def judgeHelp(self, ctx):
        embed = discord.Embed(title='Summoning Judgement Boy: ', color=0xb30000)
        embed.add_field(name=',judge @user', value='Forces the user to play the judgement game.')
        embed.add_field(name=',addjudge "prompt" "money" "love"', value='Adds a new scenario, be careful and use all\
         quotes! Use shift+enter to make a new line in your entries!')
        embed.set_footer(text="Do you know who I am?", icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url="https://i.postimg.cc/hPMQ9M4b/jb4.jpg")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(JudgementBoy(client))
