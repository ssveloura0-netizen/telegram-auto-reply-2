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
BOT_LINK = "https://t.me/Vixbyulti_bot"
CHANNEL_USERNAME = "rovixbyultimate"
CHANNEL_LINK = "https://t.me/rovixbyultimate"
PUBG_PASSWORD = "WELCOME@TO@CLN"  # 👈 Apna PUBG password yahan daalo

# ==========================================
# 🎬 GIF LINKS
# ==========================================
# Language Selection wala GIF (Kala Chazma / Will Smith)
GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"

# PUBG HACK prompt wala GIF (Mr. Bean)
MR_BEAN_GIF = "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"

# 👇 Userbot ke liye naya GIF (Office wala)
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
        "offline": "I am currently offline. Please leave a message and I will get back to you.",
        "prompt": f"""👋 **Hello!**\n\nPlease choose an option below:""",
        "join_first": f"""🚀 **PUBG HACK UNLOCK**\n\nTo get the PUBG Password, you need to join our official channel first.\n\n🔗 {CHANNEL_LINK}\n\nAfter joining, click the button below 👇""",
        "not_joined": "❌ You haven't joined the channel yet! Please join first.",
        "pubg_pass": f"""🎉 **ACCESS GRANTED**\n\n✅ You are now verified!\n\n🔐 **Your PUBG Password:**\n`{PUBG_PASSWORD}`\n\n⚠️ Keep it safe. Do not share."""
    }
}

for lang in ["hi", "my", "ar", "ur"]:
    MESSAGES[lang] = MESSAGES["en"].copy()

user_langs = {}

# ==========================================
# 1️⃣ USERBOT (Personal Account)
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
        
        # 👇 YAHAN CHANGE KIYA: Ab Userbot naye GIF ke saath reply karega
        await userbot.send_file(
            event.chat_id,
            USERBOT_GIF, # 👈 Naya office wala GIF
            caption=f"I am currently offline. Please contact me here 👉 {BOT_LINK}"
        )
        print(f"📩 Userbot GIF + Link sent to {event.sender_id}")
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
async def start_handler(event):
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
            await bot.send_file(event.chat_id, GIF_URL, caption=LANG_MENU, buttons=buttons)
    except Exception as e:
        print(f"⚠️ Start Error: {e}")

@bot.on(events.CallbackQuery(data=lambda d: d.startswith(b"lang_")))
async def lang_callback(event):
    try:
        lang = event.data.decode().replace("lang_", "")
        user_id = event.sender_id
        if lang not in MESSAGES:
            return
        user_langs[user_id] = lang
        await event.delete()

        option_buttons = [
            [Button.inline("🚀 PUBG HACK", b"opt_pubg")],
            [Button.inline("📞 Contact with Owner", b"opt_contact")],
        ]
        await bot.send_message(event.chat_id, MESSAGES[lang]["prompt"], buttons=option_buttons)
    except Exception as e:
        print(f"⚠️ Lang Error: {e}")

@bot.on(events.CallbackQuery(data=b"opt_pubg"))
async def pubg_handler(event):
    try:
        user_id = event.sender_id
        lang = user_langs.get(user_id, "en")
        await event.delete()

        joined = await is_user_joined(user_id)

        if joined:
            await bot.send_message(event.chat_id, MESSAGES[lang]["pubg_pass"])
        else:
            verify_buttons = [
                [Button.url("🔗 Join Channel", CHANNEL_LINK)],
                [Button.inline("✅ I've Joined", b"verify_join")]
            ]
            await bot.send_file(event.chat_id, MR_BEAN_GIF, caption=MESSAGES[lang]["join_first"], buttons=verify_buttons)
    except Exception as e:
        print(f"⚠️ PUBG Error: {e}")

@bot.on(events.CallbackQuery(data=b"verify_join"))
async def verify_handler(event):
    try:
        user_id = event.sender_id
        lang = user_langs.get(user_id, "en")

        joined = await is_user_joined(user_id)

        if joined:
            await event.delete()
            await bot.send_message(event.chat_id, MESSAGES[lang]["pubg_pass"])
        else:
            await event.answer(MESSAGES[lang]["not_joined"], alert=True)
    except Exception as e:
        print(f"⚠️ Verify Error: {e}")

@bot.on(events.CallbackQuery(data=b"opt_contact"))
async def contact_handler(event):
    try:
        user_id = event.sender_id
        await event.delete()
        await bot.send_message(event.chat_id, f"📞 **Contact the Owner:**\n\nPlease message here: @MG1SHWE")
    except Exception as e:
        print(f"⚠️ Contact Error: {e}")

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
