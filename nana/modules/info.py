from datetime import datetime
from time import sleep

from pyrogram import Filters, User
from pyrogram.api import functions
from pyrogram.errors import PeerIdInvalid

from nana import app, Command
from nana.helpers.PyroHelpers import ReplyCheck

__MODULE__ = "Whois"
__HELP__ = """
──「 **Whois** 」──
-> `info` `@username` or `user_id`
-> `info` "reply to a text"
To find information about a person.

"""

WHOIS = (
    "**About {first_name}**:\n"
    " - **UserID**: `{user_id}`\n"
    " - **First Name**: `{first_name}`\n"
    " - **Last Name**: `{last_name}`\n"
    " - **Username**: `{username}`\n"
    " - **Last Online**: `{last_online}`\n"
    " - **Common Groups**: `{common_groups}`\n"
    " - **Contact**: `{is_contact}`\n"
    " - **Profile**: [link](tg://user?id={user_id})\n"
    )


def LastOnline(user: User):
    if user.is_bot:
        return ""
    elif user.status == 'recently':
        return "Recently"
    elif user.status == 'within_week':
        return "Within the last week"
    elif user.status == 'within_month':
        return "Within the last month"
    elif user.status == 'long_time_ago':
        return "A long time ago :("
    elif user.status == 'online':
        return "Currently Online"
    elif user.status == 'offline':
        return datetime.fromtimestamp(user.status.date).strftime("%a, %d %b %Y, %H:%M:%S")


async def GetCommon(client, get_user):
    common = await client.send(
        functions.messages.GetCommonChats(
            user_id=await client.resolve_peer(get_user),
            max_id=0,
            limit=0))
    return common


def FullName(user: User):
    return user.first_name + " " + user.last_name if user.last_name else user.first_name


def ProfilePicUpdate(user_pic):
    return datetime.fromtimestamp(user_pic[0].date).strftime("%d.%m.%Y, %H:%M:%S")


@app.on_message(Filters.me & Filters.command("info", Command))
async def whois(client, message):
    cmd = message.command
    if not message.reply_to_message and len(cmd) == 1:
        get_user = message.from_user.id
    elif message.reply_to_message and len(cmd) == 1:
        if message.reply_to_message.forward_from:
            get_user = message.reply_to_message.forward_from.id
        else:
            get_user = message.reply_to_message.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]
        try:
            get_user = int(cmd[1])
        except ValueError:
            pass
    try:
        user = await client.get_users(get_user)
    except PeerIdInvalid:
        await message.edit("I don't know that User.")
        sleep(2)
        await message.delete()
        return
    desc = await client.get_chat(get_user)
    desc = desc.description
    common = await GetCommon(client, user.id)

    if user:
        await message.edit(
            WHOIS.format(
                full_name=FullName(user),
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name if user.last_name else "",
                username=user.username if user.username else "",
                last_online=LastOnline(user),
                common_groups=len(common.chats),
                is_contact=user.is_contact),
            disable_web_page_preview=True)