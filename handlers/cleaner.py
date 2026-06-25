from database import get_db

async def clean_service_msg(update, context):
    db = get_db()
    msg = update.message
    if not msg:
        return
    group_ids = [db["groups"].get("group1"), db["groups"].get("group2")]
    if msg.chat.id not in group_ids:
        return
    try:
        await msg.delete()
    except:
        pass