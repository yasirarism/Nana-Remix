import re

from pyrogram import Filters, Emoji
from pyrogram.errors import MessageNotModified

from nana import app, Command


heart = ['<3']
sad = [':(', '):', ':-(', ')-:']
laugh = ['xD']
kiss = [':*', ':-*']
neutral_face = [':|', '|:', ':-|', '|-:', ]


@app.on_message(~Filters.regex(r"^\.\w*") & Filters.me)
async def auto_emoji(_client, message):
    try:
        txt = None
        if message.caption:
            txt = message.caption
        elif message.text:
            txt = message.text

        for emoji in heart:
            txt = re.sub(emoji, Emoji.RED_HEART, txt, flags=re.IGNORECASE)    

        for emoji in sad:
            txt = re.sub(emoji, Emoji.CRYING_FACE, txt, flags=re.IGNORECASE)

        for emoji in laugh:
            txt = re.sub(emoji, Emoji.FACE_WITH_TEARS_OF_JOY, txt, flags=re.IGNORECASE)

        for emoji in kiss:
            txt = re.sub(emoji, Emoji.FACE_BLOWING_A_KISS, txt, flags=re.IGNORECASE)

        for emoji in neutral_face:
            txt = re.sub(emoji, Emoji.NEUTRAL_FACE, txt, flags=re.IGNORECASE)

        if message.caption:
            if txt != message.caption:
                await message.edit_caption(txt)
        elif message.text:
            if txt != message.text:
                await message.edit(txt)
    except MessageNotModified:
        return