import discord
import json
import re
from discord.ext import commands

with open('cogs/wordoftheday.json') as json_file:
    data = json.load(json_file)

word = "antiqueing"
sentinel = "ff78ger87tgh43thfdiujvhf9d8sf87gyg875rt9hfg98vfhg9fgd89gdghdfgh"


class Wordoftheday(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Word Game cog online.")
        global word
        word = (data['wordoftheday'][0]['word'])
        print("Secret word is set to: " + word + ".")

    async def find_word(self, text, search):
        result = re.findall(r'\b' + search + r'\b', text, flags=re.IGNORECASE)
        if len(result) > 0:
            return True
        else:
            return False


    @commands.Cog.listener()
    async def on_message(self, message):
        if word.casefold() in message.content.casefold() and word is not sentinel and\
                await self.find_word(message.content, word) and not message.author.bot:
            name = (str(message.author.display_name)).upper()
            embed = discord.Embed(title=name + " SAID THE SECRET WORD!!!")
            embed.set_image(url="https://i.postimg.cc/XYM1cJPk/peewee.gif")
            await message.channel.send(embed=embed)
            # await message.channel.send(name + " SAID THE SECRET WORD!!!")
            # await message.channel.send(file=discord.File('resource/peewee.gif'))

    @commands.command(aliases=['secret', 'word'])
    async def setWord(self, ctx, secret):
        if len(secret) > 13:
            await ctx.message.add_reaction('👎')
            await ctx.send("Your word is too long.")
        else:
            await ctx.message.delete()
            global word
            word = secret
            newJson = {"wordoftheday": [{"word": str(word)}]}
            with open('cogs/wordoftheday.json', 'w') as outfile:
                json.dump(newJson, outfile)

    @commands.command(aliases=['stfu', 'noword'])
    async def turnoffWord(self, ctx):
        global word
        word = sentinel
        newJson = {"wordoftheday": [{"word": sentinel}]}
        with open('cogs/wordoftheday.json', 'w') as outfile:
            json.dump(newJson, outfile)

    @commands.command(aliases=['hint'])
    async def giveHint(self, ctx):
        global word
        hint = word[0]
        length = len(word)
        for i in range(length-2):
            hint += "\*"
        hint += word[length-1]
        await ctx.send("The secret word is: " + hint + ".")

    @commands.command(aliases=['secrethelp'])
    async def secretHelp(self, ctx):
        embed = discord.Embed(title='Secret Word Help: ', color=0xf1ef5e)
        embed.add_field(name=',secret "word"', value='Set the secret word.')
        embed.add_field(name=',hint', value='Gives you a hint on what the secret word is.')
        embed.add_field(name=',stfu', value='Turns off the secret word screaming.')
        embed.set_footer(text="You know what to do when someone says the secret word?", icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url="https://i.postimg.cc/dQHzdJv5/peewee.png")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Wordoftheday(client))

