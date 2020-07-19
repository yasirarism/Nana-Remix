import os
from datetime import datetime
import requests
from asyncio import sleep

from pyrogram import Filters

from nana import app, Command, IBM_WATSON_CRED_URL, IBM_WATSON_CRED_PASSWORD
from nana.modules.downloads import download_reply_nocall


@app.on_message(Filters.me & Filters.command("stt", Command))
async def speach_to_text(client, message):
    start = datetime.now()
    input_str = message.reply_to_message.voice
    if input_str:
        required_file_name = await download_reply_nocall(client, message)
        lan = input_str
        if IBM_WATSON_CRED_URL is None or IBM_WATSON_CRED_PASSWORD is None:
            await message.edit("`no ibm watson key provided, aborting...`")
            await sleep(3)
            await message.delete()
        else:
            headers = {
                "Content-Type": message.reply_to_message.voice.mime_type,
            }
            data = open(required_file_name, "rb").read()
            response = requests.post(
                IBM_WATSON_CRED_URL + "/v1/recognize",
                headers=headers,
                data=data,
                auth=("apikey", IBM_WATSON_CRED_PASSWORD)
            )
            r = response.json()
            if "results" in r:
                # process the json to appropriate string format
                results = r["results"]
                transcript_response = ""
                transcript_confidence = ""
                for alternative in results:
                    alternatives = alternative["alternatives"][0]
                    transcript_response += " " + \
                        str(alternatives["transcript"]) + " + "
                    transcript_confidence += " " + \
                        str(alternatives["confidence"]) + " + "
                end = datetime.now()
                ms = (end - start).seconds
                if transcript_response != "":
                    string_to_show = f"Language: `{lan}`\nTRANSCRIPT: `{transcript_response}`\nTime Taken: {ms} seconds\nConfidence: `{transcript_confidence}`"
                else:
                    string_to_show = f"Language: `{lan}`\nTime Taken: {ms} seconds\n**No Results Found**"
                await message.edit(string_to_show)
            else:
                await message.edit(r["error"])
            # now, remove the temporary file
            os.remove(required_file_name)
    else:
        await message.edit("`Reply to a voice message`")
        await sleep(3)
        await message.delete()