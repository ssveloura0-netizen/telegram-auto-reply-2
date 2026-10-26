from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
from deep_translator import GoogleTranslator
from openai import OpenAI
from PIL import Image
from flask import Flask
import asyncio, os, json, threading, requests, base64, re, time, random
from datetime import datetime, timedelta

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

BOT_LINK = "https://t.me/Vixby_bot"
CHANNEL_USERNAME = "rovixbyultimate"
CHANNEL_LINK = "https://t.me/rovixbyultimate"

# 🔴 YAHAN APNA FREE FILE KA LINK PASTE KAR (Jaise: https://t.me/rovixbyultimate/15)
FREE_FILE_LINK = "https://t.me/rovixbyultimate/123" 

DM_ADMIN_1 = "@ROVIXU1ti"
DM_ADMIN_2 = "@mak1ma_7"
FILE_PASSWORD = "buyViP@79o"

ai_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY) if GROQ_API_KEY else None
ocr_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None
VISION_MODELS = ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.2-11b-vision-instruct:free"]

OFFLINE_GIF = "https://media.giphy.com/media/WykUqckDqi95YIqtFZ/giphy.gif"
ONLINE_GIF = "https://media.giphy.com/media/L3X9GvVhP1nY23Ah6u/giphy.gif"

LANG_CODES = {"en":"en","hi":"hi","mm":"my","ar":"ar","ur":"ur","th":"th","vi":"vi","eg":"ar","bn":"bn","id":"id","zh":"zh-CN","ja":"ja","ko":"ko","ru":"ru","es":"es","fr":"fr","pt":"pt","de":"de","tr":"tr","fa":"fa"}

LANG_FLAGS = {
    "en": ("🇬🇧", "English"), "hi": ("🇮🇳", "Hindi"), "mm": ("🇲🇲", "Burmese"),
    "ar": ("🇸🇦", "Arabic"), "ur": ("🇵🇰", "Urdu"), "th": ("🇹🇭", "Thai"),
    "vi": ("🇻🇳", "Vietnamese"), "bn": ("🇧🇩", "Bengali"), "id": ("🇮🇩", "Indonesian"),
    "zh": ("🇨🇳", "Chinese"), "ja": ("🇯🇵", "Japanese"), "ko": ("🇰🇷", "Korean"),
    "ru": ("🇷🇺", "Russian"), "es": ("🇪🇸", "Spanish"), "fr": ("🇫🇷", "French"),
    "pt": ("🇵🇹", "Portuguese"), "de": ("🇩🇪", "German"), "tr": ("🇹🇷", "Turkish"),
    "fa": ("🇮🇷", "Persian"),
}

AWAY_TIMEOUT = 420
OFFLINE_COOLDOWN = 360
ONLINE_COOLDOWN = 900

last_owner_activity = {}
user_last_offline_reply = {}
user_last_online_reply = {}
user_message_times = {}
SPAM_LIMIT_1 = 5
SPAM_LIMIT_2 = 10
SPAM_LIMIT_3 = 20

KEY_FILE = "license_keys.json"
SPAM_FILE = "spam_data.json"
LANG_FILE = "user_langs.json"
TRACK_FILE = "tracked_messages.json"
BACKUP_FILE = "backup_data.json"
KEY_EXPIRY_MINUTES = 30

user_states = {}

def load_json_file(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Load error {path}: {e}")
    return default

def save_json_file(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Save error {path}: {e}")

def save_keys():
    save_json_file(KEY_FILE, active_keys)

active_keys = load_json_file(KEY_FILE, {})

def create_key():
    while True:
        key = f"ROVIXU-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        if key not in active_keys:
            break
    active_keys[key] = {"used": False, "user_id": None, "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "activated_at": None, "expires_at": None}
    save_keys()
    return key

_spam_data = load_json_file(SPAM_FILE, {"banned": [], "muted": {}, "warnings": {}})
banned_users = {int(k): True for k in _spam_data.get("banned", [])}
muted_users = {int(k): v for k, v in _spam_data.get("muted", {}).items()}
spam_warnings = {int(k): v for k, v in _spam_data.get("warnings", {}).items()}

def save_spam():
    save_json_file(SPAM_FILE, {"banned": list(banned_users.keys()), "muted": {str(k): v for k, v in muted_users.items()}, "warnings": {str(k): v for k, v in spam_warnings.items()}})

_lang_data = load_json_file(LANG_FILE, {})
user_langs = {int(k): v for k, v in _lang_data.items()}

def save_langs():
    save_json_file(LANG_FILE, {str(k): v for k, v in user_langs.items()})

tracked_msgs = load_json_file(TRACK_FILE, {"bot": {}, "userbot": {}})

def save_tracking():
    save_json_file(TRACK_FILE, tracked_msgs)

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

def create_backup():
    try:
        data = {"keys": active_keys, "user_langs": user_langs, "backup_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "total_keys": len(active_keys)}
        with open(BACKUP_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return BACKUP_FILE
    except Exception as e:
        print(f"Backup error: {e}")
        return None

lang_selected = {}

# ==========================================
# MESSAGES
# ==========================================
WELCOME_MSG = """╔══════════════════════════╗
║   💎  **𝐑𝐎𝐕𝐈𝐗𝐁𝐘 𝐁𝐎𝐓**  💎  ║
╚══════════════════════════╝

✨ **Professional Gaming Service**

━━━━━━━━━━━━━━━━━━━━━━

🌐 **Please select your language first.**

👇 Choose from below:"""

MAIN_MENU_MSG = """╔══════════════════════════╗
║   💎  **𝐑𝐎𝐕𝐈𝐗𝐁𝐘 𝐁𝐎𝐓**  💎  ║
╚══════════════════════════╝

✨ **Professional Gaming Service**

━━━━━━━━━━━━━━━━━━━━━━
🔸 **Select an option below**
🤖 **Admin:** @ROVIXU1ti
━━━━━━━━━━━━━━━━━━━━━━"""

PUBG_MENU_MSG = """🎮 **𝐏𝐔𝐁𝐆 𝐒𝐄𝐑𝐕𝐈𝐂𝐄𝐒** 🎮
━━━━━━━━━━━━━━━━━━━━━━

🔸 **Select an option below:**

━━━━━━━━━━━━━━━━━━━━━━"""

PUBG_DURATION_MSG = """🎯 **𝐒𝐄𝐋𝐄𝐂𝐓 𝐃𝐔𝐑𝐀𝐓𝐈𝐎𝐍**
━━━━━━━━━━━━━━━━━━━━━━

🔸 **Choose your plan:**

━━━━━━━━━━━━━━━━━━━━━━"""

PUBG_FULL_SEASON_MSG = f"""╔══════════════════════════╗
║  🎯  **𝐅𝐔𝐋𝐋 𝐒𝐄𝐀𝐒𝐎𝐍**  🎯  ║
╚══════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━
💰 **Price:**  **$15 / 25,000 KS**
━━━━━━━━━━━━━━━━━━━━━━

💳 **𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐌𝐄𝐓𝐇𝐎𝐃𝐒:**
━━━━━━━━━━━━━━━━━━━━━━

📱 **KBZ Pay:**
`09897052554` (Raw Eis)

📱 **Wave Pay:**
👤 {DM_ADMIN_1}
👤 {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

📸 **Send payment screenshot below.**"""

PUBG_ONE_MONTH_MSG = f"""╔══════════════════════════╗
║  📅  **𝐎𝐍𝐄 𝐌𝐎𝐍𝐓𝐇**  📅  ║
╚══════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━
💰 **Price:**  **$7 / 15,000 KS**
━━━━━━━━━━━━━━━━━━━━━━

💳 **𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐌𝐄𝐓𝐇𝐎𝐃𝐒:**
━━━━━━━━━━━━━━━━━━━━━━

📱 **KBZ Pay:**
`09897052554` (Raw Eis)

📱 **Wave Pay:**
👤 {DM_ADMIN_1}
👤 {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

📸 **Send payment screenshot below.**"""

SCREENSHOT_PROMPT_MSG = """╔══════════════════════════╗
║  📸  **𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐏𝐑𝐎𝐎𝐅**  📸  ║
╚══════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━

📤 **Send your payment screenshot below** 👇

✅ **Make sure it shows:**
🔹 Amount
🔹 Date / Time
🔹 Transaction ID

━━━━━━━━━━━━━━━━━━━━━━

⚠️ **Admin will verify shortly.**"""

CONTACT_MSG = f"""╔══════════════════════════╗
║  📞  **𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐀𝐃𝐌𝐈𝐍**  📞  ║
╚══════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━

👤 **Owner:** {DM_ADMIN_1}
👤 **Admin:** {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

⏳ **Reply within 24 hours.**"""

LANGUAGE_MSG = """╔══════════════════════════╗
║  🌐  **𝐒𝐄𝐋𝐄𝐂𝐓 𝐋𝐀𝐍𝐆𝐔𝐀𝐆𝐄**  🌐  ║
╚══════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━

🔸 **Choose your language:**

━━━━━━━━━━━━━━━━━━━━━━"""

FEEDBACK_MSG = f"""╔══════════════════════════╗
║  💬  **𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊**  💬  ║
╚══════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━

📩 **Send your feedback to:**
👤 **Owner:** {DM_ADMIN_1}
👤 **Admin:** {DM_ADMIN_2}

━━━━━━━━━━━━━━━━━━━━━━

❤️ **Thank you for your support!**"""


def language_keyboard():
    return [
        [Button.text("🇬🇧 EN"), Button.text("🇲🇲 MM"), Button.text("🇮🇳 HI")],
        [Button.text("🇸🇦 AR"), Button.text("🇵🇰 UR"), Button.text("🇧🇩 BN")],
        [Button.text("🇮🇩 ID"), Button.text("🇹🇭 TH"), Button.text("🇨🇳 ZH")],
        [Button.text("🇯🇵 JA"), Button.text("🇰🇷 KO"), Button.text("🇷🇺 RU")],
        [Button.text("🇪🇸 ES"), Button.text("🇫🇷 FR"), Button.text("🇵🇹 PT")],
        [Button.text("🇩🇪 DE"), Button.text("🇹🇷 TR"), Button.text("🇮🇷 FA")],
    ]

def main_menu_keyboard():
    return [
        [Button.text("🎮 PUBG"), Button.text("📞 CONTACT")],
        [Button.text("🌐 LANGUAGE"), Button.text("💬 FEEDBACK")],
    ]

def pubg_menu_keyboard():
    return [
        [Button.text("🎁 FREE FILE")],
        [Button.text("💳 VIP PURCHASE")],
        [Button.text("⬅️ BACK")],
    ]

def pubg_purchase_keyboard():
    return [
        [Button.text("🎯 FULL SEASON")],
        [Button.text("📅 ONE MONTH")],
        [Button.text("⬅️ BACK")],
    ]

def back_keyboard():
    return [[Button.text("⬅️ BACK")]]

def screenshot_keyboard():
    return [
        [Button.text("📸 Send Payment Screenshot")],
        [Button.text("⬅️ BACK")],
    ]
    
# ==========================================
# UTILITY FUNCTIONS
# ==========================================
async def notify_owner(title, details):
    try:
        if OWNER_ID == 0:
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await bot.send_message(OWNER_ID, f"{title}\n\n{details}\n\n📅 {now}")
    except Exception as e:
        print(f"Notify error: {e}")

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
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Analyze payment screenshot.\nReply:\nSTATUS: SUCCESS or FAILED or UNKNOWN\nAMOUNT: xxx\nTXN: xxx\nDATE: xxx\nMETHOD: xxx\nBe strict."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}],
                        max_tokens=100, temperature=0.0
                    )
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, _ocr)
                text = response.choices[0].message.content.strip()
                info = {}
                for line in text.split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        info[k.strip().lower()] = v.strip()
                return {
                    "status": info.get("status", "UNKNOWN"),
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

async def extract_game_uid(image_path):
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
        resized_path = image_path + "_game.jpg"
        img.save(resized_path, "JPEG", quality=88)
        
        with open(resized_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
            
        for model_name in VISION_MODELS:
            try:
                def _ocr():
                    return ocr_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Analyze this BGMI/PUBG game screenshot. Extract the Player Name, Player UID, Kills, and Rank.\nReply strictly in this format (do not add extra text):\nPLAYER: [Name or Unknown]\nUID: [8-12 digit UID or None]\nKILLS: [Number or Unknown]\nRANK: [Rank/Position or Unknown]"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}],
                        max_tokens=100, temperature=0.0
                    )
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, _ocr)
                text = response.choices[0].message.content.strip()
                
                info = {}
                for line in text.split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        info[k.strip().upper()] = v.strip()
                
                if info.get("UID") and info.get("UID").lower() != "none":
                    return {
                        "player": info.get("PLAYER", "Unknown"),
                        "uid": info.get("UID", "Not detected"),
                        "kills": info.get("KILLS", "Unknown"),
                        "rank": info.get("RANK", "Unknown")
                    }
            except Exception as e:
                print(f"Game OCR error ({model_name}): {e}")
                continue
        return None
    except Exception as e:
        print(f"Game OCR Error: {e}")
        return None
    finally:
        try:
            if resized_path and os.path.exists(resized_path):
                os.remove(resized_path)
        except:
            pass

async def detect_language(text):
    if not ai_client:
        return "en"
    try:
        def _call():
            return ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Detect the language of the following text. Reply ONLY with the 2-letter ISO code. Examples: en, hi, my, ar, ur, th, vi, bn, id, zh, ja, ko, ru, es, fr, pt, de, tr, fa. Nothing else."},
                    {"role": "user", "content": text}
                ],
                max_tokens=5, temperature=0.1
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

async def voice_to_text(audio_path, language="en"):
    if not ai_client:
        return None
    try:
        def _transcribe():
            with open(audio_path, "rb") as f:
                return ai_client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=f,
                    language=language if language != "auto" else None
                )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _transcribe)
        return response.text
    except Exception as e:
        print(f"Voice to text error: {e}")
        return None

# 🔥 FIXED TRANSLATION (GOOGLE PRIORITY) 🔥
async def translate_text(text, target_lang):
    if not text or target_lang == "en":
        return text
        
    # 1. Try Google Translate First (Instant & Reliable for UI)
    try:
        target_code = LANG_CODES.get(target_lang, target_lang)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: GoogleTranslator(source="auto", target=target_code).translate(text))
        if result:
            return result
    except Exception as e:
        print(f"Google translate error: {e}")
        
    # 2. Fallback to AI if Google fails
    if ai_client:
        try:
            target_name = LANG_FLAGS.get(target_lang, ("", target_lang))[1]
            def _call():
                return ai_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"You are a translator. Translate the user's text to {target_name}. Keep emojis, markdown (** **), and formatting. Reply ONLY with the translated text, nothing else. No explanation."},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=1500, temperature=0.2
                )
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, _call)
            res_ai = response.choices[0].message.content.strip()
            if res_ai:
                return res_ai
        except Exception as e:
            print(f"AI translate error: {e}")
            
    return text

async def translate_to_english(text):
    if not ai_client:
        return text
    if not text:
        return text
    try:
        def _call():
            return ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Translate the user's text to English. Keep emojis and formatting. Reply ONLY the translation."},
                    {"role": "user", "content": text}
                ],
                max_tokens=1500, temperature=0.2
            )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"🚨 Translate to EN error: {e}")
        return text

def clean_btn_text(text):
    text = text.strip().upper()
    return re.sub(r'[^A-Z ]', '', text).strip()


# ==========================================
# USERBOT
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
        try:
            sender = await event.get_sender()
            if getattr(sender, 'bot', False):
                return
            if event.sender_id == 777000:
                return
        except:
            pass

        user_id = event.sender_id
        now = time.time()

        if user_id in banned_users:
            return
        if user_id in muted_users:
            if now < muted_users[user_id]:
                return
            else:
                del muted_users[user_id]
                save_spam()

        times = user_message_times.get(user_id, [])
        times = [t for t in times if now - t < 10]
        times.append(now)
        user_message_times[user_id] = times

        if len(times) >= SPAM_LIMIT_3:
            banned_users[user_id] = True
            save_spam()
            await notify_owner("🚫 USER BANNED", f"🆔 `{user_id}`")
            return
        elif len(times) >= SPAM_LIMIT_2:
            muted_users[user_id] = now + 300
            save_spam()
            await event.reply("🔇 Muted 5 min.")
            return
        elif len(times) >= SPAM_LIMIT_1:
            if spam_warnings.get(user_id, 0) == 0:
                spam_warnings[user_id] = 1
                save_spam()
                await event.reply("⚠️ Don't spam.")
            return

        if event.voice or event.audio:
            voice_path = await event.download_media()
            try:
                text_from_voice = await voice_to_text(voice_path, "auto")
                if text_from_voice:
                    detected = await detect_language(text_from_voice)
                    flag, lang_name = LANG_FLAGS.get(detected, ("🌐", "Original"))
                    en_text = await translate_to_english(text_from_voice) if detected != "en" else text_from_voice
                    await notify_owner(
                        "🎤 Voice Message!",
                        f"🆔 `{user_id}`\n\n{flag} **{lang_name}:**\n{text_from_voice}\n\n🇬🇧 **English:**\n{en_text}"
                    )
                    await event.reply("🎤 Got it! Owner will reply soon.")
            except Exception as e:
                print(f"Voice error: {e}")
            finally:
                try:
                    if voice_path and os.path.exists(voice_path):
                        os.remove(voice_path)
                except:
                    pass
            return

        user_message = event.raw_text or ""

        if user_message and len(user_message.strip()) > 1:
            try:
                detected = await detect_language(user_message)
                sender = await event.get_sender()
                username = f"@{sender.username}" if sender.username else "No username"
                if detected != "en":
                    flag, lang_name = LANG_FLAGS.get(detected, ("🌐", "Original"))
                    en_text = await translate_to_english(user_message)
                    await notify_owner(
                        "📩 **New Message**",
                        f"👤 {sender.first_name}\n🔗 {username}\n🆔 `{user_id}`\n\n{flag} **{lang_name}:**\n{user_message[:300]}\n\n🇬🇧 **English:**\n{en_text[:300]}"
                    )
                else:
                    await notify_owner(
                        "📩 New Message",
                        f"👤 {sender.first_name}\n🔗 {username}\n🆔 `{user_id}`\n💬 {user_message[:300]}"
                    )
            except Exception as e:
                print(f"Translate error: {e}")

        is_offline = (now - last_owner_activity.get(user_id, 0)) >= AWAY_TIMEOUT

        if is_offline:
            last_reply = user_last_offline_reply.get(user_id, 0)
            if now - last_reply < OFFLINE_COOLDOWN:
                return

            offline_text = f"""💎 **AUTO-REPLY** 💎
━━━━━━━━━━━━━━━━━━
💠 **OWNER IS OFFLINE**
ပိုင်ရှင် အော့ဖ်လိုင်း ဖြစ်နေပါသည်။

📢 Please contact the bot for help.
အမြန်အကူအညီအတွက် ဘော့ကို ဆက်သွယ်ပါ။
━━━━━━━━━━━━━━━━━━
🤖 ROVIXBY BOT
{BOT_LINK}
📢 ROVIXBY CHANNEL
{CHANNEL_LINK}
━━━━━━━━━━━━━━━━"""

            try:
                msg = await userbot.send_file(event.chat_id, OFFLINE_GIF, caption=offline_text)
                track_userbot(user_id, msg.id)
                user_last_offline_reply[user_id] = now
            except Exception as e:
                print(f"Offline reply error: {e}")

        else:
            last_reply = user_last_online_reply.get(user_id, 0)
            if now - last_reply < ONLINE_COOLDOWN:
                return

            online_text = """✅ **Message Received**
မက်ဆေ့ခ်ျ ရရှိပါသည်။

👤 Owner will reply soon.
ပိုင်ရှင် မကြာမီ ပြန်လည် ဖြေကြားပါမည်။"""

            try:
                msg = await userbot.send_file(event.chat_id, ONLINE_GIF, caption=online_text)
                track_userbot(user_id, msg.id)
                user_last_online_reply[user_id] = now
            except Exception as e:
                print(f"Online reply error: {e}")

    except Exception as e:
        print(f"Userbot Error: {e}")

@userbot.on(events.NewMessage(outgoing=True))
async def owner_reply_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.chat_id
        last_owner_activity[user_id] = time.time()

        text = event.text or ""

        if text.startswith("tr//"):
            try:
                parts = text.split(" ", 1)
                lang_code = parts[0].replace("tr//", "").lower()
                message_to_translate = parts[1] if len(parts) > 1 else ""
                if lang_code in LANG_CODES and message_to_translate:
                    translated = GoogleTranslator(source="en", target=LANG_CODES[lang_code]).translate(message_to_translate)
                    await userbot.send_message(user_id, translated)
                    await event.delete()
                    return
            except Exception as e:
                print(f"Translation error: {e}")

        if event.voice or event.audio:
            voice_path = await event.download_media()
            try:
                text_from_voice = await voice_to_text(voice_path, "en")
                if text_from_voice:
                    target_lang = user_langs.get(user_id, "en")
                    if target_lang != "en":
                        translated = await translate_text(text_from_voice, target_lang)
                        await userbot.send_message(user_id, translated)
                    else:
                        await userbot.send_message(user_id, f"🎤 Voice:\n\n{text_from_voice}")
            except Exception as e:
                print(f"Owner Voice error: {e}")
            finally:
                try:
                    if voice_path and os.path.exists(voice_path):
                        os.remove(voice_path)
                except:
                    pass
            return

        if text and text.startswith("/"):
            return

        if text:
            target_lang = user_langs.get(user_id, "en")
            print(f"🌐 Owner replied. Target lang: {target_lang}")
            if target_lang != "en":
                try:
                    translated = await translate_text(text, target_lang)
                    if translated and translated != text:
                        await userbot.send_message(user_id, translated)
                        try:
                            await event.delete()
                        except:
                            pass
                except Exception as e:
                    print(f"Auto-translate owner msg error: {e}")

        if str(user_id) in tracked_msgs["bot"]:
            for msg_id in list(tracked_msgs["bot"][str(user_id)]):
                try:
                    await bot.delete_messages(user_id, msg_id)
                except:
                    pass
            tracked_msgs["bot"][str(user_id)] = []

        if str(user_id) in tracked_msgs["userbot"]:
            for msg_id in list(tracked_msgs["userbot"][str(user_id)]):
                try:
                    await userbot.delete_messages(user_id, msg_id)
                except:
                    pass
            tracked_msgs["userbot"][str(user_id)] = []

        save_tracking()
    except Exception as e:
        print(f"Owner Reply Error: {e}")
        
# ==========================================
# BOT
# ==========================================
bot = TelegramClient('bot_session', API_ID, API_HASH)

# 🔥 FIXED SEND_TRANSLATED FUNCTION 🔥
async def send_translated(chat_id, text, buttons, user_id, track=True):
    try:
        user_lang = user_langs.get(user_id, "en")
        print(f"📤 Sending message to {user_id} | lang: {user_lang}")
        
        if user_lang != "en":
            translated = await translate_text(text, user_lang)
        else:
            translated = text
            
        # Safely Translate Buttons
        if user_lang != "en" and buttons:
            new_buttons = []
            for row in buttons:
                new_row = []
                for btn in row:
                    trans_text = await translate_text(btn.text, user_lang) if btn.text else ""
                    if getattr(btn, 'url', None):
                        new_row.append(Button.url(trans_text, btn.url))
                    else:
                        new_row.append(Button.text(trans_text))
                new_buttons.append(new_row)
            buttons = new_buttons

        msg = await bot.send_message(chat_id, translated, buttons=buttons)
        if track:
            track_bot(user_id, msg.id)
        return msg
    except Exception as e:
        print(f"🚨 Send translated error: {e}")
        return None

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
            await notify_owner("🔔 New User!", f"👤 {sender.first_name}\n🔗 {username}\n🆔 `{user_id}`")
        except:
            pass
        lang_selected[user_id] = False
        msg = await bot.send_message(event.chat_id, WELCOME_MSG, buttons=language_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Start Error: {e}")

# === LANGUAGE SELECT ===
@bot.on(events.NewMessage(incoming=True))
async def lang_select(event):
    try:
        if not event.is_private or not event.text:
            return
        clean = re.sub(r'[^A-Z]', '', event.text.strip().upper())
        valid = ["EN", "MM", "HI", "AR", "UR", "BN", "ID", "TH", "ZH", "JA", "KO", "RU", "ES", "FR", "PT", "DE", "TR", "FA"]
        if clean not in valid:
            return
        user_id = event.sender_id
        lang_map = {"EN": "en", "MM": "mm", "HI": "hi", "AR": "ar", "UR": "ur", "BN": "bn", "ID": "id", "TH": "th", "ZH": "zh", "JA": "ja", "KO": "ko", "RU": "ru", "ES": "es", "FR": "fr", "PT": "pt", "DE": "de", "TR": "tr", "FA": "fa"}
        user_langs[user_id] = lang_map[clean]
        save_langs()
        lang_selected[user_id] = True
        print(f"✅ User {user_id} selected language: {lang_map[clean]}")
        
        if clean == "EN":
            menu_text = MAIN_MENU_MSG
        else:
            menu_text = await translate_text(MAIN_MENU_MSG, lang_map[clean])
        
        msg = await bot.send_message(event.chat_id, f"✅ **Language:** **{clean}**\n\n" + menu_text, buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Lang Select Error: {e}")

# === NEWKEY ===
@bot.on(events.NewMessage(pattern=r'^/newkey$'))
async def newkey_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        key = create_key()
        await event.respond(f"✅ **New Key**\n\n🔑 `{key}`\n\n⏱️ 30 min after activation")
    except Exception as e:
        print(f"Newkey Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/newkey (\d+)$'))
async def newkey_multi_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        count = int(event.pattern_match.group(1))
        if count > 50:
            count = 50
        keys = [create_key() for _ in range(count)]
        key_list = "\n".join([f"{i+1}. `{k}`" for i, k in enumerate(keys)])
        await event.respond(f"✅ **{count} Keys**\n\n{key_list}")
    except Exception as e:
        print(f"Newkey Multi Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/keys$'))
async def keys_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        if not active_keys:
            await event.respond("📭 No keys.")
            return
        total = len(active_keys)
        used = sum(1 for k in active_keys.values() if k.get("used"))
        await event.respond(f"📊 **Keys**\n\n🔑 Total: `{total}`\n✅ Used: `{used}`\n🆓 Unused: `{total - used}`")
    except Exception as e:
        print(f"Keys Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/stats$'))
async def stats_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        total_keys = len(active_keys)
        used_keys = sum(1 for k in active_keys.values() if k.get("used"))
        await event.respond(f"📊 **Stats**\n\n🔑 Total: `{total_keys}`\n✅ Used: `{used_keys}`\n🆓 Unused: `{total_keys - used_keys}`\n👥 Active: `{len(last_owner_activity)}`\n🚫 Banned: `{len(banned_users)}`")
    except Exception as e:
        print(f"Stats Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/backup$'))
async def backup_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        file = create_backup()
        if file and os.path.exists(file):
            await bot.send_file(OWNER_ID, file, caption=f"💾 **Backup**\n\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Backup Error: {e}")

# === MAIN MENU HANDLERS ===
@bot.on(events.NewMessage(incoming=True))
async def pubg_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "PUBG":
            return
        user_id = event.sender_id
        await send_translated(event.chat_id, PUBG_MENU_MSG, pubg_menu_keyboard(), user_id)
    except Exception as e:
        print(f"PUBG Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def contact_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "CONTACT":
            return
        user_id = event.sender_id
        await send_translated(event.chat_id, CONTACT_MSG, back_keyboard(), user_id)
    except Exception as e:
        print(f"Contact Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def language_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "LANGUAGE":
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, LANGUAGE_MSG, buttons=language_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Language Error: {e}")

# === FEEDBACK HANDLERS ===
@bot.on(events.NewMessage(incoming=True))
async def feedback_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "FEEDBACK":
            return
        user_id = event.sender_id
        user_states[user_id] = "awaiting_feedback"
        
        feedback_prompt = """💬 **𝐏𝐋𝐄𝐀𝐒𝐄 𝐒𝐄𝐍𝐃 𝐘𝐎𝐔𝐑 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊**
━━━━━━━━━━━━━━━━━━━━━━

📝 **You can send text or a photo.**
Our team will see it directly.

👇 **Type below:**"""
        await send_translated(event.chat_id, feedback_prompt, back_keyboard(), user_id)
    except Exception as e:
        print(f"Feedback Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def feedback_receive_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id
        if user_states.get(user_id) != "awaiting_feedback":
            return
            
        if event.text and clean_btn_text(event.text) in ["BACK", "PUBG", "CONTACT", "LANGUAGE", "FEEDBACK"]:
            user_states[user_id] = None
            return
            
        user_states[user_id] = None
        
        target_channel = "@rovixbyultimate"
        try:
            await bot.forward_messages(target_channel, event.message)
            await event.reply("✅ **Feedback sent successfully!** Thank you.")
        except Exception as e:
            print(f"Forward error: {e}")
            try:
                if event.photo:
                    await bot.send_file(target_channel, event.photo, caption=event.raw_text or "Photo Feedback")
                else:
                    await bot.send_message(target_channel, f"📩 **Feedback:**\n\n{event.raw_text}")
                await event.reply("✅ **Feedback sent successfully!** Thank you.")
            except Exception as e2:
                print(f"Copy feedback error: {e2}")
                await event.reply("⚠️ Could not send feedback. Try again later.")
                
    except Exception as e:
        print(f"Feedback receive error: {e}")

# === FREE FILE ===
@bot.on(events.NewMessage(incoming=True))
async def free_file_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "FREE FILE":
            return
            
        user_id = event.sender_id
        user_lang = user_langs.get(user_id, "en")

        is_joined = False
        try:
            await userbot(GetParticipantRequest(channel=CHANNEL_USERNAME, participant=user_id))
            is_joined = True
        except UserNotParticipantError:
            is_joined = False
        except Exception as e:
            print(f"Join check error (Make sure userbot is admin in channel): {e}")
            is_joined = True 

        if not is_joined:
            join_msg = """⚠️ **𝐘𝐎𝐔 𝐌𝐔𝐒𝐓 𝐉𝐎𝐈𝐍 𝐎𝐔𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐅𝐈𝐑𝐒𝐓!**
━━━━━━━━━━━━━━━━━━━━━━

👇 **Join below to get the FREE FILE:**"""
            join_buttons = [
                [Button.url("📢 Join Channel", CHANNEL_LINK)],
                [Button.text("✅ I Joined")],
                [Button.text("⬅️ BACK")]
            ]
            await send_translated(event.chat_id, join_msg, join_buttons, user_id)
            return

        loading_texts = [
            "🔍 **𝐕𝐄𝐑𝐈𝐅𝐘𝐈𝐍𝐆...**\n\n━━━━━━━━━━━━━━━━━━━━━━\n`[░░░░░░░░░░] 0%`\n\n⏳ Please wait...\n━━━━━━━━━━━━━━━━━━━━━━",
            "🔍 **𝐕𝐄𝐑𝐈𝐅𝐘𝐈𝐍𝐆...**\n\n━━━━━━━━━━━━━━━━━━━━━━\n`[████░░░░░░] 40%`\n\n🔒 Checking...\n━━━━━━━━━━━━━━━━━━━━━━",
            "🔍 **𝐕𝐄𝐑𝐈𝐅𝐘𝐈𝐍𝐆...**\n\n━━━━━━━━━━━━━━━━━━━━━━\n`[████████░░] 80%`\n\n🔐 Validating...\n━━━━━━━━━━━━━━━━━━━━━━",
            "✅ **𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃!**\n\n━━━━━━━━━━━━━━━━━━━━━━\n`[██████████] 100%`\n\n🎉 Success!\n━━━━━━━━━━━━━━━━━━━━━━"
        ]
        if user_lang != "en":
            loading_texts = [await translate_text(t, user_lang) for t in loading_texts]

        verify_msg = await bot.send_message(event.chat_id, loading_texts[0])
        await asyncio.sleep(0.7)
        await verify_msg.edit(loading_texts[1])
        await asyncio.sleep(0.7)
        await verify_msg.edit(loading_texts[2])
        await asyncio.sleep(0.7)
        await verify_msg.edit(loading_texts[3])
        await asyncio.sleep(0.6)

        try:
            await verify_msg.delete()
        except:
            pass

        file_msg = """✅ **𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐉𝐎𝐈𝐍𝐄𝐃!**
━━━━━━━━━━━━━━━━━━━━━━

👇 **Click below to get your FREE FILE:**"""
        
        file_buttons = [
            [Button.url("📁 𝐆𝐄𝐓 𝐅𝐈𝐋𝐄", FREE_FILE_LINK)],
            [Button.text("⬅️ BACK")]
        ]
        
        await send_translated(event.chat_id, file_msg, file_buttons, user_id)
        
    except Exception as e:
        print(f"FREE FILE Error: {e}")


# === VIP PURCHASE ===
@bot.on(events.NewMessage(incoming=True))
async def vip_purchase_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "VIP PURCHASE":
            return
        user_id = event.sender_id
        await send_translated(event.chat_id, PUBG_DURATION_MSG, pubg_purchase_keyboard(), user_id)
    except Exception as e:
        print(f"VIP Purchase Error: {e}")


@bot.on(events.NewMessage(incoming=True))
async def full_season_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "FULL SEASON":
            return
        user_id = event.sender_id
        await send_translated(event.chat_id, PUBG_FULL_SEASON_MSG, screenshot_keyboard(), user_id)
    except Exception as e:
        print(f"Full Season Error: {e}")


@bot.on(events.NewMessage(incoming=True))
async def one_month_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "ONE MONTH":
            return
        user_id = event.sender_id
        await send_translated(event.chat_id, PUBG_ONE_MONTH_MSG, screenshot_keyboard(), user_id)
    except Exception as e:
        print(f"One Month Error: {e}")


@bot.on(events.NewMessage(incoming=True))
async def screenshot_prompt_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "SEND PAYMENT SCREENSHOT":
            return
        user_id = event.sender_id
        await send_translated(event.chat_id, SCREENSHOT_PROMPT_MSG, back_keyboard(), user_id)
    except Exception as e:
        print(f"Screenshot Error: {e}")


# === BACK ===
@bot.on(events.NewMessage(incoming=True))
async def back_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "BACK":
            return
        user_id = event.sender_id
        user_states[user_id] = None 
        await send_translated(event.chat_id, MAIN_MENU_MSG, main_menu_keyboard(), user_id)
    except Exception as e:
        print(f"Back Error: {e}")


# === IMAGE HANDLER ===
@bot.on(events.NewMessage(incoming=True))
async def image_handler(event):
    try:
        if not event.is_private or not event.photo:
            return
            
        user_id = event.sender_id
        if user_states.get(user_id) == "awaiting_feedback":
            return

        progress = await bot.send_message(event.chat_id, "🔍 **Analyzing Image...**")
        path = await event.download_media()
        
        payment_info = await extract_payment_info(path)
        
        if payment_info and payment_info.get("status") == "SUCCESS" and payment_info.get("amount") != "Not detected":
            await progress.edit("✅ **𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃**\n\n📸 Sent to admin. Please wait.")
            sender = await event.get_sender()
            username = f"@{sender.username}" if sender.username else "No username"
            await notify_owner("💰 NEW PAYMENT", f"👤 {sender.first_name}\n🔗 {username}\n🆔 `{user_id}`\n\n✅ SUCCESS\n💵 {payment_info.get('amount', 'N/A')}\n📅 {payment_info.get('date', 'N/A')}\n🔢 {payment_info.get('txn_id', 'N/A')}\n💳 {payment_info.get('method', 'N/A')}\n\n`/approve {user_id}`\n`/reject {user_id}`")
            try:
                await bot.send_file(OWNER_ID, event.photo, caption=f"📸 `{user_id}`")
            except:
                pass
                
        elif payment_info and payment_info.get("status") == "FAILED":
            await progress.edit("❌ **Payment Failed**\n\nSend a successful payment screenshot.")
        else:
            game_info = await extract_game_uid(path)
            
            if game_info and game_info.get("uid") != "Not detected":
                result_msg = f"""✅ **𝐏𝐋𝐀𝐘𝐄𝐑 𝐃𝐄𝐓𝐄𝐂𝐓𝐄𝐃**
━━━━━━━━━━━━━━━━━━━━━━

👤 **Player:** {game_info.get('player')}
🆔 **UID:** `{game_info.get('uid')}`
🔫 **Kills:** {game_info.get('kills')}
🏆 **Rank:** {game_info.get('rank')}

━━━━━━━━━━━━━━━━━━━━━━
📩 **Need help?** {DM_ADMIN_1}"""
                await progress.edit(result_msg)
                await notify_owner("🎮 Game Result Detected", f"User: `{user_id}`\nUID: `{game_info.get('uid')}`\nKills: {game_info.get('kills')}")
            else:
                await progress.edit("⚠️ **Cannot Verify**\n\nSend a clear successful payment screenshot or a valid Game Result screenshot.")
                
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except:
            pass
            
    except Exception as e:
        print(f"Image Handler Error: {e}")


# === ADMIN REPLY ===
@bot.on(events.NewMessage(pattern=r'^/reply (\d+) (.+)$'))
async def admin_reply_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        user_id = int(event.pattern_match.group(1))
        message = event.pattern_match.group(2)
        target_lang = user_langs.get(user_id, "en")
        if target_lang != "en":
            message = await translate_text(message, target_lang)
        await bot.send_message(user_id, f"👤 **Admin:**\n\n{message}")
        await event.respond(f"✅ Sent to `{user_id}`")
    except Exception as e:
        print(f"Admin Reply Error: {e}")


# === APPROVE ===
@bot.on(events.NewMessage(pattern=r'^/approve (\d+)$'))
async def approve_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        user_id = int(event.pattern_match.group(1))
        key = create_key()
        approve_msg = f"""╔══════════════════════════╗
║  ✅  **𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃**  ✅  ║
╚══════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━
🔑 **𝐘𝐎𝐔𝐑 𝐋𝐈𝐂𝐄𝐍𝐒𝐄 𝐊𝐄𝐘:**
`{key}`

⏱️ Valid **{KEY_EXPIRY_MINUTES} min** after activation
━━━━━━━━━━━━━━━━━━━━━━

📩 {DM_ADMIN_1}"""
        target_lang = user_langs.get(user_id, "en")
        if target_lang != "en":
            approve_msg = await translate_text(approve_msg, target_lang)
        await bot.send_message(user_id, approve_msg)
        await event.respond(f"✅ Key sent to `{user_id}`\n\n🔑 `{key}`")
        await notify_owner("🔑 AUTO KEY ISSUED", f"👤 `{user_id}`\n🔑 `{key}`")
    except Exception as e:
        print(f"Approve Error: {e}")


@bot.on(events.NewMessage(pattern=r'^/reject (\d+)$'))
async def reject_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        user_id = int(event.pattern_match.group(1))
        reject_msg = f"❌ **Payment Not Verified**\n\n📩 {DM_ADMIN_1}"
        target_lang = user_langs.get(user_id, "en")
        if target_lang != "en":
            reject_msg = await translate_text(reject_msg, target_lang)
        await bot.send_message(user_id, reject_msg)
        await event.respond(f"❌ Sent to `{user_id}`")
    except Exception as e:
        print(f"Reject Error: {e}")
        
        
# === AUTO BACKUP ===
async def auto_backup_loop():
    while True:
        try:
            await asyncio.sleep(12 * 60 * 60)
            file = create_backup()
            if file and os.path.exists(file):
                await bot.send_file(OWNER_ID, file, caption=f"💾 **Auto Backup**\n\n🔑 {len(active_keys)} keys")
        except Exception as e:
            print(f"Auto-backup error: {e}")


# === KEY EXPIRY CHECKER ===
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
                            await bot.send_message(user_id, f"⚠️ **Key Expiring**\n\n🔑 `{key}` — 5 min left.\n\n📩 {DM_ADMIN_1}")
                            notified["warning"].append(key)
                        except:
                            pass
                    if now > expiry and key not in notified["expired"]:
                        try:
                            await bot.send_message(user_id, f"❌ **Key Expired**\n\n🔑 `{key}`\n\n📩 {DM_ADMIN_1}")
                            notified["expired"].append(key)
                        except:
                            pass
                except Exception as e:
                    print(f"Key expiry parse error: {e}")
        except Exception as e:
            print(f"Key expiry checker error: {e}")


# === WEB SERVER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)


# === MAIN ===
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
    print(f"Banned: {len(banned_users)}")
    print("=" * 55)

    asyncio.create_task(auto_backup_loop())
    asyncio.create_task(key_expiry_checker())

    await asyncio.gather(userbot.run_until_disconnected(), bot.run_until_disconnected())


if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
