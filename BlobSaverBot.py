'''
@author: ed0ardo
'''

import requests
from xml.etree import ElementTree
import json
import os
import re
from pyrogram import filters
from pyrogram import Client
import feedparser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

BOT_TOKEN = "XXX"
API_ID = "12345"
API_HASH  =  "1E2D3O456"

def getLastVersions(url):
    try:
        now = datetime.now()
        feed = feedparser.parse(url)
        versions = [version for version in feed.entries if ("iPadOS" in version["title"] or "iOS" in version["title"]) and "OTA" not in version["title"] and (now - datetime.strptime(version["guid"], "%Y-%m-%dT%H:%M:%SZ")).days < 3]
        return versions
    except Exception as e:
        print(e)
        return False

global lastVers
lastVers = getLastVersions("https://ipsw.me/timeline.rss")

app = Client(
    "blobSaverBot",
    api_hash = API_HASH,
    api_id = API_ID,
    bot_token = BOT_TOKEN
)


async def aGetLastVersions(url):
    try:
        now = datetime.now()
        feed = feedparser.parse(url)
        versions = [version for version in feed.entries if ("iPadOS" in version["title"] or "iOS" in version["title"]) and "OTA" not in version["title"] and (now - datetime.strptime(version["guid"], "%Y-%m-%dT%H:%M:%SZ")).days < 3]
        return versions
    except Exception as e:
        print(e)
        return False

async def diffVers(newLV, lastN):
    try:
        diffVers = [v for v in newLV if v not in lastN]
        return diffVers
    except Exception as e:
        print(e)
        return False

async def aCheckLastVersions():
    try:
        global lastVers
        newLastVers = await aGetLastVersions("https://ipsw.me/timeline.rss")
        newer = await diffVers(newLastVers, lastVers)
        if newer:
            msg = ""
            for v in newer:
                msg += v["summary_detail"]["value"] + "\n"
            msg += "\nThe ability to download the SHSH2 files of this version takes some time!\n(It can take a couple of hours as well)"
            ids = os.listdir("./SHSH2/")
            for id in ids:
                try:
                    await app.send_message(int(id), msg)
                except:
                    pass
    except Exception as e:
        print(e)
        return False

scheduler = AsyncIOScheduler()
scheduler.add_job(aCheckLastVersions, "interval", minutes=15)
scheduler.start()

@app.on_message(filters.document)
async def bsXML(client, message):
    try:
        await app.send_message(message.chat.id, "I am analyzing the file...")
        path = "./SHSH2/" + str(message.from_user.id) + "/"
        if not os.path.exists(path):
                os.makedirs(path)
        fName = await message.download(path)
        root = ElementTree.parse(fName).getroot()
        os.remove(fName)
        devices = []
        x = ""
        par = ["ECID", "Device Identifier", "Apnonce", "Generator"]
        for item in root.findall(".//entry"):
            t = item.attrib
            t = list(t.values())
            if t[0] in par:
                x += '"' + t[0] + '"' + " : " + '"' + t[1] + '"' + ", "
                if t[0] == par[-1]:
                    devices.append("{" + x[:-2] + "}")
                    x = ""

        await app.send_message(message.chat.id, "I'm downloading the SHSH2 files, it may take a few seconds...")
        for device in devices:
            device = json.loads(device)
            path += device["ECID"] + "/"
            if not os.path.exists(path):
                os.makedirs(path)
            urlIPSW = "https://api.ipsw.me/v4/device/" + device["Device Identifier"] + "?type=ipsw"
            r = requests.get(urlIPSW)
            rawData = json.loads(r.content.decode("utf-8"))
            firmwares = rawData["firmwares"]
            boards = rawData["boards"]
            boardconfig = ""
            for firmware in firmwares:
                if firmware["signed"]:
                    if boardconfig:
                        cmd = "./tsschecker -d " + device["Device Identifier"] + " -i " + firmware["version"] + " -B " + boardconfig + " -e " + device["ECID"] + " --apnonce " + device["Apnonce"] + " --generator " + device["Generator"] + " --nocache -s --save-path " + path + " > /dev/null"
                        os.system(cmd)
                    else:
                        for board in boards:
                            cmd = "./tsschecker -d " + device["Device Identifier"] + " -i " + firmware["version"] + " -B " + board["boardconfig"] + " -e " + device["ECID"] + " --apnonce " + device["Apnonce"] + " --generator " + device["Generator"] + " --nocache -s --save-path " + path + " > /dev/null"
                            os.system(cmd)
                            if len(os.listdir(path)) > 0:
                                boardconfig = board["boardconfig"]
                                break
            path = "./SHSH2/" + str(message.from_user.id) + "/"
        dirs = [ path + d + "/" for d in os.listdir(path) if not os.path.isfile(path + d)]
        for dir in dirs:
            fNames = [ dir + d for d in os.listdir(dir) if os.path.isfile(dir + d)]
            for fName in fNames:
                try:
                    dati = fName.split("/")[-1]
                    dati = re.findall("_([0-9.]*)-|_([a-z-A-Z-0-9,]*)_", dati)
                    dati = ["".join(filter(lambda y: y, z)) for z in dati]
                    msg = "`"
                    for k in dati:
                        msg += "- " + k + " -"
                    msg += "`\n\n__@BlobSaverBot__"
                    await app.send_document(message.chat.id, fName, caption=msg)
                    os.remove(fName)
                except:
                    pass
        await app.send_message(message.chat.id, "Done!")

    except Exception as e:
        print(e)
        await app.send_message(message.chat.id, "Error:\n" + str(e) + "\n\nIf you are sure you have done everything right, please try again later")

@app.on_message(filters.command("start"))
async def start(client, message):
    try:
        msg = "Welcome " + message.from_user.first_name + ", follow [this guide](https://telegra.ph/BlobSaverBot-Setup-10-17) or if you have a Windows PC try this program.\n\nBoth will help you in the first configuration, the next times it will be enough to re-send the file you will get.\n\n[<a href=\"https://github.com/Ed0ardo/BlobSaverBot\">Source Code</a>]"
        await app.send_document(message.chat.id, "BQACAgEAAxkDAAMmYWyt-0MlCK3zDaMVHeVvlXiX6GkAAsMBAAKo9WlHMW2XwKDQ0uEeBA", caption=msg)
    except Exception as e:
        print(e)


app.run()