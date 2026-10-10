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
SESSION_STRING = os.environ.get("SESSION_STRING", "")  # Userbot ke liye
BOT_TOKEN = os.environ.get("BOT_TOKEN")                # BotFather bot ke liye

# ==========================================
# ⚙️ APNI DETAILS YAHAN SET KARO
# ==========================================
BOT_LINK = "https://t.me/Vixby_bot"
CHANNEL_USERNAME = "rovixbyultimate"
CHANNEL_LINK = "https://t.me/rovixbyultimate"
PUBG_PASSWORD = "WELCOME@TO@CLN"  # 👈 Apna password daalo

# ==========================================
# 🎬 GIF LINKS
# ==========================================
GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"     # Kala Chazma
MR_BEAN_GIF = "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif" # Mr. Bean
USERBOT_GIF = "https://media.giphy.com/media/10fxZavhBFXsUE/giphy.gif"     # Office

# ==========================================
# 🌍 MESSAGES
# ==========================================
WELCOME = """╔══════════════════════╗
   🔐 PUBG FILE PASSWORD
╚══════════════════════╝

Welcome! 👋

To get the **PUBG File Password**, click the button below 👇

━━━━━━━━━━━━━━━━━━━━━━
⚠️ You must join our channel first.
📂 **File is pinned in the channel!**
━━━━━━━━━━━━━━━━━━━━━━"""

PUBG_NOT_JOINED = f"""❌ **You haven't joined our channel yet!**

To get the PUBG File Password, please join our official channel first.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {CHANNEL_LINK}

📂 **The PUBG File is PINNED in the channel!**
After joining, check the pinned message.
━━━━━━━━━━━━━━━━━━━━━━

After joining, click **"✅ I've Joined"** button."""

PUBG_PASSWORD_MSG = f"""🎉 **ACCESS GRANTED!**

✅ You are now verified!

━━━━━━━━━━━━━━━━━━━━━━
🔐 **Your PUBG File Password:**
`{PUBG_PASSWORD}`
━━━━━━━━━━━━━━━━━━━━━━

📂 **Don't forget to check the PINNED file in our channel:**
🔗 {CHANNEL_LINK}

⚠️ Keep it safe. Do not share with anyone."""

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

        await userbot.send_file(event.chat_id, USERBOT_GIF, caption=away_text)
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
async def start_handler(event):
    try:
        if not event.is_private:
            return
        buttons = [
            [Button.inline("🔐 Get PUBG File Password", b"get_pubg")],
            [Button.url("📢 Join Our Channel", CHANNEL_LINK)],
        ]
        await bot.send_file(event.chat_id, GIF_URL, caption=WELCOME, buttons=buttons)
    except Exception as e:
        print(f"⚠️ Start Error: {e}")

@bot.on(events.CallbackQuery(data=b"get_pubg"))
async def get_pubg_handler(event):
    try:
        user_id = event.sender_id
        await event.delete()

        joined = await is_user_joined(user_id)

        if joined:
            await bot.send_message(event.chat_id, PUBG_PASSWORD_MSG)
        else:
            verify_buttons = [
                [Button.url("📢 Join Channel", CHANNEL_LINK)],
                [Button.inline("✅ I've Joined", b"verify_join")],
            ]
            await bot.send_file(event.chat_id, MR_BEAN_GIF, caption=PUBG_NOT_JOINED, buttons=verify_buttons)
    except Exception as e:
        print(f"⚠️ PUBG Error: {e}")

@bot.on(events.CallbackQuery(data=b"verify_join"))
async def verify_handler(event):
    try:
        user_id = event.sender_id
        joined = await is_user_joined(user_id)

        if joined:
            await event.delete()
            await bot.send_message(event.chat_id, PUBG_PASSWORD_MSG)
        else:
            await event.answer("❌ You haven't joined the channel yet! Please join first.", alert=True)
    except Exception as e:
        print(f"⚠️ Verify Error: {e}")

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
    # Userbot start karo
    await userbot.start()
    me_user = await userbot.get_me()
    print("=" * 55)
    print("✅ USERBOT RUNNING!")
    print(f"👤 Personal: {me_user.first_name}")
    print("=" * 55)

    # Bot start karo
    await bot.start(bot_token=BOT_TOKEN)
    me_bot = await bot.get_me()
    print("=" * 55)
    print("✅ BOT RUNNING!")
    print(f"🤖 Bot: @{me_bot.username}")
    print("=" * 55)

    # Dono ko ek saath chalao
    await asyncio.gather(
        userbot.run_until_disconnected(),
        bot.run_until_disconnected()
    )

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
