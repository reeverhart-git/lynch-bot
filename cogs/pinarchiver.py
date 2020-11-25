import discord
from discord.ext import commands


# Cog for transferring pinned messages from one channel to another
class PinArchiver(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Get all pins in the context's channel and send them to the specified channel.
    @commands.command(aliases=['arc'])
    async def archive(self, ctx, *, archive: discord.TextChannel):
        print("Fetching pins")
        channel = ctx.message.channel
        pinlist = await channel.pins()
        # So far only supports pins with embeds. Most of our pins tend to be embeds anyways.
        for pin in pinlist:
            pid = pin.id
            owner = pin.author
            print(owner.name)
            # embeds and attachments are stored in a list by default, so we have to iterate through it.
            # get embeds
            for em in pin.embeds:
                em.set_author(name=owner.name)
                em.set_footer(text=pin.content)
                await archive.send(f'From: {owner}')
                await archive.send(embed=em)
                await pin.unpin()
            # get attachments
            for atch in pin.attachments:
                await archive.send(f'From: {owner}')
                await archive.send(atch.url)
                await pin.unpin()


def setup(client):
    client.add_cog(PinArchiver(client))