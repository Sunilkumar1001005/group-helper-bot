import logging
import os
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ChatMemberHandler, filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

from config import OWNER_ID
from database import get_db, save_db
from handlers.admin import (
    set_admin1, set_admin2, set_admin3
)
from handlers.welcome import (
    set_welcome1, set_welcome2, set_welcome3, on_member_join
)
from handlers.rules import set_rule, show_rule
from handlers.antilink import check_link
from handlers.antitag import check_tag
from handlers.cleaner import clean_service_msg
from handlers.stats import show_stats
from handlers.daily_report import send_daily_report
from handlers.mute_manager import unmute_expired

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def set_group1(update, context):
    db = get_db()
    if update.effective_user.id != db["owner_id"]:
        return
    db["groups"]["group1"] = update.effective_chat.id
    save_db(db)
    await update.message.reply_text(f"Group1 set: {update.effective_chat.id}")

async def set_group2(update, context):
    db = get_db()
    if update.effective_user.id != db["owner_id"]:
        return
    db["groups"]["group2"] = update.effective_chat.id
    save_db(db)
    await update.message.reply_text(f"Group2 set: {update.effective_chat.id}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Group setup
    app.add_handler(CommandHandler("setgroup1", set_group1))
    app.add_handler(CommandHandler("setgroup2", set_group2))

    # Admin commands
    app.add_handler(CommandHandler("admin", set_admin1))
    app.add_handler(CommandHandler("admin2", set_admin2))
    app.add_handler(CommandHandler("admin3", set_admin3))

    # Welcome
    app.add_handler(CommandHandler("welcome", set_welcome1))
    app.add_handler(CommandHandler("welcome2", set_welcome2))
    app.add_handler(CommandHandler("welcome3", set_welcome3))
    app.add_handler(ChatMemberHandler(on_member_join, ChatMemberHandler.CHAT_MEMBER))

    # Rules
    app.add_handler(CommandHandler("setrule", set_rule))
    app.add_handler(CommandHandler("rule", show_rule))

    # Stats
    app.add_handler(CommandHandler("stats", show_stats))

    # Service message cleaner
    app.add_handler(MessageHandler(filters.StatusUpdate.ALL, clean_service_msg))

    # Anti-link + Anti-tag (order matters)
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, check_link))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, check_tag))

    # Scheduler
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Kolkata"))
    scheduler.add_job(send_daily_report, "cron", hour=6, minute=0, args=[app.bot])
    scheduler.add_job(unmute_expired, "interval", minutes=5, args=[app.bot])
    scheduler.start()

    app.run_polling(allowed_updates=["message", "chat_member", "my_chat_member"])

if __name__ == "__main__":
    main()