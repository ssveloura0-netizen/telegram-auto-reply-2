from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
from deep_translator import GoogleTranslator
from flask import Flask
import asyncio
import os
import json
import threading
from datetime import datetime

# ==========================================
# RENDER ENVIRONMENT VARIABLES
# ==========================================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

# ==========================================
# ⚙️ APNI DETAILS
# ==========================================
BOT_LINK = "https://t.me/Vixby_bot"
CHANNEL_USERNAME = "rovixbyultimate"
CHANNEL_LINK = "https://t.me/rovixbyultimate"
DM_ADMIN_1 = "@ROVIXU1ti"
DM_ADMIN_2 = "@she_Shutara"

# ==========================================
# 🎬 GIF LINKS
# ==========================================
GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"
MR_BEAN_GIF = "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"
USERBOT_GIF = "https://media.giphy.com/media/10fxZavhBFXsUE/giphy.gif"

# ==========================================
# 🔄 LANG CODES (tr// ke liye)
# ==========================================
LANG_CODES = {
    "en": "en", "hi": "hi", "mm": "my", "ar": "ar",
    "ur": "ur", "th": "th", "vi": "vi", "eg": "ar",
}

user_langs = {}
user_back_state = {}  # BACK button ke liye state tracking

# ==========================================
# 🎯 MESSAGES
# ==========================================
WELCOME_MSG = """💎 **ROVIXBY BOT**
🚀 **PROFESSIONAL GAMING SERVICE**

━━━━━━━━━━━━━━━━━━━━━━

✨ **Welcome!**

Select an option below.

🤖 Bot created by @ROVIXU1ti

━━━━━━━━━━━━━━━━━━━━━━"""

PUBG_MENU_MSG = """🎮 **PUBG** 🎮

━━━━━━━━━━━━━━━━━━━━━━

**What do you need?**"""

PUBG_FREE_MSG = f"""🎮 **PUBG FREE MODS**

━━━━━━━━━━━━━━━━━━━━━━

📢 **JOIN OUR CHANNEL:**
🔗 {CHANNEL_LINK}

📂 **CHECK PINNED MESSAGE**
After joining, check the pinned message for free files.

━━━━━━━━━━━━━━━━━━━━━━

✅ Enjoy free mods & hacks!"""

PUBG_DURATION_MSG = """🎯 **SELECT DURATION**

━━━━━━━━━━━━━━━━━━━━━━

📅 **Choose your plan:**

━━━━━━━━━━━━━━━━━━━━━━"""

PUBG_FULL_SEASON_MSG = f"""🎯 **FULL SEASON**

━━━━━━━━━━━━━━━━━━━━━━

💰 **Price: $15 / 25,000 KS**

━━━━━━━━━━━━━━━━━━━━━━

📩 Contact admin for purchase:
👤 {DM_ADMIN_1}
👤 {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

⏳ Reply time: Usually within 24 hours"""

PUBG_ONE_MONTH_MSG = f"""📅 **ONE MONTH PACKAGE**

━━━━━━━━━━━━━━━━━━━━━━

💰 **Price: $7 / 15,000 KS**

━━━━━━━━━━━━━━━━━━━━━━

📩 Contact admin for purchase:
👤 {DM_ADMIN_1}
👤 {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

⏳ Reply time: Usually within 24 hours"""

MLBB_MENU_MSG = """🎮 **MOBILE LEGENDS** 🎮

━━━━━━━━━━━━━━━━━━━━━━

**Choose an option:**"""

MLBB_PURCHASE_MSG = f"""🎮 **MOBILE LEGENDS PURCHASE**

━━━━━━━━━━━━━━━━━━━━━━

💰 **Price: 5000 KS / $2 per file**

━━━━━━━━━━━━━━━━━━━━━━
💳 **PAYMENT METHODS:**
━━━━━━━━━━━━━━━━━━━━━━

📱 **KBZ Pay:**
   09897052554 (Raw Eis)

📱 **Wave Pay:**
   Contact Admin
   👤 {DM_ADMIN_1}
   👤 {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

📸 After payment, send screenshot to:
👤 {DM_ADMIN_1}
👤 {DM_ADMIN_2}

⏳ Reply time: Usually within 24 hours"""

CONTACT_MSG = f"""📞 **CONTACT OWNER**

━━━━━━━━━━━━━━━━━━━━━━

👤 Admin 1: {DM_ADMIN_1}
👤 Admin 2: {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

⏳ Reply time: Usually within 24 hours"""

JOIN_CHANNEL_MSG = f"""📢 **JOIN OUR CHANNEL**

━━━━━━━━━━━━━━━━━━━━━━

🔗 {CHANNEL_LINK}

📂 **Check the pinned message after joining!**

━━━━━━━━━━━━━━━━━━━━━━"""

LANGUAGE_MSG = """🌐 **SELECT LANGUAGE**

━━━━━━━━━━━━━━━━━━━━━━

**Choose your language:**"""

FEEDBACK_MSG = f"""💬 **FEEDBACK**

━━━━━━━━━━━━━━━━━━━━━━

We'd love to hear your feedback!

Please send your feedback to:
👤 {DM_ADMIN_1}
👤 {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

Thank you for your support! ❤️"""

DM_ADMIN_MSG = f"""📩 **DM the Admin:**

👤 {DM_ADMIN_1}
👤 {DM_ADMIN_2}

⏳ Please wait for their reply."""

# ==========================================
# ⌨️ KEYBOARDS
# ==========================================
def main_menu_keyboard():
    return [
        [Button.text("🎮 PUBG"), Button.text("🎮 MLBB")],
        [Button.text("📞 CONTACT"), Button.text("📢 JOIN CHANNEL")],
        [Button.text("🌐 LANGUAGE"), Button.text("💬 FEEDBACK")],
    ]

def pubg_menu_keyboard():
    return [
        [Button.text("🎁 FREE"), Button.text("💳 PUBG PURCHASE")],
        [Button.text("⬅️ BACK")],
    ]

def pubg_purchase_keyboard():
    return [
        [Button.text("🎯 FULL SEASON")],
        [Button.text("📅 ONE MONTH")],
        [Button.text("⬅️ BACK")],
    ]

def dm_admin_keyboard():
    return [
        [Button.text("💬 DM ADMIN")],
        [Button.text("⬅️ BACK")],
    ]

def mlbb_menu_keyboard():
    return [
        [Button.text("💳 MLBB PURCHASE")],
        [Button.text("⬅️ BACK")],
    ]

def back_keyboard():
    return [[Button.text("⬅️ BACK")]]

def language_keyboard():
    return [
        [Button.text("🇬🇧 EN"), Button.text("🇲🇲 MM")],
        [Button.text("🇮🇳 HI"), Button.text("🇸🇦 AR")],
        [Button.text("🇵🇰 UR"), Button.text("🇹🇭 TH")],
        [Button.text("🇻🇳 VI"), Button.text("🇪🇬 EG")],
        [Button.text("⬅️ BACK")],
    ]

def join_keyboard():
    return [
        [Button.url("🔗 Join Channel", CHANNEL_LINK)],
        [Button.text("⬅️ BACK")],
    ]

# ==========================================
# 💾 FILE-BASED TRACKING
# ==========================================
TRACK_FILE = "tracked_messages.json"

def load_tracking():
    try:
        if os.path.exists(TRACK_FILE):
            with open(TRACK_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Load error: {e}")
    return {"bot": {}, "userbot": {}}

def save_tracking():
    try:
        with open(TRACK_FILE, "w") as f:
            json.dump(tracked_msgs, f)
    except Exception as e:
        print(f"⚠️ Save error: {e}")

tracked_msgs = load_tracking()

def track_bot(user_id, msg_id):
    uid = str(user_id)
    if uid not in tracked_msgs["bot"]:
        tracked_msgs["bot"][uid] = []
    tracked_msgs["bot"][uid].append(msg_id)
    save_tracking()

def track_userbot(user_id, msg_id):
    uid = str(user_id)
    if uid not in tracked_msgs["userbot"]:
        tracked_msgs["userbot"][uid] = []
    tracked_msgs["userbot"][uid].append(msg_id)
    save_tracking()

# ==========================================
# 🔔 OWNER NOTIFICATION
# ==========================================
async def notify_owner(title, details):
    try:
        if OWNER_ID == 0:
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await bot.send_message(OWNER_ID, f"{title}\n\n{details}\n\n📅 Time: {now}")
    except Exception as e:
        print(f"⚠️ Notify error: {e}")

# ==========================================
# 1️⃣ USERBOT
# ==========================================
userbot = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@userbot.on(events.NewMessage(incoming=True))
async def userbot_handler(event):
    try:
        if not event.is_private:
            return
        me = await userbot.get_me()
        if event.sender_id == me.id:
            return

        away_text = f"""╔═════════════════════════╗
       💤  OFFLINE MODE
╚═════════════════════════╝

Hello,

Thank you for contacting me. I am currently **offline** right now and will get back to you as soon as possible.

📢 **JOIN OUR OFFICIAL CHANNEL**
🔗 {CHANNEL_LINK}

📂 **HACK FILE IS PINNED** in the channel! Join now to grab it.

🤖 **Contact My Assistant Bot:**
👉 {BOT_LINK}

━━━━━━━━━━━━━━━━━━━━━━━
⏳ Please wait for my reply. Thank you!"""

        msg = await userbot.send_file(event.chat_id, USERBOT_GIF, caption=away_text)
        track_userbot(event.sender_id, msg.id)

        try:
            sender = await event.get_sender()
            username = f"@{sender.username}" if sender.username else "No username"
            await notify_owner(
                "📩 **New Personal Message!**",
                f"👤 Name: {sender.first_name}\n"
                f"🔗 Username: {username}\n"
                f"🆔 ID: `{event.sender_id}`\n"
                f"💬 Message: {event.raw_text[:100]}"
            )
        except Exception:
            pass

        print(f"📩 Userbot reply sent to {event.sender_id}")
    except Exception as e:
        print(f"⚠️ Userbot Error: {e}")

# 🗑️ OWNER REPLY + tr// TRANSLATION
@userbot.on(events.NewMessage(outgoing=True))
async def owner_reply_handler(event):
    try:
        if not event.is_private:
            return

        user_id = event.chat_id
        text = event.text or ""

        # 🌐 tr// TRANSLATION
        if text.startswith("tr//"):
            try:
                parts = text.split(" ", 1)
                lang_code = parts[0].replace("tr//", "").lower()
                message_to_translate = parts[1] if len(parts) > 1 else ""

                if lang_code in LANG_CODES and message_to_translate:
                    translated = GoogleTranslator(source="en", target=LANG_CODES[lang_code]).translate(message_to_translate)
                    await userbot.send_message(user_id, translated)
                    print(f"✅ Translated ({lang_code}): {message_to_translate} → {translated}")
                    await event.delete()
                    return
            except Exception as e:
                print(f"⚠️ Translation error: {e}")

        # 🗑️ AUTO-DELETE
        if text and text.startswith("/"):
            return

        print(f"👤 Owner replied to {user_id} — cleaning up...")
        deleted = 0

        if str(user_id) in tracked_msgs["bot"]:
            for msg_id in list(tracked_msgs["bot"][str(user_id)]):
                try:
                    await bot.delete_messages(user_id, msg_id)
                    deleted += 1
                except Exception:
                    pass
            tracked_msgs["bot"][str(user_id)] = []

        if str(user_id) in tracked_msgs["userbot"]:
            for msg_id in list(tracked_msgs["userbot"][str(user_id)]):
                try:
                    await userbot.delete_messages(user_id, msg_id)
                    deleted += 1
                except Exception:
                    pass
            tracked_msgs["userbot"][str(user_id)] = []

        save_tracking()
        print(f"🗑️ {deleted} messages deleted for {user_id}")
    except Exception as e:
        print(f"⚠️ Owner Reply Error: {e}")

# ==========================================
# 2️⃣ BOTFATHER BOT
# ==========================================
bot = TelegramClient('bot_session', API_ID, API_HASH)

async def is_user_joined(user_id):
    try:
        await bot(GetParticipantRequest(channel=CHANNEL_USERNAME, participant=user_id))
        return True
    except UserNotParticipantError:
        return False
    except ChatAdminRequiredError:
        print("⚠️ Bot ko channel ka admin banao!")
        return False
    except Exception as e:
        print(f"⚠️ Group check error: {e}")
        return False

# === START ===
@bot.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id

        try:
            sender = await event.get_sender()
            username = f"@{sender.username}" if sender.username else "No username"
            await notify_owner(
                "🔔 **New User Started Bot!**",
                f"👤 Name: {sender.first_name}\n🔗 Username: {username}\n🆔 ID: `{user_id}`"
            )
        except Exception:
            pass

        msg = await bot.send_message(event.chat_id, WELCOME_MSG, buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Start Error: {e}")

# === PUBG MENU ===
@bot.on(events.NewMessage(pattern=r'^🎮 PUBG$'))
async def pubg_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_MENU_MSG, buttons=pubg_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ PUBG Error: {e}")

# === PUBG FREE ===
@bot.on(events.NewMessage(pattern=r'^🎁 FREE$'))
async def pubg_free_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_FREE_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ PUBG FREE Error: {e}")

# === PUBG PURCHASE ===
@bot.on(events.NewMessage(pattern=r'^💳 PUBG PURCHASE$'))
async def pubg_purchase_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_DURATION_MSG, buttons=pubg_purchase_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ PUBG Purchase Error: {e}")

# === FULL SEASON ===
@bot.on(events.NewMessage(pattern=r'^🎯 FULL SEASON$'))
async def full_season_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_FULL_SEASON_MSG, buttons=dm_admin_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Full Season Error: {e}")

# === ONE MONTH ===
@bot.on(events.NewMessage(pattern=r'^📅 ONE MONTH$'))
async def one_month_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_ONE_MONTH_MSG, buttons=dm_admin_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ One Month Error: {e}")

# === MLBB MENU ===
@bot.on(events.NewMessage(pattern=r'^🎮 MLBB$'))
async def mlbb_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, MLBB_MENU_MSG, buttons=mlbb_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ MLBB Error: {e}")

# === MLBB PURCHASE ===
@bot.on(events.NewMessage(pattern=r'^💳 MLBB PURCHASE$'))
async def mlbb_purchase_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, MLBB_PURCHASE_MSG, buttons=dm_admin_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ MLBB Purchase Error: {e}")

# === CONTACT ===
@bot.on(events.NewMessage(pattern=r'^📞 CONTACT$'))
async def contact_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, CONTACT_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Contact Error: {e}")

# === JOIN CHANNEL ===
@bot.on(events.NewMessage(pattern=r'^📢 JOIN CHANNEL$'))
async def join_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, JOIN_CHANNEL_MSG, buttons=join_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Join Error: {e}")

# === LANGUAGE ===
@bot.on(events.NewMessage(pattern=r'^🌐 LANGUAGE$'))
async def language_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, LANGUAGE_MSG, buttons=language_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Language Error: {e}")

# === LANGUAGE SELECT ===
@bot.on(events.NewMessage(pattern=r'^(🇬🇧 EN|🇲🇲 MM|🇮🇳 HI|🇸🇦 AR|🇵🇰 UR|🇹🇭 TH|🇻🇳 VI|🇪🇬 EG)$'))
async def lang_select(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        text = event.text

        lang_map = {
            "🇬🇧 EN": "en", "🇲🇲 MM": "my", "🇮🇳 HI": "hi", "🇸🇦 AR": "ar",
            "🇵🇰 UR": "ur", "🇹🇭 TH": "th", "🇻🇳 VI": "vi", "🇪🇬 EG": "eg",
        }
        lang = lang_map.get(text, "en")
        user_langs[user_id] = lang

        try:
            sender = await event.get_sender()
            await notify_owner(
                "🌐 **Language Selected!**",
                f"👤 Name: {sender.first_name}\n🆔 ID: `{user_id}`\n🗣️ Language: `{lang.upper()}`"
            )
        except Exception:
            pass

        msg = await bot.send_message(event.chat_id, f"✅ Language set to **{text}**\n\nNow use the menu below:", buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Lang Select Error: {e}")

# === FEEDBACK ===
@bot.on(events.NewMessage(pattern=r'^💬 FEEDBACK$'))
async def feedback_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, FEEDBACK_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Feedback Error: {e}")

# === BACK ===
@bot.on(events.NewMessage(pattern=r'^⬅️ BACK$'))
async def back_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, WELCOME_MSG, buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Back Error: {e}")

# === DM ADMIN ===
@bot.on(events.NewMessage(pattern=r'^💬 DM ADMIN$'))
async def dm_admin_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, DM_ADMIN_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ DM Admin Error: {e}")

# ==========================================
# 🌐 WEB SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# MAIN
# ==========================================
async def main():
    await userbot.start()
    me_user = await userbot.get_me()
    print("=" * 55)
    print("✅ USERBOT RUNNING!")
    print(f"👤 Personal: {me_user.first_name}")
    print("=" * 55)

    await bot.start(bot_token=BOT_TOKEN)
    me_bot = await bot.get_me()
    print("=" * 55)
    print("✅ BOT RUNNING!")
    print(f"🤖 Bot: @{me_bot.username}")
    print(f"👤 Owner ID: {OWNER_ID}")
    print("=" * 55)

    await asyncio.gather(
        userbot.run_until_disconnected(),
        bot.run_until_disconnected()
    )

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
