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
DM_ADMIN_1 = "@ROVIXU1ti"
DM_ADMIN_2 = "@she_Shutara"
FILE_PASSWORD = "buyViP@79o"

ai_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY) if GROQ_API_KEY else None
ocr_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None
VISION_MODELS = ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.2-11b-vision-instruct:free"]
USERBOT_GIF = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"
LANG_CODES = {"en":"en","hi":"hi","mm":"my","ar":"ar","ur":"ur","th":"th","vi":"vi","eg":"ar","bn":"bn","id":"id","zh":"zh-CN","ja":"ja","ko":"ko","ru":"ru","es":"es","fr":"fr","pt":"pt","de":"de","tr":"tr","fa":"fa"}

user_langs = {}
ai_mode = {}
last_owner_activity = {}
user_auto_reply_count = {}
AWAY_TIMEOUT = 300
MAX_AUTO_REPLIES = 3
user_message_times = {}
SPAM_LIMIT_1 = 5
SPAM_LIMIT_2 = 10
SPAM_LIMIT_3 = 20
KEY_FILE = "license_keys.json"
SPAM_FILE = "spam_data.json"
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

def create_key():
    while True:
        key = f"ROVIX-{random.randint(10000, 99999)}"
        if key not in active_keys:
            break
    active_keys[key] = {"used": False, "user_id": None, "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "activated_at": None, "expires_at": None}
    save_keys()
    return key

def load_spam():
    try:
        if os.path.exists(SPAM_FILE):
            with open(SPAM_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Spam load error: {e}")
    return {"banned": [], "muted": {}, "warnings": {}}

def save_spam():
    try:
        with open(SPAM_FILE, "w") as f:
            json.dump({"banned": list(banned_users.keys()), "muted": {str(k): v for k, v in muted_users.items()}, "warnings": {str(k): v for k, v in spam_warnings.items()}}, f)
    except Exception as e:
        print(f"Spam save error: {e}")

_spam_data = load_spam()
banned_users = {int(k): True for k in _spam_data.get("banned", [])}
muted_users = {int(k): v for k, v in _spam_data.get("muted", {}).items()}
spam_warnings = {int(k): v for k, v in _spam_data.get("warnings", {}).items()}

BACKUP_FILE = "backup_data.json"

def create_backup():
    try:
        data = {"keys": active_keys, "backup_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "total_keys": len(active_keys)}
        with open(BACKUP_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return BACKUP_FILE
    except Exception as e:
        print(f"Backup error: {e}")
        return None

live_chat_mode = {}

WELCOME_MSG = """💎 **ROVIXBY**
Professional Gaming Service
━━━━━━━━━━━━━━━━━━━━━━
Select an option below.
🤖 @ROVIXU1ti
━━━━━━━━━━━━━━━━━━━━━━"""

PUBG_MENU_MSG = """🎮 **PUBG**
━━━━━━━━━━━━━━━━━━━━━━
Select an option:"""

PUBG_NOT_JOINED_MSG = f"""❌ **Join Required**
━━━━━━━━━━━━━━━━━━━━━━
Please join our channel first:
🔗 {CHANNEL_LINK}
━━━━━━━━━━━━━━━━━━━━━━
Then click **✅ I've Joined**"""

PUBG_ENTER_KEY_MSG = f"""🎁 **PUBG FREE FILE**
━━━━━━━━━━━━━━━━━━━━━━
🔐 **Enter License Code**
📩 Send: `ROVIX-XXXXX`
━━━━━━━━━━━━━━━━━━━━━━
⚠️ 1 code = 1 user (30 min)
📩 DM: {DM_ADMIN_1}"""

PUBG_DURATION_MSG = """🎯 **Select Duration**
━━━━━━━━━━━━━━━━━━━━━━"""

PUBG_FULL_SEASON_MSG = f"""🎯 **Full Season**
━━━━━━━━━━━━━━━━━━━━━━
💰 Price: **$15 / 25,000 KS**
💳 Payment:
📱 KBZ: `09897052554`
📱 Wave: {DM_ADMIN_1}
━━━━━━━━━━━━━━━━━━━━━━
📸 Send payment screenshot below."""

PUBG_ONE_MONTH_MSG = f"""📅 **One Month**
━━━━━━━━━━━━━━━━━━━━━━
💰 Price: **$7 / 15,000 KS**
💳 Payment:
📱 KBZ: `09897052554`
📱 Wave: {DM_ADMIN_1}
━━━━━━━━━━━━━━━━━━━━━━
📸 Send payment screenshot below."""

MLBB_MENU_MSG = """🎮 **Mobile Legends**
━━━━━━━━━━━━━━━━━━━━━━
Select an option:"""

MLBB_PURCHASE_MSG = f"""🎮 **MLBB Purchase**
━━━━━━━━━━━━━━━━━━━━━━
💰 Price: **5000 KS / $2**
💳 Payment:
📱 KBZ: `09897052554`
📱 Wave: {DM_ADMIN_1}
━━━━━━━━━━━━━━━━━━━━━━
📸 Send payment screenshot below."""

SCREENSHOT_PROMPT_MSG = """📸 **Send Payment Screenshot**
━━━━━━━━━━━━━━━━━━━━━━
Send a clear screenshot showing:
• Amount
• Date/Time
• Transaction ID
━━━━━━━━━━━━━━━━━━━━━━
Admin will verify shortly."""

CONTACT_MSG = f"""📞 **Contact Admin**
━━━━━━━━━━━━━━━━━━━━━━
👤 {DM_ADMIN_1}
👤 {DM_ADMIN_2}
━━━━━━━━━━━━━━━━━━━━━━
⏳ Reply within 24 hours."""

JOIN_CHANNEL_MSG = f"""📢 **Join Channel**
━━━━━━━━━━━━━━━━━━━━━━
🔗 {CHANNEL_LINK}
📂 Check pinned message after joining."""

LANGUAGE_MSG = """🌐 **Select Language**
━━━━━━━━━━━━━━━━━━━━━━"""

FEEDBACK_MSG = f"""💬 **Feedback**
━━━━━━━━━━━━━━━━━━━━━━
Send feedback to:
👤 {DM_ADMIN_1}
👤 {DM_ADMIN_2}
━━━━━━━━━━━━━━━━━━━━━━
Thank you! ❤️"""

AI_INTRO_MSG = """🤖 **Ask AI**
━━━━━━━━━━━━━━━━━━━━━━
Ask me anything.
👇 Type your question."""

LIVE_CHAT_MSG = """💬 **Live Chat**
━━━━━━━━━━━━━━━━━━━━━━
Type your message below.
Admin will reply personally.
━━━━━━━━━━━━━━━━━━━━━━
Type `/cancel` to exit."""

def main_menu_keyboard():
    return [
        [Button.text("🤖 ASK AI"), Button.text("🎮 PUBG")],
        [Button.text("🎮 MLBB"), Button.text("📞 CONTACT")],
        [Button.text("📢 JOIN CHANNEL"), Button.text("🌐 LANGUAGE")],
        [Button.text("💬 FEEDBACK"), Button.text("💬 LIVE CHAT")],
    ]

def pubg_menu_keyboard():
    return [
        [Button.text("🎁 FREE FILE")],
        [Button.text("💳 PUBG PURCHASE")],
        [Button.text("⬅️ BACK")],
    ]

def pubg_purchase_keyboard():
    return [
        [Button.text("🎯 FULL SEASON")],
        [Button.text("📅 ONE MONTH")],
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
        [Button.text("✅ I've Joined")],
        [Button.text("⬅️ BACK")],
    ]

def screenshot_keyboard():
    return [
        [Button.text("📸 Send Payment Screenshot")],
        [Button.text("⬅️ BACK")],
    ]

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
                    return ocr_client.chat.completions.create(model=model_name, messages=[{"role": "user", "content": [{"type": "text", "text": "Analyze payment screenshot.\nReply:\nSTATUS: SUCCESS or FAILED or UNKNOWN\nAMOUNT: xxx\nTXN: xxx\nDATE: xxx\nMETHOD: xxx\nBe strict."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}], max_tokens=100, temperature=0.0)
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, _ocr)
                text = response.choices[0].message.content.strip()
                info = {}
                for line in text.split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        info[k.strip().lower()] = v.strip()
                return {"status": info.get("status", "UNKNOWN"), "amount": info.get("amount", "Not detected"), "txn_id": info.get("txn", "Not detected"), "date": info.get("date", "Not detected"), "method": info.get("method", "Not detected")}
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

async def exa_search(query):
    if not EXA_API_KEY:
        return None
    try:
        def _search():
            return requests.post("https://api.exa.ai/search", headers={"x-api-key": EXA_API_KEY, "Content-Type": "application/json"}, json={"query": query, "numResults": 3, "type": "instant", "contents": {"text": {"maxCharacters": 500}}}, timeout=5)
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
        print(f"Exa error: {e}")
    return None

async def detect_language(text):
    if not ai_client:
        return "en"
    try:
        def _call():
            return ai_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": "Detect language. Reply ONLY 2-letter code."}, {"role": "user", "content": text}], max_tokens=5, temperature=0.1)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call)
        code = response.choices[0].message.content.strip().lower()
        return code if code in LANG_CODES else ("en" if len(code) != 2 else code)
    except Exception as e:
        print(f"Lang error: {e}")
        return "en"

async def voice_to_text(audio_path, language="en"):
    if not ai_client:
        return None
    try:
        def _transcribe():
            with open(audio_path, "rb") as f:
                return ai_client.audio.transcriptions.create(model="whisper-large-v3", file=f, language=language if language != "auto" else None)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _transcribe)
        return response.text
    except Exception as e:
        print(f"Voice error: {e}")
        return None

async def ask_ai(user_message, user_id=None):
    if not ai_client:
        return "AI not available."
    if user_id and user_id not in user_langs:
        user_langs[user_id] = await detect_language(user_message)
    lang = user_langs.get(user_id, "en") if user_id else "en"
    context = ""
    if EXA_API_KEY and len(user_message) > 5:
        try:
            exa_result = await asyncio.wait_for(exa_search(user_message), timeout=5.0)
            if exa_result:
                context = f"\n\nWeb search:\n{exa_result}"
        except:
            pass
    try:
        def _call():
            return ai_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": f"You are ROVIXBY Assistant. Reply in {LANG_CODES.get(lang, 'en')}. Short, helpful, 3-5 lines.{context}"}, {"role": "user", "content": user_message}], max_tokens=700, temperature=0.75)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call)
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return "AI error. Try again."

async def ask_ai_userbot(user_message):
    if not ai_client:
        return "I'll reply soon."
    try:
        detected_lang = await detect_language(user_message)
    except:
        detected_lang = "en"
    try:
        def _call():
            return ai_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": f"ROVIXBY auto-reply. Reply in {LANG_CODES.get(detected_lang, 'en')}. Short (2-3 lines). Owner is offline, will reply soon."}, {"role": "user", "content": user_message}], max_tokens=300, temperature=0.7)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Userbot AI Error: {e}")
        return "I'll reply soon."

async def translate_to_user_lang(text, user_id):
    if not ai_client:
        return text
    lang = user_langs.get(user_id, "en")
    if lang == "en":
        return text
    try:
        def _call():
            return ai_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": f"Translate to {LANG_CODES.get(lang, 'en')}. Reply ONLY translation."}, {"role": "user", "content": text}], max_tokens=500, temperature=0.3)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Translate error: {e}")
        return text

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
        if now - last_owner_activity.get(user_id, 0) < AWAY_TIMEOUT:
            return
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
                    english_text = await translate_to_user_lang(text_from_voice, OWNER_ID)
                    await notify_owner("🎤 Voice!", f"🆔 `{user_id}`\n📝 {text_from_voice}\n🇬🇧 {english_text}")
                    await event.reply("🎤 Got it! Owner will reply.")
            except Exception as e:
                print(f"Voice error: {e}")
            finally:
                try:
                    if voice_path and os.path.exists(voice_path):
                        os.remove(voice_path)
                except:
                    pass
            return
        count = user_auto_reply_count.get(user_id, 0)
        if count >= MAX_AUTO_REPLIES:
            return
        user_message = event.raw_text or ""
        ai_reply = await ask_ai_userbot(user_message)
        away_text = f"""💎 **ROVIXBY AUTO-REPLY**
━━━━━━━━━━━━━━━━━━━━━━━━━━

💠 **Owner is Busy**

📢 Contact the bot for instant help.

━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 {ai_reply}

━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 {BOT_LINK}
📢 {CHANNEL_LINK}

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ ROVIXBY ULTIMATE"""
        msg = await userbot.send_file(event.chat_id, USERBOT_GIF, caption=away_text)
        track_userbot(user_id, msg.id)
        user_auto_reply_count[user_id] = count + 1
        try:
            sender = await event.get_sender()
            username = f"@{sender.username}" if sender.username else "No username"
            await notify_owner("📩 New Message!", f"👤 {sender.first_name}\n🔗 {username}\n🆔 `{user_id}`\n💬 {user_message[:100]}\n🔢 {count + 1}/{MAX_AUTO_REPLIES}")
        except:
            pass
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
                    translated = await translate_to_user_lang(text_from_voice, user_id)
                    await userbot.send_message(user_id, f"🎤 Voice:\n\n{translated}")
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

bot = TelegramClient('bot_session', API_ID, API_HASH)

async def is_user_joined(user_id):
    try:
        await bot(GetParticipantRequest(channel=CHANNEL_USERNAME, participant=user_id))
        return True
    except (UserNotParticipantError, ChatAdminRequiredError):
        return False
    except:
        return False

def clean_btn_text(text):
    text = text.strip().upper()
    return re.sub(r'[^A-Z ]', '', text).strip()

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
        msg = await bot.send_message(event.chat_id, WELCOME_MSG, buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Start Error: {e}")

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
        lang_stats = {}
        for l in user_langs.values():
            lang_stats[l] = lang_stats.get(l, 0) + 1
        top_langs = sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        lang_str = "\n".join([f"  • {k}: {v}" for k, v in top_langs]) or "  • No data"
        await event.respond(f"📊 **Stats**\n\n🔑 Total: `{total_keys}`\n✅ Used: `{used_keys}`\n🆓 Unused: `{total_keys - used_keys}`\n👥 Active: `{len(last_owner_activity)}`\n🚫 Banned: `{len(banned_users)}`\n🌐 Langs:\n{lang_str}")
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

@bot.on(events.NewMessage(incoming=True))
async def ask_ai_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "ASK AI":
            return
        user_id = event.sender_id
        ai_mode[user_id] = True
        msg = await bot.send_message(event.chat_id, AI_INTRO_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Ask AI Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def pubg_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "PUBG":
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_MENU_MSG, buttons=pubg_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"PUBG Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def free_file_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "FREE FILE":
            return
        user_id = event.sender_id
        joined = await is_user_joined(user_id)
        if joined:
            verify_msg = await bot.send_message(event.chat_id, """🔍 **Verifying Your Access**
━━━━━━━━━━━━━━━━━━━━━━
`[░░░░░░░░░░] 0%`

⏳ Please wait...
━━━━━━━━━━━━━━━━━━━━━━""")
            await asyncio.sleep(0.7)
            await verify_msg.edit("""🔍 **Verifying Your Access**
━━━━━━━━━━━━━━━━━━━━━━
`[████░░░░░░] 40%`

🔒 Checking credentials...
━━━━━━━━━━━━━━━━━━━━━━""")
            await asyncio.sleep(0.7)
            await verify_msg.edit("""🔍 **Verifying Your Access**
━━━━━━━━━━━━━━━━━━━━━━
`[████████░░] 80%`

🔐 Validating access...
━━━━━━━━━━━━━━━━━━━━━━""")
            await asyncio.sleep(0.7)
            await verify_msg.edit("""🔍 **Verifying Your Access**
━━━━━━━━━━━━━━━━━━━━━━
`[██████████] 100%`

🎉 Almost done...
━━━━━━━━━━━━━━━━━━━━━━""")
            await asyncio.sleep(0.5)
            if random.random() < 0.30:
                await verify_msg.edit("""❌ **Verification Failed**
━━━━━━━━━━━━━━━━━━━━━━
😔 Access could not be verified.

🔄 Please try again.
━━━━━━━━━━━━━━━━━━━━━━""",
                    buttons=[[Button.text("🔄 Try Again")], [Button.text("⬅️ BACK")]]
                )
                return
            else:
                try:
                    await verify_msg.delete()
                except:
                    pass
                msg = await bot.send_message(event.chat_id, PUBG_ENTER_KEY_MSG, buttons=back_keyboard())
                track_bot(user_id, msg.id)
        else:
            msg = await bot.send_message(event.chat_id, PUBG_NOT_JOINED_MSG, buttons=join_keyboard())
            track_bot(user_id, msg.id)
    except Exception as e:
        print(f"FREE FILE Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def try_again_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "TRY AGAIN":
            return
        user_id = event.sender_id
        verify_msg = await bot.send_message(event.chat_id, """🔍 **Verifying Your Access**
━━━━━━━━━━━━━━━━━━━━━━
`[░░░░░░░░░░] 0%`

⏳ Please wait...
━━━━━━━━━━━━━━━━━━━━━━""")
        await asyncio.sleep(0.7)
        await verify_msg.edit("""🔍 **Verifying Your Access**
━━━━━━━━━━━━━━━━━━━━━━
`[████░░░░░░] 40%`
━━━━━━━━━━━━━━━━━━━━━━""")
        await asyncio.sleep(0.7)
        await verify_msg.edit("""🔍 **Verifying Your Access**
━━━━━━━━━━━━━━━━━━━━━━
`[████████░░] 80%`
━━━━━━━━━━━━━━━━━━━━━━""")
        await asyncio.sleep(0.7)
        await verify_msg.edit("""🔍 **Verifying Your Access**
━━━━━━━━━━━━━━━━━━━━━━
`[██████████] 100%`
━━━━━━━━━━━━━━━━━━━━━━""")
        await asyncio.sleep(0.5)
        if random.random() < 0.30:
            await verify_msg.edit("""❌ **Verification Failed Again**
━━━━━━━━━━━━━━━━━━━━━━
😔 Still could not verify.

🔄 Try one more time.
━━━━━━━━━━━━━━━━━━━━━━""",
                buttons=[[Button.text("🔄 Try Again")], [Button.text("⬅️ BACK")]]
            )
            return
        else:
            try:
                await verify_msg.delete()
            except:
                pass
            msg = await bot.send_message(event.chat_id, PUBG_ENTER_KEY_MSG, buttons=back_keyboard())
            track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Try Again Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def joined_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        clean = clean_btn_text(event.text)
        if clean not in ["I VE JOINED", "I JOINED"]:
            return
        user_id = event.sender_id
        joined = await is_user_joined(user_id)
        if joined:
            verify_msg = await bot.send_message(event.chat_id, "🔍 **Verifying**\n\n`[░░░░░░░░░░] 0%`\n\n⏳ Please wait...")
            await asyncio.sleep(0.7)
            await verify_msg.edit("🔍 **Verifying**\n\n`[████░░░░░░] 40%`")
            await asyncio.sleep(0.7)
            await verify_msg.edit("🔍 **Verifying**\n\n`[████████░░] 80%`")
            await asyncio.sleep(0.7)
            await verify_msg.edit("🔍 **Verifying**\n\n`[██████████] 100%`")
            await asyncio.sleep(0.5)
            try:
                await verify_msg.delete()
            except:
                pass
            msg = await bot.send_message(event.chat_id, PUBG_ENTER_KEY_MSG, buttons=back_keyboard())
            track_bot(user_id, msg.id)
        else:
            msg = await bot.send_message(event.chat_id, "❌ **Not Joined**\n\nPlease join first.", buttons=join_keyboard())
            track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Joined Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def pubg_purchase_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "PUBG PURCHASE":
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_DURATION_MSG, buttons=pubg_purchase_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"PUBG Purchase Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def full_season_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "FULL SEASON":
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, PUBG_FULL_SEASON_MSG, buttons=screenshot_keyboard())
        track_bot(user_id, msg.id)
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
        msg = await bot.send_message(event.chat_id, PUBG_ONE_MONTH_MSG, buttons=screenshot_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"One Month Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def mlbb_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "MLBB":
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, MLBB_MENU_MSG, buttons=mlbb_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"MLBB Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def mlbb_purchase_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "MLBB PURCHASE":
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, MLBB_PURCHASE_MSG, buttons=screenshot_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"MLBB Purchase Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def screenshot_prompt_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "SEND PAYMENT SCREENSHOT":
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, SCREENSHOT_PROMPT_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Screenshot Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def contact_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "CONTACT":
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, CONTACT_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Contact Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def join_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "JOIN CHANNEL":
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, JOIN_CHANNEL_MSG, buttons=join_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Join Error: {e}")

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
        msg = await bot.send_message(event.chat_id, f"✅ **Language:** {clean}", buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Lang Select Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def feedback_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "FEEDBACK":
            return
        user_id = event.sender_id
        msg = await bot.send_message(event.chat_id, FEEDBACK_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Feedback Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def live_chat_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "LIVE CHAT":
            return
        user_id = event.sender_id
        live_chat_mode[user_id] = True
        msg = await bot.send_message(event.chat_id, LIVE_CHAT_MSG, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Live Chat Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def back_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        if clean_btn_text(event.text) != "BACK":
            return
        user_id = event.sender_id
        ai_mode[user_id] = False
        live_chat_mode[user_id] = False
        msg = await bot.send_message(event.chat_id, WELCOME_MSG, buttons=main_menu_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"Back Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def key_verify_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        text = event.text.strip().upper()
        if not re.match(r'^ROVIX-\d{5}$', text):
            return
        user_id = event.sender_id
        key = text
        if key not in active_keys:
            msg = await bot.send_message(event.chat_id, "❌ **Invalid Code**", buttons=back_keyboard())
            track_bot(user_id, msg.id)
            return
        key_data = active_keys[key]
        if key_data.get("used"):
            if key_data.get("user_id") != user_id:
                msg = await bot.send_message(event.chat_id, "❌ **Already Used**", buttons=back_keyboard())
                track_bot(user_id, msg.id)
                return
            expires_at = key_data.get("expires_at")
            if expires_at:
                try:
                    expiry = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                    if datetime.now() > expiry:
                        msg = await bot.send_message(event.chat_id, f"❌ **Key Expired**\n\n📩 {DM_ADMIN_1}", buttons=back_keyboard())
                        track_bot(user_id, msg.id)
                        return
                except:
                    pass
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expires_str = (datetime.now() + timedelta(minutes=KEY_EXPIRY_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")
        active_keys[key]["used"] = True
        active_keys[key]["user_id"] = user_id
        active_keys[key]["activated_at"] = now_str
        active_keys[key]["expires_at"] = expires_str
        save_keys()
        success_msg = f"""🎉 **Access Granted**
━━━━━━━━━━━━━━━━━━━━━━
✅ Code: `{key}`
⏱️ Valid until: `{expires_str}`
━━━━━━━━━━━━━━━━━━━━━━

🔐 **File Password:**
`{FILE_PASSWORD}`

━━━━━━━━━━━━━━━━━━━━━━
⚠️ Do not share password."""
        msg = await bot.send_message(event.chat_id, success_msg, buttons=back_keyboard())
        track_bot(user_id, msg.id)
        try:
            sender = await event.get_sender()
            await notify_owner("🔑 CODE ACTIVATED", f"👤 {sender.first_name}\n🆔 `{user_id}`\n🔑 `{key}`\n⏱️ {expires_str}")
        except:
            pass
    except Exception as e:
        print(f"Key Verify Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def image_handler(event):
    try:
        if not event.is_private or not event.photo:
            return
        user_id = event.sender_id
        progress = await bot.send_message(event.chat_id, "🔍 **Analyzing...**")
        path = await event.download_media()
        payment_info = await extract_payment_info(path)
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except:
            pass
        if payment_info and payment_info.get("status") == "SUCCESS" and payment_info.get("amount") != "Not detected":
            await progress.edit("✅ **Payment Received**\n\n📸 Sent to admin. Please wait.")
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
            await progress.edit("⚠️ **Cannot Verify**\n\nSend a clear successful payment screenshot.")
    except Exception as e:
        print(f"Image Handler Error: {e}")

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
        btn_texts = ["ASK AI", "PUBG", "MLBB", "CONTACT", "JOIN CHANNEL", "LANGUAGE", "FEEDBACK", "LIVE CHAT", "FREE FILE", "PUBG PURCHASE", "FULL SEASON", "ONE MONTH", "BACK", "I VE JOINED", "I JOINED", "TRY AGAIN", "MLBB PURCHASE", "SEND PAYMENT SCREENSHOT"]
        if clean_btn_text(event.text) in btn_texts:
            return
        try:
            sender = await event.get_sender()
            username = f"@{sender.username}" if sender.username else "No username"
            await notify_owner("💬 LIVE CHAT", f"👤 {sender.first_name}\n🔗 {username}\n🆔 `{user_id}`\n💬 {event.text}\n\n👉 `/reply {user_id} msg`")
        except:
            pass
        await event.reply("✅ Sent to admin.")
    except Exception as e:
        print(f"Live Chat Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/reply (\d+) (.+)$'))
async def admin_reply_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        user_id = int(event.pattern_match.group(1))
        message = event.pattern_match.group(2)
        await bot.send_message(user_id, f"👤 **Admin:**\n\n{message}")
        await event.respond(f"✅ Sent to `{user_id}`")
    except Exception as e:
        print(f"Admin Reply Error: {e}")

@bot.on(events.NewMessage(incoming=True))
async def ai_reply_handler(event):
    try:
        if not event.is_private or not event.text:
            return
        try:
            sender = await event.get_sender()
            if getattr(sender, 'bot', False):
                return
        except:
            pass
        text = event.text
        if text.startswith("/"):
            return
        if text.upper().startswith("ROVIX-"):
            return
        user_id = event.sender_id
        if live_chat_mode.get(user_id):
            return
        if not ai_mode.get(user_id, False):
            return
        clean = clean_btn_text(text)
        blocked = ["ASK AI", "PUBG", "MLBB", "CONTACT", "JOIN CHANNEL", "LANGUAGE", "FEEDBACK", "LIVE CHAT", "FREE FILE", "PUBG PURCHASE", "FULL SEASON", "ONE MONTH", "MLBB PURCHASE", "BACK", "SEND PAYMENT SCREENSHOT", "I VE JOINED", "I JOINED", "TRY AGAIN"]
        if clean in blocked:
            return
        langs = ["EN", "MM", "HI", "AR", "UR", "BN", "ID", "TH", "ZH", "JA", "KO", "RU", "ES", "FR", "PT", "DE", "TR", "FA"]
        if clean in langs:
            return
        reply = await ask_ai(text, user_id)
        msg = await bot.send_message(event.chat_id, reply, buttons=back_keyboard())
        track_bot(user_id, msg.id)
    except Exception as e:
        print(f"AI Reply Error: {e}")

@bot.on(events.NewMessage(pattern=r'^/approve (\d+)$'))
async def approve_handler(event):
    try:
        if event.sender_id != OWNER_ID:
            return
        user_id = int(event.pattern_match.group(1))
        key = create_key()
        expires_str = (datetime.now() + timedelta(minutes=KEY_EXPIRY_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")
        approve_msg = f"""✅ **Payment Verified**
━━━━━━━━━━━━━━━━━━━━━━

🔑 **Your License Key:**
`{key}`

⏱️ Valid {KEY_EXPIRY_MINUTES} min after activation

━━━━━━━━━━━━━━━━━━━━━━

**How to use:**
1. Click 🎁 FREE FILE
2. Send key: `{key}`
3. Get file password

━━━━━━━━━━━━━━━━━━━━━━
📩 {DM_ADMIN_1}"""
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
        await bot.send_message(user_id, f"❌ **Payment Not Verified**\n\n📩 {DM_ADMIN_1}")
        await event.respond(f"❌ Sent to `{user_id}`")
    except Exception as e:
        print(f"Reject Error: {e}")

async def auto_backup_loop():
    while True:
        try:
            await asyncio.sleep(12 * 60 * 60)
            file = create_backup()
            if file and os.path.exists(file):
                await bot.send_file(OWNER_ID, file, caption=f"💾 **Auto Backup**\n\n🔑 {len(active_keys)} keys")
        except Exception as e:
            print(f"Auto-backup error: {e}")

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

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

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
