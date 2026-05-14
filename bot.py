"""
URL Shortener Telegram Bot - Premium Version v2
================================================
- ২১টা নতুন Cutt.ly + ১৩টা TinyURL API key
- পালা করে Cutt.ly ও TinyURL ব্যবহার করে
- একটা key limit হলে অটো পরেরটায় যায়
- প্রতিটা লিংক সম্পূর্ণ unique
- Premium বাটন UI

ইনস্টল:
    pip install python-telegram-bot requests

চালাও:
    python bot.py
"""

import logging
import requests
import time
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

TELEGRAM_TOKEN = "8733539808:AAH19m_M8QmbrOb_qTb8-S7zQR8AikobPZY"

# ✅ সব Cutt.ly API Keys (পুরনো ১১টা + নতুন ২১টা = মোট ৩২টা)
CUTTLY_KEYS = [
    # পুরনো ১১টা
    "e44b823fb02a09939a39c169b27bc15ee199f",
    "8bbe84efcb5a66b174be860f8bae32b63d0da",
    "7ca062975c0c4142a75b6213f6a20fc87cbcb",
    "e75d42f3aae146f30dd42686ba91bfdaf8c19",
    "fd4a5fe2d17a5094133844c75c64ee4e87e43",
    "b8618627fbcad6862440f0ac5adc8d4e97fd6",
    "81efd1a090a10a40c966526d19ded9d31de08",
    "a9262d23b44c9dba76e56628dc4f03e093b59",
    "219be5fb9377a9d7fb7bfba8e622dfa0e09aa",
    "428220825764968c721492e1c07b2a0407112",
    "bce5c6bd9f305fec3706682226553b1636737",
    # নতুন ২১টা
    "ea1f70b8bac17a937521b5032d033374ad263",
    "e4b8b30f63fd53f2f4da37399bc4ec77ab12a",
    "5b5feb95193d6ea6208ae76e76cf2aa8ba57b",
    "c408ea74e293ff2eff978729aef07fcdb3b51",
    "cda0c97dc9643826f863f4f4c149417fa718b",
    "fb8e35635f397f4ce17e61d21879f3debe49c",
    "d0c8a2bf6aa865f9ca1330a36a2e37f28d816",
    "1977e7e28b4395a38b4db19921b3eb8e1eb9c",
    "16e4d523d663de08653d6711e33df74247575",
    "7089691001e5771f3741863096d09456f22ae",
    "760d2e3345bad8a6a0539bb4d5b12afa356c7",
    "9f4ff63b083970b6fe7676c58a9822234c592",
    "ba7a7abf7fc204ebcdf106f4d1af985efa861",
    "9357c9cd8a50ee49995b7c91d28457d92d1ef",
    "89b445fdd1acaffb075635712f6027e964c18",
    "8cf2808a0e07fd2f8ae80f6546a4ba6b71f93",
    "7187730320449eda3f75d46ceb9fbad9f751b",
    "b568b88ff0181926e046a74fc86f788918462",
    "5360a0a26bf2ad65ed7a991d044bc787e8927",
    "4d58ce8def854d5831bbe2c136e917269045a",
    "7e78adc04726b2833fcc6418567b872837027",
]

# ✅ সব TinyURL API Keys (পুরনো ১২টা + নতুন ১টা = মোট ১৩টা)
TINYURL_KEYS = [
    # পুরনো ১২টা
    "jCzJccgmwKs5oGSrleSWRzz3G1mFYYQtuGXGJml5JQEJtiQVBCkH1en1whTZ",
    "wKHhgRP8LXBFHndu8KFtnvGUQyS4GxbOhVqGs3aO9cWk3H9Sdcb7Ihr6Tsaz",
    "wQvOPeI3Fv6KvVBs8eyqAJvyLtfspsA8b1lL4SQ60kfEoO0amLLc4HcXBkos",
    "bF952EfUIZDlIJQneivPqrJHzw2DIghg1ZHQhid5xuXTS0s27yu5nb4OIY0L",
    "kBpZOqiIYlo2sKOrpIihZx8IRFS4XeVlTSoi1pAiISyqhihq00oOa6rfCTxj",
    "I07sYkpGof8hh6RJQkykryvVTcLu11Qazc2dsVmHaluzKZJClpJGAbeJK2rD",
    "d7b5TeRh0XldEj5dkmjjNssiVxrK92yvnW8P385YTzn9kjlZ75c2VmcJPdPX",
    "1vFC2Yy49aod9tmh1JgwcDdJLKKUfzJUWsolxUyD4nohco5cHXtaskyU3Ic5",
    "emxsndlU2ysRlJwhE4uYzFLKQqaZpMF5WRx78ZA9PPeJVJ5giidWmiwBnUgb",
    "kb88dOX28AMsObUPFCsUNpjcPd7FjW9zYwBaObh5sxxbxzw9MRkj934aY5Zf",
    "7wc4Db5YhqMjvkZIXnlPJSO4U33z6vO524MunuAxinDOmZELz5CA4TnnkfLx",
    # নতুন ১টা
    "A0AJOEnf4PtGeRHKNziu9FDYKIs3mukcrZkkQ4Hp1rA1tOMAVmN4fG2Yateg",
]

cuttly_index = 0
tinyurl_index = 0
turn = 0

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
user_urls = {}


def random_string(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def make_unique_url(base_url: str) -> str:
    rand = random_string(10)
    if "?" in base_url:
        return f"{base_url}&_uid={rand}"
    else:
        return f"{base_url}?_uid={rand}"


def shorten_cuttly(long_url: str) -> str:
    global cuttly_index
    attempts = 0
    while attempts < len(CUTTLY_KEYS):
        key = CUTTLY_KEYS[cuttly_index % len(CUTTLY_KEYS)]
        try:
            response = requests.get(
                "https://cutt.ly/api/api.php",
                params={"key": key, "short": long_url},
                timeout=10
            )
            data = response.json()
            status = data.get("url", {}).get("status")
            if status == 7:
                cuttly_index += 1
                return data["url"]["shortLink"]
            else:
                cuttly_index += 1
                attempts += 1
        except:
            cuttly_index += 1
            attempts += 1
    return None


def shorten_tinyurl(long_url: str) -> str:
    global tinyurl_index
    attempts = 0
    while attempts < len(TINYURL_KEYS):
        key = TINYURL_KEYS[tinyurl_index % len(TINYURL_KEYS)]
        try:
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                "https://api.tinyurl.com/create",
                json={"url": long_url},
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                short = data.get("data", {}).get("tiny_url")
                if short:
                    tinyurl_index += 1
                    return short
            tinyurl_index += 1
            attempts += 1
        except:
            tinyurl_index += 1
            attempts += 1

    # সব key শেষ হলে ফ্রি endpoint
    try:
        fallback = requests.get(
            "https://tinyurl.com/api-create.php",
            params={"url": long_url},
            timeout=10
        )
        if fallback.status_code == 200 and fallback.text.startswith("https://"):
            return fallback.text.strip()
    except:
        pass
    return None


def shorten_url(base_url: str) -> str:
    global turn
    unique_url = make_unique_url(base_url)
    if turn == 0:
        result = shorten_cuttly(unique_url)
        turn = 1
    else:
        result = shorten_tinyurl(unique_url)
        turn = 0
    return result


def is_valid_url(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://")


def get_count_buttons():
    keyboard = [
        [
            InlineKeyboardButton("🔟 ১০টা", callback_data="count_10"),
            InlineKeyboardButton("2️⃣0️⃣ ২০টা", callback_data="count_20"),
            InlineKeyboardButton("3️⃣0️⃣ ৩০টা", callback_data="count_30"),
        ],
        [
            InlineKeyboardButton("5️⃣0️⃣ ৫০টা", callback_data="count_50"),
            InlineKeyboardButton("7️⃣5️⃣ ৭৫টা", callback_data="count_75"),
            InlineKeyboardButton("💯 ১০০টা", callback_data="count_100"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ *URL Shortener Bot* ⚡\n\n"
        "🔗 লিংক পাঠাও → কতটা চাও বেছে নাও → ব্যস!\n\n"
        "✅ *৩২টা Cutt.ly + ১৩টা TinyURL key*\n"
        "✅ প্রতিটা লিংক সম্পূর্ণ আলাদা\n"
        "✅ Unlimited ব্যবহার করা যাবে\n"
        "✅ 24/7 চলে\n\n"
        "📌 এখনই যেকোনো লিংক পাঠাও!",
        parse_mode="Markdown"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not is_valid_url(text):
        await update.message.reply_text(
            "⚠️ *Valid URL দাও!*\n`http://` বা `https://` দিয়ে শুরু হতে হবে।",
            parse_mode="Markdown"
        )
        return

    user_id = update.effective_user.id
    user_urls[user_id] = text

    await update.message.reply_text(
        "✅ *লিংক পেয়েছি!*\n\n"
        "👇 *কতটা Short লিংক বানাবে?*",
        parse_mode="Markdown",
        reply_markup=get_count_buttons()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    if not data.startswith("count_"):
        return

    count = int(data.split("_")[1])
    base_url = user_urls.get(user_id)

    if not base_url:
        await query.edit_message_text("⚠️ আগে একটা লিংক পাঠাও!")
        return

    await query.edit_message_text(
        f"⏳ *{count}টি Short লিংক বানানো হচ্ছে...*\n"
        f"একটু অপেক্ষা করো 🙏",
        parse_mode="Markdown"
    )

    short_links = []
    failed = 0

    for i in range(1, count + 1):
        short = shorten_url(base_url)
        if short:
            short_links.append(short)
        else:
            failed += 1

        if i % 10 == 0:
            try:
                await query.edit_message_text(
                    f"⏳ *{i}/{count} টি হয়েছে...*",
                    parse_mode="Markdown"
                )
            except:
                pass

        time.sleep(0.2)

    if not short_links:
        await query.edit_message_text("❌ কোনো লিংক বানানো যায়নি। আবার চেষ্টা করো।")
        return

    await query.edit_message_text(
        f"✅ *{len(short_links)}টি Short লিংক তৈরি হয়েছে!*\n"
        f"{'⚠️ ' + str(failed) + 'টি ব্যর্থ' if failed > 0 else '🎉 সব সফল!'}",
        parse_mode="Markdown"
    )

    # শুধু লিংক পাঠাও
    chunk_size = 20
    for chunk_start in range(0, len(short_links), chunk_size):
        chunk = short_links[chunk_start:chunk_start + chunk_size]
        await update.effective_message.reply_text("\n".join(chunk))
        time.sleep(0.5)

    await update.effective_message.reply_text(
        "🔄 *আরো লিংক বানাতে নতুন লিংক পাঠাও!*",
        parse_mode="Markdown",
        reply_markup=get_count_buttons()
    )


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")


def main():
    print("🤖 URL Shortener Premium Bot চালু হচ্ছে...")
    print(f"✅ Cutt.ly keys: {len(CUTTLY_KEYS)}টা")
    print(f"✅ TinyURL keys: {len(TINYURL_KEYS)}টা")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    print("✅ Bot চালু হয়েছে!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
