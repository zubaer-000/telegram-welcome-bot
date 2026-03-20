import os
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# =============== FLASK HEALTH CHECK ===============
flask_app = Flask(__name__)

@flask_app.route("/")
def health():
    return "Bot is alive and running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


# =============== CONSTANTS & LINKS ===============
LINKS = {
    "central_hub": "https://tss-central-hub.blogspot.com/",
    "tarkik":      "https://tss-tarkik.blogspot.com/",
    "bio_bridge":  "https://tss-bio-bridge.blogspot.com/",
}

# =============== TEXT HELPERS ===============

def get_main_menu_text(name: str) -> str:
    return (
        f"আসসালামু আলাইকুম, <b>{name}</b>! 👋\n"
        "স্বাগতম <b>ঠাকুরগাঁও সায়েন্স সোসাইটি (TSS)</b>-তে! 🌟\n\n"
        "আমি তোমাকে TSS-এর সব কিছু জানাতে এখানে আছি। "
        "নিচে থেকে তোমার পছন্দের বিষয়টা বেছে নাও 👇"
    )

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🏠 TSS কী? (পরিচয়)",          callback_data="about_tss")],
        [InlineKeyboardButton("🧠 তার্কিক - যুক্তিবিদ্যা ক্লাব",  callback_data="tarkik")],
        [InlineKeyboardButton("🔬 বায়োব্রিজ - জীববিজ্ঞান ক্লাব", callback_data="bio_bridge")],
        [InlineKeyboardButton("📚 কীভাবে যোগ দেব?",             callback_data="how_to_join")],
        [InlineKeyboardButton("🗓️ ইভেন্ট ও প্রতিযোগিতা",        callback_data="events")],
        [InlineKeyboardButton("❓ আরও প্রশ্ন আছে?",             callback_data="faq")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(back_target: str = "main_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 মূল মেনুতে ফিরে যাও", callback_data=back_target)
    ]])

# ---- Individual section texts ----

ABOUT_TSS_TEXT = (
    "🏫 <b>ঠাকুরগাঁও সায়েন্স সোসাইটি (TSS) কী?</b>\n\n"
    "TSS হলো ঠাকুরগাঁওয়ের ৬ষ্ঠ থেকে ১০ম শ্রেণীর বিজ্ঞান-প্রেমী শিক্ষার্থীদের জন্য একটি বিশেষ প্ল্যাটফর্ম। "
    "এখানে তুমি:\n\n"
    "✅ বিজ্ঞান ও যুক্তিবিদ্যা শিখতে পারবে\n"
    "✅ জীববিজ্ঞানের গভীরে যেতে পারবে\n"
    "✅ প্রতিযোগিতায় অংশ নিতে পারবে\n"
    "✅ নতুন বন্ধু বানাতে পারবে\n\n"
    f"🔗 <b>TSS Central Hub:</b> {LINKS['central_hub']}\n\n"
    "সব তথ্য পাবে Central Hub-এ গেলে। এখানে সব কিছু একসাথে আছে!"
)

TARKIK_TEXT = (
    "🧠 <b>তার্কিক — TSS যুক্তিবিদ্যা ও বিজ্ঞান ক্লাব</b>\n\n"
    "তার্কিক হলো TSS-এর যুক্তি-তর্ক ও বিজ্ঞান-বিশ্লেষণ বিভাগ। "
    "এখানে তুমি শিখবে কীভাবে সঠিকভাবে যুক্তি দিতে হয়, "
    "সমস্যা সমাধান করতে হয়, এবং বৈজ্ঞানিক পদ্ধতিতে চিন্তা করতে হয়।\n\n"
    "📌 <b>কীভাবে শুরু করবে?</b>\n"
    "১. নিচের লিংকে যাও\n"
    "২. Level 1 ও Level 2-এর Playlist দেখো\n"
    "৩. সব ভিডিও দেখে শেষ করো\n"
    "৪. ছোট একটা পরীক্ষা দাও — পাস করলেই সদস্যপদ! 🎉\n\n"
    f"🔗 <b>তার্কিক লিংক:</b> {LINKS['tarkik']}\n\n"
    "💡 <i>টিপস: Level 1 দিয়ে শুরু করো, তাড়াহুড়ো করো না!</i>"
)

BIO_BRIDGE_TEXT = (
    "🔬 <b>বায়োব্রিজ — TSS জীববিজ্ঞান ক্লাব</b>\n\n"
    "বায়োব্রিজ হলো TSS-এর জীববিজ্ঞান বিভাগ। "
    "জীব, কোষ, বিবর্তন, বাস্তুতন্ত্র — সব কিছু মজার ভাবে শেখানো হয় এখানে।\n\n"
    "📌 <b>বায়োব্রিজে কী পাবে?</b>\n"
    "✅ সহজ ভাষায় জীববিজ্ঞান শেখার রিসোর্স\n"
    "✅ অলিম্পিয়াড প্রস্তুতির উপকরণ\n"
    "✅ বিশেষজ্ঞদের সাথে আলোচনার সুযোগ\n"
    "✅ প্রজেক্ট ও রিসার্চে অংশগ্রহণ\n\n"
    f"🔗 <b>বায়োব্রিজ লিংক:</b> {LINKS['bio_bridge']}\n\n"
    "💡 <i>জীববিজ্ঞান ভালোবাসো? তাহলে বায়োব্রিজই তোমার জায়গা!</i>"
)

HOW_TO_JOIN_TEXT = (
    "📝 <b>TSS-এ কীভাবে যোগ দেবে?</b>\n\n"
    "যোগ দেওয়া একদম সহজ! নিচের ধাপগুলো অনুসরণ করো:\n\n"
    "<b>তার্কিকের জন্য:</b>\n"
    f"1️⃣ {LINKS['tarkik']} — এই লিংকে যাও\n"
    "2️⃣ Level 1 → Level 2 Playlist দেখো\n"
    "3️⃣ নির্ধারিত পরীক্ষায় পাস করো\n"
    "4️⃣ সদস্যপদ নিশ্চিত হবে ✅\n\n"
    "<b>বায়োব্রিজের জন্য:</b>\n"
    f"1️⃣ {LINKS['bio_bridge']} — এই লিংকে যাও\n"
    "2️⃣ সাইটে রেজিস্ট্রেশন ফর্ম পূরণ করো\n"
    "3️⃣ গ্রুপে অ্যাডমিনকে জানাও\n\n"
    "<b>সব তথ্যের জন্য:</b>\n"
    f"🏠 TSS Central Hub: {LINKS['central_hub']}\n\n"
    "❓ কোনো সমস্যা হলে গ্রুপে বা এখানে জানাও!"
)

EVENTS_TEXT = (
    "🗓️ <b>TSS ইভেন্ট ও প্রতিযোগিতা</b>\n\n"
    "TSS নিয়মিত নানা রকম ইভেন্ট আয়োজন করে:\n\n"
    "🏆 <b>বিজ্ঞান অলিম্পিয়াড</b> — জাতীয় পর্যায়ে অংশগ্রহণের সুযোগ\n"
    "🧪 <b>সায়েন্স ফেয়ার</b> — নিজের প্রজেক্ট প্রদর্শন করো\n"
    "💬 <b>বিতর্ক প্রতিযোগিতা</b> — যুক্তি দিয়ে জয়ী হও\n"
    "📖 <b>কুইজ কম্পিটিশন</b> — জ্ঞান যাচাই করো\n"
    "🔭 <b>ওয়ার্কশপ</b> — বিশেষজ্ঞদের কাছ থেকে শেখো\n\n"
    "সর্বশেষ ইভেন্টের আপডেট পেতে:\n"
    f"👉 Central Hub: {LINKS['central_hub']}\n\n"
    "💡 <i>ইভেন্টে অংশ নেওয়া সদস্যরা সার্টিফিকেট পায়!</i>"
)

FAQ_TEXT = (
    "❓ <b>সাধারণ জিজ্ঞাসা (FAQ)</b>\n\n"
    "🔸 <b>TSS কি শুধু ঠাকুরগাঁওয়ের জন্য?</b>\n"
    "→ মূলত ঠাকুরগাঁওয়ের শিক্ষার্থীদের জন্য, তবে অনলাইনে সবাই অংশ নিতে পারো।\n\n"
    "🔸 <b>কোন শ্রেণীর শিক্ষার্থীরা যোগ দিতে পারবে?</b>\n"
    "→ ৬ষ্ঠ থেকে ১০ম শ্রেণী পর্যন্ত সবাই।\n\n"
    "🔸 <b>যোগ দেওয়া কি বিনামূল্যে?</b>\n"
    "→ হ্যাঁ! সম্পূর্ণ বিনামূল্যে।\n\n"
    "🔸 <b>তার্কিক ও বায়োব্রিজ দুটোতেই যোগ দিতে পারব?</b>\n"
    "→ অবশ্যই! দুটোতেই যোগ দিতে পারবে।\n\n"
    "🔸 <b>পরীক্ষায় পাস না করলে কী হবে?</b>\n"
    "→ আবার দিতে পারবে! চেষ্টা চালিয়ে যাও 💪\n\n"
    "🔸 <b>আরও প্রশ্ন থাকলে?</b>\n"
    "→ সরাসরি গ্রুপে লেখো বা এখানে মেসেজ দাও!"
)

# keyword → callback mapping for smart private chat
KEYWORD_MAP = {
    # Tarkik related
    "তার্কিক": "tarkik",
    "tarkik": "tarkik",
    "যুক্তি": "tarkik",
    "debate": "tarkik",
    "level": "tarkik",

    # Bio Bridge related
    "বায়োব্রিজ": "bio_bridge",
    "bio": "bio_bridge",
    "জীব": "bio_bridge",
    "biology": "bio_bridge",
    "বিজ্ঞান": "bio_bridge",

    # Join related
    "যোগ": "how_to_join",
    "join": "how_to_join",
    "ভর্তি": "how_to_join",
    "রেজিস্ট্রেশন": "how_to_join",
    "registration": "how_to_join",
    "member": "how_to_join",
    "সদস্য": "how_to_join",

    # Events
    "ইভেন্ট": "events",
    "event": "events",
    "প্রতিযোগিতা": "events",
    "অলিম্পিয়াড": "events",
    "olympiad": "events",
    "quiz": "events",
    "কুইজ": "events",

    # TSS / about
    "tss": "about_tss",
    "সায়েন্স সোসাইটি": "about_tss",
    "কী": "about_tss",
    "কি": "about_tss",
    "পরিচয়": "about_tss",
    "hub": "about_tss",
    "হাব": "about_tss",
}


# =============== CALLBACK QUERY HANDLER ===============

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        await query.edit_message_text(
            get_main_menu_text(query.from_user.first_name or "বন্ধু"),
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
    elif data == "about_tss":
        await query.edit_message_text(ABOUT_TSS_TEXT, parse_mode="HTML",
                                      reply_markup=get_back_keyboard())
    elif data == "tarkik":
        await query.edit_message_text(TARKIK_TEXT, parse_mode="HTML",
                                      reply_markup=get_back_keyboard())
    elif data == "bio_bridge":
        await query.edit_message_text(BIO_BRIDGE_TEXT, parse_mode="HTML",
                                      reply_markup=get_back_keyboard())
    elif data == "how_to_join":
        await query.edit_message_text(HOW_TO_JOIN_TEXT, parse_mode="HTML",
                                      reply_markup=get_back_keyboard())
    elif data == "events":
        await query.edit_message_text(EVENTS_TEXT, parse_mode="HTML",
                                      reply_markup=get_back_keyboard())
    elif data == "faq":
        await query.edit_message_text(FAQ_TEXT, parse_mode="HTML",
                                      reply_markup=get_back_keyboard())


# =============== COMMAND: /start ===============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "বন্ধু"
    await update.message.reply_text(
        get_main_menu_text(name),
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(),
    )


# =============== COMMAND: /help ===============

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 <b>আমি তোমাকে কী কী বিষয়ে সাহায্য করতে পারি:</b>\n\n"
        "• TSS সম্পর্কে জানতে\n"
        "• তার্কিক ক্লাব সম্পর্কে জানতে\n"
        "• বায়োব্রিজ সম্পর্কে জানতে\n"
        "• কীভাবে যোগ দেবে\n"
        "• ইভেন্ট ও প্রতিযোগিতার তথ্য\n\n"
        "শুধু /start লিখলেই মূল মেনু আসবে! 😊",
        parse_mode="HTML",
    )


# =============== PRIVATE CHAT HANDLER ===============

async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return

    user = update.effective_user
    name = user.first_name or "বন্ধু"
    text = (update.message.text or "").lower().strip()

    # Smart keyword detection
    detected_section = None
    for keyword, section in KEYWORD_MAP.items():
        if keyword.lower() in text:
            detected_section = section
            break

    # Build responses for known keywords
    section_texts = {
        "about_tss":   ABOUT_TSS_TEXT,
        "tarkik":      TARKIK_TEXT,
        "bio_bridge":  BIO_BRIDGE_TEXT,
        "how_to_join": HOW_TO_JOIN_TEXT,
        "events":      EVENTS_TEXT,
        "faq":         FAQ_TEXT,
    }

    if detected_section:
        await update.message.reply_text(
            section_texts[detected_section],
            parse_mode="HTML",
            reply_markup=get_back_keyboard("main_menu"),
        )
    else:
        # Default: show main menu
        await update.message.reply_text(
            f"তুমি লিখেছো: «{update.message.text}»\n\n"
            + get_main_menu_text(name),
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )


# =============== GROUP JOIN WELCOME (with auto-delete after 6 hours) ===============

async def _delete_message_later(bot, chat_id: int, message_id: int, delay_seconds: int):
    """Coroutine that sleeps then deletes a message."""
    await asyncio.sleep(delay_seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"[Auto-Delete] Could not delete message {message_id}: {e}")


async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        if user.id == context.bot.id:
            continue

        name = user.first_name or "সদস্য"
        bot_username = context.bot.username

        keyboard = [[
            InlineKeyboardButton(
                "বিস্তারিত জানতে এখানে ক্লিক করো ✨",
                url=f"https://t.me/{bot_username}",
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        group_msg = (
            f"👋 আমাদের পরিবারে স্বাগতম, <b>{name}</b>! 🎉\n\n"
            "গ্রুপের পিন করা মেসেজগুলো একটু চেক করো।\n"
            "TSS সম্পর্কে সব কিছু জানতে নিচের বাটনে ক্লিক করে আমাকে মেসেজ দাও 👇\n\n"
            "<i>⏳ এই মেসেজটি ৬ ঘণ্টা পর স্বয়ংক্রিয়ভাবে মুছে যাবে।</i>"
        )

        try:
            sent = await update.message.reply_text(
                group_msg, parse_mode="HTML", reply_markup=reply_markup
            )
            # Schedule deletion after 6 hours (21600 seconds)
            asyncio.create_task(
                _delete_message_later(
                    context.bot,
                    chat_id=sent.chat_id,
                    message_id=sent.message_id,
                    delay_seconds=6 * 3600,
                )
            )
        except Exception as e:
            print(f"[Welcome] Error sending welcome: {e}")


# =============== MAIN ===============

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ BOT_TOKEN not set!")
        exit(1)

    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            handle_private_message,
        )
    )

    print("🤖 TSS Bot is active!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
