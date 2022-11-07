
import random
import string
from pyrogram import Client, filters
from pyrogram import types
import datetime
import time
from database.broadcast_db import get_broadcast_info, new_broadcast, update_broadcast
from database.users_chats_db import db
from info import ADMINS, LOG_CHANNEL
from utils import broadcast_messages

broadcast_ids = {} 


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def verupikkals(bot, message: types.Message):
    try:
        await main_broadcast_handler(message)
    except Exception as e:
        print(e)

@Client.on_message(filters.command("stop_broadcast") & filters.user(ADMINS))
async def verupikkals(bot, message: types.Message):
    cmd = message.command
    if len(cmd) == 1:
        return await message.reply("`/stop_broadcast broadcast_id`")
    elif len(cmd) == 2:
        broadcast_id = cmd[1]
        await update_broadcast(broadcast_id=broadcast_id, value={"ongoing": False})
        await message.reply("Broadcast has been Stopped")

async def resume_broadcast(c: Client, broadcast_id):
    info = await get_broadcast_info(broadcast_id)

    if info["ongoing"]:
        try:
            chat_id = info["chat_id"]
            msg_id = info["broadcast_message_id"]
            broadcast_message = await c.get_messages(chat_id, msg_id)
            broadcast_message = await broadcast_message.copy(LOG_CHANNEL)
            await broadcast_message.reply(f"Resuming this broadcast.... from {info['total_users_done']} user")
            message = await broadcast_message.reply(f"/broadcast {info['total_users']}")
            message.command = ["broadcast", info['total_users']]
            await main_broadcast_handler(message, info['total_users_done'],new_b=False,broadcast_id=broadcast_id)
        except Exception as e:
            print(e)

async def main_broadcast_handler(message: types.Message, offset: int = 0, new_b=True, broadcast_id=None):
    users = await db.get_all_users(offset=offset)
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )
    
    if new_b:
        while True:
            broadcast_id = ''.join([random.choice(string.ascii_letters) for _ in range(3)])
            if not broadcast_ids.get(broadcast_id):
                break

    start_time = time.time()

    cmd = message.command or []
    total_users = int(cmd[1]) if len(cmd)==2 else await db.total_users_count()
    done = offset
    blocked = 0
    deleted = 0
    failed =0
    success = 0

    if new_b:
        await new_broadcast(broadcast_id, total_users, b_msg.id, b_msg.chat.id)


    async for user in users:
        pti, sh = await broadcast_messages(int(user['id']), b_msg)
        if pti:
            success += 1
        elif sh == "Blocked":
            blocked+=1
        elif sh == "Deleted":
            deleted += 1
        elif sh == "Error":
            failed += 1
        done += 1
        if not done % 20:
            
            info = await get_broadcast_info(broadcast_id)
            if not info["ongoing"]:
                break

            await sts.edit(f"ID: `{broadcast_id}`\nBroadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}") 
            await update_broadcast(broadcast_id, {"total_users_done": done})

        if done >= total_users:
            break

    try:
        await update_broadcast(broadcast_id, {"ongoing": False, "total_users_done": done})
    except Exception as e:
        print(e)
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"ID: `{broadcast_id}`\nBroadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
