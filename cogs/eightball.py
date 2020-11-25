import discord
import random
from discord.ext import commands

# This was made from this tutorial series: https://youtu.be/nW8c7vT6Hl4?list=PLW3GfRiBCHOhfVoiDZpSz8SM_HybXRPzZ
# Modified to be a cog, just for fun.


class EightBall(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Print that this cog is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("8ball cog online.")

    # magic 8ball command, because 8ball is an invalid command name, we use an alias.
    @commands.command(aliases =['8ball'])
    async def _8ball(self, ctx, *, question):
        responses = ['It is certain.',
                     'It is decidedly so.',
                     'Without a doubt.',
                     'Yes - definitely.',
                     'You may rely on it.',
                     'As I see it,  yes.',
                     'Most likely.',
                     'Outlook good.',
                     'Yes.',
                     'Signs point to yes.',
                     'Reply hazy, try again.',
                     'Ask again later.',
                     'Better not tell you now.',
                     'Cannot predict now.',
                     'Concentrate and ask again.',
                     "Don't count on it.",
                     'My reply is no.',
                     'My sources say no.',
                     'Outlook not so good.',
                     'Very doubtful.']
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')


def setup(client):
    client.add_cog(EightBall(client))