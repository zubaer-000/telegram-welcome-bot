import os
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

# =============== CONSTANTS & TEXTS ===============
def get_private_welcome_text(name):
    return (
        f"হ্যালো {name}! স্বাগতম আমাদের পরিবারে। ❤️\n\n"
        "তুমি **তার্কিকে** যুক্ত হতে চাও? তাহলে নিচের লিংকে গিয়ে লেভেল ১ এবং ২ এর প্লেলিস্ট দেখে শিখে ফেলো সব এবং ছোট পরীক্ষা দিয়ে দাও।\n\n"
        "🔗 তার্কিকের লিঙ্ক: https://tss-tarkik.blogspot.com/\n\n"
        "তুমি **বায়োব্রিজে** যুক্ত হতে চাও? তাহলে তো সেরা!\n\n"
        "🔗 লিঙ্ক: https://tss-bio-bridge.blogspot.com/\n\n"
        "কোনো প্রশ্ন বা সাহায্য লাগলে গ্রুপে জানিও!"
    )

# =============== AUTO-DELETE HELPER ===============
DELETE_AFTER_SECONDS = 6 * 60 * 60  # 6 hours

async def delete_message_later(context: ContextTypes.DEFAULT_TYPE):
    """Job callback: deletes a message using data stored in job context."""
    job = context.job
    chat_id = job.data["chat_id"]
    message_id = job.data["message_id"]
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"Could not delete message {message_id} in chat {chat_id}: {e}")

def schedule_delete(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
    """Schedule a message to be deleted after DELETE_AFTER_SECONDS."""
    context.application.job_queue.run_once(
        delete_message_later,
        when=DELETE_AFTER_SECONDS,
        data={"chat_id": chat_id, "message_id": message_id},
        name=f"delete_{chat_id}_{message_id}"
    )

# =============== TELEGRAM BOT LOGIC ===============

# 1. Handle /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "সদস্য"
    sent = await update.message.reply_text(get_private_welcome_text(name), parse_mode="Markdown")
    schedule_delete(context, sent.chat_id, sent.message_id)

# 2. Handle ANY text message sent to the bot privately
async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        user = update.effective_user
        name = user.first_name or "সদস্য"
        sent = await update.message.reply_text(
            f"তুমি লিখেছো: '{update.message.text}'\n\n" + get_private_welcome_text(name),
            parse_mode="Markdown"
        )
        schedule_delete(context, sent.chat_id, sent.message_id)

# 3. Handle Group Joins
async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        if user.id == context.bot.id:
            continue

        name = user.first_name or "সদস্য"
        bot_username = context.bot.username

        keyboard = [[InlineKeyboardButton("বিস্তারিত জানতে এখানে ক্লিক করো ✨", url=f"https://t.me/{bot_username}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        group_msg = (
            f" আমাদের পরিবারে সদস্য হিসেবে স্বাগতম তোমাকে, <b>{name}</b>! 🎉\n\n"
            "গ্রুপের উপরে পিন করা মেসেজগুলো একটু চেক করে দেখো।\n\n"
            "সব কিছু একসাথে জানতে নিচের বাটনে ক্লিক করে আমাকে মেসেজ দাও: 👇"
        )

        try:
            sent = await update.message.reply_text(group_msg, parse_mode="HTML", reply_markup=reply_markup)
            schedule_delete(context, sent.chat_id, sent.message_id)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        exit(1)

    threading.Thread(target=run_flask, daemon=True).start()

    # job_queue requires: pip install "python-telegram-bot[job-queue]"
    app = ApplicationBuilder().token(TOKEN).build()

    # --- HANDLERS ---
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE, handle_private_message))

    print("🤖 Bot is active and will now reply to ALL private messages!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
