import asyncio
from database import get_db, save_db
from handlers.admin import is_privileged
from handlers.welcome import delete_after

async def set_rule(update, context):
    db = get_db()
    if not is_privileged(update.effective_user.id, db):
        await update.message.reply_text("❌ Permission nahi hai.")
        return
    if not context.args:
        await update.message.reply_text("❌ Rules text do.")
        return
    db["rules"] = " ".join(context.args)
    save_db(db)
    await update.message.reply_text("✅ Rules save ho gaye.")

async def show_rule(update, context):
    db = get_db()
    group_ids = [db["groups"].get("group1"), db["groups"].get("group2")]
    if update.effective_chat.id not in group_ids:
        return
    if not db["rules"]:
        await update.message.reply_text("❌ Koi rule set nahi hai.")
        return
    sent = await update.message.reply_text(f"📋 Group Rules:\n\n{db['rules']}")
    asyncio.create_task(delete_after(context.bot, update.effective_chat.id, sent.message_id, 3600))