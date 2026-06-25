from datetime import datetime
from telegram import ChatPermissions
from database import get_db, save_db

async def unmute_expired(bot):
    db = get_db()
    now = datetime.utcnow()
    to_remove = []
    for uid, record in db["mutes"].items():
        until = datetime.fromisoformat(record["until"])
        if now >= until:
            try:
                await bot.restrict_chat_member(
                    record["chat_id"], int(uid),
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True
                    )
                )
            except:
                pass
            to_remove.append(uid)
    for uid in to_remove:
        del db["mutes"][uid]
    if to_remove:
        save_db(db)