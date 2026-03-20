import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# =============== FLASK HEALTH CHECK (keeps bot instant 24/7) ===============
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is alive and running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# =============== TELEGRAM BOT LOGIC ===============
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        # Don't welcome the bot itself
        if user.id == (await context.bot.get_me()).id:
            continue

        name = user.first_name or user.username or "সদস্য"

        # === GROUP WELCOME MESSAGE ===
        group_msg = (
            f"👋 আমাদের পরিবারে সদস্য হিসেবে স্বাগতম তোমাকে, **{name}**! 🎉\n\n"
            "গ্রুপে উপরে পিন করা মেসেজগুলা একটু চেক করে দেখো। হয়তো টিএসএসকে বুঝতে পারবা তুমি।\n\n"
            f"সব একসাথে জানতে চাও → Message me here: @{context.bot.username}"
        )
        
        try:
            await update.message.reply_text(group_msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Group message failed: {e}")

        # === PRIVATE MESSAGE (PRIMARY — detailed guidance) ===
        private_text = (
            f"হ্যালো {name}! স্বাগতম আমাদের গ্রুপে\n\n"
            "তুমি **তার্কিকে** যুক্ত হতে চাও? তাহলে নিচের লিংকে গিয়ে লেভেল ১ এবং ২ এর প্লেলিস্ট দেখে শিখে ফেলো সব এবং ছোট পরীক্ষা দিয়ে দাও।\n"
            "পরীক্ষা কাট মার্ক পার করলেই আমরা ধরে নিবো ডিবেটিং এর কনসেপ্ট শিখে ফেলছো। তারপর তোমাকে লেভেল থ্রি তে যুক্ত হয়ে ডিবেট করার সুযোগ দিব।\n"
            "তার্কিকের লিঙ্ক → https://tss-tarkik.blogspot.com/\n\n"
            "তুমি **বায়োব্রিজে** যুক্ত হতে চাও? তাহলে তো সেরা!\n"
            "আমাদের সাইটে গিয়ে বায়োলজির সিলেবাস দেখো... তারপর বায়োলিম্পে অংশ নাও।\n"
            "লিঙ্ক → https://tss-bio-bridge.blogspot.com/\n\n"
            "কোনো প্রশ্ন/সাহায্য লাগলে group এ বলো --আমরা আছি তোমার পাশে! ❤️"
        )
        
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=private_text,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
            print(f"✅ Private message sent to {name} (ID: {user.id})")
        except Exception as e:
            print(f"ℹ️ Could not send private message to {name}: {str(e)} "
                  f"(Normal — user hasn't started the bot yet)")

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ BOT_TOKEN missing!")
        exit(1)

    # Start keep-alive server
    threading.Thread(target=run_flask, daemon=True).start()

    print("🤖 Bot started — Group + Private welcome (Primary)")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    app.run_polling(allowed_updates=Update.ALL_TYPES)
