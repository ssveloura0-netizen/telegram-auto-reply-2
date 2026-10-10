from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
from flask import Flask
import asyncio
import os
import json
import threading

# ==========================================
# RENDER ENVIRONMENT VARIABLES
# ==========================================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

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
GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"
MR_BEAN_GIF = "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"
USERBOT_GIF = "https://media.giphy.com/media/10fxZavhBFXsUE/giphy.gif"

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
# 💾 FILE-BASED TRACKING (Render restart ke liye)
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
# tracked_msgs = {"bot": {user_id: [msg_ids]}, "userbot": {user_id: [msg_ids]}}

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

        msg = await userbot.send_file(event.chat_id, USERBOT_GIF, caption=away_text)
        track_userbot(event.sender_id, msg.id)
        print(f"📩 Userbot reply sent to {event.sender_id}")
    except Exception as e:
        print(f"⚠️ Userbot Error: {e}")

# 🗑️ Jab owner reply kare — DONO ke messages delete karo
@userbot.on(events.NewMessage(outgoing=True))
async def owner_cleanup(event):
    try:
        if not event.is_private:
            return
        if event.text and event.text.startswith("/"):
            return

        user_id = str(event.chat_id)
        print(f"👤 Owner replied to {user_id} — cleaning up...")

        deleted = 0

        # 1️⃣ Bot ke messages delete karo
        if user_id in tracked_msgs["bot"]:
            for msg_id in list(tracked_msgs["bot"][user_id]):
                try:
                    await bot.delete_messages(int(user_id), msg_id)
                    deleted += 1
                except Exception:
                    pass
            tracked_msgs["bot"][user_id] = []

        # 2️⃣ Userbot ke messages delete karo
        if user_id in tracked_msgs["userbot"]:
            for msg_id in list(tracked_msgs["userbot"][user_id]):
                try:
                    await userbot.delete_messages(int(user_id), msg_id)
                    deleted += 1
                except Exception:
                    pass
            tracked_msgs["userbot"][user_id] = []

        save_tracking()
        print(f"🗑️ {deleted} messages deleted for {user_id}")
    except Exception as e:
        print(f"⚠️ Owner Cleanup Error: {e}")

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
        buttons = [
            [Button.inline("🔐 Get PUBG File Password", b"get_pubg")],
            [Button.url("📢 Join Our Channel", CHANNEL_LINK)],
        ]
        msg = await bot.send_file(event.chat_id, GIF_URL, caption=WELCOME, buttons=buttons)
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Start Error: {e}")

@bot.on(events.CallbackQuery(data=b"get_pubg"))
async def get_pubg_handler(event):
    try:
        user_id = event.sender_id
        await event.delete()

        joined = await is_user_joined(user_id)

        if joined:
            msg = await bot.send_message(event.chat_id, PUBG_PASSWORD_MSG)
            track_bot(user_id, msg.id)
        else:
            verify_buttons = [
                [Button.url("📢 Join Channel", CHANNEL_LINK)],
                [Button.inline("✅ I've Joined", b"verify_join")],
            ]
            msg = await bot.send_file(event.chat_id, MR_BEAN_GIF, caption=PUBG_NOT_JOINED, buttons=verify_buttons)
            track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ PUBG Error: {e}")

@bot.on(events.CallbackQuery(data=b"verify_join"))
async def verify_handler(event):
    try:
        user_id = event.sender_id
        joined = await is_user_joined(user_id)

        if joined:
            await event.delete()
            msg = await bot.send_message(event.chat_id, PUBG_PASSWORD_MSG)
            track_bot(user_id, msg.id)
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
