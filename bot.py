import os
import threading
import logging
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# Enable logging to see exactly what's happening in Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# =============== FLASK HEALTH CHECK ===============
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# =============== BOT LOGIC ===============

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (f"হ্যালো {user.first_name}! ❤️\n\n"
            "🔗 তার্কিক লিঙ্ক: https://tss-tarkik.blogspot.com/\n"
            "🔗 বায়োব্রিজ লিঙ্ক: https://tss-bio-bridge.blogspot.com/")
    await update.message.reply_text(text, parse_mode="Markdown")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
    for user in update.message.new_chat_members:
        if user.id == context.bot.id: continue
        
        # Try to delete the system "joined" message
        try:
            await update.message.delete()
        except:
            pass

        btn = InlineKeyboardMarkup([[InlineKeyboardButton("বিস্তারিত জানুন ✨", url=f"https://t.me/{context.bot.username}")]])
        await update.message.reply_text(
            f"স্বাগতম {user.first_name}! আমাদের পরিবারে যুক্ত হওয়ার জন্য ধন্যবাদ। 👇",
            reply_markup=btn
        )

# =============== STARTUP ===============

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ ERROR: BOT_TOKEN is missing!")
        exit(1)

    # Start Flask first
    threading.Thread(target=run_flask, daemon=True).start()

    # Build and Start Bot
    print("🚀 Starting Bot on Python 3.12 stable...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, start_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    app.run_polling(drop_pending_updates=True)
