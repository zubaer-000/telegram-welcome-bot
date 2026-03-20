import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# =============== FLASK HEALTH CHECK (keeps bot alive on Render) ===============
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
        "পরীক্ষা কাট মার্ক পার করলেই আমরা ধরে নিবো ডিবেটিং এর কনসেপ্ট শিখে ফেলছো। তারপর তোমাকে লেভেল থ্রি তে যুক্ত হয়ে ডিবেট করার সুযোগ দিব।\n"
        "🔗 তার্কিকের লিঙ্ক: https://tss-tarkik.blogspot.com/\n\n"
        "তুমি **বায়োব্রিজে** যুক্ত হতে চাও? তাহলে তো সেরা!\n"
        "আমাদের সাইটে গিয়ে বায়োলজির সিলেবাস দেখো... তারপর বায়োলিম্পে অংশ নাও।\n"
        "🔗 লিঙ্ক: https://tss-bio-bridge.blogspot.com/\n\n"
        "কোনো প্রশ্ন বা সাহায্য লাগলে গ্রুপে জানিও, আমরা আছি তোমার পাশে!"
    )

# =============== TELEGRAM BOT LOGIC ===============

# 1. Handle people joining the group
async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        # Skip if the new member is the bot itself
        if user.id == context.bot.id:
            continue

        name = user.first_name or user.username or "সদস্য"
        bot_username = context.bot.username
        
        # Fixing the link issue by using a proper Markdown URL
        group_msg = (
            f"👋 আমাদের পরিবারে সদস্য হিসেবে স্বাগতম তোমাকে, **{name}**! 🎉\n\n"
            "গ্রুপের উপরে পিন করা মেসেজগুলো একটু চেক করে দেখো। আশা করি টিএসএস সম্পর্কে জানতে পারবে।\n\n"
            f"সব একসাথে জানতে সরাসরি আমাকে এখানে মেসেজ দাও: [@{bot_username}](https://t.me/{bot_username})"
        )
        
        # Send Public Message in Group
        try:
            await update.message.reply_text(group_msg, parse_mode="Markdown", disable_web_page_preview=True)
        except Exception as e:
            print(f"Error in group message: {e}")

        # Try to send Private Message (only works if user has 'Started' the bot before)
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=get_private_welcome_text(name),
                parse_mode="Markdown"
            )
            print(f"✅ Private DM sent to {name}")
        except Exception:
            print(f"ℹ️ Could not DM {name} (User hasn't started the bot yet)")

# 2. Handle when someone clicks the link and presses "START"
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "সদস্য"
    await update.message.reply_text(get_private_welcome_text(name), parse_mode="Markdown")

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ Error: BOT_TOKEN environment variable is missing!")
        exit(1)

    # Start Flask background thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Build Bot
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))

    print("🤖 Bot is active. Listening for new members and /start commands...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
