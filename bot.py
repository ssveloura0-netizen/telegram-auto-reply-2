from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
from deep_translator import GoogleTranslator
from openai import OpenAI
from PIL import Image
from flask import Flask
import asyncio
import os
import json
import threading
import requests
import base64
import re
import time
from datetime import datetime

# ==========================================
# ENV VARIABLES
# ==========================================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# ==========================================
# APNI DETAILS
# ==========================================
BOT_LINK = "https://t.me/Vixby_bot"
CHANNEL_USERNAME = "rovixbyultimate"
CHANNEL_LINK = "https://t.me/rovixbyultimate"
DM_ADMIN_1 = "@ROVIXU1ti"
DM_ADMIN_2 = "@she_Shutara"

# ==========================================
# AI CLIENTS
# ==========================================
ai_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY) if GROQ_API_KEY else None
ocr_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None

VISION_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.2-11b-vision-instruct:free",
]

# ==========================================
# GIF LINKS
# ==========================================
GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"
MR_BEAN_GIF = "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"
USERBOT_GIF = "https://media.giphy.com/media/10fxZavhBFXsUE/giphy.gif"

# ==========================================
# LANG CODES
# ==========================================
LANG_CODES = {
    "en": "en", "hi": "hi", "mm": "my", "ar": "ar",
    "ur": "ur", "th": "th", "vi": "vi", "eg": "ar",
    "bn": "bn", "id": "id", "zh": "zh-CN", "ja": "ja",
    "ko": "ko", "ru": "ru", "es": "es", "fr": "fr",
    "pt": "pt", "de": "de", "tr": "tr", "fa": "fa",
}

user_langs = {}
ai_mode = {}

# ==========================================
# 🕐 AWAY MODE (1 MINUTE)
# ==========================================
last_owner_activity = {}  # {user_id: timestamp}
AWAY_TIMEOUT = 60  # 1 minute

# ==========================================
# MESSAGES
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

AI_INTRO_MSG = """🤖 **ASK AI** 🤖

━━━━━━━━━━━━━━━━━━━━━━

Ask me anything — I'll reply in your language!

👇 Type your question below."""

# ==========================================
# KEYBOARDS
# ==========================================
def main_menu_keyboard():
    return [
        [Button.text("🤖 ASK AI"), Button.text("🎮 PUBG")],
        [Button.text("🎮 MLBB"), Button.text("📞 CONTACT")],
        [Button.text("📢 JOIN CHANNEL"), Button.text("🌐 LANGUAGE")],
        [Button.text("💬 FEEDBACK")],
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
        [Button.text("🇬🇧 EN"), Button.text("🇲🇲 MM"), Button.text("🇮🇳 HI")],
        [Button.text("🇸🇦 AR"), Button.text("🇵🇰 UR"), Button.text("🇧🇩 BN")],
        [Button.text("🇮🇩 ID"), Button.text("🇹🇭 TH"), Button.text("🇨🇳 ZH")],
        [Button.text("🇯🇵 JA"), Button.text("🇰🇷 KO"), Button.text("🇷🇺 RU")],
        [Button.text("🇪🇸 ES"), Button.text("🇫🇷 FR"), Button.text("🇵🇹 PT")],
        [Button.text("🇩🇪 DE"), Button.text("🇹🇷 TR"), Button.text("🇮🇷 FA")],
        [Button.text("⬅️ BACK")],
    ]

def join_keyboard():
    return [
        [Button.url("🔗 Join Channel", CHANNEL_LINK)],
        [Button.text("⬅️ BACK")],
    ]

# ==========================================
# TRACKING
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
# OWNER NOTIFICATION
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
# OCR
# ==========================================
async def extract_pubg_kills(image_path):
    if not ocr_client:
        return None
    resized_path = None
    try:
        img = Image.open(image_path)
        W, H = img.size
        if W > 1280:
            ratio = 1280 / W
            img = img.resize((1280, int(H * ratio)), Image.LANCZOS)
        if img.mode != "RGB":
            img = img.convert("RGB")
        resized_path = image_path + "_resized.jpg"
        img.save(resized_path, "JPEG", quality=88)
        with open(resized_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        for model_name in VISION_MODELS:
            try:
                def _ocr():
                    return ocr_client.chat.completions.create(
                        model=model_name,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Look at this PUBG Mobile screenshot. Find 'Eliminations XX' in top-left. Reply ONLY the digits. If not found reply 0."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }],
                        max_tokens=10,
                        temperature=0.0
                    )
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, _ocr)
                text = response.choices[0].message.content.strip()
                match = re.search(r'(\d{1,3})', text)
                if match:
                    kills = int(match.group(1))
                    return kills if 0 <= kills <= 99 else 0
            except Exception as e:
                print(f"⚠️ OCR model error ({model_name}): {e}")
                continue
        return 0
    except Exception as e:
        print(f"❌ OCR Error: {e}")
        return None
    finally:
        try:
            if resized_path and os.path.exists(resized_path):
                os.remove(resized_path)
        except:
            pass

# ==========================================
# EXA SEARCH
# ==========================================
async def exa_search(query):
    if not EXA_API_KEY:
        return None
    try:
        def _search():
            return requests.post(
                "https://api.exa.ai/search",
                headers={"x-api-key": EXA_API_KEY, "Content-Type": "application/json"},
                json={"query": query, "numResults": 3, "type": "instant", "contents": {"text": {"maxCharacters": 500}}},
                timeout=5
            )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _search)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                combined = ""
                for r in results[:3]:
                    combined += f"**{r.get('title','')}**\n{r.get('text','')[:300]}\n🔗 {r.get('url','')}\n\n"
                return combined.strip()
    except Exception as e:
        print(f"⚠️ Exa error: {e}")
    return None

# ==========================================
# LANGUAGE DETECT
# ==========================================
async def detect_language(text):
    if not ai_client:
        return "en"
    try:
        def _call():
            return ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Detect the language of the text. Reply ONLY with the 2-letter ISO code (e.g., en, hi, my, ar, ur, th, vi, bn, id, zh, ja, ko, ru, es, fr, pt, de, tr, fa). Nothing else."},
                    {"role": "user", "content": text}
                ],
                max_tokens=5,
                temperature=0.1
            )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call)
        code = response.choices[0].message.content.strip().lower()
        if code in LANG_CODES:
            return code
        if len(code) == 2:
            return code
        return "en"
    except Exception as e:
        print(f"⚠️ Lang detect error: {e}")
        return "en"

# ==========================================
# AI FUNCTIONS
# ==========================================
async def ask_ai(user_message, user_id=None):
    if not ai_client:
        return "⚠️ AI is not available right now."
    if user_id and user_id not in user_langs:
        detected = await detect_language(user_message)
        user_langs[user_id] = detected
        print(f"🌐 Auto-detected: {detected}")
    lang = user_langs.get(user_id, "en") if user_id else "en"

    context = ""
    if EXA_API_KEY and len(user_message) > 5:
        try:
            exa_result = await asyncio.wait_for(exa_search(user_message), timeout=5.0)
            if exa_result:
                context = f"\n\nWeb search results:\n{exa_result}"
        except:
            pass

    try:
        def _call():
            return ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are ROVIXBY Assistant. Reply in {LANG_CODES.get(lang, 'en')} language. Be helpful, short (3-5 lines), friendly.{context}"},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=700,
                temperature=0.75
            )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call)
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ AI Error: {e}")
        return "⚠️ AI error. Please try again."

async def ask_ai_userbot(user_message):
    if not ai_client:
        return "I'll reply to you soon. Thank you for your patience!"
    try:
        detected_lang = await detect_language(user_message)
    except Exception:
        detected_lang = "en"
    try:
        def _call():
            return ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"""You are ROVIXBY Assistant (personal auto-reply).
Reply in {LANG_CODES.get(detected_lang, 'en')} language.
Be helpful, friendly, professional. Short reply (2-3 lines max).
Say that owner is currently offline and will reply soon.
Don't overpromise. Don't share personal info."""},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call)
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Userbot AI Error: {e}")
        return "I'll reply to you soon. Thank you for your patience!"

# ==========================================
# USERBOT (WITH AI + AWAY MODE)
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

        user_id = event.sender_id
        now = time.time()

        # 🕐 AWAY MODE: Check karo tum active ho ya nahi
        last_activity = last_owner_activity.get(user_id, 0)
        if now - last_activity < AWAY_TIMEOUT:
            print(f"⏭️ Skipped (you're active with {user_id})")
            return

        # 🤖 AI reply bhejo (tum 1 min se inactive ho)
        user_message = event.raw_text or ""
        ai_reply = await ask_ai_userbot(user_message)

        away_text = f"""╔═════════════════════════╗
       💤  OFFLINE MODE
╚═════════════════════════╝

{ai_reply}

━━━━━━━━━━━━━━━━━━━━━━━
📢 **JOIN OUR OFFICIAL CHANNEL**
🔗 {CHANNEL_LINK}

📂 **HACK FILE IS PINNED** in the channel! Join now to grab it.

🤖 **Contact My Assistant Bot:**
👉 {BOT_LINK}

━━━━━━━━━━━━━━━━━━━━━━━
⏳ I'll reply personally soon. Thank you!"""

        msg = await userbot.send_file(event.chat_id, USERBOT_GIF, caption=away_text)
        track_userbot(user_id, msg.id)

        try:
            sender = await event.get_sender()
            username = f"@{sender.username}" if sender.username else "No username"
            await notify_owner(
                "📩 **New Personal Message!**",
                f"👤 Name: {sender.first_name}\n🔗 Username: {username}\n🆔 ID: `{user_id}`\n💬 Message: {user_message[:100]}\n\n🤖 AI Reply: {ai_reply[:200]}"
            )
        except Exception:
            pass
        print(f"📩 Userbot AI reply sent to {user_id}")
    except Exception as e:
        print(f"⚠️ Userbot Error: {e}")

@userbot.on(events.NewMessage(outgoing=True))
async def owner_reply_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.chat_id

        # 🕐 TRACK: Tumhari activity save karo
        last_owner_activity[user_id] = time.time()
        print(f"🕐 Owner active with {user_id}")

        text = event.text or ""

        if text.startswith("tr//"):
            try:
                parts = text.split(" ", 1)
                lang_code = parts[0].replace("tr//", "").lower()
                message_to_translate = parts[1] if len(parts) > 1 else ""
                if lang_code in LANG_CODES and message_to_translate:
                    translated = GoogleTranslator(source="en", target=LANG_CODES[lang_code]).translate(message_to_translate)
                    await userbot.send_message(user_id, translated)
                    print(f"✅ Translated ({lang_code})")
                    await event.delete()
                    return
            except Exception as e:
                print(f"⚠️ Translation error: {e}")

        if text and text.startswith("/"):
            return

        print(f"👤 Owner replied — cleaning up...")
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
        print(f"🗑️ {deleted} messages deleted")
    except Exception as e:
        print(f"⚠️ Owner Reply Error: {e}")

# ==========================================
# BOT
# ==========================================
bot = TelegramClient('bot_session', API_ID, API_HASH)

async def is_user_joined(user_id):
    try:
        await bot(GetParticipantRequest(channel=CHANNEL_USERNAME, participant=user_id))
        return True
    except (UserNotParticipantError, ChatAdminRequiredError):
        return False
    except Exception:
        return False

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

@bot.on(events.NewMessage(pattern=r'^🤖 ASK AI$'))
async def ask_ai_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        ai_mode[user_id] = True
        msg = await bot.send_message(event.chat_id, AI_INTRO_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Ask AI Error: {e}")

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

@bot.on(events.NewMessage(pattern=r'^(🇬🇧 EN|🇲🇲 MM|🇮🇳 HI|🇸🇦 AR|🇵🇰 UR|🇧🇩 BN|🇮🇩 ID|🇹🇭 TH|🇨🇳 ZH|🇯🇵 JA|🇰🇷 KO|🇷🇺 RU|🇪🇸 ES|🇫🇷 FR|🇵🇹 PT|🇩🇪 DE|🇹🇷 TR|🇮🇷 FA)$'))
async def lang_select(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        text = event.text
        lang_map = {
            "🇬🇧 EN": "en", "🇲🇲 MM": "mm", "🇮🇳 HI": "hi", "🇸🇦 AR": "ar",
            "🇵🇰 UR": "ur", "🇧🇩 BN": "bn", "🇮🇩 ID": "id", "🇹🇭 TH": "th",
            "🇨🇳 ZH": "zh", "🇯🇵 JA": "ja", "🇰🇷 KO": "ko", "🇷🇺 RU": "ru",
            "🇪🇸 ES": "es", "🇫🇷 FR": "fr", "🇵🇹 PT": "pt", "🇩🇪 DE": "de",
            "🇹🇷 TR": "tr", "🇮🇷 FA": "fa",
        }
        lang = lang_map.get(text, "en")
        user_langs[user_id] = lang
        try:
            sender = await event.get_sender()
            await notify_owner(
                "🌐 **Language Selected!**",
                f"👤 Name: {sender.first_name}\n🆔 ID: `{user_id}`\n🗣️ Language: `{text}`"
            )
        except Exception:
            pass
        msg = await bot.send_message(event.chat_id, f"✅ Language set to **{text}**\n\nNow use the menu below:", buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Lang Select Error: {e}")

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

@bot.on(events.NewMessage(pattern=r'^⬅️ BACK$'))
async def back_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        ai_mode[user_id] = False
        msg = await bot.send_message(event.chat_id, WELCOME_MSG, buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Back Error: {e}")

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

# === IMAGE OCR ===
@bot.on(events.NewMessage(incoming=True))
async def image_handler(event):
    try:
        if not event.is_private or not event.photo:
            return
        user_id = event.sender_id
        await bot.send_message(event.chat_id, "🔍 **Analyzing your PUBG screenshot...**")
        path = await event.download_media()
        kills = await extract_pubg_kills(path)
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except:
            pass
        if kills is not None:
            msg = await bot.send_message(
                event.chat_id,
                f"🎮 **PUBG SCREENSHOT ANALYZED**\n\n🎯 **Eliminations:** `{kills}`\n\n━━━━━━━━━━━━━━━━━━━━━━\n🤖 Analyzed by ROVIXBY AI",
                buttons=back_keyboard()
            )
            track_bot(user_id, msg.id)
            try:
                sender = await event.get_sender()
                await notify_owner(
                    "📸 **New PUBG Screenshot!**",
                    f"👤 Name: {sender.first_name}\n🆔 ID: `{user_id}`\n🎯 Kills: `{kills}`"
                )
            except Exception:
                pass
        else:
            msg = await bot.send_message(event.chat_id, "⚠️ Could not analyze the image.", buttons=back_keyboard())
            track_bot(user_id, msg.id)
    except Exception as e:
        print(f"⚠️ Image Handler Error: {e}")

# === AI REPLY ===
@bot.on(events.NewMessage(incoming=True))
async def ai_reply_handler(event):
    try:
        if not event.is_private:
            return
        text = event.text or ""
        if not text or text.startswith("/"):
            return

        button_texts = [
            "🤖 ASK AI", "🎮 PUBG", "🎮 MLBB", "📞 CONTACT", "📢 JOIN CHANNEL
