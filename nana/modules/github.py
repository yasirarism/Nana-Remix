import aiohttp
import aiofiles
import git
from pyrogram import Filters
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
import asyncio
import datetime
import os
from asyncio import sleep
from glob import iglob
from random import randint

from pyrogram import Filters

from nana import app, Command
from nana.helpers.PyroHelpers import ReplyCheck
from nana.helpers.aiohttp_helper import AioHttp

__MODULE__ = "Github"
__HELP__ = """
This module can help you find information about a github user!

──「 **Github User Info** 」──
-> `git (username)`
Finding information about a github user.

──「 **Github Graph** 」──
-> `ggraph (username)` or `commitgraph (username)`
Output a user's Commit Graph.

"""

@app.on_message(Filters.me & Filters.command("git", Command))
async def github(_client, message):
    if len(message.text.split()) == 1:
            await message.edit("Usage: `git (username)`")
            return
    username = message.text.split(None, 1)[1]
    URL = f"https://api.github.com/users/{username}"
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as request:
            if request.status == 404:
                return await message.edit("`" + username +
                                        " not found`")

            result = await request.json()

            url = result.get("html_url", None)
            name = result.get("name", None)
            company = result.get("company", None)
            bio = result.get("bio", None)
            created_at = result.get("created_at", "Not Found")

            REPLY = (
                f"**GitHub Info for `{username}**`"
                f"\n**Username:** `{name}`\n**Bio:** `{bio}`\n**URL:** {url}"
                f"\n**Company:** `{company}`\n**Created at:** `{created_at}`"
                f"\n**Repository:** [Link](https://github.com/{username}?tab=repositories)"
            )

            await message.edit(REPLY)


@app.on_message(Filters.command(['ggraph', 'commitgraph'], Command) & Filters.me)
async def commit_graph(client, message):
    if len(message.command) < 2:
        await message.edit("Please provide a github profile username to generate the graph!")
        await sleep(2)
        await message.delete()
        return
    else:
        git_user = message.command[1]

    url = f"https://ghchart.rshah.org/{git_user}"
    file_name = f"{randint(1, 999)}{git_user}"

    resp = await AioHttp.get_raw(url)
    f = await aiofiles.open(f"{file_name}.svg", mode='wb')
    await f.write(resp)
    await f.close()

    try:
        drawing = svg2rlg(f"{file_name}.svg")
        renderPM.drawToFile(drawing, f"{file_name}.png")
    except UnboundLocalError:
        await message.edit("Username does not exist!")
        await sleep(2)
        await message.delete()
        return

    await asyncio.gather(
        client.send_photo(
            chat_id=message.chat.id,
            photo=f"{file_name}.png",
            caption=git_user,
            reply_to_message_id=ReplyCheck(message)
        ),
        message.delete()
    )

    for file in iglob(f"{file_name}.*"):
        os.remove(file)