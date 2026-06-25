import random
import asyncio
from telegram import Update, ChatMemberUpdated
from telegram.ext import ContextTypes
from database import get_db, save_db
from handlers.admin import is_privileged

async def _set_welcome(update, context, slot):
    db = get_db()
    if not is_privileged(update.effective_user.id, db):
        return
    if not context.args:
        await update.message.reply_text("❌ Welcome message text do.\nExample: /welcome Swagat hai {fullname}!")
        return
    msg = " ".join(context.args)
    db["welcome_messages"][slot] = msg
    save_db(db)
    await update.message.reply_text(f"✅ {slot} set ho gaya.")

async def set_welcome1(update, context): await _set_welcome(update, context, "w1")
async def set_welcome2(update, context): await _set_welcome(update, context, "w2")
async def set_welcome3(update, context): await _set_welcome(update, context, "w3")

async def on_member_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result: ChatMemberUpdated = update.chat_member
    if result is None:
        return
    old = result.old_chat_member
    new = result.new_chat_member

    # Only trigger on join
    if old.status in ["left", "kicked"] and new.status == "member":
        db = get_db()
        group_ids = [db["groups"].get("group1"), db["groups"].get("group2")]
        if result.chat.id not in group_ids:
            return

        user = new.user
        uid = str(user.id)

        # Track join count
        db["join_counts"][uid] = db["join_counts"].get(uid, 0) + 1
        save_db(db)

        # Track in daily stats
        for gkey in ["group1", "group2"]:
            if db["groups"].get(gkey) == result.chat.id:
                db["daily_stats"][gkey]["new_members"] += 1
                save_db(db)

        # Track user
        db["users"][uid] = {
            "id": user.id,
            "name": user.full_name,
            "username": user.username,
            "is_bot": user.is_bot
        }
        save_db(db)

        # Pick random welcome
        msgs = [v for v in db["welcome_messages"].values() if v]
        if not msgs:
            return

        msg_template = random.choice(msgs)
        username = f"@{user.username}" if user.username else "-"
        join_count = db["join_counts"][uid]
        text = msg_template.replace("{fullname}", user.full_name)
        text = text.replace("{username}", username)
        text = text.replace("{id}", str(user.id))
        text = text.replace("{join_count}", str(join_count))

        sent = await context.bot.send_message(result.chat.id, text)

        # Auto-delete after 1 hour
        asyncio.create_task(delete_after(context.bot, result.chat.id, sent.message_id, 3600))

async def delete_after(bot, chat_id, msg_id, delay):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, msg_id)
    except:
        pass