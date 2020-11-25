import discord
import json
import datetime
import asyncio
from discord.ext import commands, tasks

URL = "http://172.222.228.170:5000/"
weekdays = {1: "Mondays", 2: "Tuesdays", 3: "Wednesdays", 4: "Thursdays", 5: "Fridays",
            6: "Saturdays", 7: "Sundays"}

times = {"1AM": 1, "2AM": 2, "3AM": 3, "4AM": 4, "5AM": 5,
         "6AM": 6, "7AM": 7, "8AM": 8, "9AM": 9, "10AM": 10,
         "11AM": 11, "12PM": 12, "1PM": 13, "2PM": 14, "3PM": 15,
         "4PM": 16, "5PM": 17, "6PM": 18, "7PM": 19, "8PM": 20, "9PM": 21,
         "10PM": 22, "11PM": 23, "12AM": 24}


def getDay(day):
    today = datetime.datetime.now().isoweekday()
    if day == "Weekends":
        if weekdays[today] == weekdays[6] or weekdays[7]:
            return True
        else:
            return False
    elif weekdays[today] == day:
        return True
    else:
        return False


def getTime(time, tolerance):
    now = datetime.datetime.now().time()
    n_hour = int(now.hour)
    n_minute = int(now.minute)
    if time in times:
        t_hour = times[time]
        d_minute = n_minute / 60
        d_hour = float((t_hour - n_hour) - d_minute)

        if d_hour <= tolerance:
            return True
        else:
            return False
    else:
        return False


class Events(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_ready(self):
        print("Events cog online.")
        try:
            self.advertiseEvents.start()
        except RuntimeError:
            print("Task loop is still running.")

    @tasks.loop(hours=1, reconnect=True)
    async def advertiseEvents(self):
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
        if "channel" in data:
            channel = ""
            for g in self.client.guilds:
                channel = discord.utils.get(g.text_channels, id= int(data["channel"]))
                if channel is not None:
                    break
            try:
                if channel != "" or None:
                    for e in data["event"]:
                        if "date" in e and "time" in e:
                            if getDay(e["date"]) and int(e["adcount"]) == 0:
                                string = ""
                                if "participants" in e:
                                    for p in e['participants']:
                                        if "id" in p:
                                            mention = "<@" + str(p['id']) + ">"
                                            string += mention + " "
                                embed = discord.Embed(title=e["name"] + " is happening soon!", color=0xe79943)
                                embed.description = e["desc"]
                                if string != "":
                                    embed.add_field(name="Calling:", value=string, inline=True)
                                embed.add_field(name="Happening:", value=e["date"] + ", " + e["time"], inline=True)
                                await channel.send(embed=embed)
                                if "adcount" in e:
                                    e["adcount"] = 6
                            else:
                                if "adcount" in e:
                                    if e["adcount"] <= 0:
                                        e["adcount"] = 0
                                    else:
                                        e["adcount"] = e["adcount"]-1
                            with open('cogs/events.json', 'w') as outfile:
                                json.dump(data, outfile)
            except OSError:
                # This was causing a mystery error...
                pass


    @commands.command(aliases=["setevad"])
    async def setAdChannel(self, ctx):
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
            if "channel" not in data:
                data.append({"channel": ctx.message.channel.id})
            else:
                data["channel"] = ctx.message.channel.id
            print(ctx.message.channel.name)
            with open('cogs/events.json', 'w') as outfile:
                json.dump(data, outfile)
            await ctx.message.add_reaction('👍')

    @commands.command(aliases=['events'])
    async def getAllEvents(self, ctx):
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
        embed = discord.Embed(title='Planned Events:', color=0xe79943)
        for e in data['event']:
            if e['server'] == str(ctx.guild) or "Website":
                if "participants" in e:
                    members = e['participants'][0]['name']
                    if members == "Website":
                        members = "RSVP'D:"
                    index = 0
                    for m in e['participants']:
                        if index == 0:
                            pass
                        else:
                            if e['participants'][index]['name'] != "Website":
                                members += ", " + e['participants'][index]['name']
                        index += 1
                else:
                    members = f'Nobody yet...\nUse ,evjoin "{e["name"]}"'
                name = e['name']
                if "date" in e:
                    name += "\n" + e['date']
                if "time" in e:
                    name += ", " + e['time']
                if len(members) > 0:
                    embed.add_field(name=name, value=members, inline=True)
                else:
                    embed.add_field(name=name, value="Nobody!", inline=True)
                embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.description = f"[Add Event]({URL})"
        embed.set_footer(text="Use ,evjoin to join one! Try ,evhelp!"\
                         , icon_url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['evadd'])
    async def addEvent(self, ctx, name, time="none"):
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
        user = ctx.message.author
        data['event'].append({
            "name": name,
            "expiration": time,
            "server": str(ctx.guild),
            "participants": [{
              "name": str(user),
                "id": user.id

            }]
        })
        with open('cogs/events.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')
        await self.getAllEvents(ctx)


    @commands.command(aliases=['evdel'])
    async def removeEvent(self, ctx, name):
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
        index = 0
        for e in data['event']:
            if e['name'] == name:
                del data['event'][index]
            index += 1
        with open('cogs/events.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')
        await self.getAllEvents(ctx)

    @commands.command(aliases=['evjoin'])
    async def joinEvent(self, ctx, name):
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
        index = 0
        user = ctx.message.author
        for e in data['event']:
            if e['name'] == name:
                e['participants'].append({'name': str(user), 'id': user.id})
            index += 1
        with open('cogs/events.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['evleave'])
    async def leaveEvent(self, ctx, name):
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
        index = 0
        user = ctx.message.author
        for e in data['event']:
            if e['name'] == name:
                index2 = 0
                for p in e['participants']:
                    print(len(p))
                    if len(p) <= 2:
                        print("No more users in this event, deleting")
                        del data['event'][index]
                    elif p['name'] == str(user):
                        print("Removing from event")
                        del data['event'][index]['participants'][index2]
                    index2 += 1
            index += 1
        with open('cogs/events.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')

    @commands.command(aliases=['evping'])
    async def pingEvent(self, ctx, name):
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
        index = 0
        string = ""
        guild = ctx.guild
        for e in data['event']:
            if e['name'] == name:
                for p in e['participants']:
                    if "id" in p:
                        mention = "<@" + str(p['id']) + ">"
                        string += mention + " "
            index += 1
        await ctx.send(name + ": " + string)

    @commands.command(aliases=['evtime'])
    async def setTime(self, ctx, name, time):
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
        index = 0
        for e in data['event']:
            if e['name'] == name:
                e['expiration'] = time
            index += 1
        with open('cogs/events.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')
        await self.getAllEvents(ctx)

    @commands.command(aliases=['evname'])
    async def changeName(self, ctx, name, new):
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
        index = 0
        for e in data['event']:
            if e['name'] == name:
                e['name'] = new
            index += 1
        with open('cogs/events.json', 'w') as outfile:
            json.dump(data, outfile)
        await ctx.message.add_reaction('👍')
        await self.getAllEvents(ctx)

    @commands.command(aliases=['evlink'])
    async def eventWebsite(self, ctx):
        embed = discord.Embed(title='Event Website: ', color=0xe79943)
        embed.description = f"[Click me to go to the event planner!]({URL})"
        await ctx.send(embed=embed)

    @commands.command(aliases=['evhelp'])
    async def eventHelp(self, ctx):
        embed=discord.Embed(title='Event Help: ', color=0xe79943)
        embed.add_field(name=',events', value='Shows all events on the server.')
        embed.add_field(name=',evjoin "Name"', value='Join the event.')
        embed.add_field(name=',evleave "Name"', value='Leave the event')
        embed.add_field(name=',evadd "Name" "Time"', value='Creates a new event with the specified name.\
         Including a time is optional.')
        embed.add_field(name=',evdel "Name"', value='Deletes the event.')
        embed.add_field(name=',events', value='Shows all events on the server.')
        embed.add_field(name=',evname "Name" "New"', value='Renames the event to the New name.')
        embed.add_field(name=',evtime "Name" "Time"', value='Changes the event\\s time to the new Time.')
        embed.add_field(name=',evping "Name"', value='Mentions all users who joined the event.')
        embed.set_footer(text="Now go and join/plan some events!", icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url="https://i.postimg.cc/rs3JNPq3/masks.png")
        await ctx.send(embed=embed)

    @commands.command(aliases=['ads'])
    async def showAds(self, ctx):
        with open('cogs/ads.json') as json_file:
            data = json.load(json_file)
        embed = discord.Embed(title="Ads", color=0xe79943)
        admsg = await ctx.send(embed=embed)
        iterations = 4
        for loop in range(0, iterations):
            for index in range(0, len(data["ads"])):
                try:
                    if "name" in data["ads"][index]:
                        if not str(data["ads"][index]["name"]).isspace() and len(data["ads"][index]["name"]) > 0:
                            nembed = discord.Embed(title=data["ads"][index]["name"], color=0xe79943)
                        else:
                            nembed = discord.Embed(title="Unknown", color=0xe79943)
                    else:
                        nembed = discord.Embed(title="Unknown", color=0xe79943)
                    if "img" in data["ads"][index]:
                        if not str(data["ads"][index]["img"]).isspace() and len(data["ads"][index]["img"]) > 0:
                            nembed.set_image(url=data["ads"][index]["img"])
                    nembed.description = f'[Advertise here!]({URL+"ads"})'
                    if "desc" in data["ads"][index]:
                        if not str(data["ads"][index]["desc"]).isspace() and len(data["ads"][index]["desc"]) > 0:
                            nembed.add_field(name='Description:', value=data["ads"][index]["desc"], inline=False)
                    if "owner" in data["ads"][index]:
                        if not str(data["ads"][index]["owner"]).isspace() and len(data["ads"][index]["owner"]) > 0:
                            nembed.set_footer(text=f'Ad {index+1} of {len(data["ads"])}\nBrought to you by: {data["ads"][index]["owner"]}')
                    else:
                        nembed.set_footer(text=f'Ad {index + 1} of {len(data["ads"])}')
                    await admsg.edit(embed=nembed)
                    await asyncio.sleep(10)
                except discord.HTTPException:
                    pass


def setup(client):
    client.add_cog(Events(client))
