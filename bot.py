from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import GetPeerDialogsRequest
from telethon.tl.types import PeerUser
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
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
import random
from datetime import datetime, timedelta, date

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
FEEDBACK_BOT_URL = "https://t.me/kairixaizenfeedbackbot"
FILE_PASSWORD = "buyViP@79o"

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
USERBOT_GIF = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"

# ==========================================
# LANG CODES
# ==========================================
LANG_CODES = {
    "en": "en", "hi": "hi", "my": "my", "ar": "ar",
    "ur": "ur", "th": "th", "vi": "vi", "bn": "bn",
    "id": "id", "zh-CN": "zh-CN", "ja": "ja", "ko": "ko",
    "ru": "ru", "es": "es", "fr": "fr", "pt": "pt",
    "de": "de", "tr": "tr", "fa": "fa",
}

# ==========================================
# STATE
# ==========================================
user_langs = {}
ai_mode = {}
live_chat_mode = {}
broadcast_mode = {}
password_change_mode = {}
user_selected_package = {}
package_duration = {}
owner_notes = {}
user_names = {}
all_users = set()
start_count = 0
daily_users = {}
daily_actions = {}
translation_cache = {}

# ==========================================
# AWAY MODE
# ==========================================
last_owner_activity = {}
user_auto_reply_count = {}
AWAY_TIMEOUT = 300
MAX_AUTO_REPLIES = 3

# ==========================================
# LICENSE KEY SYSTEM
# ==========================================
KEY_FILE = "license_keys.json"
KEY_EXPIRY_MINUTES = 30

def load_keys():
    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Key load error: {e}")
    return {}

def save_keys():
    try:
        with open(KEY_FILE, "w") as f:
            json.dump(active_keys, f)
    except Exception as e:
        print(f"Key save error: {e}")

active_keys = load_keys()

def generate_key():
    number = random.randint(10000, 99999)
    return f"ROVIX-{number}"

def create_key():
    key = generate_key()
    while key in active_keys:
        key = generate_key()
    active_keys[key] = {
        "used": False,
        "user_id": None,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "activated_at": None,
        "expires_at": None
    }
    save_keys()
    return key

# ==========================================
# BACKUP
# ==========================================
BACKUP_FILE = "backup_data.json"

def create_backup():
    try:
        data = {
            "keys": active_keys,
            "backup_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_keys": len(active_keys)
        }
        with open(BACKUP_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return BACKUP_FILE
    except Exception as e:
        print(f"Backup error: {e}")
        return None

# ==========================================
# HELPERS
# ==========================================
def increment_count(user_id):
    global start_count
    today = str(date.today())
    start_count += 1
    if user_id not in daily_users.get(today, set()):
        daily_users.setdefault(today, set()).add(user_id)
    daily_actions[today] = daily_actions.get(today, 0) + 1

# ==========================================
# MESSAGES
# ==========================================
WELCOME_MSG = """ROVIXBY BOT
PROFESSIONAL GAMING SERVICE

━━━━━━━━━━━━━━━━━━━━━━

Welcome!

Select an option below.

Bot created by @ROVIXU1ti

━━━━━━━━━━━━━━━━━━━━━━"""

PUBG_MENU_MSG = """PUBG

━━━━━━━━━━━━━━━━━━━━━━

What do you need?"""

PUBG_NOT_JOINED_MSG = f"""You haven't joined our channel yet!

━━━━━━━━━━━━━━━━━━━━━━
JOIN CHANNEL FIRST:
{CHANNEL_LINK}

Check pinned message after joining.
━━━━━━━━━━━━━━━━━━━━━━

After joining, click "I've Joined"."""

PUBG_SHARE_MSG = f"""SHARE REQUIRED

━━━━━━━━━━━━━━━━━━━━━━

You've joined the channel!

Step 1: Share the channel link with 5 people.

Channel Link:
{CHANNEL_LINK}

━━━━━━━━━━━━━━━━━━━━━━

Step 2: After sharing, click "I Shared"."""

PUBG_NOT_SHARED_MSG = f"""You haven't shared yet!

━━━━━━━━━━━━━━━━━━━━━━

Please share the channel link with 5 people first.

Channel Link:
{CHANNEL_LINK}

━━━━━━━━━━━━━━━━━━━━━━

After sharing, click "I Shared"."""

PUBG_ENTER_KEY_MSG = f"""VERIFICATION COMPLETE

━━━━━━━━━━━━━━━━━━━━━━
ENTER YOUR LICENSE KEY
━━━━━━━━━━━━━━━━━━━━━━

Send your license key below.

Format: ROVIX-XXXXX

━━━━━━━━━━━━━━━━━━━━━━

1 KEY = 1 USER (30 min valid)
Don't have a key? DM: {DM_ADMIN_1}

Type /cancel to exit."""

PUBG_DURATION_MSG = """SELECT DURATION

━━━━━━━━━━━━━━━━━━━━━━

Choose your plan:

━━━━━━━━━━━━━━━━━━━━━━"""

PUBG_FULL_SEASON_MSG = f"""FULL SEASON PACKAGE

━━━━━━━━━━━━━━━━━━━━━━

Price: $15 / 25,000 KS

━━━━━━━━━━━━━━━━━━━━━━
PAYMENT METHODS:
━━━━━━━━━━━━━━━━━━━━━━

KBZ Pay:
   09897052554 (Raw Eis)

Wave Pay:
   Contact Admin
   {DM_ADMIN_1}
   {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

After payment, click below to send screenshot."""

PUBG_ONE_MONTH_MSG = f"""ONE MONTH PACKAGE

━━━━━━━━━━━━━━━━━━━━━━

Price: $7 / 15,000 KS

━━━━━━━━━━━━━━━━━━━━━━
PAYMENT METHODS:
━━━━━━━━━━━━━━━━━━━━━━

KBZ Pay:
   09897052554 (Raw Eis)

Wave Pay:
   Contact Admin
   {DM_ADMIN_1}
   {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

After payment, click below to send screenshot."""

MLBB_MENU_MSG = """MOBILE LEGENDS

━━━━━━━━━━━━━━━━━━━━━━

Choose an option:"""

MLBB_PURCHASE_MSG = f"""MOBILE LEGENDS PURCHASE

━━━━━━━━━━━━━━━━━━━━━━

Price: 5000 KS / $2 per file

━━━━━━━━━━━━━━━━━━━━━━
PAYMENT METHODS:
━━━━━━━━━━━━━━━━━━━━━━

KBZ Pay:
   09897052554 (Raw Eis)

Wave Pay:
   Contact Admin
   {DM_ADMIN_1}
   {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

After payment, click below to send screenshot."""

SCREENSHOT_PROMPT_MSG = """SEND PAYMENT SCREENSHOT

━━━━━━━━━━━━━━━━━━━━━━

Please send your payment screenshot below.

Make sure it shows:
  - Amount
  - Date/Time
  - Transaction ID

━━━━━━━━━━━━━━━━━━━━━━

After verification, admin will send you the file."""

CONTACT_MSG = f"""CONTACT OWNER

━━━━━━━━━━━━━━━━━━━━━━

Admin 1: {DM_ADMIN_1}
Admin 2: {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

Reply time: Within 24 hours."""

JOIN_CHANNEL_MSG = f"""JOIN OUR CHANNEL

━━━━━━━━━━━━━━━━━━━━━━

{CHANNEL_LINK}

Check pinned message after joining.

━━━━━━━━━━━━━━━━━━━━━━"""

LANGUAGE_MSG = """SELECT LANGUAGE

━━━━━━━━━━━━━━━━━━━━━━

Please choose your preferred language.

━━━━━━━━━━━━━━━━━━━━━━"""

FEEDBACK_MSG = f"""FEEDBACK

━━━━━━━━━━━━━━━━━━━━━━

We'd love to hear your feedback!

Send your feedback to:
{DM_ADMIN_1}
{DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

Thank you for your support!"""

DM_ADMIN_MSG = f"""DM THE ADMIN

━━━━━━━━━━━━━━━━━━━━━━

{DM_ADMIN_1}
{DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

Please wait for their reply.

━━━━━━━━━━━━━━━━━━━━━━"""

AI_INTRO_MSG = """ASK AI

━━━━━━━━━━━━━━━━━━━━━━

Ask me anything - I'll reply in your language!

Type your question below.

━━━━━━━━━━━━━━━━━━━━━━"""

LIVE_CHAT_MSG = """LIVE CHAT WITH ADMIN

━━━━━━━━━━━━━━━━━━━━━━

Type your message below.

Admin will reply to you personally.

━━━━━━━━━━━━━━━━━━━━━━

Type /cancel to exit.

━━━━━━━━━━━━━━━━━━━━━━"""

CONTACT_ADMIN_MSG = f"""CONTACT ADMIN

━━━━━━━━━━━━━━━━━━━━━━

Admin 1: {DM_ADMIN_1}
Admin 2: {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

For purchase or inquiries, message admins directly.

Reply time: Within 24 hours."""

# ==========================================
# KEYBOARDS (NO EMOJI)
# ==========================================
def main_menu_keyboard():
    return [
        [Button.text("ASK AI"), Button.text("PUBG")],
        [Button.text("MLBB"), Button.text("CONTACT")],
        [Button.text("JOIN CHANNEL"), Button.text("LANGUAGE")],
        [Button.text("FEEDBACK"), Button.text("LIVE CHAT")],
    ]

def pubg_menu_keyboard():
    return [
        [Button.text("File Password")],
        [Button.text("PUBG PURCHASE")],
        [Button.text("BACK")],
    ]

def pubg_purchase_keyboard():
    return [
        [Button.text("FULL SEASON")],
        [Button.text("ONE MONTH")],
        [Button.text("BACK")],
    ]

def mlbb_menu_keyboard():
    return [
        [Button.text("MLBB PURCHASE")],
        [Button.text("BACK")],
    ]

def back_keyboard():
    return [[Button.text("BACK")]]

def language_keyboard():
    return [
        [Button.text("EN - English"), Button.text("MM - Burmese")],
        [Button.text("HI - Hindi"), Button.text("AR - Arabic")],
        [Button.text("UR - Urdu"), Button.text("BN - Bengali")],
        [Button.text("ID - Indonesian"), Button.text("TH - Thai")],
        [Button.text("ZH - Chinese"), Button.text("JA - Japanese")],
        [Button.text("KO - Korean"), Button.text("RU - Russian")],
        [Button.text("ES - Spanish"), Button.text("FR - French")],
        [Button.text("PT - Portuguese"), Button.text("DE - German")],
        [Button.text("TR - Turkish"), Button.text("FA - Persian")],
        [Button.text("BACK")],
    ]

def join_keyboard():
    return [
        [Button.url("Join Channel", CHANNEL_LINK)],
        [Button.text("I've Joined")],
        [Button.text("BACK")],
    ]

def share_keyboard():
    share_url = f"https://t.me/share/url?url={CHANNEL_LINK}&text=Check%20this%20channel!"
    return [
        [Button.url("Share Channel", share_url)],
        [Button.text("I Shared")],
        [Button.text("I Haven't Shared")],
        [Button.text("BACK")],
    ]

def screenshot_keyboard():
    return [
        [Button.text("Send Payment Screenshot")],
        [Button.text("Contact Admin")],
        [Button.text("BACK")],
    ]

def my_work_keyboard():
    return [
        [Button.text("/stats")],
        [Button.text("/users")],
        [Button.text("/broadcast")],
        [Button.text("/backup")],
        [Button.text("BACK")],
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
        print(f"Load error: {e}")
    return {"bot": {}, "userbot": {}}

def save_tracking():
    try:
        with open(TRACK_FILE, "w") as f:
            json.dump(tracked_msgs, f)
    except Exception as e:
        print(f"Save error: {e}")

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
        await bot.send_message(OWNER_ID, f"{title}\n\n{details}\n\nTime: {now}")
    except Exception as e:
        print(f"Notify error: {e}")

# ==========================================
# OCR - PUBG Screenshot
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
                print(f"OCR error ({model_name}): {e}")
                continue
        return 0
    except Exception as e:
        print(f"OCR Error: {e}")
        return None
    finally:
        try:
            if resized_path and os.path.exists(resized_path):
                os.remove(resized_path)
        except:
            pass

# ==========================================
# PAYMENT OCR
# ==========================================
async def extract_payment_info(image_path):
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
        resized_path = image_path + "_payment.jpg"
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
                                {"type": "text", "text": """Look at this payment screenshot. Extract:
1. Amount (with currency like KS or MMK)
2. Transaction ID (if visible)
3. Date and Time
4. Payment method (KBZ, Wave, etc.)

Reply in this EXACT format:
AMOUNT: xxx
TXN: xxx
DATE: xxx
METHOD: xxx

If not found, write "Not detected"."""},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }],
                        max_tokens=100,
                        temperature=0.0
                    )
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, _ocr)
                text = response.choices[0].message.content.strip()

                info = {}
                for line in text.split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        info[key.strip().lower()] = val.strip()

                return {
                    "amount": info.get("amount", "Not detected"),
                    "txn_id": info.get("txn", "Not detected"),
                    "date": info.get("date", "Not detected"),
                    "method": info.get("method", "Not detected")
                }
            except Exception as e:
                print(f"Payment OCR error ({model_name}): {e}")
                continue
        return None
    except Exception as e:
        print(f"Payment OCR Error: {e}")
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
                    combined += f"**{r.get('title','')}**\n{r.get('text','')[:300]}\nLink: {r.get('url','')}\n\n"
                return combined.strip()
    except Exception as e:
        print(f"Exa error: {e}")
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
        print(f"Lang detect error: {e}")
        return "en"

# ==========================================
# TRANSLATE TEXT
# ==========================================
async def translate_text(text, target_lang):
    if not ai_client or target_lang == "en":
        return text
    cache_key = f"{target_lang}:{text[:100]}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    try:
        def _call():
            return ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"Translate the following text to {LANG_CODES.get(target_lang, 'en')} language. Keep formatting. Reply ONLY the translation."},
                    {"role": "user", "content": text}
                ],
                max_tokens=1500,
                temperature=0.2
            )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call)
        translated = response.choices[0].message.content.strip()
        translation_cache[cache_key] = translated
        return translated
    except Exception as e:
        print(f"Translate error: {e}")
        return text

# ==========================================
# AI FUNCTIONS
# ==========================================
async def ask_ai(user_message, user_id=None):
    if not ai_client:
        return "AI is not available right now. Please try again later."
    if user_id and user_id not in user_langs:
        detected = await detect_language(user_message)
        user_langs[user_id] = detected
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
        print(f"AI Error: {e}")
        return "AI service is temporarily unavailable. Please try again."

async def ask_ai_userbot(user_message):
    if not ai_client:
        return "The owner is currently offline. They will reply to you as soon as possible."
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
        print(f"Userbot AI Error: {e}")
        return "The owner is currently offline. They will reply to you as soon as possible."
        
# ==========================================
# USERBOT (AI AUTO-REPLY + AWAY MODE)
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

        # Away mode check (5 min)
        last_activity = last_owner_activity.get(user_id, 0)
        if now - last_activity < AWAY_TIMEOUT:
            print(f"Skipped (you're active with {user_id})")
            return

        # Auto-reply limit (3 times)
        count = user_auto_reply_count.get(user_id, 0)
        if count >= MAX_AUTO_REPLIES:
            print(f"Skipped (already 3 replies to {user_id})")
            return

        user_message = event.raw_text or ""
        ai_reply = await ask_ai_userbot(user_message)

        away_text = f"""╔═════════════════════════╗
   OWNER OFFLINE
╚═════════════════════════╝

{ai_reply}

━━━━━━━━━━━━━━━━━━━━━━━
CHAT WITH MY BOT: {BOT_LINK}
━━━━━━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━━━━━━
JOIN OUR CHANNEL: {CHANNEL_LINK}
━━━━━━━━━━━━━━━━━━━━━━━

HACK FILE PINNED!"""

        msg = await userbot.send_file(event.chat_id, USERBOT_GIF, caption=away_text)
        track_userbot(user_id, msg.id)
        user_auto_reply_count[user_id] = count + 1

        try:
            sender = await event.get_sender()
            username = f"@{sender.username}" if sender.username else "No username"
            await notify_owner(
                "New Personal Message!",
                f"Name: {sender.first_name}\nUsername: {username}\nID: {user_id}\nMessage: {user_message[:100]}\nAuto-reply: {count + 1}/{MAX_AUTO_REPLIES}"
            )
        except Exception:
            pass
        print(f"Userbot reply #{count + 1} sent to {user_id}")
    except Exception as e:
        print(f"Userbot Error: {e}")

@userbot.on(events.NewMessage(outgoing=True))
async def owner_reply_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.chat_id
        last_owner_activity[user_id] = time.time()
        user_auto_reply_count[user_id] = 0
        print(f"Owner active with {user_id}")

        text = event.text or ""
        if text and text.startswith("/"):
            return

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
        print(f"{deleted} messages deleted")
    except Exception as e:
        print(f"Owner Reply Error: {e}")

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

# === START ===
@bot.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        user_name = event.sender.first_name if event.sender else "User"
        username = f"@{event.sender.username}" if event.sender and event.sender.username else "No username"
        user_names[user_id] = f"{user_name} ({username})"
        increment_count(user_id)
        if user_id not in all_users:
            all_users.add(user_id)
            try:
                await bot.send_message(OWNER_ID, f"NEW USER\n\nName: {user_name}\nID: {user_id}\nUsername: {username}\nTotal: {len(all_users)}")
            except Exception:
                pass

        try:
            sender = await event.get_sender()
            await notify_owner(
                "New User Started Bot!",
                f"Name: {sender.first_name}\nUsername: {username}\nID: {user_id}"
            )
        except Exception:
            pass

        msg = await bot.send_message(event.chat_id, WELCOME_MSG, buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Start Error: {e}")

# === KEY GENERATION ===
@bot.on(events.NewMessage(pattern=r'^/newkey$'))
async def newkey_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        key = create_key()
        await event.respond(f"NEW KEY GENERATED\n\nKey: {key}\n\nValid 30 minutes after activation.")
    except Exception as e:
        print(f"Newkey Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/newkey (\d+)$'))
async def newkey_multi_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        count = int(event.pattern_match.group(1))
        if count > 50:
            count = 50
        keys = [create_key() for _ in range(count)]
        key_list = "\n".join([f"{i+1}. {k}" for i, k in enumerate(keys)])
        await event.respond(f"{count} NEW KEYS\n\n{key_list}")
    except Exception as e:
        print(f"Newkey Multi Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/keys$'))
async def keys_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        if not active_keys:
            await event.respond("No keys yet.")
            return
        total = len(active_keys)
        used = sum(1 for k in active_keys.values() if k.get("used"))
        unused = total - used
        await event.respond(f"KEYS STATUS\n\nTotal: {total}\nUsed: {used}\nUnused: {unused}")
    except Exception as e:
        print(f"Keys Error: {e}")

# === STATS ===
@bot.on(events.NewMessage(pattern=r'^/stats$'))
async def stats_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        today = str(date.today())
        daily_count = len(daily_users.get(today, set()))
        daily_act = daily_actions.get(today, 0)
        total_keys = len(active_keys)
        used_keys = sum(1 for k in active_keys.values() if k.get("used"))
        unused_keys = total_keys - used_keys

        lang_stats = {}
        for l in user_langs.values():
            lang_stats[l] = lang_stats.get(l, 0) + 1
        top_langs = sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        lang_str = "\n".join([f"  {k}: {v}" for k, v in top_langs]) or "  No data"

        stats_msg = f"""LIVE STATS

━━━━━━━━━━━━━━━━━━━━━━
KEYS
  Total: {total_keys}
  Used: {used_keys}
  Unused: {unused_keys}

USERS
  Total: {len(all_users)}
  Today: {daily_count}
  Actions: {daily_act}

LANGUAGES (Top 5)
{lang_str}

TIME: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
━━━━━━━━━━━━━━━━━━━━━━"""
        await event.respond(stats_msg)
    except Exception as e:
        print(f"Stats Error: {e}")

# === USERS ===
@bot.on(events.NewMessage(pattern=r'^/users$'))
async def users_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        if not all_users:
            await event.respond("No users yet.")
            return
        ulist = ""
        for uid in list(all_users)[:50]:
            ulist += f"- {uid} - {user_names.get(uid, 'Unknown')}\n"
        await event.respond(f"USERS ({len(all_users)})\n\n{ulist}")
    except Exception as e:
        print(f"Users Error: {e}")

# === BROADCAST ===
@bot.on(events.NewMessage(pattern=r'^/broadcast$'))
async def broadcast_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        broadcast_mode[event.sender_id] = True
        await event.respond("BROADCAST MODE\n\nSend the message you want to broadcast to all users.")
    except Exception as e:
        print(f"Broadcast Error: {e}")

# === BACKUP ===
@bot.on(events.NewMessage(pattern=r'^/backup$'))
async def backup_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        file = create_backup()
        if file and os.path.exists(file):
            await bot.send_file(OWNER_ID, file, caption=f"MANUAL BACKUP\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Backup Error: {e}")

# === SET NOTE ===
@bot.on(events.NewMessage(pattern=r"^/setnote\s+(.+)"))
async def set_note_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        note_text = event.pattern_match.group(1)
        owner_notes["notes"] = note_text
        await event.respond(f"Note saved!\n\n{note_text}")
    except Exception as e:
        print(f"Set Note Error: {e}")

# === CLEAR NOTE ===
@bot.on(events.NewMessage(pattern=r'^/clearnote$'))
async def clear_note_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        owner_notes.pop("notes", None)
        await event.respond("Note cleared!")
    except Exception as e:
        print(f"Clear Note Error: {e}")

# === ASK AI ===
@bot.on(events.NewMessage(pattern=r'^ASK AI$'))
async def ask_ai_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        ai_mode[user_id] = True
        msg = await bot.send_message(event.chat_id, AI_INTRO_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Ask AI Error: {e}")

# === PUBG MENU ===
@bot.on(events.NewMessage(pattern=r'^PUBG$'))
async def pubg_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_MENU_MSG, buttons=pubg_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"PUBG Error: {e}")

# === FILE PASSWORD ===
@bot.on(events.NewMessage(pattern=r'^File Password$'))
async def file_password_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        joined = await is_user_joined(user_id)
        if joined:
            msg = await bot.send_message(event.chat_id, PUBG_SHARE_MSG, buttons=share_keyboard())
            track_bot(user_id, msg.id)
        else:
            msg = await bot.send_message(event.chat_id, PUBG_NOT_JOINED_MSG, buttons=join_keyboard())
            track_bot(user_id, msg.id)
    except Exception as e:
        print(f"File Password Error: {e}")

# === I'VE JOINED ===
@bot.on(events.NewMessage(pattern=r"^I've Joined$"))
async def joined_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        joined = await is_user_joined(user_id)
        if joined:
            msg = await bot.send_message(event.chat_id, PUBG_SHARE_MSG, buttons=share_keyboard())
            track_bot(user_id, msg.id)
        else:
            msg = await bot.send_message(event.chat_id, "You haven't joined yet. Please join first.", buttons=join_keyboard())
            track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Joined Error: {e}")

# === I SHARED (FAKE VERIFY) ===
@bot.on(events.NewMessage(pattern=r'^I Shared$'))
async def shared_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id

        verify_msg = await bot.send_message(event.chat_id, """VERIFYING YOUR SHARE

━━━━━━━━━━━━━━━━━━━━━━
Please wait...

[░░░░░░░░░░] 0%
━━━━━━━━━━━━━━━━━━━━━━""")

        await asyncio.sleep(0.8)
        await verify_msg.edit("""VERIFYING YOUR SHARE

━━━━━━━━━━━━━━━━━━━━━━
[████░░░░░░] 40%
━━━━━━━━━━━━━━━━━━━━━━""")

        await asyncio.sleep(0.8)
        await verify_msg.edit("""VERIFYING YOUR SHARE

━━━━━━━━━━━━━━━━━━━━━━
[████████░░] 80%
━━━━━━━━━━━━━━━━━━━━━━""")

        await asyncio.sleep(0.8)
        await verify_msg.edit("""VERIFYING YOUR SHARE

━━━━━━━━━━━━━━━━━━━━━━
[██████████] 100%
━━━━━━━━━━━━━━━━━━━━━━""")

        await asyncio.sleep(0.5)

        if random.random() < 0.2:
            await verify_msg.edit("""VERIFICATION FAILED

━━━━━━━━━━━━━━━━━━━━━━
Please try again!
━━━━━━━━━━━━━━━━━━━━━━""",
                buttons=[
                    [Button.url("Share Again", f"https://t.me/share/url?url={CHANNEL_LINK}&text=Check%20this%20channel!")],
                    [Button.text("Try Again")],
                    [Button.text("BACK")],
                ]
            )
            return

        msg = await bot.send_message(event.chat_id, PUBG_ENTER_KEY_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Shared Error: {e}")

# === I HAVEN'T SHARED ===
@bot.on(events.NewMessage(pattern=r"^I Haven't Shared$"))
async def not_shared_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_NOT_SHARED_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Not Shared Error: {e}")

# === TRY AGAIN ===
@bot.on(events.NewMessage(pattern=r'^Try Again$'))
async def try_again_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_ENTER_KEY_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Try Again Error: {e}")

# === PUBG PURCHASE ===
@bot.on(events.NewMessage(pattern=r'^PUBG PURCHASE$'))
async def pubg_purchase_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_DURATION_MSG, buttons=pubg_purchase_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"PUBG Purchase Error: {e}")

@bot.on(events.NewMessage(pattern=r'^FULL SEASON$'))
async def full_season_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_FULL_SEASON_MSG, buttons=screenshot_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Full Season Error: {e}")

@bot.on(events.NewMessage(pattern=r'^ONE MONTH$'))
async def one_month_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_ONE_MONTH_MSG, buttons=screenshot_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"One Month Error: {e}")

# === MLBB ===
@bot.on(events.NewMessage(pattern=r'^MLBB$'))
async def mlbb_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, MLBB_PURCHASE_MSG, buttons=screenshot_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"MLBB Error: {e}")

# === SCREENSHOT PROMPT ===
@bot.on(events.NewMessage(pattern=r'^Send Payment Screenshot$'))
async def screenshot_prompt_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, SCREENSHOT_PROMPT_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Screenshot Error: {e}")

# === CONTACT ADMIN ===
@bot.on(events.NewMessage(pattern=r'^Contact Admin$'))
async def contact_admin_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, CONTACT_ADMIN_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Contact Admin Error: {e}")

# === CONTACT ===
@bot.on(events.NewMessage(pattern=r'^CONTACT$'))
async def contact_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, CONTACT_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Contact Error: {e}")

# === JOIN ===
@bot.on(events.NewMessage(pattern=r'^JOIN CHANNEL$'))
async def join_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, JOIN_CHANNEL_MSG, buttons=join_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Join Error: {e}")

# === LANGUAGE ===
@bot.on(events.NewMessage(pattern=r'^LANGUAGE$'))
async def language_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, LANGUAGE_MSG, buttons=language_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Language Error: {e}")

@bot.on(events.NewMessage(pattern=r'^(EN - English|MM - Burmese|HI - Hindi|AR - Arabic|UR - Urdu|BN - Bengali|ID - Indonesian|TH - Thai|ZH - Chinese|JA - Japanese|KO - Korean|RU - Russian|ES - Spanish|FR - French|PT - Portuguese|DE - German|TR - Turkish|FA - Persian)$'))
async def lang_select(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        text = event.text
        lang_map = {
            "EN - English": "en", "MM - Burmese": "my", "HI - Hindi": "hi", "AR - Arabic": "ar",
            "UR - Urdu": "ur", "BN - Bengali": "bn", "ID - Indonesian": "id", "TH - Thai": "th",
            "ZH - Chinese": "zh", "JA - Japanese": "ja", "KO - Korean": "ko", "RU - Russian": "ru",
            "ES - Spanish": "es", "FR - French": "fr", "PT - Portuguese": "pt", "DE - German": "de",
            "TR - Turkish": "tr", "FA - Persian": "fa",
        }
        lang = lang_map.get(text, "en")
        user_langs[user_id] = lang

        confirm = await bot.send_message(
            event.chat_id,
            f"Language set to {text}\n\nLoading menu...",
            buttons=back_keyboard()
        )
        await asyncio.sleep(1)
        try:
            await confirm.delete()
        except:
            pass

        msg = await bot.send_message(event.chat_id, WELCOME_MSG, buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Lang Select Error: {e}")

# === FEEDBACK ===
@bot.on(events.NewMessage(pattern=r'^FEEDBACK$'))
async def feedback_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        msg = await bot.send_message(
            event.chat_id,
            FEEDBACK_MSG,
            buttons=[
                [Button.url("Open Feedback Bot", FEEDBACK_BOT_URL)],
                [Button.text("BACK")],
            ]
        )
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Feedback Error: {e}")

# === LIVE CHAT ===
@bot.on(events.NewMessage(pattern=r'^LIVE CHAT$'))
async def live_chat_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        live_chat_mode[user_id] = True
        msg = await bot.send_message(event.chat_id, LIVE_CHAT_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Live Chat Error: {e}")

# === BACK ===
@bot.on(events.NewMessage(pattern=r'^BACK$'))
async def back_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        ai_mode[user_id] = False
        live_chat_mode[user_id] = False
        msg = await bot.send_message(event.chat_id, WELCOME_MSG, buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Back Error: {e}")

# === LICENSE KEY VERIFY ===
@bot.on(events.NewMessage(pattern=r'^ROVIX-\d{5}$'))
async def key_verify_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        key = event.text.strip().upper()

        if key not in active_keys:
            msg = await bot.send_message(event.chat_id, "Invalid Code!\n\nPlease check and try again.", buttons=back_keyboard())
            track_bot(user_id, msg.id)
            return

        key_data = active_keys[key]

        if key_data.get("used") and key_data.get("user_id") != user_id:
            msg = await bot.send_message(event.chat_id, "This code is already used!", buttons=back_keyboard())
            track_bot(user_id, msg.id)
            return

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expires_str = (datetime.now() + timedelta(minutes=KEY_EXPIRY_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")

        active_keys[key]["used"] = True
        active_keys[key]["user_id"] = user_id
        active_keys[key]["activated_at"] = now_str
        active_keys[key]["expires_at"] = expires_str
        save_keys()

        success_msg = f"""ACCESS GRANTED!

━━━━━━━━━━━━━━━━━━━━━━
Code Verified!
Key: {key}
Valid until: {expires_str}
━━━━━━━━━━━━━━━━━━━━━━

YOUR FILE PASSWORD:

{FILE_PASSWORD}

━━━━━━━━━━━━━━━━━━━━━━

File: Check the pinned message in the channel.
Do NOT share this password!

Expires in {KEY_EXPIRY_MINUTES} minutes."""

        msg = await bot.send_message(event.chat_id, success_msg, buttons=back_keyboard())
        track_bot(user_id, msg.id)

        try:
            sender = await event.get_sender()
            await notify_owner(
                "CODE ACTIVATED!",
                f"Name: {sender.first_name}\nID: {user_id}\nKey: {key}\nExpires: {expires_str}"
            )
        except Exception:
            pass
    except Exception as e:
        print(f"Key Verify Error: {e}")

# === IMAGE HANDLER ===
@bot.on(events.NewMessage(incoming=True))
async def image_handler(event):
    try:
        if not event.is_private or not event.photo:
            return
        user_id = event.sender_id

        sender = await event.get_sender()
        username = f"@{sender.username}" if sender.username else "No username"

        await notify_owner(
            "NEW PAYMENT SCREENSHOT!",
            f"Name: {sender.first_name}\nUsername: {username}\nID: {user_id}\n\n/approve {user_id} to approve\n/reject {user_id} to reject"
        )

        try:
            await bot.send_file(OWNER_ID, event.photo, caption=f"Payment from {user_id}")
        except Exception:
            pass

        await event.reply("PAYMENT RECEIVED!\n\nScreenshot sent to admin.\nPlease wait for verification.")
    except Exception as e:
        print(f"Image Error: {e}")

# === LIVE CHAT FORWARD ===
@bot.on(events.NewMessage(incoming=True))
async def live_chat_forwarder(event):
    try:
        if not event.is_private or not event.text:
            return
        user_id = event.sender_id
        if not live_chat_mode.get(user_id):
            return
        if event.text.startswith("/"):
            return

        try:
            sender = await event.get_sender()
            username = f"@{sender.username}" if sender.username else "No username"
            await notify_owner(
                "LIVE CHAT MESSAGE",
                f"Name: {sender.first_name}\nUsername: {username}\nID: {user_id}\nMessage: {event.text}\n\nReply: /reply {user_id} your_message"
            )
        except Exception:
            pass
        await event.reply("Message sent to admin. Please wait for reply.")
    except Exception as e:
        print(f"Live Chat Error: {e}")

# === BROADCAST MESSAGE HANDLER ===
@bot.on(events.NewMessage(incoming=True))
async def broadcast_message_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        if not broadcast_mode.get(event.sender_id):
            return
        broadcast_msg = event.raw_text
        broadcast_mode[event.sender_id] = False
        sent = failed = 0
        for uid in list(all_users):
            try:
                await bot.send_message(uid, broadcast_msg)
                sent += 1
                await asyncio.sleep(0.1)
            except Exception:
                failed += 1
        await event.respond(f"Broadcast Complete!\n\nSent: {sent}\nFailed: {failed}")
    except Exception as e:
        print(f"Broadcast Msg Error: {e}")

# === PASSWORD CHANGE HANDLER ===
@bot.on(events.NewMessage(incoming=True))
async def password_change_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        if not password_change_mode.get(event.sender_id):
            return
        password_change_mode[event.sender_id] = False
        new_pass = event.raw_text.strip()
        if new_pass.lower() == "/cancel":
            await event.respond("Password change cancelled.")
            return
        if len(new_pass) < 4:
            await event.respond("Password must be at least 4 characters.")
            return
        global FILE_PASSWORD
        old = FILE_PASSWORD
        FILE_PASSWORD = new_pass
        await event.respond(f"PASSWORD CHANGED!\n\nOld: {old}\nNew: {new_pass}")
    except Exception as e:
        print(f"Password Change Error: {e}")

# === ADMIN REPLY ===
@bot.on(events.NewMessage(pattern=r'^/reply (\d+) (.+)$'))
async def admin_reply_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        user_id = int(event.pattern_match.group(1))
        message = event.pattern_match.group(2)
        await bot.send_message(user_id, f"Admin Reply:\n\n{message}")
        await event.respond(f"Reply sent to {user_id}")
    except Exception as e:
        print(f"Admin Reply Error: {e}")

# === AI REPLY ===
@bot.on(events.NewMessage(incoming=True))
async def ai_reply_handler(event):
    try:
        if not event.is_private:
            return
        text = event.text or ""
        if not text or text.startswith("/"):
            return
        if text.startswith("ROVIX-"):
            return
        user_id = event.sender_id
        if live_chat_mode.get(user_id):
            return

        button_texts = [
            "ASK AI", "PUBG", "MLBB", "CONTACT", "JOIN CHANNEL",
            "LANGUAGE", "FEEDBACK", "File Password", "LIVE CHAT",
            "PUBG PURCHASE", "FULL SEASON", "ONE MONTH",
            "MLBB PURCHASE", "Send Payment Screenshot", "Contact Admin",
            "I've Joined", "I Shared", "I Haven't Shared", "Try Again",
            "BACK",
            "EN - English", "MM - Burmese", "HI - Hindi", "AR - Arabic",
            "UR - Urdu", "BN - Bengali", "ID - Indonesian", "TH - Thai",
            "ZH - Chinese", "JA - Japanese", "KO - Korean", "RU - Russian",
            "ES - Spanish", "FR - French", "PT - Portuguese", "DE - German",
            "TR - Turkish", "FA - Persian",
        ]
        if text in button_texts:
            return

        reply = await ask_ai(text, user_id)
        msg = await bot.send_message(event.chat_id, reply, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"AI Reply Error: {e}")
        # ==========================================
# PAYMENT APPROVE
# ==========================================
@bot.on(events.NewMessage(pattern=r'^/approve (\d+)$'))
async def approve_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        user_id = int(event.pattern_match.group(1))

        approve_msg = f"""PAYMENT VERIFIED!

━━━━━━━━━━━━━━━━━━━━━━
Your payment has been approved!

Contact admin for VIP file:
{DM_ADMIN_1}
{DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

Admin will send you the file shortly."""

        await bot.send_message(user_id, approve_msg)
        await event.respond(f"Approval message sent to {user_id}")
        print(f"Payment approved for {user_id}")
    except Exception as e:
        print(f"Approve Error: {e}")

# ==========================================
# PAYMENT REJECT
# ==========================================
@bot.on(events.NewMessage(pattern=r'^/reject (\d+)$'))
async def reject_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            await event.respond("Owner only!")
            return
        user_id = int(event.pattern_match.group(1))

        reject_msg = f"""PAYMENT NOT VERIFIED

━━━━━━━━━━━━━━━━━━━━━━
We couldn't verify your payment.

Please contact admin:
{DM_ADMIN_1}
{DM_ADMIN_2}
━━━━━━━━━━━━━━━━━━━━━━"""

        await bot.send_message(user_id, reject_msg)
        await event.respond(f"Rejection message sent to {user_id}")
        print(f"Payment rejected for {user_id}")
    except Exception as e:
        print(f"Reject Error: {e}")

# ==========================================
# AUTO-BACKUP LOOP (Every 12 hours)
# ==========================================
async def auto_backup_loop():
    while True:
        try:
            await asyncio.sleep(12 * 60 * 60)
            print("Auto-backup starting...")
            file = create_backup()
            if file and os.path.exists(file):
                await bot.send_file(
                    OWNER_ID,
                    file,
                    caption=f"AUTO BACKUP\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nTotal Keys: {len(active_keys)}"
                )
                print(f"Auto-backup sent to owner")
        except Exception as e:
            print(f"Auto-backup error: {e}")

# ==========================================
# KEY EXPIRY CHECKER (Every 1 minute)
# ==========================================
async def key_expiry_checker():
    notified = {"warning": [], "expired": []}
    while True:
        try:
            await asyncio.sleep(60)
            now = datetime.now()
            for key, data in list(active_keys.items()):
                if not data.get("used"):
                    continue
                expires_at = data.get("expires_at")
                if not expires_at:
                    continue
                try:
                    expiry = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                    diff = (expiry - now).total_seconds() / 60
                    user_id = data.get("user_id")

                    if 4 <= diff <= 5 and key not in notified["warning"]:
                        try:
                            await bot.send_message(
                                user_id,
                                f"KEY EXPIRY WARNING\n\nYour key {key} will expire in 5 minutes!\n\nContact admin for new key:\n{DM_ADMIN_1}\n{DM_ADMIN_2}"
                            )
                            notified["warning"].append(key)
                        except Exception:
                            pass

                    if now > expiry and key not in notified["expired"]:
                        try:
                            await bot.send_message(
                                user_id,
                                f"KEY EXPIRED\n\nYour key {key} has expired.\n\nDM admin for a new key:\n{DM_ADMIN_1}\n{DM_ADMIN_2}"
                            )
                            notified["expired"].append(key)
                        except Exception:
                            pass
                except Exception as e:
                    print(f"Key expiry parse error: {e}")
        except Exception as e:
            print(f"Key expiry checker error: {e}")

# ==========================================
# WEB SERVER (Render ke liye)
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
    print("USERBOT RUNNING!")
    print(f"Personal: {me_user.first_name}")
    print("=" * 55)

    await bot.start(bot_token=BOT_TOKEN)
    me_bot = await bot.get_me()
    print("=" * 55)
    print("BOT RUNNING!")
    print(f"Bot: @{me_bot.username}")
    print(f"Owner ID: {OWNER_ID}")
    print(f"Total Keys: {len(active_keys)}")
    print(f"Key Expiry: {KEY_EXPIRY_MINUTES} minutes")
    print(f"File Password: {FILE_PASSWORD}")
    print("=" * 55)

    asyncio.create_task(auto_backup_loop())
    asyncio.create_task(key_expiry_checker())

    await asyncio.gather(
        userbot.run_until_disconnected(),
        bot.run_until_disconnected()
    )

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
