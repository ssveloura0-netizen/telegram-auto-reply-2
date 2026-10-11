from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
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
# ⚙️ APNI DETAILS YAHAN SET KARO
# ==========================================
BOT_LINK = "https://t.me/Vixby_bot"
CHANNEL_USERNAME = "rovixbyultimate"
CHANNEL_LINK = "https://t.me/rovixbyultimate"
ADMIN_1 = "@ROVIXU1ti"
ADMIN_2 = "@she_Shutara"

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
        "not_joined": f"""❌ **You haven't joined our channel yet!**

To get the PUBG File Password, please join our official channel first.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {CHANNEL_LINK}

📂 **The PUBG File is PINNED in the channel!**
After joining, check the pinned message.
━━━━━━━━━━━━━━━━━━━━━━

After joining, click **"✅ I've Joined"** button.""",
        "submit": f"""🎉 **ACCESS GRANTED!**

✅ You are now verified!

━━━━━━━━━━━━━━━━━━━━━━
📸 **SUBMIT YOUR SCREENSHOT TO OUR ADMINS**
━━━━━━━━━━━━━━━━━━━━━━

To get the PUBG File Password, please send your **screenshot** to our admins:

👤 {ADMIN_1}
👤 {ADMIN_2}

📌 **Instructions:**
1️⃣ Send a screenshot of this verification message to admins.
2️⃣ Wait for their response.
3️⃣ They will provide you the PUBG File Password.

━━━━━━━━━━━━━━━━━━━━━━
📂 **Don't forget to check the PINNED file in our channel:**
🔗 {CHANNEL_LINK}
━━━━━━━━━━━━━━━━━━━━━━

⚠️ Only verified users will get the password."""
    },
    "hi": {
        "prompt": "👋 **नमस्ते!**\n\nकृपया नीचे एक विकल्प चुनें:",
        "not_joined": f"""❌ **आपने अभी तक चैनल जॉइन नहीं किया!**

PUBG File Password पाने के लिए पहले हमारा चैनल जॉइन करें।

━━━━━━━━━━━━━━━━━━━━━━
🔗 {CHANNEL_LINK}

📂 **PUBG फाइल चैनल में PINNED है!**
जॉइन करने के बाद pinned message देखें।
━━━━━━━━━━━━━━━━━━━━━━

जॉइन करने के बाद **"✅ I've Joined"** दबाएं।""",
        "submit": f"""🎉 **एक्सेस मिल गया!**

✅ आप वेरिफाइड हो गए!

━━━━━━━━━━━━━━━━━━━━━━
📸 **अपना स्क्रीनशॉट एडमिन को भेजें**
━━━━━━━━━━━━━━━━━━━━━━

PUBG File Password पाने के लिए अपना **स्क्रीनशॉट** इन एडमिन को भेजें:

👤 {ADMIN_1}
👤 {ADMIN_2}

📌 **निर्देश:**
1️⃣ इस वेरिफिकेशन मैसेज का स्क्रीनशॉट एडमिन को भेजें।
2️⃣ उनके जवाब का इंतज़ार करें।
3️⃣ वो आपको PUBG File Password देंगे।

━━━━━━━━━━━━━━━━━━━━━━
📂 **चैनल में PINNED फाइल देखना न भूलें:**
🔗 {CHANNEL_LINK}
━━━━━━━━━━━━━━━━━━━━━━

⚠️ सिर्फ वेरिफाइड यूज़र्स को पासवर्ड मिलेगा।"""
    },
    "my": {
        "prompt": "👋 **မင်္ဂလာပါ!**\n\nအောက်တွင် ရွေးချယ်ပါ:",
        "not_joined": f"""❌ **သင်သည် ချန်နယ်သို့ မဝင်ရောက်ရသေးပါ!**

PUBG File Password ရရှိရန် ကျွန်ုပ်တို့၏ ချန်နယ်သို့ ဦးစွာဝင်ပါ။

━━━━━━━━━━━━━━━━━━━━━━
🔗 {CHANNEL_LINK}

📂 **PUBG ဖိုင် ချန်နယ်တွင် PINNED ဖြစ်သည်!**
ဝင်ပြီးပါက pinned message ကို ကြည့်ပါ။
━━━━━━━━━━━━━━━━━━━━━━

ဝင်ပြီးပါက **"✅ I've Joined"** ကို နှိပ်ပါ။""",
        "submit": f"""🎉 **ဝင်ရောက်ခွင့် ရပါပြီ!**

✅ အတည်ပြုပြီးပါပြီ!

━━━━━━━━━━━━━━━━━━━━━━
📸 **သင့် screenshot ကို admin များထံ ပေးပို့ပါ**
━━━━━━━━━━━━━━━━━━━━━━

PUBG File Password ရရှိရန် သင့် **screenshot** ကို admin များထံ ပေးပို့ပါ:

👤 {ADMIN_1}
👤 {ADMIN_2}

📌 **ညွှန်ကြားချက်များ:**
1️⃣ ဤ verification message ၏ screenshot ကို admin များထံ ပေးပို့ပါ။
2️⃣ သူတို့၏ အဖြေကို စောင့်ပါ။
3️⃣ သူတို့ သင့်အား PUBG File Password ပေးပါမည်။

━━━━━━━━━━━━━━━━━━━━━━
📂 **ချန်နယ်ရှိ PINNED ဖိုင်ကို ကြည့်ရန် မမေ့ပါနှင့်:**
🔗 {CHANNEL_LINK}
━━━━━━━━━━━━━━━━━━━━━━

⚠️ အတည်ပြုပြီးသော user များသာ password ရရှိမည်။"""
    },
    "ar": {
        "prompt": "👋 **مرحباً!**\n\nاختر خياراً أدناه:",
        "not_joined": f"""❌ **لم تنضم إلى قناتنا بعد!**

للحصول على PUBG File Password، انضم إلى قناتنا الرسمية أولاً.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {CHANNEL_LINK}

📂 **ملف PUBG مثبت في القناة!**
بعد الانضمام، تحقق من الرسالة المثبتة.
━━━━━━━━━━━━━━━━━━━━━━

بعد الانضمام، اضغط على **"✅ I've Joined"**.""",
        "submit": f"""🎉 **تم منح الوصول!**

✅ تم التحقق منك!

━━━━━━━━━━━━━━━━━━━━━━
📸 **أرسل لقطة الشاشة إلى المشرفين**
━━━━━━━━━━━━━━━━━━━━━━

للحصول على PUBG File Password، أرسل **لقطة الشاشة** إلى المشرفين:

👤 {ADMIN_1}
👤 {ADMIN_2}

📌 **التعليمات:**
1️⃣ أرسل لقطة شاشة لرسالة التحقق هذه إلى المشرفين.
2️⃣ انتظر ردهم.
3️⃣ سيوفرون لك PUBG File Password.

━━━━━━━━━━━━━━━━━━━━━━
📂 **لا تنسَ التحقق من الملف المثبت في القناة:**
🔗 {CHANNEL_LINK}
━━━━━━━━━━━━━━━━━━━━━━

⚠️ فقط المستخدمون الموثقون سيحصلون على كلمة المرور."""
    },
    "ur": {
        "prompt": "👋 **السلام علیکم!**\n\nنیچے ایک آپشن منتخب کریں:",
        "not_joined": f"""❌ **آپ نے ابھی تک چینل جوائن نہیں کیا!**

PUBG File Password حاصل کرنے کے لیے پہلے ہمارا چینل جوائن کریں۔

━━━━━━━━━━━━━━━━━━━━━━
🔗 {CHANNEL_LINK}

📂 **PUBG فائل چینل میں PINNED ہے!**
جوائن کرنے کے بعد pinned message دیکھیں۔
━━━━━━━━━━━━━━━━━━━━━━

جوائن کرنے کے بعد **"✅ I've Joined"** دبائیں۔""",
        "submit": f"""🎉 **رسائی مل گئی!**

✅ آپ کی تصدیق ہو گئی!

━━━━━━━━━━━━━━━━━━━━━━
📸 **اپنا اسکرین شاٹ ایڈمنز کو بھیجیں**
━━━━━━━━━━━━━━━━━━━━━━

PUBG File Password حاصل کرنے کے لیے اپنا **اسکرین شاٹ** ان ایڈمنز کو بھیجیں:

👤 {ADMIN_1}
👤 {ADMIN_2}

📌 **ہدایات:**
1️⃣ اس تصدیقی پیغام کا اسکرین شاٹ ایڈمنز کو بھیجیں۔
2️⃣ ان کے جواب کا انتظار کریں۔
3️⃣ وہ آپ کو PUBG File Password دیں گے۔

━━━━━━━━━━━━━━━━━━━━━━
📂 **چینل میں PINNED فائل دیکھنا نہ بھولیں:**
🔗 {CHANNEL_LINK}
━━━━━━━━━━━━━━━━━━━━━━

⚠️ صرف تصدیق شدہ صارفین کو پاس ورڈ ملے گا۔"""
    },
    "th": {
        "prompt": "👋 **สวัสดี!**\n\nกรุณาเลือกตัวเลือกด้านล่าง:",
        "not_joined": f"""❌ **คุณยังไม่ได้เข้าร่วมช่องของเรา!**

เพื่อรับ PUBG File Password กรุณาเข้าร่วมช่องอย่างเป็นทางการของเราก่อน

━━━━━━━━━━━━━━━━━━━━━━
🔗 {CHANNEL_LINK}

📂 **ไฟล์ PUBG ถูก PINNED ในช่อง!**
หลังจากเข้าร่วมแล้ว ตรวจสอบข้อความที่ pinned
━━━━━━━━━━━━━━━━━━━━━━

หลังจากเข้าร่วมแล้ว กด **"✅ I've Joined"**""",
        "submit": f"""🎉 **ได้รับอนุญาตแล้ว!**

✅ คุณได้รับการยืนยันแล้ว!

━━━━━━━━━━━━━━━━━━━━━━
📸 **ส่งภาพหน้าจอของคุณให้ผู้ดูแลของเรา**
━━━━━━━━━━━━━━━━━━━━━━

เพื่อรับ PUBG File Password กรุณาส่ง **ภาพหน้าจอ** ให้ผู้ดูแลของเรา:

👤 {ADMIN_1}
👤 {ADMIN_2}

📌 **คำแนะนำ:**
1️⃣ ส่งภาพหน้าจอของข้อความยืนยันนี้ให้ผู้ดูแล
2️⃣ รอการตอบกลับของพวกเขา
3️⃣ พวกเขาจะให้ PUBG File Password แก่คุณ

━━━━━━━━━━━━━━━━━━━━━━
📂 **อย่าลืมตรวจสอบไฟล์ PINNED ในช่อง:**
🔗 {CHANNEL_LINK}
━━━━━━━━━━━━━━━━━━━━━━

⚠️ เฉพาะผู้ใช้ที่ยืนยันแล้วเท่านั้นที่จะได้รับรหัสผ่าน"""
    },
    "vi": {
        "prompt": "👋 **Xin chào!**\n\nVui lòng chọn một tùy chọn bên dưới:",
        "not_joined": f"""❌ **Bạn chưa tham gia kênh của chúng tôi!**

Để nhận PUBG File Password, vui lòng tham gia kênh chính thức của chúng tôi trước.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {CHANNEL_LINK}

📂 **Tệp PUBG được PINNED trong kênh!**
Sau khi tham gia, hãy kiểm tra tin nhắn được ghim.
━━━━━━━━━━━━━━━━━━━━━━

Sau khi tham gia, nhấn **"✅ I've Joined"**.""",
        "submit": f"""🎉 **ĐÃ ĐƯỢC CẤP QUYỀN!**

✅ Bạn đã được xác minh!

━━━━━━━━━━━━━━━━━━━━━━
📸 **GỬI ẢNH CHỤP MÀN HÌNH CHO QUẢN TRỊ VIÊN**
━━━━━━━━━━━━━━━━━━━━━━

Để nhận PUBG File Password, vui lòng gửi **ảnh chụp màn hình** cho quản trị viên của chúng tôi:

👤 {ADMIN_1}
👤 {ADMIN_2}

📌 **Hướng dẫn:**
1️⃣ Gửi ảnh chụp màn hình của tin nhắn xác minh này cho quản trị viên.
2️⃣ Chờ phản hồi của họ.
3️⃣ Họ sẽ cung cấp cho bạn PUBG File Password.

━━━━━━━━━━━━━━━━━━━━━━
📂 **Đừng quên kiểm tra tệp PINNED trong kênh:**
🔗 {CHANNEL_LINK}
━━━━━━━━━━━━━━━━━━━━━━

⚠️ Chỉ người dùng đã xác minh mới nhận được mật khẩu."""
    },
    "eg": {
        "prompt": "👋 **أهلاً!**\n\nاختار من الخيارات اللي تحت:",
        "not_joined": f"""❌ **لسه ما انضميتش لقناتنا!**

عشان تجيب PUBG File Password، لازم تنضم لقناتنا الرسمية الأول.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {CHANNEL_LINK}

📂 **ملف PUBG متثبت في القناة!**
بعد ما تنضم، بص على الرسالة المثبتة.
━━━━━━━━━━━━━━━━━━━━━━

بعد ما تنضم، اضغط على **"✅ I've Joined"**.""",
        "submit": f"""🎉 **تم منح الوصول!**

✅ تم التحقق منك!

━━━━━━━━━━━━━━━━━━━━━━
📸 **ابعت لقطة الشاشة للمشرفين**
━━━━━━━━━━━━━━━━━━━━━━

عشان تجيب PUBG File Password، ابعت **لقطة الشاشة** للمشرفين:

👤 {ADMIN_1}
👤 {ADMIN_2}

📌 **التعليمات:**
1️⃣ ابعت لقطة شاشة لرسالة التحقق دي للمشرفين.
2️⃣ استنى ردهم.
3️⃣ هما هيدوك PUBG File Password.

━━━━━━━━━━━━━━━━━━━━━━
📂 **ما تنساش تبص على الملف المثبت في القناة:**
🔗 {CHANNEL_LINK}
━━━━━━━━━━━━━━━━━━━━━━

⚠️ بس المستخدمين اللي اتأكدوا هما اللي هياخدوا الباسورد."""
    }
}

user_langs = {}

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
# 🔔 OWNER NOTIFICATION FUNCTION
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

        # 🔔 Owner ko notification
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

        if user_id in tracked_msgs["bot"]:
            for msg_id in list(tracked_msgs["bot"][user_id]):
                try:
                    await bot.delete_messages(int(user_id), msg_id)
                    deleted += 1
                except Exception:
                    pass
            tracked_msgs["bot"][user_id] = []

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

        # 🔔 Owner ko notification
        try:
            sender = await event.get_sender()
            username = f"@{sender.username}" if sender.username else "No username"
            await notify_owner(
                "🔔 **New User Started Bot!**",
                f"👤 Name: {sender.first_name}\n"
                f"🔗 Username: {username}\n"
                f"🆔 ID: `{user_id}`"
            )
        except Exception:
            pass

        if user_id not in user_langs:
            buttons = [
                [Button.inline("🇬🇧 English", b"lang_en")],
                [Button.inline("🇮🇳 हिन्दी (Hindi)", b"lang_hi")],
                [Button.inline("🇲🇲 မြန်မာ (Burmese)", b"lang_my")],
                [Button.inline("🇸🇦 العربية (Arabic)", b"lang_ar")],
                [Button.inline("🇵🇰 اردو (Urdu)", b"lang_ur")],
                [Button.inline("🇹🇭 ไทย (Thai)", b"lang_th")],
                [Button.inline("🇻🇳 Tiếng Việt (Vietnamese)", b"lang_vi")],
                [Button.inline("🇪🇬 مصري (Egyptian)", b"lang_eg")],
            ]
            msg = await bot.send_file(event.chat_id, GIF_URL, caption=LANG_MENU, buttons=buttons)
            track_bot(user_id, msg.id)
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

        # 🔔 Owner ko notification
        try:
            sender = await event.get_sender()
            await notify_owner(
                "🌐 **Language Selected!**",
                f"👤 Name: {sender.first_name}\n"
                f"🆔 ID: `{user_id}`\n"
                f"🗣️ Language: `{lang.upper()}`"
            )
        except Exception:
            pass

        buttons = [
            [Button.inline("🔐 PUBG FILE PASSWORD", b"opt_pubg")],
            [Button.url("📢 Join Our Channel", CHANNEL_LINK)],
        ]
        msg = await bot.send_message(event.chat_id, MESSAGES[lang]["prompt"], buttons=buttons)
        track_bot(user_id, msg.id)
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
            msg = await bot.send_message(event.chat_id, MESSAGES[lang]["submit"])
            track_bot(user_id, msg.id)
        else:
            verify_buttons = [
                [Button.url("📢 Join Channel", CHANNEL_LINK)],
                [Button.inline("✅ I've Joined", b"verify_join")],
            ]
            msg = await bot.send_file(event.chat_id, MR_BEAN_GIF, caption=MESSAGES[lang]["not_joined"], buttons=verify_buttons)
            track_bot(user_id, msg.id)
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
            msg = await bot.send_message(event.chat_id, MESSAGES[lang]["submit"])
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
    print(f"👤 Owner ID: {OWNER_ID}")
    print("=" * 55)

    await asyncio.gather(
        userbot.run_until_disconnected(),
        bot.run_until_disconnected()
    )

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
