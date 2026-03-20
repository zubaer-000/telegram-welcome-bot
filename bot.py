import os
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# =============== FLASK HEALTH CHECK ===============
# This keeps the bot alive on Render
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is alive and running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# =============== AUTO-DELETE LOGIC ===============

async def delete_message_job(context: ContextTypes.DEFAULT_TYPE):
    """Callback function to delete the message after the timer expires"""
    job = context.job
    try:
        await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data)
        print(f"🗑️ Auto-deleted message {job.data} in chat {job.chat_id}")
    except Exception as e:
        print(f"⚠️ Could not delete message (it might have been deleted manually): {e}")

# =============== TEXT CONTENT ===============

def get_welcome_info(name):
    return (
        f"হ্যালো {name}! স্বাগতম আমাদের পরিবারে। ❤️\n\n"
        "তুমি **তার্কিকে** যুক্ত হতে চাও? তাহলে নিচের লিংকে গিয়ে লেভেল ১ এবং ২ এর প্লেলিস্ট দেখে শিখে ফেলো সব এবং ছোট পরীক্ষা দিয়ে দাও।\n"
        "🔗 তার্কিকের লিঙ্ক: https://tss-tarkik.blogspot.com/\n\n"
        "তুমি **বায়োব্রিজে** যুক্ত হতে চাও? তাহলে তো সেরা!\n"
        "🔗 লিঙ্ক: https://tss-bio-bridge.blogspot.com/\n\n"
        "কোনো প্রশ্ন বা সাহায্য লাগলে গ্রুপে জানিও!"
    )

# =============== BOT HANDLERS ===============

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start and any private messages"""
    user = update.effective_user
    name = user.first_name or "সদস্য"
    print(f"DEBUG: Private message/start from {name}")
    await update.message.reply_text(get_welcome_info(name), parse_mode="Markdown")

async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles new members joining the group"""
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        if user.id == context.bot.id:
            continue
        
        name = user.first_name or "সদস্য"
        print(f"DEBUG: {name} joined the group.")

        # 1. Try to delete the 'User joined' system notification
        try:
            await update.message.delete()
        except Exception as e:
            print(f"Could not delete join notification: {e}")

        # 2. Send the Welcome Message with Button
        btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("বিস্তারিত জানতে এখানে ক্লিক করো ✨", url=f"https://t.me/{context.bot.username}")
        ]])
        
        group_text = (
            f"👋 আমাদের পরিবারে সদস্য হিসেবে স্বাগতম তোমাকে, <b>{name}</b>! 🎉\n\n"
            "গ্রুপের উপরে পিন করা মেসেজগুলো একটু চেক করে দেখো। আশা করি টিএসএস সম্পর্কে জানতে পারবে।\n\n"
            "সব কিছু একসাথে জানতে নিচের বাটনে ক্লিক করে আমাকে মেসেজ দাও: 👇"
        )
        
        try:
            sent_msg = await update.message.reply_text(
                group_text, 
                parse_mode="HTML", 
                reply_markup=btn
            )
            
            # 3. Schedule Auto-Delete (6 hours = 21600 seconds)
            # Change to 10 for testing
            delete_delay = 6 * 60 * 60 
            context.job_queue.run_once(
                delete_message_job, 
                when=delete_delay, 
                chat_id=update.effective_chat.id, 
                data=sent_msg.message_id
            )
            print(f"🕒 Scheduled deletion for message {sent_msg.message_id} in {delete_delay}s")

        except Exception as e:
            print(f"❌ Error in group greeting: {e}")

# =============== MAIN RUNNER ===============

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ CRITICAL: BOT_TOKEN not found!")
        exit(1)

    # 1. Start Flask in background thread
    print("🌐 Starting Flask Server...")
    threading.Thread(target=run_flask, daemon=True).start()

    # 2. Build the Application with JobQueue enabled
    print("🤖 Initializing Bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    # 3. Add Handlers
    app.add_handler(CommandHandler("start", start_handler))
    # Handles text in private chat
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, start_handler))
    # Handles new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))

    # 4. Start Polling
    print("🚀 BOT IS LIVE. Waiting for events...")
    app.run_polling(drop_pending_updates=True)
