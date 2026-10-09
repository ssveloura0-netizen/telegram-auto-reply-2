from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
from flask import Flask
import asyncio
import os
import threading

# ==========================================
# RENDER ENVIRONMENT VARIABLES
# ==========================================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

# ==========================================
# ⚙️ APNI DETAILS YAHAN SET KARO
# ==========================================
BOT_LINK = "https://t.me/Vixby_bot"
CHANNEL_USERNAME = "rovixbyultimate"
CHANNEL_LINK = "https://t.me/rovixbyultimate"
OWNER_CONTACT = "@she_Shutara"
PUBG_PASSWORD = "WELCOME@TO@CLN"  # 👈 Apna password yahan daalo

# ==========================================
# 🎬 GIF LINKS
# ==========================================
GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"
MR_BEAN_GIF = "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"
USERBOT_GIF = "https://media.giphy.com/media/10fxZavhBFXsUE/giphy.gif"

# ==========================================
# 🌍 MESSAGES
# ==========================================
LANG_MENU = """╔══════════════════════╗
   🌐  LANGUAGE SELECTION
╚══════════════════════╝

Welcome! Please select your preferred language.

━━━━━━━━━━━━━━━━━━━━━━
👇 **Tap a button below to continue**
━━━━━━━━━━━━━━━━━━━━━━"""

MESSAGES = {
    "en": {
        "prompt": "👋 **Hello!**\n\nPlease choose an option below:",
        "join_first": f"""🚀 **PUBG FILE PASSWORD UNLOCK**

To get the PUBG File Password, you need to join our official channel first.

🔗 {CHANNEL_LINK}

After joining, click the button below 👇""",
        "not_joined": "❌ You haven't joined the channel yet! Please join first.",
        "pubg_pass": f"""🎉 **ACCESS GRANTED**

✅ You are now verified!

🔐 **Your PUBG File Password:**
`{PUBG_PASSWORD}`

⚠️ Keep it safe. Do not share.""",
        "contact": f"""📞 **Contact the Owner:**

Please message here: {OWNER_CONTACT}"""
    }
}

for lang in ["hi", "my", "ar", "ur"]:
    MESSAGES[lang] = MESSAGES["en"].copy()

user_langs = {}

# ==========================================
# 🗑️ MESSAGE TRACKING (Delete ke liye)
# ==========================================
# Har user ke liye, bot aur userbot ke messages ki IDs alag-alag save karo
tracked_bot_msgs = {}      # {user_id: [msg_id1, ...]}  -> Bot ke messages
tracked_userbot_msgs = {}  # {user_id: [msg_id1, ...]}  -> Userbot ke messages


def track_bot_msg(user_id, msg_id):
    if user_id not in tracked_bot_msgs:
        tracked_bot_msgs[user_id] = []
    tracked_bot_msgs[user_id].append(msg_id)


def track_userbot_msg(user_id, msg_id):
    if user_id not in tracked_userbot_msgs:
        tracked_userbot_msgs[user_id] = []
    tracked_userbot_msgs[user_id].append(msg_id)


# ==========================================
# 1️⃣ USERBOT (Personal Account)
# ==========================================
userbot = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


@userbot.on(events.NewMessage(incoming=True))
async def userbot_incoming(event):
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
🔗 https://t.me/rovixbyultimate

📂 **HACK FILE PINNED** in the channel! Join now to grab it.

🤖 **Contact My Assistant Bot:**
👉 {BOT_LINK}

━━━━━━━━━━━━━━━━━━━━━━━
⏳ Please wait for my reply. Thank you!"""

        sent = await userbot.send_file(event.chat_id, USERBOT_GIF, caption=away_text)
        # Userbot ke bheje message ko track karo
        track_userbot_msg(event.sender_id, sent.id)
        print(f"📩 Userbot reply sent to {event.sender_id}")
    except Exception as e:
        print(f"⚠️ Userbot Error: {e}")


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


@bot.on(events.NewMessage(pattern=r'^/start$'))
async def bot_start(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id

        if user_id not in user_langs:
            buttons = [
                [Button.inline("🇬🇧 English", b"lang_en")],
                [Button.inline("🇮🇳 हिन्दी (Hindi)", b"lang_hi")],
                [Button.inline("🇲🇲 မြန်မာ (Burmese)", b"lang_my")],
                [Button.inline("🇸🇦 العربية (Arabic)", b"lang_ar")],
                [Button.inline("🇵🇰 اردو (Urdu)", b"lang_ur")],
            ]
            msg = await bot.send_file(event.chat_id, GIF_URL, caption=LANG_MENU, buttons=buttons)
            track_bot_msg(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Start Error: {e}")


@bot.on(events.CallbackQuery(data=lambda d: d.startswith(b"lang_")))
async def bot_lang(event):
    try:
        lang = event.data.decode().replace("lang_", "")
        user_id = event.sender_id
        if lang not in MESSAGES:
            return
        user_langs[user_id] = lang
        await event.delete()

        buttons = [
            [Button.inline("🔐 PUBG FILE PASSWORD", b"opt_pubg")],
            [Button.inline("📞 Contact with Owner", b"opt_contact")],
        ]
        msg = await bot.send_message(event.chat_id, MESSAGES[lang]["prompt"], buttons=buttons)
        track_bot_msg(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Lang Error: {e}")


@bot.on(events.CallbackQuery(data=b"opt_pubg"))
async def bot_pubg(event):
    try:
        user_id = event.sender_id
        lang = user_langs.get(user_id, "en")
        await event.delete()

        joined = await is_user_joined(user_id)

        if joined:
            msg = await bot.send_message(event.chat_id, MESSAGES[lang]["pubg_pass"])
            track_bot_msg(user_id, msg.id)
        else:
            buttons = [
                [Button.url("🔗 Join Channel", CHANNEL_LINK)],
                [Button.inline("✅ I've Joined", b"verify_join")]
            ]
            msg = await bot.send_file(event.chat_id, MR_BEAN_GIF, caption=MESSAGES[lang]["join_first"], buttons=buttons)
            track_bot_msg(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ PUBG Error: {e}")


@bot.on(events.CallbackQuery(data=b"verify_join"))
async def bot_verify(event):
    try:
        user_id = event.sender_id
        lang = user_langs.get(user_id, "en")

        joined = await is_user_joined(user_id)
        if joined:
            await event.delete()
            msg = await bot.send_message(event.chat_id, MESSAGES[lang]["pubg_pass"])
            track_bot_msg(user_id, msg.id)
        else:
            await event.answer(MESSAGES[lang]["not_joined"], alert=True)
    except Exception as e:
        print(f"⚠️ Verify Error: {e}")


@bot.on(events.CallbackQuery(data=b"opt_contact"))
async def bot_contact(event):
    try:
        user_id = event.sender_id
        lang = user_langs.get(user_id, "en")
        await event.delete()
        msg = await bot.send_message(event.chat_id, MESSAGES[lang]["contact"])
        track_bot_msg(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Contact Error: {e}")


# ==========================================
# 🗑️ AUTO-DELETE: Jab OWNER manually reply kare
# ==========================================
@userbot.on(events.NewMessage(outgoing=True))
async def owner_reply(event):
    try:
        if not event.is_private:
            return
        if event.text and event.text.startswith("/"):
            return

        user_id = event.chat_id
        print(f"👤 Owner replied to {user_id} — cleaning up...")

        # 1️⃣ Bot ke messages delete karo (bot khud delete karega)
        if user_id in tracked_bot_msgs and tracked_bot_msgs[user_id]:
            for msg_id in list(tracked_bot_msgs[user_id]):
                try:
                    await bot.delete_messages(user_id, msg_id)
                except Exception as e:
                    print(f"⚠️ Bot delete skip: {e}")
            tracked_bot_msgs[user_id] = []
            print(f"🗑️ Bot messages cleared for {user_id}")

        # 2️⃣ Userbot ke messages delete karo (userbot khud delete karega)
        if user_id in tracked_userbot_msgs and tracked_userbot_msgs[user_id]:
            for msg_id in list(tracked_userbot_msgs[user_id]):
                try:
                    await userbot.delete_messages(user_id, msg_id)
                except Exception as e:
                    print(f"⚠️ Userbot delete skip: {e}")
            tracked_userbot_msgs[user_id] = []
            print(f"🗑️ Userbot messages cleared for {user_id}")

    except Exception as e:
        print(f"⚠️ Owner Reply Error: {e}")


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
    print("=" * 55)

    await asyncio.gather(
        userbot.run_until_disconnected(),
        bot.run_until_disconnected()
    )


if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
