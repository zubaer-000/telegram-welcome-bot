import os
import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import re

# =============== FLASK HEALTH CHECK ===============
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is alive and running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# =============== CONSTANTS & TEXTS ===============
import html
def escape_markdown(text):
    return re.sub(r'([_*[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def get_private_welcome_text(name):
    # html.escape is better for HTML mode than a custom regex
    name = html.escape(name)
    
    lines = [
        f"🌟 <b>TSS MEGA GUIDE</b> 🌟",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"👋 হ্যালো <b>{name}</b>!",
        f"স্বাগতম ঠাকুরগাঁও সায়েন্স সোসাইটির পরিবারে ❤️",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"🌿 <b>TSS::Bio-Bridge</b> 🌿",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"🔬 জীববিজ্ঞান নিয়ে কাজ করার সেকশন",
        f"",
        f"📌 Biolympo অলিম্পিয়াডে অংশগ্রহণ করতে পারবে",
        f"📚 সিলেবাসভিত্তিক প্রস্তুতি কন্টেন্ট পাওয়া যাবে",
        f"",
        f"🌐 Website:",
        f"https://tss-bio-bridge.blogspot.com",
        f"",
        f"📢 Telegram Channels:",
        f"🔹 Level-1 (৬ষ্ঠ–৮ম):",
        f"https://t.me/+ITrndBAZKCI2YWM1",
        f"",
        f"🔹 Level-2 (৯ম–১০ম):",
        f"https://t.me/+odcmO_NmEU1kMzdl",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"⚡️ <b>TSS::GigaHertz</b> ⚡️",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"🏫 School-level Volunteer Group",
        f"",
        f"📌 কাজ:",
        f"▪️ TSS event প্রচারণা",
        f"▪️ স্কুলে কার্যক্রম পরিচালনা",
        f"▪️ ভলান্টিয়ার হিসেবে কাজ",
        f"",
        f"📋 Member List:",
        f"https://tss-member-list.blogspot.com",
        f"",
        f"📝 Join Form:",
        f"https://tss-membership.blogspot.com",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f" <b>TSS::III (Triple I)</b> ",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"🔍 অলিম্পিয়াড তথ্য ও প্রস্তুতির হাব",
        f"",
        f"🌐 Main Website:",
        f"https://tss-triple-eye.blogspot.com/",
        f"",
        f"📅 Deadlines:",
        f"https://tss-reg-deadline.blogspot.com",
        f"",
        f"📖 Olympiad Info:",
        f"https://tss-olympiad-list.blogspot.com",
        f"https://tss-olympiad-details.blogspot.com",
        f"",
        f"💡 Resources:",
        f"https://tss-olympiad-resource.blogspot.com",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"💻 <b>TSS::CodeBase</b> 💻",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"🚀 Competitive Programming Community",
        f"",
        f"📌 শিখবে:",
        f"▪️ C++ Programming",
        f"▪️ Problem Solving",
        f"▪️ Contest & Leaderboard",
        f"",
        f"📢 Telegram Channel:",
        f"https://t.me/+vDuAwXCegvA",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"🎙 <b>TSS::Tarkik</b> 🎙",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"🗣️ Debate Section",
        f"",
        f"📌 শিখবে:",
        f"▪️ সনাতনী বিতর্ক",
        f"▪️ সংসদীয় বিতর্ক",
        f"",
        f"🌐 Website:",
        f"https://tss-tarkik.blogspot.com/?m=1#home",
        f"",
        f"📢 Telegram (Level 1 & 2):",
        f"https://t.me/addlist/dcz-1OtBDdl",
        f"",
        f"📌 Level System:",
        f"🔹 Level 1 → সনাতনী বিতর্ক + পরীক্ষা",
        f"🔹 Level 2 → সংসদীয় বিতর্ক + পরীক্ষা",
        f"🔹 Level 3 → Advanced Entry",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"💬 <b>শেষ কথা</b>",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"🔥 তুমি যে সেকশনেই আগ্রহী হও — আজই শুরু করো!",
        f"📢 কোনো সাহায্য লাগলে অবশ্যই জানাবে",
        f"",
        f"✨ Learn • Grow • Shine with TSS ✨"
    ]
    return "\n".join(lines)
    
# =============== AUTO-DELETE HELPER ===============
# ⚠️ DIAGNOSTIC MODE: set to 30 seconds for testing
DELETE_AFTER_SECONDS = 2 * 60 * 60  # Change to 6 * 60 * 60 for production

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
    # Change parse_mode to HTML
    sent = await update.message.reply_text(get_private_welcome_text(name), parse_mode="HTML")
    schedule_delete(context, sent.chat_id, sent.message_id)

async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        user = update.effective_user
        name = user.first_name or "সদস্য"
        
        # Use html.escape for the user's input to avoid breaking tags
        user_text = html.escape(update.message.text) if update.message.text else ""

        # Change parse_mode to HTML
        sent = await update.message.reply_text(
            f"তুমি লিখেছো: '<b>{user_text}</b>'\n\n" + get_private_welcome_text(name),
            parse_mode="HTML"
        )
        

async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        if user.id == context.bot.id:
            continue

        name = user.first_name or "সদস্য"
        bot_username = context.bot.username
        print(f"[GROUP JOIN] user_id={user.id} name={name} in chat_id={update.message.chat_id}")

        keyboard = [[InlineKeyboardButton("এখানে ক্লিক করো ✨", url=f"https://t.me/{bot_username}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        group_msg = (
            f"🌟 <b>Welcome to TSS Family</b> 🌟\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"👋 হ্যালো <b>{name}</b>!\n"
            f"আমাদের পরিবারে তোমাকে স্বাগতম 🎉\n\n"
            f"📌 <b>শুরু করার আগে:</b>\n"
            f"1. গ্রুপের উপরে পিন করা মেসেজগুলো অবশ্যই দেখে নিও 👀\n\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"🤖 <b>সবকিছু একসাথে জানতে চাও?</b>\n"
            f"নিচের বাটনে ক্লিক করে আমাকে 'Hi' দাও 👇\n\n"
            f"⚠️ <i>Hi না লিখলে কিন্তু কাজ করবে না!</i>\n"
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
