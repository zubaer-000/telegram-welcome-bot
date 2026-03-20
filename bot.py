from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from flask import Flask
import os
import threading

# =============== FLASK HEALTH CHECK (keeps bot instant 24/7) ===============
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is alive and running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

# =============== TELEGRAM BOT — ONLY GROUP WELCOME ===============
async def welcome(update: Update, context):
    for member in update.message.new_chat_members:
        user = member
        name = user.first_name or user.username or "নতুন সদস্য"

        group_msg = (
            f"👋 আমাদের পরিবারে সদস্য হিসেবে স্বাগতম তোমাকে, **{name}**! 🎉\n\n"
            "গ্রুপে উপরে পিন করা মেসেজগুলো একটু চেক করে দেখো।\n"
            "হয়তো TSS-কে ভালোভাবে বুঝতে পারবে তুমি।\n\n"
            "কোনো প্রশ্ন থাকলে গ্রুপেই জিজ্ঞাসা করো — সবাই মিলে সাহায্য করবো! ❤️"
        )

        await update.message.reply_text(group_msg, parse_mode="Markdown")

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")

    # Start health check (prevents sleep)
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot started — only group welcome messages (instant response)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
