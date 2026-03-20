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
    # use_reloader=False is critical in threaded environments
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

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
    print(f"DEBUG: Received /start from {user.first_name}")
    await update.message.reply_text(get_welcome_text(user.first_name), parse_mode="Markdown")

async def group_join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
    for user in update.message.new_chat_members:
        if user.id == context.bot.id: continue
        
        name = user.first_name or "সদস্য"
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("বিস্তারিত জানুন ✨", url=f"https://t.me/{context.bot.username}")]])
        
        await update.message.reply_text(
            f"স্বাগতম <b>{name}</b>! আমাদের পরিবারে যুক্ত হওয়ার জন্য ধন্যবাদ। সব জানতে নিচের বাটনে ক্লিক করো: 👇",
            reply_markup=btn,
            parse_mode="HTML"
        )

# =============== MAIN STARTUP ===============

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    
    if not TOKEN:
        print("❌ ERROR: BOT_TOKEN variable is missing!")
        exit(1)

    # 1. Start Flask in background
    print("🌐 Starting Flask...")
    threading.Thread(target=run_flask, daemon=True).start()

    # 2. Setup Bot
    print("🤖 Initializing Bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    # 3. Add Handlers
    app.add_handler(CommandHandler("start", start_handler))
    # Catch-all text handler for private chats
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, start_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_join_handler))

    # 4. Run Polling (Blocking call)
    print("✅ BOT IS LIVE. Waiting for messages...")
    app.run_polling(drop_pending_updates=True)
