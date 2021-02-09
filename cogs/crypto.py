import discord
import datetime
import json
import random
from discord.ext import commands
from pycoingecko import CoinGeckoAPI

with open('cogs/theme.json') as json_file:
    data = json.load(json_file)

cg = CoinGeckoAPI()
coins = {"btc": "bitcoin",
         "eth": "ethereum",
         "ltc": "litecoin",
         "doge": "dogecoin",
         "xmr": "monero",
         "grt": "the-graph",
         "dgb": "digibyte",
         "bat": "basic-attention-token",
         "mana": "decentraland"}

class Crypto(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.mode = data["themes"][0]["theme"]

    @commands.Cog.listener()
    async def on_ready(self):
        print("Crypto cog online.")

    @commands.command(aliases=['pr'])
    async def getCryptoPrice(self, ctx, slug):
        try:
            # check if a common coin abbreviation was used
            rand = random.randint(0, 3)
            if slug.lower() in coins:
                slug = coins[slug.lower()]
            # fetch a dictionary using API
            price = cg.get_price(ids=slug, vs_currencies=["usd", "eur", "cad"], include_24hr_change="true",
                                 include_last_updated_at="true")
            # determine if 24h change is positive or negative
            change = round(price[slug]["usd_24h_change"], 2)
            arrow = "🔼"
            if change < 0:
                arrow = "🔽"
            elif change <= -10:
                arrow = "⏬"
            elif change > 20:
                arrow = "⏫"
            if price is False:
                await ctx.send("That coin wasn't found, try spelling it out and using dashes. EG: bitcoin, the-graph")
            else:
                em = discord.Embed(title=slug.capitalize(), color=0xDAA520)
                # Use the themes for jokes/pranks
                if self.mode == "cdi" and rand >= 3:
                    em.set_thumbnail(url="https://i.postimg.cc/k58xCzBg/morshusanim.gif")
                    em.set_footer(
                        text="Bitcoin? Ethereum? DigiByte? You want it? It's yours my friend, as long as you have enough rubies.",
                        icon_url=self.client.user.avatar_url)
                else:
                    em.set_thumbnail(url="https://i.postimg.cc/jS1BJ08Q/btc.gif")
                    em.set_footer(
                        text="NOTE: Always check important info on a real exchange, this is for convenience only.",
                        icon_url=self.client.user.avatar_url)
                em.add_field(name="USD", value="```" + "$ " + str(price[slug]["usd"]) + "```")
                em.add_field(name="EUR", value="```" + "€ " + str(price[slug]["eur"]) + "```")
                em.add_field(name="CAD", value="```" + "$ " + str(price[slug]["cad"]) + "```")
                em.add_field(name="Last Updated",
                             value="```" + str(datetime.datetime.fromtimestamp(price[slug]["last_updated_at"])) + "```",
                             inline=True)
                em.add_field(name="24h Change",
                             value="```" + arrow + " " + str(change) + "%" + "```",
                             inline=True)
                await ctx.send(embed=em)
        except KeyError:
            await ctx.send("That coin wasn't found, try spelling it out and using dashes. EG: bitcoin, the-graph")

    @commands.command(aliases=['btc', 'BTC', 'bitcoin'])
    async def getBitcoinPrice(self, ctx):
        await self.getCryptoPrice(ctx, "bitcoin")

    @commands.command(aliases=['eth', 'ETH', 'ethereum'])
    async def getEthereumPrice(self, ctx):
        await self.getCryptoPrice(ctx, "ethereum")


def setup(client):
    client.add_cog(Crypto(client))