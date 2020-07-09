from asyncio import sleep
import subprocess
import os

from nana import setbot, app, Command, Owner
from pyrogram import Filters
from nana.modules.downloads import download_reply_nocall
from nana.helpers.PyroHelpers import ReplyCheck

__MODULE__ = "Video Note"
__HELP__ = """
Video Note Maker
──「 **VN Maker** 」──
-> `mkvn`
Reply a video to make it as video note
"""


@app.on_message(Filters.me & Filters.command(["mkvn"], Command))
async def vn_maker(client, message):
	if message.reply_to_message and message.reply_to_message.video and message.reply_to_message.animation:
		dlvid = await download_reply_nocall(client, message)
		if dlvid:
			await message.edit("__Converting...__")
			try:
				subprocess.Popen("ffmpeg", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			except Exception as err:
				if "The system cannot find the file specified" in str(err) or "No such file or directory" in str(err):
					await message.edit("an error occured! check assistant for more details")
					await sleep(5)
					await message.delete()
					await setbot.send_message(
                        Owner,
                        "Hello 🙂\nYou need to install ffmpeg to make audio works better"
                    )
					return
			os.system(
                f'''ffmpeg -loglevel panic -i "{dlvid}" -vf scale="'if(gt(iw,ih),-1,299):if(gt(iw,ih),299,-1)', crop=299:299" -strict -2 -y "{dlvid}_converted.mp4"'''
                )
			await client.send_video_note(message.chat.id,
                                        f"{dlvid}_converted.mp4",
                                        reply_to_message_id=ReplyCheck(message)
                                    )
			await message.delete()
			os.remove(dlvid)
			os.remove(dlvid+"_converted.mp4")
	else:
		await message.edit("`reply to a video to convert`")
