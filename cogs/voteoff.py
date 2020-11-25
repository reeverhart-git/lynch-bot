import discord
import asyncio
from discord.ext import commands

# hard implementing some basic variables, tied to server atm.
emoji = "rock"
threshold = 3
time = 60


class VoteOff(commands.Cog):

    def __init__(self, client):
        self.client = client

    # checks every message in the cache for reactions
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # print('Reaction detected.')
        # print(reaction.emoji.name)
        # Check if the reaction emoji is the one we are looking for, and its been used N times.
        try:
            if reaction.emoji.name == emoji:
                print('Reaction was the emoji checked.')
                if reaction.count >= threshold:
                    print(f"REACTION COUNT OVER {threshold}!")
                    victim = reaction.message.author
                    server = reaction.message.guild
                    msg = reaction.message
                    role = discord.Role
                    if discord.utils.get(server.roles, name="IN JAIL"):
                        # print("Role exists in the server, so we didn't make one.")
                        role = discord.utils.find(lambda r: r.name == 'IN JAIL', server.roles)
                    else:
                        role = await server.create_role(name="IN JAIL", colour = discord.Colour(0xff0000), hoist=True)
                    await victim.add_roles(role)
                    await msg.clear_reactions()
                    # await msg.delete()
                    await msg.channel.send(f'{victim.display_name} has been ROCKED! SHAME THEM! @here')
                    await asyncio.sleep(time)
                    await victim.remove_roles(role)
                    await msg.channel.send(f'{victim.display_name} has been released from their shame!')
                else:
                    print(f'Count is: {reaction.count}')
        except:
            pass




def setup(client):
    client.add_cog(VoteOff(client))
