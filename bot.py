"""
URL Shortener Telegram Bot - Premium v7
========================================
- Cutt.ly, TinyURL, Spoo.me (API key header দিয়ে)
- সব মোড

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

TELEGRAM_TOKEN = "8976897474:AAH3LtHE7ESulO7XPoEwENAYSwtp6fgRQws"
SPOOME_API_KEY = "spoo_7jx8npCBVV-uIjaNOo8RN1pPAKOyW9Hp7I4g4E9KDuQ"

CUTTLY_KEYS = [
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

TINYURL_KEYS = [
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
    "A0AJOEnf4PtGeRHKNziu9FDYKIs3mukcrZkkQ4Hp1rA1tOMAVmN4fG2Yateg",
]

cuttly_index = 0
tinyurl_index = 0
mix_turn = 0
pair_turns = {"ct": 0, "ts": 0, "cs": 0}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
user_data = {}


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
            url_data = data.get("url", {})
            status = url_data.get("status")
            if status in [7, 2]:
                cuttly_index += 1
                return url_data.get("shortLink")
            else:
                cuttly_index += 1
                attempts += 1
        except Exception as e:
            logger.error(f"Cutt.ly error: {e}")
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
        except Exception as e:
            logger.error(f"TinyURL error: {e}")
            tinyurl_index += 1
            attempts += 1
    # Fallback
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


def shorten_spoome(long_url: str) -> str:
    """Spoo.me — API key header এ পাঠাও"""
    try:
        response = requests.post(
            "https://spoo.me/",
            data={"url": long_url},
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-API-Key": SPOOME_API_KEY
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            short = data.get("short_url")
            if short:
                if not short.startswith("http"):
                    short = "https://spoo.me/" + short
                return short
        # API key ছাড়া try করো
        response2 = requests.post(
            "https://spoo.me/",
            data={"url": long_url},
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=10
        )
        if response2.status_code == 200:
            data = response2.json()
            short = data.get("short_url")
            if short:
                if not short.startswith("http"):
                    short = "https://spoo.me/" + short
                return short
        logger.error(f"Spoo.me: {response.status_code} - {response.text[:100]}")
        return None
    except Exception as e:
        logger.error(f"Spoo.me exception: {e}")
        return None


def shorten_by_mode(base_url: str, mode: str) -> str:
    global mix_turn, pair_turns
    unique_url = make_unique_url(base_url)

    if mode == "mix":
        if mix_turn == 0:
            result = shorten_cuttly(unique_url)
            mix_turn = 1
        elif mix_turn == 1:
            result = shorten_tinyurl(unique_url)
            mix_turn = 2
        else:
            result = shorten_spoome(unique_url)
            mix_turn = 0
        return result
    elif mode == "ct":
        if pair_turns["ct"] == 0:
            result = shorten_cuttly(unique_url)
            pair_turns["ct"] = 1
        else:
            result = shorten_tinyurl(unique_url)
            pair_turns["ct"] = 0
        return result
    elif mode == "ts":
        if pair_turns["ts"] == 0:
            result = shorten_tinyurl(unique_url)
            pair_turns["ts"] = 1
        else:
            result = shorten_spoome(unique_url)
            pair_turns["ts"] = 0
        return result
    elif mode == "cs":
        if pair_turns["cs"] == 0:
            result = shorten_cuttly(unique_url)
            pair_turns["cs"] = 1
        else:
            result = shorten_spoome(unique_url)
            pair_turns["cs"] = 0
        return result
    elif mode == "cuttly":
        return shorten_cuttly(unique_url)
    elif mode == "tinyurl":
        return shorten_tinyurl(unique_url)
    elif mode == "spoome":
        return shorten_spoome(unique_url)
    return None


def is_valid_url(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://")


def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🔀 Auto Mix", callback_data="mode_mix")],
        [InlineKeyboardButton("🟢+🔵 Cutt.ly & TinyURL", callback_data="mode_ct")],
        [InlineKeyboardButton("🔵+🟣 TinyURL & Spoo.me", callback_data="mode_ts")],
        [InlineKeyboardButton("🟢+🟣 Cutt.ly & Spoo.me", callback_data="mode_cs")],
        [
            InlineKeyboardButton("🟢 Cutt.ly", callback_data="mode_cuttly"),
            InlineKeyboardButton("🔵 TinyURL", callback_data="mode_tinyurl"),
            InlineKeyboardButton("🟣 Spoo.me", callback_data="mode_spoome"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_count_buttons():
    keyboard = [
        [
            InlineKeyboardButton("1️⃣ ১টা", callback_data="count_1"),
            InlineKeyboardButton("🔟 ১০টা", callback_data="count_10"),
            InlineKeyboardButton("2️⃣0️⃣ ২০টা", callback_data="count_20"),
        ],
        [
            InlineKeyboardButton("3️⃣0️⃣ ৩০টা", callback_data="count_30"),
            InlineKeyboardButton("5️⃣0️⃣ ৫০টা", callback_data="count_50"),
            InlineKeyboardButton("💯 ১০০টা", callback_data="count_100"),
        ],
        [InlineKeyboardButton("🔙 পিছে যাও", callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ *URL Shortener Bot* ⚡\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔀 *Auto Mix* — তিনটা পালা করে\n"
        "🟢+🔵 *Cutt.ly & TinyURL*\n"
        "🔵+🟣 *TinyURL & Spoo.me*\n"
        "🟢+🟣 *Cutt.ly & Spoo.me*\n"
        "🟢 *Cutt.ly Only*\n"
        "🔵 *TinyURL Only*\n"
        "🟣 *Spoo.me Only*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📌 *এখনই যেকোনো লিংক পাঠাও!*",
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
    user_data[user_id] = {"url": text, "mode": None}

    await update.message.reply_text(
        f"✅ *লিংক পেয়েছি!*\n\n"
        f"🔗 `{text}`\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👇 *কোন মোডে Short করবে?*",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    if data == "back_menu":
        if user_id in user_data and user_data[user_id].get("url"):
            url = user_data[user_id]["url"]
            await query.edit_message_text(
                f"✅ *লিংক পেয়েছি!*\n\n🔗 `{url}`\n\n"
                f"━━━━━━━━━━━━━━━━━━\n👇 *কোন মোডে Short করবে?*",
                parse_mode="Markdown",
                reply_markup=get_main_menu()
            )
        return

    if data.startswith("mode_"):
        mode = data.split("_")[1]
        if user_id not in user_data:
            await query.edit_message_text("⚠️ আগে একটা লিংক পাঠাও!")
            return

        user_data[user_id]["mode"] = mode
        mode_names = {
            "mix": "🔀 Auto Mix",
            "ct": "🟢+🔵 Cutt.ly & TinyURL",
            "ts": "🔵+🟣 TinyURL & Spoo.me",
            "cs": "🟢+🟣 Cutt.ly & Spoo.me",
            "cuttly": "🟢 Cutt.ly Only",
            "tinyurl": "🔵 TinyURL Only",
            "spoome": "🟣 Spoo.me Only",
        }
        await query.edit_message_text(
            f"✅ *{mode_names.get(mode)}* সিলেক্ট!\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👇 *কতটা Short লিংক বানাবে?*",
            parse_mode="Markdown",
            reply_markup=get_count_buttons()
        )
        return

    if data.startswith("count_"):
        count = int(data.split("_")[1])
        if user_id not in user_data or not user_data[user_id].get("url"):
            await query.edit_message_text("⚠️ আগে একটা লিংক পাঠাও!")
            return

        base_url = user_data[user_id]["url"]
        mode = user_data[user_id].get("mode", "mix")
        mode_names = {
            "mix": "🔀 Auto Mix",
            "ct": "🟢+🔵 Cutt.ly & TinyURL",
            "ts": "🔵+🟣 TinyURL & Spoo.me",
            "cs": "🟢+🟣 Cutt.ly & Spoo.me",
            "cuttly": "🟢 Cutt.ly",
            "tinyurl": "🔵 TinyURL",
            "spoome": "🟣 Spoo.me",
        }

        await query.edit_message_text(
            f"⏳ *{mode_names.get(mode)} দিয়ে {count}টি লিংক বানানো হচ্ছে...*\n"
            f"একটু অপেক্ষা করো 🙏",
            parse_mode="Markdown"
        )

        short_links = []
        failed = 0

        for i in range(1, count + 1):
            short = shorten_by_mode(base_url, mode)
            if short:
                short_links.append(short)
            else:
                failed += 1

            if count > 1 and i % 10 == 0:
                try:
                    await query.edit_message_text(
                        f"⏳ *{i}/{count} টি হয়েছে...*",
                        parse_mode="Markdown"
                    )
                except:
                    pass
            time.sleep(0.3)

        if not short_links:
            await query.edit_message_text(
                "❌ কোনো লিংক বানানো যায়নি।\nঅন্য মোড চেষ্টা করো।"
            )
            return

        await query.edit_message_text(
            f"✅ *{len(short_links)}টি Short লিংক তৈরি!*\n"
            f"{'⚠️ ' + str(failed) + 'টি ব্যর্থ' if failed > 0 else '🎉 সব সফল!'}",
            parse_mode="Markdown"
        )

        chunk_size = 20
        for chunk_start in range(0, len(short_links), chunk_size):
            chunk = short_links[chunk_start:chunk_start + chunk_size]
            await update.effective_message.reply_text("\n".join(chunk))
            time.sleep(0.3)

        await update.effective_message.reply_text(
            "━━━━━━━━━━━━━━━━━━\n🔄 *আরো লিংক বানাতে নতুন লিংক পাঠাও!*",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")


def main():
    print("🤖 URL Shortener Premium Bot v7 চালু হচ্ছে...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    print("✅ Bot চালু হয়েছে!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
