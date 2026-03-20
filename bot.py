import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# --- Flask for Render Health Check ---
flask_app = Flask(__name__)
@flask_app.route('/')
def health(): return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- Bot Logic ---
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"হ্যালো {user.first_name}! ❤️\n🔗 তার্কিক: https://tss-tarkik.blogspot.com/\n🔗 বায়োব্রিজ: https://tss-bio-bridge.blogspot.com/")

async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        if user.id == context.bot.id: continue
        try: await update.message.delete()
        except: pass
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("বিস্তারিত জানুন ✨", url=f"https://t.me/{context.bot.username}")]])
        await update.message.reply_text(f"স্বাগতম {user.first_name}! আমাদের পরিবারে যুক্ত হওয়ার জন্য ধন্যবাদ। 👇", reply_markup=btn)

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, start_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))
    app.run_polling(drop_pending_updates=True)
