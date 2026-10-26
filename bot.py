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

# 🔴 YAHAN APNA FREE FILE KA LINK PASTE KAR (Link change karne ke liye sirf yeh number badalna)
FREE_FILE_LINK = "https://t.me/rovixbyultimate/49" 

DM_ADMIN_1 = "@ROVIXU1ti"
DM_ADMIN_2 = "@mak1ma_7"

ai_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY) if GROQ_API_KEY else None
ocr_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None
VISION_MODELS = ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.2-11b-vision-instruct:free"]

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
BACKUP_FILE = "backup_data.json"

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
    active_keys[key] = {"used": False, "user_id": None, "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    save_keys()
    return key

_spam_data = load_json_file(SPAM_FILE, {"banned": [], "muted": {}, "warnings": {}})
banned_users = {int(k): True for k in _spam_data.get("banned", [])}
muted_users = {int(k): v for k, v in _spam_data.get("muted", {}).items()}
spam_warnings = {int(k): v for k, v in _spam_data.get("warnings", {}).items()}

def save_spam():
    save_json_file(SPAM_FILE, {"banned": list(banned_users.keys()), "muted": {str(k): v for k, v in muted_users.items()}, "warnings": {str(k): v for k, v in spam_warnings.items()}})

tracked_msgs = load_json_file("tracked_messages.json", {"bot": {}, "userbot": {}})

def save_tracking():
    save_json_file("tracked_messages.json", tracked_msgs)

def track_bot(user_id, msg_id):
    uid = str(user_id)
    if uid not in tracked_msgs["bot"]: tracked_msgs["bot"][uid] = []
    tracked_msgs["bot"][uid].append(msg_id)
    save_tracking()

def track_userbot(user_id, msg_id):
    uid = str(user_id)
    if uid not in tracked_msgs["userbot"]: tracked_msgs["userbot"][uid] = []
    tracked_msgs["userbot"][uid].append(msg_id)
    save_tracking()

def create_backup():
    try:
        data = {"keys": active_keys, "backup_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        with open(BACKUP_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return BACKUP_FILE
    except Exception as e:
        return None

# ==========================================
# MESSAGES (BILINGUAL)
# ==========================================
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

def main_menu_keyboard():
    return [
        [Button.text("🎮 PUBG"), Button.text("📞 CONTACT")],
        [Button.text("💬 FEEDBACK")],
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
        if OWNER_ID == 0: return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await bot.send_message(OWNER_ID, f"{title}\n\n{details}\n\n📅 {now}")
    except Exception as e:
        print(f"Notify error: {e}")

async def extract_payment_info(image_path):
    if not ocr_client: return None
    resized_path = None
    try:
        img = Image.open(image_path)
        W, H = img.size
        if W > 1280:
            ratio = 1280 / W
            img = img.resize((1280, int(H * ratio)), Image.LANCZOS)
        if img.mode != "RGB": img = img.convert("RGB")
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
            except:
                continue
        return None
    except Exception as e:
        return None
    finally:
        try:
            if resized_path and os.path.exists(resized_path): os.remove(resized_path)
        except: pass

async def extract_game_uid(image_path):
    if not ocr_client: return None
    resized_path = None
    try:
        img = Image.open(image_path)
        W, H = img.size
        if W > 1280:
            ratio = 1280 / W
            img = img.resize((1280, int(H * ratio)), Image.LANCZOS)
        if img.mode != "RGB": img = img.convert("RGB")
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
            except:
                continue
        return None
    except:
        return None
    finally:
        try:
            if resized_path and os.path.exists(resized_path): os.remove(resized_path)
        except: pass

async def detect_language(text):
    if not ai_client: return "en"
    try:
        def _call():
            return ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Detect the language of the following text. Reply ONLY with the 2-letter ISO code. Nothing else."},
                    {"role": "user", "content": text}
                ],
                max_tokens=5, temperature=0.1
            )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call)
        code = response.choices[0].message.content.strip().lower()
        return code if len(code) == 2 else "en"
    except:
        return "en"

async def voice_to_text(audio_path, language="en"):
    if not ai_client: return None
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
    except:
        return None

async def translate_to_english(text):
    if not ai_client or not text: return text
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
    except:
        return text

def clean_btn_text(text):
    text = text.strip().upper()
    return re.sub(r'[^A-Z ]', '', text).strip()

async def translate_burmese(text):
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: GoogleTranslator(source="en", target="my").translate(text))
    except Exception as e:
        print(f"Burmese translate error: {e}")
        return ""

async def send_bilingual(chat_id, english_text, buttons, track=True):
    try:
        burmese_text = await translate_burmese(english_text)
        
        final_text = english_text
        if burmese_text and burmese_text.strip() != english_text.strip():
            final_text = f"{english_text}\n\n{burmese_text}"

        msg = await bot.send_message(chat_id, final_text, buttons=buttons)
        if track:
            track_bot(chat_id, msg.id)
        return msg
    except Exception as e:
        print(f"🚨 Send error: {e}")
        return None


# ==========================================
# USERBOT
# ==========================================
userbot = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@userbot.on(events.NewMessage(incoming=True))
async def userbot_handler(event):
    try:
        if not event.is_private: return
        me = await userbot.get_me()
        if event.sender_id == me.id: return
        try:
            sender = await event.get_sender()
            if getattr(sender, 'bot', False) or event.sender_id == 777000: return
        except: pass

        user_id = event.sender_id
        now = time.time()

        if user_id in banned_users: return
        if user_id in muted_users:
            if now < muted_users[user_id]: return
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
                    en_text = await translate_to_english(text_from_voice) if detected != "en" else text_from_voice
                    await notify_owner(
                        "🎤 Voice Message!",
                        f"🆔 `{user_id}`\n\n**Original:**\n{text_from_voice}\n\n🇬🇧 **English:**\n{en_text}"
                    )
                    await event.reply("🎤 Got it! Owner will reply soon.")
            except Exception as e:
                print(f"Voice error: {e}")
            finally:
                try:
                    if voice_path and os.path.exists(voice_path): os.remove(voice_path)
                except: pass
            return

        user_message = event.raw_text or ""

        if user_message and len(user_message.strip()) > 1:
            try:
                detected = await detect_language(user_message)
                sender = await event.get_sender()
                username = f"@{sender.username}" if sender.username else "No username"
                if detected != "en":
                    en_text = await translate_to_english(user_message)
                    await notify_owner(
                        "📩 **New Message**",
                        f"👤 {sender.first_name}\n🔗 {username}\n🆔 `{user_id}`\n\n**Original:**\n{user_message[:300]}\n\n🇬🇧 **English:**\n{en_text[:300]}"
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
            if now - last_reply < OFFLINE_COOLDOWN: return

            # Simple text, no gif, no "AUTO-REPLY" text
            offline_text = f"""OWNER IS OFFLINE
ပိုင်ရှင် အော့ဖ်လိုင်း ဖြစ်နေပါသည်။

Please contact the bot for help.
အမြန်အကူအညီအတွက် ဘော့ကို ဆက်သွယ်ပါ။

ROVIXBY BOT
{BOT_LINK}
ROVIXBY CHANNEL
{CHANNEL_LINK}"""

            try:
                msg = await userbot.send_message(event.chat_id, offline_text)
                track_userbot(user_id, msg.id)
                user_last_offline_reply[user_id] = now
            except Exception as e:
                print(f"Offline reply error: {e}")

        else:
            last_reply = user_last_online_reply.get(user_id, 0)
            if now - last_reply < ONLINE_COOLDOWN: return

            # Simple text, no gif
            online_text = """Message Received
မက်ဆေ့ခ်ျ ရရှိပါသည်။

Owner will reply soon.
ပိုင်ရှင် မကြာမီ ပြန်လည် ဖြေကြားပါမည်။"""

            try:
                msg = await userbot.send_message(event.chat_id, online_text)
                track_userbot(user_id, msg.id)
                user_last_online_reply[user_id] = now
            except Exception as e:
                print(f"Online reply error: {e}")

    except Exception as e:
        print(f"Userbot Error: {e}")

@userbot.on(events.NewMessage(outgoing=True))
async def owner_reply_handler(event):
    try:
        if not event.is_private: return
        user_id = event.chat_id
        last_owner_activity[user_id] = time.time()
        text = event.text or ""

        if text.startswith("tr//"):
            try:
                parts = text.split(" ", 1)
                lang_code = parts[0].replace("tr//", "").lower()
                message_to_translate = parts[1] if len(parts) > 1 else ""
                if message_to_translate:
                    translated = GoogleTranslator(source="en", target="my").translate(message_to_translate)
                    await userbot.send_message(user_id, translated)
                    await event.delete()
                    return
            except: pass

        if event.voice or event.audio:
            voice_path = await event.download_media()
            try:
                text_from_voice = await voice_to_text(voice_path, "en")
                if text_from_voice:
                    translated = GoogleTranslator(source="en", target="my").translate(text_from_voice)
                    await userbot.send_message(user_id, translated)
            except: pass
            finally:
                try:
                    if voice_path and os.path.exists(voice_path): os.remove(voice_path)
                except: pass
            return

        if text and text.startswith("/"): return

        if text:
            try:
                translated = GoogleTranslator(source="en", target="my").translate(text)
                if translated and translated != text:
                    await userbot.send_message(user_id, translated)
                    try: await event.delete()
                    except: pass
            except: pass

        if str(user_id) in tracked_msgs["bot"]:
            for msg_id in list(tracked_msgs["bot"][str(user_id)]):
                try: await bot.delete_messages(user_id, msg_id)
                except: pass
            tracked_msgs["bot"][str(user_id)] = []

        if str(user_id) in tracked_msgs["userbot"]:
            for msg_id in list(tracked_msgs["userbot"][str(user_id)]):
                try: await userbot.delete_messages(user_id, msg_id)
                except: pass
            tracked_msgs["userbot"][str(user_id)] = []

        save_tracking()
    except Exception as e:
        print(f"Owner Reply Error: {e}")
        
# ==========================================
# BOT
# ==========================================
bot = TelegramClient('bot_session', API_ID, API_HASH)

# === START ===
@bot.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    try:
        if not event.is_private: return
        user_id = event.sender_id
        try:
            sender = await event.get_sender()
            await notify_owner("🔔 New User!", f"👤 {sender.first_name}\n🆔 `{user_id}`")
        except: pass
        
        await send_bilingual(event.chat_id, MAIN_MENU_MSG, main_menu_keyboard())
    except Exception as e:
        print(f"Start Error: {e}")

# === NEWKEY ===
@bot.on(events.NewMessage(pattern=r'^/newkey$'))
async def newkey_handler(event):
    try:
        if event.sender_id != OWNER_ID: return
        key = create_key()
        await event.respond(f"✅ **New Key**\n\n🔑 `{key}`")
    except Exception as e: print(f"Newkey Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/keys$'))
async def keys_handler(event):
    try:
        if event.sender_id != OWNER_ID: return
        total = len(active_keys)
        used = sum(1 for k in active_keys.values() if k.get("used"))
        await event.respond(f"📊 **Keys**\n\n🔑 Total: `{total}`\n✅ Used: `{used}`\n🆓 Unused: `{total - used}`")
    except Exception as e: print(f"Keys Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/backup$'))
async def backup_handler(event):
    try:
        if event.sender_id != OWNER_ID: return
        file = create_backup()
        if file and os.path.exists(file):
            await bot.send_file(OWNER_ID, file, caption=f"💾 **Backup**")
    except Exception as e: print(f"Backup Error: {e}")

# === MAIN MENU HANDLERS ===
@bot.on(events.NewMessage(incoming=True))
async def pubg_handler(event):
    try:
        if not event.is_private or not event.text: return
        if clean_btn_text(event.text) != "PUBG": return
        await send_bilingual(event.chat_id, PUBG_MENU_MSG, pubg_menu_keyboard())
    except Exception as e: print(f"PUBG Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def contact_handler(event):
    try:
        if not event.is_private or not event.text: return
        if clean_btn_text(event.text) != "CONTACT": return
        await send_bilingual(event.chat_id, CONTACT_MSG, back_keyboard())
    except Exception as e: print(f"Contact Error: {e}")

# === FEEDBACK ===
@bot.on(events.NewMessage(incoming=True))
async def feedback_handler(event):
    try:
        if not event.is_private or not event.text: return
        if clean_btn_text(event.text) != "FEEDBACK": return
        user_id = event.sender_id
        user_states[user_id] = "awaiting_feedback"
        
        feedback_prompt = """💬 **PLEASE SEND YOUR FEEDBACK**
━━━━━━━━━━━━━━━━━━━━━━

📝 **You can send text or a photo.**
Our team will see it directly.

👇 **Type below:**"""
        await send_bilingual(event.chat_id, feedback_prompt, back_keyboard())
    except Exception as e: print(f"Feedback Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def feedback_receive_handler(event):
    try:
        if not event.is_private: return
        user_id = event.sender_id
        if user_states.get(user_id) != "awaiting_feedback": return
            
        if event.text and clean_btn_text(event.text) in ["BACK", "PUBG", "CONTACT", "FEEDBACK"]:
            user_states[user_id] = None
            return
            
        user_states[user_id] = None
        target_channel = "@rovixbyultimate"
        try:
            await bot.forward_messages(target_channel, event.message)
            await event.reply("✅ **Feedback sent successfully!** Thank you.")
        except:
            try:
                if event.photo: await bot.send_file(target_channel, event.photo, caption=event.raw_text or "Photo Feedback")
                else: await bot.send_message(target_channel, f"📩 **Feedback:**\n\n{event.raw_text}")
                await event.reply("✅ **Feedback sent successfully!** Thank you.")
            except: await event.reply("⚠️ Could not send feedback. Try again later.")
    except Exception as e: print(f"Feedback receive error: {e}")

# === FREE FILE (UPDATED NO FAKE LOADING) ===
@bot.on(events.NewMessage(incoming=True))
async def free_file_handler(event):
    try:
        if not event.is_private or not event.text: return
        if clean_btn_text(event.text) != "FREE FILE": return
            
        user_id = event.sender_id
        is_joined = False
        try:
            await userbot(GetParticipantRequest(channel=CHANNEL_USERNAME, participant=user_id))
            is_joined = True
        except UserNotParticipantError:
            is_joined = False
        except:
            is_joined = True 

        if not is_joined:
            join_msg = """⚠️ **YOU MUST JOIN OUR CHANNEL FIRST!**
━━━━━━━━━━━━━━━━━━━━━━

👇 **Join below to get the FREE FILE:**"""
            join_buttons = [
                [Button.url("📢 Join Channel", CHANNEL_LINK)],
                [Button.text("✅ I Joined")],
                [Button.text("⬅️ BACK")]
            ]
            await send_bilingual(event.chat_id, join_msg, join_buttons)
            return

        # Directly send the file link without fake loading
        file_msg = """✅ **CHANNEL JOINED!**
━━━━━━━━━━━━━━━━━━━━━━

👇 **Click below to get your FREE FILE:**"""
        
        file_buttons = [
            [Button.url("Click Here", FREE_FILE_LINK)],
            [Button.text("⬅️ BACK")]
        ]
        await send_bilingual(event.chat_id, file_msg, file_buttons)
    except Exception as e: print(f"FREE FILE Error: {e}")

# === VIP PURCHASE ===
@bot.on(events.NewMessage(incoming=True))
async def vip_purchase_handler(event):
    try:
        if not event.is_private or not event.text: return
        if clean_btn_text(event.text) != "VIP PURCHASE": return
        await send_bilingual(event.chat_id, PUBG_DURATION_MSG, pubg_purchase_keyboard())
    except Exception as e: print(f"VIP Purchase Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def full_season_handler(event):
    try:
        if not event.is_private or not event.text: return
        if clean_btn_text(event.text) != "FULL SEASON": return
        await send_bilingual(event.chat_id, PUBG_FULL_SEASON_MSG, screenshot_keyboard())
    except Exception as e: print(f"Full Season Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def one_month_handler(event):
    try:
        if not event.is_private or not event.text: return
        if clean_btn_text(event.text) != "ONE MONTH": return
        await send_bilingual(event.chat_id, PUBG_ONE_MONTH_MSG, screenshot_keyboard())
    except Exception as e: print(f"One Month Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def screenshot_prompt_handler(event):
    try:
        if not event.is_private or not event.text: return
        if clean_btn_text(event.text) != "SEND PAYMENT SCREENSHOT": return
        await send_bilingual(event.chat_id, SCREENSHOT_PROMPT_MSG, back_keyboard())
    except Exception as e: print(f"Screenshot Error: {e}")

# === BACK ===
@bot.on(events.NewMessage(incoming=True))
async def back_handler(event):
    try:
        if not event.is_private or not event.text: return
        if clean_btn_text(event.text) != "BACK": return
        user_id = event.sender_id
        user_states[user_id] = None 
        await send_bilingual(event.chat_id, MAIN_MENU_MSG, main_menu_keyboard())
    except Exception as e: print(f"Back Error: {e}")

# === IMAGE HANDLER ===
@bot.on(events.NewMessage(incoming=True))
async def image_handler(event):
    try:
        if not event.is_private or not event.photo: return
        user_id = event.sender_id
        if user_states.get(user_id) == "awaiting_feedback": return

        progress = await bot.send_message(event.chat_id, "🔍 **Analyzing Image...**")
        path = await event.download_media()
        payment_info = await extract_payment_info(path)
        
        if payment_info and payment_info.get("status") == "SUCCESS" and payment_info.get("amount") != "Not detected":
            await progress.edit("✅ **PAYMENT RECEIVED**\n\n📸 Sent to admin. Please wait.")
            sender = await event.get_sender()
            await notify_owner("💰 NEW PAYMENT", f"👤 {sender.first_name}\n🆔 `{user_id}`\n\n✅ SUCCESS\n💵 {payment_info.get('amount', 'N/A')}\n📅 {payment_info.get('date', 'N/A')}\n🔢 {payment_info.get('txn_id', 'N/A')}\n💳 {payment_info.get('method', 'N/A')}\n\n`/approve {user_id}`\n`/reject {user_id}`")
            try: await bot.send_file(OWNER_ID, event.photo, caption=f"📸 `{user_id}`")
            except: pass
        elif payment_info and payment_info.get("status") == "FAILED":
            await progress.edit("❌ **Payment Failed**\n\nSend a successful payment screenshot.")
        else:
            game_info = await extract_game_uid(path)
            if game_info and game_info.get("uid") != "Not detected":
                result_msg = f"""✅ **PLAYER DETECTED**
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
            if path and os.path.exists(path): os.remove(path)
        except: pass
    except Exception as e: print(f"Image Handler Error: {e}")

# === ADMIN REPLY ===
@bot.on(events.NewMessage(pattern=r'^/reply (\d+) (.+)$'))
async def admin_reply_handler(event):
    try:
        if event.sender_id != OWNER_ID: return
        user_id = int(event.pattern_match.group(1))
        message = event.pattern_match.group(2)
        translated = GoogleTranslator(source="en", target="my").translate(message)
        await bot.send_message(user_id, f"👤 **Admin:**\n\n{translated}")
        await event.respond(f"✅ Sent to `{user_id}`")
    except Exception as e: print(f"Admin Reply Error: {e}")

# === APPROVE ===
@bot.on(events.NewMessage(pattern=r'^/approve (\d+)$'))
async def approve_handler(event):
    try:
        if event.sender_id != OWNER_ID: return
        user_id = int(event.pattern_match.group(1))
        key = create_key()
        approve_msg = f"""✅ **PAYMENT VERIFIED**
━━━━━━━━━━━━━━━━━━━━━━
🔑 **YOUR LICENSE KEY:**
`{key}`
━━━━━━━━━━━━━━━━━━━━━━
📩 {DM_ADMIN_1}"""
        await send_bilingual(user_id, approve_msg, None, track=False)
        await event.respond(f"✅ Key sent to `{user_id}`\n🔑 `{key}`")
    except Exception as e: print(f"Approve Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/reject (\d+)$'))
async def reject_handler(event):
    try:
        if event.sender_id != OWNER_ID: return
        user_id = int(event.pattern_match.group(1))
        reject_msg = f"❌ **Payment Not Verified**\n\n📩 {DM_ADMIN_1}"
        await send_bilingual(user_id, reject_msg, None, track=False)
        await event.respond(f"❌ Sent to `{user_id}`")
    except Exception as e: print(f"Reject Error: {e}")

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
    await bot.start(bot_token=BOT_TOKEN)
    print("=" * 55)
    print("BOT & USERBOT RUNNING!")
    print("=" * 55)
    await asyncio.gather(userbot.run_until_disconnected(), bot.run_until_disconnected())

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
