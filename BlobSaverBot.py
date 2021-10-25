'''
@author: ed0ardo
'''

import requests
from xml.etree import ElementTree
import json
import os
from pyrogram import filters
from pyrogram import Client

BOT_TOKEN = "XXX"
API_ID = "12345"
API_HASH  =  "1E2D3O456"

app = Client(
    "blobSaverBot",
    api_hash = API_HASH,
    api_id = API_ID,
    bot_token = BOT_TOKEN
)


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
                    await app.send_document(message.chat.id, fName, caption="__@BlobSaverBot__")
                    os.remove(fName)
                except:
                    pass
        await app.send_message(message.chat.id, "Done!")

    except Exception as e:
        print(e)
        await app.send_message(message.chat.id, "Error:\n" + str(e) + "\n\nIf you are sure you have done everything right, please try again later")


@app.on_message(filters.command("start"))
async def regioni(client, message):
    try:
        msg = "Welcome " + message.from_user.first_name + ", follow [this guide](https://telegra.ph/BlobSaverBot-Setup-10-17) or if you have a Windows PC try this program.\n\nBoth will help you in the first configuration, the next times it will be enough to re-send the file you will get.\n\n[<a href=\"https://github.com/Ed0ardo/BlobSaverBot\">Source Code</a>]"
        await app.send_document(message.chat.id, "BQACAgEAAxkDAAMmYWyt-0MlCK3zDaMVHeVvlXiX6GkAAsMBAAKo9WlHMW2XwKDQ0uEeBA", caption=msg)
    except Exception as e:
        print(e)


app.run()
