import traceback
import sys
import os
import re
import subprocess

from pyrogram import Filters

from nana import Owner, logging, setbot
from nana.modules.devs import aexec


@setbot.on_message(Filters.user(Owner) & Filters.command(["py"]))
async def executor(client, message):
    if len(message.text.split()) == 1:
        await message.reply("Usage: `/py await message.reply('edited!')`")
        return
    args = message.text.split(None, 1)
    code = args[1]
    try:
        await aexec(client, message, code)
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
        await message.reply("**Execute**\n`{}`\n\n**Failed:**\n```{}```".format(code, "".join(errors)))
        logging.exception("Execution error")


@setbot.on_message(Filters.user(Owner) & Filters.command(["sh"]))
async def terminal(client, message):
    if len(message.text.split()) == 1:
        await message.reply("Usage: `/sh ping -c 5 google.com`")
        return
    args = message.text.split(None, 1)
    teks = args[1]
    if "\n" in teks:
        code = teks.split("\n")
        output = ""
        for x in code:
            shell = re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', x)
            try:
                process = subprocess.Popen(
                    shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except Exception as err:
                print(err)
                await message.reply("""
**Input:**
```{}```

**Error:**
```{}```
""".format(teks, err))
            output += "**{}**\n".format(code)
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    else:
        shell = re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', teks)
        for a in range(len(shell)):
            shell[a] = shell[a].replace('"', "")
        try:
            process = subprocess.Popen(
                shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
            await message.reply("""**Input:**\n```{}```\n\n**Error:**\n```{}```""".format(teks, "".join(errors)))
            return
        output = process.stdout.read()[:-1].decode("utf-8")
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            file = open("nana/cache/output.txt", "w+")
            file.write(output)
            file.close()
            await client.send_document(message.chat.id, "nana/cache/output.txt", reply_to_message_id=message.message_id,
                                       caption="`Output file`")
            os.remove("nana/cache/output.txt")
            return
        await message.reply("""**Input:**\n```{}```\n\n**Output:**\n```{}```""".format(teks, output))
    else:
        await message.reply("**Input: **\n`{}`\n\n**Output: **\n`No Output`".format(teks))