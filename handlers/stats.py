from database import get_db

async def show_stats(update, context):
    db = get_db()
    if update.effective_user.id != db["owner_id"]:
        return

    users = db.get("users", {})
    total = len(users)
    bots = sum(1 for u in users.values() if u.get("is_bot"))
    deleted = sum(1 for u in users.values() if not u.get("name"))
    active = total - deleted - bots

    admins = db.get("admins", {})
    admin_lines = []
    admin_count = 0
    for slot, a in admins.items():
        if a:
            admin_count += 1
            uname = f"@{a['username']}" if a.get("username") else "-"
            admin_lines.append(f"  {slot}: {a['name']} | {uname} | {a['id']}")

    groups = db.get("groups", {})
    group_lines = []
    total_groups = 0
    for gkey, gid in groups.items():
        if gid:
            total_groups += 1
            try:
                chat = await context.bot.get_chat(gid)
                count = await context.bot.get_chat_member_count(gid)
                group_lines.append(f"  {gkey}: {chat.title} | ID: {gid} | Members: {count}")
            except:
                group_lines.append(f"  {gkey}: ID {gid} (fetch failed)")

    text = f"""📊 Bot Statistics

👥 Total Users: {total}
✅ Active Users: {active}
🤖 Total Bots: {bots}
🗑 Deleted Accounts: {deleted}

🏘 Total Groups: {total_groups}
{''.join([chr(10)+g for g in group_lines])}

👮 Admin Count: {admin_count}
{''.join([chr(10)+a for a in admin_lines])}
"""
    await context.bot.send_message(db["owner_id"], text)