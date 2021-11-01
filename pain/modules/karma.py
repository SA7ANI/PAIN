# Ported From WilliamButcher Bot.
# Credits Goes to WilliamButcherBot
# Ported from https://github.com/TheHamkerCat/WilliamButcherBot

from typing import Dict, Union

from pyrogram import filters

from pain.modules.utils.karma import is_karma_on, karma_off, karma_on
from pain.services.mongo import db
from pain.services.pyrogram import pbot
from pain.services.pyrogram import pbot as app

karmadb = db.karma
karma_positive_group = 3
karma_negative_group = 4


async def int_to_alpha(user_id: int) -> str:
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    text = ""
    user_id = str(user_id)
    for i in user_id:
        text += alphabet[int(i)]
    return text


async def alpha_to_int(user_id_alphabet: str) -> int:
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    user_id = ""
    for i in user_id_alphabet:
        index = alphabet.index(i)
        user_id += str(index)
    user_id = int(user_id)
    return user_id


async def get_karmas_count() -> dict:
    chats = karmadb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return {}
    chats_count = 0
    karmas_count = 0
    for chat in await chats.to_list(length=1000000):
        for i in chat["karma"]:
            karmas_count += chat["karma"][i]["karma"]
        chats_count += 1
    return {"chats_count": chats_count, "karmas_count": karmas_count}


async def get_karmas(chat_id: int) -> Dict[str, int]:
    karma = await karmadb.find_one({"chat_id": chat_id})
    if karma:
        karma = karma["karma"]
    else:
        karma = {}
    return karma


async def get_karma(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    karmas = await get_karmas(chat_id)
    if name in karmas:
        return karmas[name]


async def update_karma(chat_id: int, name: str, karma: dict):
    name = name.lower().strip()
    karmas = await get_karmas(chat_id)
    karmas[name] = karma
    await karmadb.update_one(
        {"chat_id": chat_id}, {"$set": {"karma": karmas}}, upsert=True
    )


#permissions
async def member_permissions(chat_id, user_id):
    perms = []
    member = await pbot.get_chat_member(chat_id, user_id)
    if member.can_post_messages:
        perms.append("can_post_messages")
    if member.can_edit_messages:
        perms.append("can_edit_messages")
    if member.can_delete_messages:
        perms.append("can_delete_messages")
    if member.can_restrict_members:
        perms.append("can_restrict_members")
    if member.can_promote_members:
        perms.append("can_promote_members")
    if member.can_change_info:
        perms.append("can_change_info")
    if member.can_invite_users:
        perms.append("can_invite_users")
    if member.can_pin_messages:
        perms.append("can_pin_messages")
    return perms


async def current_chat_permissions(chat_id):
    perms = []
    perm = (await pbot.get_chat(chat_id)).permissions
    if perm.can_send_messages:
        perms.append("can_send_messages")
    if perm.can_send_media_messages:
        perms.append("can_send_media_messages")
    if perm.can_send_stickers:
        perms.append("can_send_stickers")
    if perm.can_send_animations:
        perms.append("can_send_animations")
    if perm.can_send_games:
        perms.append("can_send_games")
    if perm.can_use_inline_bots:
        perms.append("can_use_inline_bots")
    if perm.can_add_web_page_previews:
        perms.append("can_add_web_page_previews")
    if perm.can_send_polls:
        perms.append("can_send_polls")
    if perm.can_change_info:
        perms.append("can_change_info")
    if perm.can_invite_users:
        perms.append("can_invite_users")
    if perm.can_pin_messages:
        perms.append("can_pin_messages")

    return perms


regex_upvote = r"^((?i)\+|\+\+|\+1|thx|tnx|ty|thank you|thanx|thanks|pro|cool|good|👍)$"
regex_downvote = r"^(\-|\-\-|\-1|👎)$"


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_upvote)
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=karma_positive_group,
)
async def upvote(_, message):

    if not await is_karma_on(message.chat.id):
        return
    try:
        if message.reply_to_message.from_user.id == message.from_user.id:
            return
    except:
        return
    chat_id = message.chat.id
    try:
        user_id = message.reply_to_message.from_user.id
    except:
        return
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma + 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    else:
        karma = 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    await message.reply_text(
        f"Incremented Karma of {user_mention} By 1 \nTotal Points: {karma}"
    )


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_downvote)
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=karma_negative_group,
)
async def downvote(_, message):

    if not await is_karma_on(message.chat.id):
        return
    try:
        if message.reply_to_message.from_user.id == message.from_user.id:
            return
    except:
        return
    chat_id = message.chat.id
    try:
        user_id = message.reply_to_message.from_user.id
    except:
        return
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma - 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    else:
        karma = 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    await message.reply_text(
        f"Decremented Karma Of {user_mention} By 1 \nTotal Points: {karma}"
    )


@app.on_message(filters.command("karma") & filters.group)
async def karma(_, message):
    chat_id = message.chat.id
    if len(message.command) != 2:
        if not message.reply_to_message:
            karma = await get_karmas(chat_id)
            msg = f"**Karma list of {message.chat.title}:- **\n"
            limit = 0
            karma_dicc = {}
            for i in karma:
                user_id = await alpha_to_int(i)
                user_karma = karma[i]["karma"]
                karma_dicc[str(user_id)] = user_karma
                karma_arranged = dict(
                    sorted(karma_dicc.items(), key=lambda item: item[1], reverse=True)
                )
            for user_idd, karma_count in karma_arranged.items():
                if limit > 9:
                    break
                try:
                    user_name = (await app.get_users(int(user_idd))).username
                except Exception:
                    continue
                msg += f"{user_name} : `{karma_count}`\n"
                limit += 1
            await message.reply_text(msg)
        else:
            user_id = message.reply_to_message.from_user.id
            karma = await get_karma(chat_id, await int_to_alpha(user_id))
            if karma:
                karma = karma["karma"]
                await message.reply_text(f"**Total Points**: __{karma}__")
            else:
                karma = 0
                await message.reply_text(f"**Total Points**: __{karma}__")
        return
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    user_id = message.from_user.id
    permissions = await member_permissions(chat_id, user_id)
    if "can_change_info" not in permissions:
        await message.reply_text("You don't have enough permissions.")
        return
    if status == "on" or status == "ON":
        await karma_on(chat_id)
        await message.reply_text(
            f"Added Chat {chat_id} To Database. Karma will be enabled here"
        )
    elif status == "off" or status == "OFF":
        await karma_off(chat_id)
        await message.reply_text(
            f"Removed Chat {chat_id} To Database. Karma will be disabled here"
        )


__mod_name__ = "Karma"

__help__ = """
Use this feature gives karma points to user's in your group!

<b>[UPVOTE]</b> - Use upvote keywords like "+", "+1", "thanks" etc to upvote a cb.message.
<b>[DOWNVOTE]</b> - Use downvote keywords like "-", "-1", etc to downvote a cb.message.

- /karma [ON/OFF]: Enable/Disable karma in group. 
- /karma [Reply to a message]: Check user's karma
- /karma: Chek karma list of top 10 users
"""