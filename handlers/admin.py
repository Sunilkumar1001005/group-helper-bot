from telegram import Update
from telegram.ext import ContextTypes
from database import get_db, save_db

async def _set_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, slot: str):
    db = get_db()
    uid = update.effective_user.id
    if uid != db["owner_id"]:
        await update.message.reply_text("❌ Sirf Owner ye command use kar sakta hai.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Kisi user ke message ko reply karo.")
        return
    target = update.message.reply_to_message.from_user
    db["admins"][slot] = {"id": target.id, "name": target.full_name, "username": target.username}
    save_db(db)
    await update.message.reply_text(f"✅ {target.full_name} ko {slot} banaya gaya.")

async def set_admin1(update, context):
    await _set_admin(update, context, "admin1")

async def set_admin2(update, context):
    await _set_admin(update, context, "admin2")

async def set_admin3(update, context):
    await _set_admin(update, context, "admin3")

def get_admin_ids(db):
    ids = []
    for slot in ["admin1", "admin2", "admin3"]:
        if db["admins"].get(slot):
            ids.append(db["admins"][slot]["id"])
    return ids

def is_privileged(user_id, db):
    return user_id == db["owner_id"] or user_id in get_admin_ids(db)