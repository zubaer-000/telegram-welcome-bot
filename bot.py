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
# ⚠️ DIAGNOSTIC MODE: set to 30 seconds for testing
DELETE_AFTER_SECONDS = 30  # Change to 6 * 60 * 60 for production

async def delete_message_later(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data["chat_id"]
    message_id = job.data["message_id"]
    print(f"[DELETE JOB FIRED] Attempting to delete message_id={message_id} in chat_id={chat_id}")
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        print(f"[DELETE SUCCESS] message_id={message_id} deleted from chat_id={chat_id}")
    except Exception as e:
        print(f"[DELETE FAILED] message_id={message_id} chat_id={chat_id} | Reason: {e}")

def schedule_delete(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
    job_queue = context.application.job_queue
    if job_queue is None:
        print(f"[SCHEDULE ERROR] job_queue is None! Job-queue extra not installed properly.")
        return
    job = job_queue.run_once(
        delete_message_later,
        when=DELETE_AFTER_SECONDS,
        data={"chat_id": chat_id, "message_id": message_id},
        name=f"delete_{chat_id}_{message_id}"
    )
    print(f"[SCHEDULED] message_id={message_id} in chat_id={chat_id} will be deleted in {DELETE_AFTER_SECONDS}s | job={job}")

# =============== TELEGRAM BOT LOGIC ===============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "সদস্য"
    print(f"[/start] from user_id={user.id} name={name}")
    sent = await update.message.reply_text(get_private_welcome_text(name), parse_mode="Markdown")
    print(f"[/start] sent message_id={sent.message_id} in chat_id={sent.chat_id}")
    schedule_delete(context, sent.chat_id, sent.message_id)

async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        user = update.effective_user
        name = user.first_name or "সদস্য"
        print(f"[PRIVATE MSG] from user_id={user.id} text='{update.message.text}'")
        sent = await update.message.reply_text(
            f"তুমি লিখেছো: '{update.message.text}'\n\n" + get_private_welcome_text(name),
            parse_mode="Markdown"
        )
        print(f"[PRIVATE MSG] sent message_id={sent.message_id} in chat_id={sent.chat_id}")
        schedule_delete(context, sent.chat_id, sent.message_id)

async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        if user.id == context.bot.id:
            continue

        name = user.first_name or "সদস্য"
        bot_username = context.bot.username
        print(f"[GROUP JOIN] user_id={user.id} name={name} in chat_id={update.message.chat_id}")

        keyboard = [[InlineKeyboardButton("বিস্তারিত জানতে এখানে ক্লিক করো ✨", url=f"https://t.me/{bot_username}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        group_msg = (
            f"👋 আমাদের পরিবারে সদস্য হিসেবে স্বাগতম তোমাকে, <b>{name}</b>! 🎉\n\n"
            "গ্রুপের উপরে পিন করা মেসেজগুলো একটু চেক করে দেখো।\n\n"
            "সব কিছু একসাথে জানতে নিচের বাটনে ক্লিক করে আমাকে মেসেজ দাও: 👇"
        )

        try:
            sent = await update.message.reply_text(group_msg, parse_mode="HTML", reply_markup=reply_markup)
            print(f"[GROUP JOIN] sent message_id={sent.message_id} in chat_id={sent.chat_id}")
            schedule_delete(context, sent.chat_id, sent.message_id)
        except Exception as e:
            print(f"[GROUP JOIN ERROR] {e}")

# =============== STARTUP DIAGNOSTIC ===============
async def post_init(application):
    jq = application.job_queue
    print(f"[STARTUP] job_queue = {jq}")
    if jq is None:
        print("[STARTUP WARNING] ❌ job_queue is None — install python-telegram-bot[job-queue]")
    else:
        print("[STARTUP] ✅ job_queue is active")
        # Schedule a test self-delete diagnostic job at startup
        async def _test_job(ctx):
            print("[TEST JOB FIRED] ✅ job_queue is working correctly!")
        jq.run_once(_test_job, when=5, name="startup_test")
        print("[STARTUP] Test job scheduled — watch for '[TEST JOB FIRED]' in 5 seconds")

# =============== MAIN ===============
def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("[FATAL] BOT_TOKEN not set")
        exit(1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    threading.Thread(target=run_flask, daemon=True).start()

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    print(f"[STARTUP] job_queue at build time = {app.job_queue}")

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE, handle_private_message))

    print("🤖 Bot is active and will now reply to ALL private messages!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
