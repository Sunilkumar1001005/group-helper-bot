import re
import asyncio
from datetime import datetime, timedelta
from telegram import ChatPermissions
from database import get_db, save_db
from handlers.admin import is_privileged

LINK_PATTERN = re.compile(
    r"(https?://|t\.me/|telegram\.me/)", re.IGNORECASE
)

async def check_link(update, context):
    db = get_db()
    msg = update.message
    if not msg or not msg.text:
        return

    group_ids = [db["groups"].get("group1"), db["groups"].get("group2")]
    if msg.chat.id not in group_ids:
        return

    user = msg.from_user
    if is_privileged(user.id, db):
        return

    # Check group admin
    member = await context.bot.get_chat_member(msg.chat.id, user.id)
    if member.status in ["administrator", "creator"]:
        return

    if LINK_PATTERN.search(msg.text):
        await msg.delete()
        mute_until = datetime.utcnow() + timedelta(hours=6)
        try:
            await context.bot.restrict_chat_member(
                msg.chat.id, user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=mute_until
            )
        except:
            pass

        # Save mute record
        uid = str(user.id)
        db["mutes"][uid] = {
            "chat_id": msg.chat.id,
            "until": mute_until.isoformat()
        }
        # Track links deleted
        for gkey in ["group1", "group2"]:
            if db["groups"].get(gkey) == msg.chat.id:
                db["daily_stats"][gkey]["links_deleted"] += 1
        save_db(db)