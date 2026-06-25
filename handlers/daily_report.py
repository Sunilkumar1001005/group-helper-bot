from datetime import datetime
import pytz
from database import get_db, save_db

DEFAULT_STATS = {"new_members": 0, "left_members": 0, "messages": 0, "links_deleted": 0}

async def send_daily_report(bot):
    db = get_db()
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz).strftime("%d %B %Y")

    for gkey in ["group1", "group2"]:
        gid = db["groups"].get(gkey)
        if not gid:
            continue
        stats = db["daily_stats"].get(gkey, DEFAULT_STATS)
        try:
            chat = await bot.get_chat(gid)
            name = chat.title
        except:
            name = gkey

        report = f"""📅 Daily Activity Report

Date: {now}
Group: {name}

➕ New Members: {stats['new_members']}
➖ Left Members: {stats['left_members']}
💬 Messages Sent: {stats['messages']}
🔗 Links Deleted: {stats['links_deleted']}
"""
        try:
            await bot.send_message(gid, report)
        except:
            pass

        # Reset stats
        db["daily_stats"][gkey] = dict(DEFAULT_STATS)

    save_db(db)