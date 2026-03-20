import os
import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# =============== FLASK HEALTH CHECK ===============
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is alive and running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# =============== CLUB DATA ===============
CLUBS = [
    {
        "id": "tarkik",
        "emoji": "⚔️",
        "name": "TSS :: Tarkik",
        "tag": "Debate",
        "short": "Master the art of argument.",
        "detail": (
            "⚔️ *TSS :: Tarkik — Debate*\n\n"
            "Master the art of argument. Tarkik trains debaters from fundamentals to national-level parliamentary and traditional debate.\n\n"
            "📚 *কী শিখবে?*\n"
            "• Parliamentary Debate (WSDC, NHSDC format)\n"
            "• Traditional Bengali Debate\n"
            "• Rebuttal, POI, and case-building skills\n\n"
            "🔗 *শুরু করতে এখানে যাও:* https://tss-tarkik.blogspot.com/\n\n"
            "যোগ দিতে চাইলে লেভেল ১ ও ২ এর প্লেলিস্ট দেখে ছোট পরীক্ষা দিয়ে দাও!"
        ),
    },
    {
        "id": "numero",
        "emoji": "🔢",
        "name": "TSS :: Numero Odyssey",
        "tag": "Math Olympiad",
        "short": "A journey through numbers.",
        "detail": (
            "🔢 *TSS :: Numero Odyssey — Math Olympiad*\n\n"
            "A journey through numbers. Prepare for district, regional and national mathematics olympiads.\n\n"
            "📚 *কী শিখবে?*\n"
            "• Number Theory, Combinatorics, Geometry\n"
            "• BdMO জেলা → জাতীয় প্রস্তুতি\n"
            "• Problem-solving strategy & proof writing\n\n"
            "আগ্রহী হলে গ্রুপে জানাও — আমরা তোমাকে সঠিক পথ দেখাবো! 🧮"
        ),
    },
    {
        "id": "iii",
        "emoji": "🌐",
        "name": "TSS :: III",
        "tag": "Opportunity Seeking",
        "short": "Discover olympiads, programs & global opportunities.",
        "detail": (
            "🌐 *TSS :: III — Opportunity Seeking*\n\n"
            "Helps students discover olympiad deadlines, programs and global opportunities.\n\n"
            "📚 *কী পাবে?*\n"
            "• আন্তর্জাতিক প্রোগ্রাম ও স্কলারশিপের আপডেট\n"
            "• Olympiad registration deadlines\n"
            "• Summer schools, exchange programs, fellowships\n\n"
            "সুযোগ হাতছাড়া না করতে এখনই যুক্ত হয়ে যাও! 🌍"
        ),
    },
    {
        "id": "biobridge",
        "emoji": "🧬",
        "name": "TSS :: Bio-Bridge",
        "tag": "Biology",
        "short": "Bridge classroom biology and real science.",
        "detail": (
            "🧬 *TSS :: Bio-Bridge — Biology*\n\n"
            "Bridge the gap between classroom biology and real science — olympiad prep, research thinking and life sciences.\n\n"
            "📚 *কী শিখবে?*\n"
            "• BBO, IBO প্রস্তুতি\n"
            "• Cell biology, genetics, ecology, physiology\n"
            "• Research-based problem solving\n\n"
            "🔗 *শুরু করতে:* https://tss-bio-bridge.blogspot.com/\n\n"
            "জীববিজ্ঞানের জগতে স্বাগতম! 🔬"
        ),
    },
    {
        "id": "codebase",
        "emoji": "💻",
        "name": "TSS :: Codebase",
        "tag": "Programming",
        "short": "From first lines of code to competitive programming.",
        "detail": (
            "💻 *TSS :: Codebase — Programming*\n\n"
            "From first lines of code to competitive programming. Codebase builds the developers of tomorrow.\n\n"
            "📚 *কী শিখবে?*\n"
            "• Python, C++ basics থেকে advanced\n"
            "• Competitive programming (Codeforces, ICPC prep)\n"
            "• Data structures & algorithms\n\n"
            "কোড লিখতে ভালোবাসো? তাহলে Codebase তোমার জন্যই! 🚀"
        ),
    },
    {
        "id": "metamorphosis",
        "emoji": "✍️",
        "name": "TSS :: Metamorphosis",
        "tag": "English Language",
        "short": "Transform your command of English.",
        "detail": (
            "✍️ *TSS :: Metamorphosis — English Language*\n\n"
            "Transform your command of English — writing, speaking and comprehension for a globalized future.\n\n"
            "📚 *কী শিখবে?*\n"
            "• Essay writing, creative writing\n"
            "• Public speaking & presentation\n"
            "• Reading comprehension & vocabulary\n\n"
            "ইংরেজিতে দক্ষ হতে চাইলে Metamorphosis তোমার রূপান্তর শুরু করবে! 🦋"
        ),
    },
    {
        "id": "lubdhok",
        "emoji": "📖",
        "name": "TSS :: Lubdhok",
        "tag": "Bengali Language & Literature",
        "short": "Nurture Bengali writing, literature & culture.",
        "detail": (
            "📖 *TSS :: Lubdhok — Bengali Language & Literature*\n\n"
            "Celebrate the mother tongue. Lubdhok nurtures Bengali writing, literature and cultural expression.\n\n"
            "📚 *কী শিখবে?*\n"
            "• বাংলা রচনা, গল্প, কবিতা লেখা\n"
            "• সাহিত্যের ইতিহাস ও বিশ্লেষণ\n"
            "• বাংলা ভাষা অলিম্পিয়াড প্রস্তুতি\n\n"
            "মাতৃভাষাকে ভালোবাসো — Lubdhok-এ স্বাগতম! 🖊️"
        ),
    },
    {
        "id": "nh5",
        "emoji": "🧭",
        "name": "TSS :: NH5",
        "tag": "Guidance & Mentorship",
        "short": "Your compass through academic & career decisions.",
        "detail": (
            "🧭 *TSS :: NH5 — Guidance & Mentorship*\n\n"
            "Your compass through academic and career decisions. NH5 provides mentorship and life-skills guidance.\n\n"
            "📚 *কী পাবে?*\n"
            "• বিশ্ববিদ্যালয় ভর্তি গাইডেন্স\n"
            "• Career counseling & path planning\n"
            "• Life skills, time management, goal setting\n\n"
            "সঠিক দিকনির্দেশনা পেতে NH5 সবসময় তোমার পাশে আছে! 🌟"
        ),
    },
    {
        "id": "optocoupler",
        "emoji": "⚡",
        "name": "TSS :: Optocoupler",
        "tag": "Physics",
        "short": "Explore the laws that govern the universe.",
        "detail": (
            "⚡ *TSS :: Optocoupler — Physics*\n\n"
            "Explore the laws that govern the universe. Olympiad preparation and deep conceptual physics training.\n\n"
            "📚 *কী শিখবে?*\n"
            "• BPhO, IPhO প্রস্তুতি\n"
            "• Mechanics, Electromagnetism, Optics, Modern Physics\n"
            "• Conceptual problem solving & derivations\n\n"
            "পদার্থবিজ্ঞানের রহস্য উন্মোচন করতে Optocoupler-এ আসো! 🔭"
        ),
    },
    {
        "id": "chemicompound",
        "emoji": "⚗️",
        "name": "TSS :: Chemicompound",
        "tag": "Chemistry",
        "short": "Reactions, elements & analytical thinking.",
        "detail": (
            "⚗️ *TSS :: Chemicompound — Chemistry*\n\n"
            "Reactions, elements and analytical thinking. Chemicompound prepares students for chemistry olympiads and beyond.\n\n"
            "📚 *কী শিখবে?*\n"
            "• BChO, IChO প্রস্তুতি\n"
            "• Organic, Inorganic & Physical Chemistry\n"
            "• Lab techniques & analytical reasoning\n\n"
            "রসায়নের রঙিন দুনিয়ায় তোমাকে স্বাগতম! 🧪"
        ),
    },
    {
        "id": "bizznexus",
        "emoji": "📊",
        "name": "TSS :: Bizz Nexus",
        "tag": "Business",
        "short": "Cultivate entrepreneurial thinking & business acumen.",
        "detail": (
            "📊 *TSS :: Bizz Nexus — Business*\n\n"
            "The meeting point of ideas and enterprise. Bizz Nexus cultivates entrepreneurial thinking and business acumen.\n\n"
            "📚 *কী শিখবে?*\n"
            "• Business plan তৈরি ও pitch করা\n"
            "• Economics, finance basics\n"
            "• Entrepreneurship, startups & case studies\n\n"
            "উদ্যোক্তা হওয়ার স্বপ্ন দেখো? Bizz Nexus তোমার শুরুর জায়গা! 💼"
        ),
    },
]

# =============== KEYBOARDS ===============

def get_clubs_keyboard():
    """Build 2-column inline keyboard for all 11 clubs."""
    buttons = []
    row = []
    for i, club in enumerate(CLUBS):
        btn = InlineKeyboardButton(
            f"{club['emoji']} {club['name']}",
            callback_data=f"club_{club['id']}"
        )
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:  # odd one out gets its own row centered
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

def get_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 সব ক্লাব দেখো", callback_data="back_to_clubs")]
    ])

# =============== WELCOME TEXT ===============

INTRO_TEXT = (
    "হ্যালো! স্বাগতম TSS পরিবারে। ❤️\n\n"
    "আমরা *The Science Society (TSS)* — একটি শিক্ষার্থী-চালিত সংগঠন যেখানে বিতর্ক থেকে শুরু করে বিজ্ঞান অলিম্পিয়াড পর্যন্ত সবকিছু নিয়ে কাজ হয়।\n\n"
    "নিচে আমাদের সব ক্লাব দেওয়া আছে। তোমার পছন্দের ক্লাবটিতে ক্লিক করো এবং বিস্তারিত জেনে নাও! 👇"
)

# =============== HANDLERS ===============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        INTRO_TEXT,
        parse_mode="Markdown",
        reply_markup=get_clubs_keyboard()
    )

async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text(
            INTRO_TEXT,
            parse_mode="Markdown",
            reply_markup=get_clubs_keyboard()
        )

async def handle_club_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back_to_clubs":
        await query.edit_message_text(
            INTRO_TEXT,
            parse_mode="Markdown",
            reply_markup=get_clubs_keyboard()
        )
        return

    if data.startswith("club_"):
        club_id = data[len("club_"):]
        club = next((c for c in CLUBS if c["id"] == club_id), None)
        if club:
            await query.edit_message_text(
                club["detail"],
                parse_mode="Markdown",
                reply_markup=get_back_keyboard()
            )

# =============== GROUP WELCOME (with auto-delete after 6 hours) ===============

async def delete_message_later(bot, chat_id, message_id, delay_seconds):
    await asyncio.sleep(delay_seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"[Auto-delete] Could not delete message {message_id}: {e}")

async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        if user.id == context.bot.id:
            continue

        name = user.first_name or "সদস্য"
        bot_username = context.bot.username

        keyboard = [[InlineKeyboardButton("বিস্তারিত জানতে এখানে ক্লিক করো ✨", url=f"https://t.me/{bot_username}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        group_msg = (
            f"👋 আমাদের পরিবারে সদস্য হিসেবে স্বাগতম তোমাকে, <b>{name}</b>! 🎉\n\n"
            "গ্রুপের উপরে পিন করা মেসেজগুলো একটু চেক করে দেখো।\n\n"
            "সব কিছু একসাথে জানতে নিচের বাটনে ক্লিক করে আমাকে মেসেজ দাও: 👇"
        )

        try:
            sent = await update.message.reply_text(
                group_msg,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            # Schedule auto-delete after 6 hours (21600 seconds)
            asyncio.create_task(
                delete_message_later(context.bot, sent.chat_id, sent.message_id, 21600)
            )
        except Exception as e:
            print(f"Error sending welcome: {e}")

# =============== MAIN ===============

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ BOT_TOKEN not set!")
        exit(1)

    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_group))
    app.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE,
        handle_private_message
    ))
    app.add_handler(CallbackQueryHandler(handle_club_callback))

    print("🤖 Bot is active!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
