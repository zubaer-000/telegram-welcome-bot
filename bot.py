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
        "তুমি **তার্কিকে** যুক্ত হতে চাও? তাহলে নিচের লিংকে গিয়ে লেভেল ১ এবং ২ এর প্লেলিস্ট দেখে শিখে ফেলো সব এবং ছোট পরীক্ষা দিয়ে দাও।\n"
        "🔗 তার্কিকের লিঙ্ক: https://tss-tarkik.blogspot.com/\n\n"
        "তুমি **বায়োব্রিজে** যুক্ত হতে চাও? তাহলে তো সেরা!\n"
        "🔗 লিঙ্ক: https://tss-bio-bridge.blogspot.com/\n\n"
        "কোনো প্রশ্ন বা সাহায্য লাগলে গ্রুপে জানিও!"
    )

# =============== TELEGRAM BOT LOGIC ===============

async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        if user.id == context.bot.id:
            continue

        name = user.first_name or "সদস্য"
        bot_username = context.bot.username
        
        # 1. Create the Button
        keyboard = [
            [InlineKeyboardButton("বিস্তারিত জানতে এখানে ক্লিক করো ✨", url=f"https://t.me/{bot_username}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 2. Simplified Group Message
        group_msg = (
            f"👋 আমাদের পরিবারে সদস্য হিসেবে স্বাগতম তোমাকে, <b>{name}</b>! 🎉\n\n"
            "গ্রুপের উপরে পিন করা মেসেজগুলো একটু চেক করে দেখো। আশা করি টিএসএস সম্পর্কে জানতে পারবে।\n\n"
            "সব কিছু একসাথে জানতে নিচের বাটনে ক্লিক করে আমাকে মেসেজ দাও: 👇"
        )
        
        try:
            await update.message.reply_text(
                group_msg, 
                parse_mode="HTML", 
                reply_markup=reply_markup # This adds the button!
            )
        except Exception as e:
            print(f"Error in group message: {e}")

        # 3. Try to send Private Message
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=get_private_welcome_text(name),
                parse_mode="Markdown"
            )
        except Exception:
            pass

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "সদস্য"
    await update.message.reply_text(get_private_welcome_text(name), parse_mode="Markdown")

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        exit(1)

    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))

    print("🤖 Bot is active with Button Support!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
