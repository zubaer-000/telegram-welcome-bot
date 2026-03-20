import os
import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# =============== FLASK HEALTH CHECK ===============
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is alive and running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# =============== AUTO-DELETE LOGIC ===============

async def delete_message_job(context: ContextTypes.DEFAULT_TYPE):
    """This function runs after the timer expires"""
    job = context.job
    try:
        await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data)
        print(f"🗑️ Auto-deleted message {job.data} in chat {job.chat_id}")
    except Exception as e:
        print(f"⚠️ Could not delete message: {e}")

# =============== TEXT LOGIC ===============
def get_welcome_text(name):
    return (
        f"হ্যালো {name}! স্বাগতম আমাদের পরিবারে। ❤️\n\n"
        "🔗 তার্কিকের লিঙ্ক: https://tss-tarkik.blogspot.com/\n"
        "🔗 বায়োব্রিজ লিঙ্ক: https://tss-bio-bridge.blogspot.com/\n\n"
        "কোনো সাহায্য লাগলে গ্রুপে জানিও!"
    )

# =============== BOT HANDLERS ===============

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(get_welcome_text(user.first_name), parse_mode="Markdown")

async def group_join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
    
    for user in update.message.new_chat_members:
        if user.id == context.bot.id: continue
        
        name = user.first_name or "সদস্য"
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("বিস্তারিত জানুন ✨", url=f"https://t.me/{context.bot.username}")]])
        
        # Send the message
        sent_message = await update.message.reply_text(
            f"স্বাগতম <b>{name}</b>! আমাদের পরিবারে যুক্ত হওয়ার জন্য ধন্যবাদ। সব জানতে নিচের বাটনে ক্লিক করো: 👇",
            reply_markup=btn,
            parse_mode="HTML"
        )

        # SCHEDULE DELETE: 6 hours = 6 * 60 * 60 seconds
        delete_time = 6 * 60 * 60 
        
        context.job_queue.run_once(
            delete_message_job, 
            when=delete_time, 
            chat_id=update.effective_chat.id, 
            data=sent_message.message_id
        )
        print(f"🕒 Scheduled deletion for message {sent_message.message_id} in {delete_time} seconds.")

# =============== MAIN STARTUP ===============

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        exit(1)

    threading.Thread(target=run_flask, daemon=True).start()

    # Build Bot with Job Queue enabled
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, start_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_join_handler))

    print("✅ BOT IS LIVE with 6-hour Auto-Delete enabled!")
    app.run_polling(drop_pending_updates=True)
