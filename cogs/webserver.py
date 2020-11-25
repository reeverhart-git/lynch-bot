import discord
import json
import sys
from quart import Quart, redirect, url_for, render_template, request, flash
from discord.ext import commands, tasks

sys.path.append("bot.py")
from bot import app


@app.route("/")
async def home():
    try:
        with open('cogs/events.json') as json_file:
            data = json.load(json_file)
        return await render_template("index.html", events=data["event"])
    except ConnectionAbortedError:
        # This error happens mostly when the browser is closed, non issue.
        pass


@app.route("/addEvent", methods=['POST'])
async def addEvent():
    with open('cogs/events.json') as json_file:
        data = json.load(json_file)
    ename = (await request.form)['ename']
    edesc = (await request.form)['edesc']
    etime = (await request.form)['etime']
    edate = (await request.form)['edate']
    data['event'].append({
        "name": ename,
        "desc": edesc,
        "date": edate,
        "time": etime,
        "server": "Website",
        "adcount": 0,
        "participants":[{
            "name": "Website"
        }]
    })
    with open('cogs/events.json', 'w') as outfile:
        json.dump(data, outfile)
    return redirect(url_for('home'))

@app.route("/removeEvent", methods=['POST'])
async def removeEvent():
    with open('cogs/events.json') as json_file:
        data = json.load(json_file)
    index = 0
    ename = (await request.form)['event_name']
    for e in data['event']:
        if e['name'] == ename:
            del data['event'][index]
        index += 1
    with open('cogs/events.json', 'w') as outfile:
        json.dump(data, outfile)
    return redirect(url_for('home'))

@app.route("/ads")
async def adhome():
    try:
        with open('cogs/ads.json') as json_file:
            data = json.load(json_file)
        return await render_template("adindex.html", ads=data["ads"])
    except ConnectionAbortedError:
        # This error happens mostly when the browser is closed, non issue.
        pass

@app.route("/removeAd", methods=['POST'])
async def removeAd():
    with open('cogs/ads.json') as json_file:
        data = json.load(json_file)
    index = 0
    aname = (await request.form)['ad_name']
    for a in data['ads']:
        if a['name'] == aname:
            del data['ads'][index]
        index += 1
    with open('cogs/ads.json', 'w') as outfile:
        json.dump(data, outfile)
    return redirect(url_for('adhome'))


@app.route("/addAd", methods=['POST'])
async def addAd():
    with open('cogs/ads.json') as json_file:
        data = json.load(json_file)
    aname = (await request.form)['aname']
    adesc = (await request.form)['adesc']
    aowner = (await request.form)['aowner']
    aimg = (await request.form)['aimg']
    data['ads'].append({
        "name": aname,
        "desc": adesc,
        "owner": aowner,
        "img": aimg,
    })
    with open('cogs/ads.json', 'w') as outfile:
        json.dump(data, outfile)
    return redirect(url_for('adhome'))


class WebServer(commands.Cog):

    def __init__(self, client):
        self.client = client



    @commands.Cog.listener()
    async def on_ready(self):
        print("Web Server Cog online.")



def setup(client):
    client.add_cog(WebServer(client))