import re
from datetime import datetime, timedelta
from telegram import ChatPermissions
from database import get_db, save_db
from handlers.admin import is_privileged

TAG_PATTERN = re.compile(r"@\w+")

async def check_tag(update, context):
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

    member = await context.bot.get_chat_member(msg.chat.id, user.id)
    if member.status in ["administrator", "creator"]:
        return

    if TAG_PATTERN.search(msg.text):
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

        uid = str(user.id)
        db["mutes"][uid] = {
            "chat_id": msg.chat.id,
            "until": mute_until.isoformat()
        }
        save_db(db)