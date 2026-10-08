from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from deep_translator import GoogleTranslator
import asyncio
import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

is_away = True
last_activity = time.time()

GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"
CONTACT_GIF_URL = "https://media.giphy.com/media/z4lwT4QTkK3sYITR7Z/giphy.gif"

GROUP_LINK = "https://t.me/rovixbyultimate"
GROUP_USERNAME = "rovixbyultimate"
OWNER_CONTACT = "@MG1SHWE"

# ==========================================
# 🌍 OFFLINE MESSAGES — Professional
# ==========================================
OFFLINE_MESSAGES = {
    "en": """╔══════════════════════╗
   💼  AWAY MESSAGE
╚══════════════════════╝

Dear Sender,

Thank you for reaching out. I am currently **away from my desk** and unable to respond right away.

Your message has been received and will be reviewed as soon as I return.

━━━━━━━━━━━━━━━━━━━━━━
📌 Response will be provided at the earliest opportunity.
━━━━━━━━━━━━━━━━━━━━━━

Best regards,
[Your Name]""",

    "hi": """╔══════════════════════╗
   💼  अनुपस्थित संदेश
╚══════════════════════╝

प्रिय भेजने वाले,

संपर्क करने के लिए धन्यवाद। मैं वर्तमान में **अपने डेस्क से दूर** हूँ और तुरंत उत्तर देने में असमर्थ हूँ।

आपका संदेश प्राप्त हो गया है और मेरे लौटते ही इसकी समीक्षा की जाएगी।

━━━━━━━━━━━━━━━━━━━━━━
📌 जल्द से जल्द उत्तर दिया जाएगा।
━━━━━━━━━━━━━━━━━━━━━━

सादर,
[आपका नाम]""",

    "my": """╔══════════════════════╗
   💼  မရှိချိန် အသိပေးစာ
╚══════════════════════╝

ချစ်ခင်ရပါသော ပေးပို့သူ၊

ဆက်သွယ်ပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။ ကျွန်တော်သည် **စားပွဲမှ ဝေးနေပါသည်**၊ ချက်ချင်းပြန်လည်ဖြေကြားနိုင်မည် မဟုတ်ပါ။

သင့်စာ လက်ခံရရှိပါပြီ၊ ပြန်ရောက်သည်နှင့် စစ်ဆေးပါမည်။

━━━━━━━━━━━━━━━━━━━━━━
📌 အမြန်ဆုံး ပြန်လည်ဖြေကြားပါမည်။
━━━━━━━━━━━━━━━━━━━━━━

လေးစားစွာဖြင့်၊
[သင့်နာမည်]""",

    "ar": """╔══════════════════════╗
   💼  رسالة الغياب
╚══════════════════════╝

عزيزي المرسل،

شكراً لتواصلك معي. أنا حالياً **بعيد عن مكتبي** ولا أستطيع الرد فوراً.

لقد تم استلام رسالتك وسيتم مراجعتها فور عودتي.

━━━━━━━━━━━━━━━━━━━━━━
📌 سيتم الرد في أقرب فرصة ممكنة.
━━━━━━━━━━━━━━━━━━━━━━

مع خالص التحية،
[اسمك]""",

    "ur": """╔══════════════════════╗
   💼  غیر حاضری کا پیغام
╚══════════════════════╝

محترم بھیجنے والے،

رابطہ کرنے کا شکریہ۔ میں اس وقت **اپنے ڈیسک سے دور** ہوں اور فوری جواب دینے سے قاصر ہوں۔

آپ کا پیغام موصول ہو گیا ہے اور واپسی پر اس کا جائزہ لیا جائے گا۔

━━━━━━━━━━━━━━━━━━━━━━
📌 جلد از جلد جواب دیا جائے گا۔
━━━━━━━━━━━━━━━━━━━━━━

بہترین احترام کے ساتھ،
[آپ کا نام]"""
}

# ==========================================
# 🌐 LANGUAGE MENU (English Alphabet)
# ==========================================
LANG_MENU = """╔══════════════════════╗
   🌐  LANGUAGE SELECTION
╚══════════════════════╝

Welcome! Please select your preferred language below.

━━━━━━━━━━━━━━━━━━━━━━
   1️⃣  English
   2️⃣  Hindi
   3️⃣  Burmese
   4️⃣  Arabic
   5️⃣  Urdu
━━━━━━━━━━━━━━━━━━━━━━

📩 **Reply with a number (1-5)** to continue.

_Your messages will be auto-translated to English._"""

# ==========================================
# 🎯 ACTION MESSAGES
# ==========================================
ACTION_MESSAGES = {
    "en": {
        "prompt": """╔══════════════════════╗
   📋  CHOOSE AN OPTION
╚══════════════════════╝

   1️⃣  📞  Contact with Owner
   2️⃣  🚀  HACK

━━━━━━━━━━━━━━━━━━━━━━
📩 **Reply with 1 or 2**""",
        "contact": f"""╔══════════════════════╗
   ⏳  PLEASE BE PATIENT
╚══════════════════════╝

Thank you for your patience.

The owner is currently **unavailable** and will get back to you as soon as possible.

━━━━━━━━━━━━━━━━━━━━━━
📞  **Alternative Contact:**
   👤 {OWNER_CONTACT}

Feel free to message for urgent matters.
━━━━━━━━━━━━━━━━━━━━━━""",
        "join_first": f"""╔══════════════════════╗
   🚀  UNLOCK PASSWORD
╚══════════════════════╝

To receive the secret password, please join our official group first.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

✅ After joining, reply with **YES** to verify.""",
        "not_joined": f"""╔══════════════════════╗
   ❌  NOT VERIFIED
╚══════════════════════╝

You haven't joined our group yet.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

Please join first, then reply with **YES** again.""",
        "welcome": """╔══════════════════════╗
   🎉  ACCESS GRANTED
╚══════════════════════╝

✅ You are now **verified**!

━━━━━━━━━━━━━━━━━━━━━━
🔐  YOUR SECRET PASSWORD:

   `WELCOME@TO@CLN`
━━━━━━━━━━━━━━━━━━━━━━

⚠️ Keep it safe. Do not share."""
    },
    "hi": {
        "prompt": """╔══════════════════════╗
   📋  विकल्प चुनें
╚══════════════════════╝

   1️⃣  📞  मालिक से संपर्क
   2️⃣  🚀  HACK

━━━━━━━━━━━━━━━━━━━━━━
📩 **1 या 2 लिखकर जवाब दें**""",
        "contact": f"""╔══════════════════════╗
   ⏳  कृपया धैर्य रखें
╚══════════════════════╝

आपके धैर्य के लिए धन्यवाद।

मालिक अभी **अनुपलब्ध** हैं और जल्द ही आपसे संपर्क करेंगे।

━━━━━━━━━━━━━━━━━━━━━━
📞  **वैकल्पिक संपर्क:**
   👤 {OWNER_CONTACT}

ज़रूरी मामलों के लिए संपर्क करें।
━━━━━━━━━━━━━━━━━━━━━━""",
        "join_first": f"""╔══════════════════════╗
   🚀  पासवर्ड अनलॉक करें
╚══════════════════════╝

गुप्त पासवर्ड प्राप्त करने के लिए पहले हमारे आधिकारिक ग्रुप में शामिल हों।

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

✅ जॉइन करने के बाद **YES** लिखकर भेजें।""",
        "not_joined": f"""╔══════════════════════╗
   ❌  वेरिफाई नहीं हुआ
╚══════════════════════╝

आपने अभी तक ग्रुप जॉइन नहीं किया।

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

पहले जॉइन करें, फिर **YES** लिखकर भेजें।""",
        "welcome": """╔══════════════════════╗
   🎉  एक्सेस मिल गया
╚══════════════════════╝

✅ आप **वेरिफाइड** हो गए हैं!

━━━━━━━━━━━━━━━━━━━━━━
🔐  आपका सीक्रेट पासवर्ड:

   `WELCOME@TO@CLN`
━━━━━━━━━━━━━━━━━━━━━━

⚠️ इसे संभाल कर रखें। किसी को न दें।"""
    },
    "my": {
        "prompt": """╔══════════════════════╗
   📋  ရွေးချယ်ပါ
╚══════════════════════╝

   1️⃣  📞  ပိုင်ရှင်နှင့် ဆက်သွယ်
   2️⃣  🚀  HACK

━━━━━━━━━━━━━━━━━━━━━━
📩 **1 သို့မဟုတ် 2 လို့ ပြန်ပို့ပါ**""",
        "contact": f"""╔══════════════════════╗
   ⏳  ခဏစောင့်ပါ
╚══════════════════════╝

စောင့်ဆိုင်းပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။

ပိုင်ရှင်က **မရှိပါ**၊ မကြာမီ ပြန်လည်ဆက်သွယ်ပါမယ်။

━━━━━━━━━━━━━━━━━━━━━━
📞  **အခြားဆက်သွယ်ရန်:**
   👤 {OWNER_CONTACT}

အရေးကြီးကိစ္စများအတွက် ဆက်သွယ်ပါ။
━━━━━━━━━━━━━━━━━━━━━━""",
        "join_first": f"""╔══════════════════════╗
   🚀  စကားဝှက် ဖွင့်ပါ
╚══════════════════════╝

လျှို့ဝှက်စကားဝှက် ရရှိရန် ကျွန်ုပ်တို့၏ တရားဝင်အုပ်စုသို့ ဦးစွာဝင်ပါ။

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

✅ ဝင်ပြီးပါက **YES** လို့ ပြန်ပို့ပါ။""",
        "not_joined": f"""╔══════════════════════╗
   ❌  အတည်ပြုမရသေးပါ
╚══════════════════════╝

သင်သည် အုပ်စုသို့ မဝင်ရောက်ရသေးပါ။

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

ဦးစွာဝင်ပါ၊ ပြီးနောက် **YES** လို့ ပြန်ပို့ပါ။""",
        "welcome": """╔══════════════════════╗
   🎉  ဝင်ရောက်ခွင့် ရပါပြီ
╚══════════════════════╝

✅ အတည်ပြုပြီးပါပြီ!

━━━━━━━━━━━━━━━━━━━━━━
🔐  သင့်လျှို့ဝှက်စကားဝှက်:

   `WELCOME@TO@CLN`
━━━━━━━━━━━━━━━━━━━━━━

⚠️ လုံခြုံစွာ သိမ်းထားပါ။ မမျှဝေပါနှင့်။"""
    },
    "ar": {
        "prompt": """╔══════════════════════╗
   📋  اختر خياراً
╚══════════════════════╝

   1️⃣  📞  التواصل مع المالك
   2️⃣  🚀  HACK

━━━━━━━━━━━━━━━━━━━━━━
📩 **الرد بـ 1 أو 2**""",
        "contact": f"""╔══════════════════════╗
   ⏳  يرجى الانتظار
╚══════════════════════╝

شكراً لصبرك.

المالك **غير متوفر** حالياً وسيتواصل معك في أقرب وقت ممكن.

━━━━━━━━━━━━━━━━━━━━━━
📞  **جهة اتصال بديلة:**
   👤 {OWNER_CONTACT}

تواصل معنا للأمور العاجلة.
━━━━━━━━━━━━━━━━━━━━━━""",
        "join_first": f"""╔══════════════════════╗
   🚀  فتح كلمة المرور
╚══════════════════════╝

للحصول على كلمة المرور السرية، يرجى الانضمام إلى مجموعتنا الرسمية أولاً.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

✅ بعد الانضمام، أرسل **YES** للتحقق.""",
        "not_joined": f"""╔══════════════════════╗
   ❌  لم يتم التحقق
╚══════════════════════╝

لم تنضم إلى مجموعتنا بعد.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

انضم أولاً، ثم أرسل **YES** مرة أخرى.""",
        "welcome": """╔══════════════════════╗
   🎉  تم منح الوصول
╚══════════════════════╝

✅ تم التحقق منك!

━━━━━━━━━━━━━━━━━━━━━━
🔐  كلمة المرور السرية:

   `WELCOME@TO@CLN`
━━━━━━━━━━━━━━━━━━━━━━

⚠️ احتفظ بها بأمان. لا تشاركها."""
    },
    "ur": {
        "prompt": """╔══════════════════════╗
   📋  ایک آپشن منتخب کریں
╚══════════════════════╝

   1️⃣  📞  مالک سے رابطہ
   2️⃣  🚀  HACK

━━━━━━━━━━━━━━━━━━━━━━
📩 **1 یا 2 لکھ کر جواب دیں**""",
        "contact": f"""╔══════════════════════╗
   ⏳  براہ کرم صبر کریں
╚══════════════════════╝

آپ کے صبر کا شکریہ۔

مالک اس وقت **دستیاب نہیں** ہیں اور جلد از جلد آپ سے رابطہ کریں گے۔

━━━━━━━━━━━━━━━━━━━━━━
📞  **متبادل رابطہ:**
   👤 {OWNER_CONTACT}

اہم معاملات کے لیے رابطہ کریں۔
━━━━━━━━━━━━━━━━━━━━━━""",
        "join_first": f"""╔══════════════════════╗
   🚀  پاس ورڈ حاصل کریں
╚══════════════════════╝

خفیہ پاس ورڈ حاصل کرنے کے لیے پہلے ہمارے آفیشل گروپ میں شامل ہوں۔

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

✅ شامل ہونے کے بعد **YES** لکھ کر بھیجیں۔""",
        "not_joined": f"""╔══════════════════════╗
   ❌  تصدیق نہیں ہوئی
╚══════════════════════╝

آپ نے ابھی تک گروپ میں شمولیت نہیں کی۔

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

پہلے شامل ہوں، پھر **YES** لکھ کر بھیجیں۔""",
        "welcome": """╔══════════════════════╗
   🎉  رسائی مل گئی
╚══════════════════════╝

✅ آپ کی تصدیق ہو گئی ہے!

━━━━━━━━━━━━━━━━━━━━━━
🔐  آپ کا خفیہ پاس ورڈ:

   `WELCOME@TO@CLN`
━━━━━━━━━━━━━━━━━━━━━━

⚠️ اسے محفوظ رکھیں۔ کسی کو نہ بتائیں۔"""
    }
}

user_langs = {}
bot_messages = {}
waiting_for_lang = set()
waiting_for_choice = set()
waiting_for_yes = set()
bot_sent_ids = set()

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def is_user_in_group(user_id):
    try:
        await client(GetParticipantRequest(channel=GROUP_USERNAME, participant=user_id))
        return True
    except UserNotParticipantError:
        return False
    except Exception as e:
        print(f"⚠️ Group check error: {e}")
        return False

async def delete_bot_messages(user_id):
    try:
        if user_id in bot_messages:
            for msg_id in bot_messages[user_id]:
                try:
                    await client.delete_messages(user_id, msg_id)
                except Exception:
                    pass
            bot_messages[user_id] = []
    except Exception as e:
        print(f"⚠️ Delete error: {e}")

def track_message(user_id, message):
    if user_id not in bot_messages:
        bot_messages[user_id] = []
    bot_messages[user_id].append(message.id)
    bot_sent_ids.add(message.id)

@client.on(events.NewMessage(incoming=True))
async def auto_reply_handler(event):
    global last_activity
    try:
        if not event.is_private:
            return
        me = await client.get_me()
        if event.sender_id == me.id:
            return
        user_id = event.sender_id
        text = (event.text or "").strip().upper()

        # === LANGUAGE SELECTION ===
        if user_id in waiting_for_lang:
            lang_map = {"1": "en", "2": "hi", "3": "my", "4": "ar", "5": "ur"}
            if text in lang_map:
                user_langs[user_id] = lang_map[text]
                waiting_for_lang.discard(user_id)
                user_lang = lang_map[text]

                confirm = {
                    "en": "✅ Language set to **English**",
                    "hi": "✅ भाषा **हिन्दी** सेट हो गई",
                    "my": "✅ ဘာသာစကား **မြန်မာ** သတ်မှတ်ပြီးပါပြီ",
                    "ar": "✅ تم تعيين اللغة إلى **العربية**",
                    "ur": "✅ زبان **اردو** منتخب ہو گئی"
                }
                msg = await client.send_message(event.chat_id, confirm[user_lang])
                track_message(user_id, msg)

                await asyncio.sleep(0.5)
                msg1 = await client.send_file(event.chat_id, GIF_URL, caption=OFFLINE_MESSAGES[user_lang])
                track_message(user_id, msg1)

                waiting_for_choice.add(user_id)
                msg2 = await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["prompt"])
                track_message(user_id, msg2)
                return
            else:
                await client.send_message(event.chat_id, "❌ Invalid. Reply with **1-5**")
                return

        # === ACTION CHOICE ===
        if user_id in waiting_for_choice:
            user_lang = user_langs.get(user_id, "en")
            if text == "1":
                waiting_for_choice.discard(user_id)
                msg = await client.send_file(event.chat_id, CONTACT_GIF_URL, caption=ACTION_MESSAGES[user_lang]["contact"])
                track_message(user_id, msg)
                return
            elif text == "2":
                waiting_for_choice.discard(user_id)
                joined = await is_user_in_group(user_id)
                if joined:
                    msg = await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["welcome"])
                    track_message(user_id, msg)
                else:
                    waiting_for_yes.add(user_id)
                    msg = await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["join_first"])
                    track_message(user_id, msg)
                return
            else:
                await client.send_message(event.chat_id, "❌ Reply with **1 or 2**")
                return

        # === YES ===
        if user_id in waiting_for_yes:
            user_lang = user_langs.get(user_id, "en")
            if text == "YES":
                joined = await is_user_in_group(user_id)
                if joined:
                    waiting_for_yes.discard(user_id)
                    msg = await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["welcome"])
                    track_message(user_id, msg)
                else:
                    msg = await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["not_joined"])
                    track_message(user_id, msg)
                return

        # === FIRST TIME USER ===
        if user_id not in user_langs:
            waiting_for_lang.add(user_id)
            msg = await client.send_file(event.chat_id, GIF_URL, caption=LANG_MENU)
            track_message(user_id, msg)
            return

        # === NORMAL USER MESSAGE ===
        user_lang = user_langs[user_id]
        waiting_for_choice.add(user_id)
        msg = await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["prompt"])
        track_message(user_id, msg)

        if event.text and user_lang != "en":
            try:
                translated = GoogleTranslator(source='auto', target='en').translate(event.text)
                await client.send_message("me", f"📩 **From** `{user_id}` [{user_lang.upper()}]\n\n**Original:** {event.text}\n**English:** {translated}")
            except Exception as e:
                print(f"⚠️ Translation error: {e}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

@client.on(events.NewMessage(outgoing=True))
async def outgoing_handler(event):
    global last_activity
    try:
        if event.message.id in bot_sent_ids:
            bot_sent_ids.discard(event.message.id)
            return
        last_activity = time.time()
        if not event.is_private:
            return
        if event.text and event.text.startswith("/"):
            return
        user_id = event.chat_id
        if user_id in bot_messages and bot_messages[user_id]:
            await delete_bot_messages(user_id)
    except Exception as e:
        print(f"⚠️ Outgoing Error: {e}")

@client.on(events.NewMessage(pattern=r'^/stop$'))
async def stop_handler(event):
    global is_away
    if event.is_private and event.out:
        is_away = False
        await event.reply("✅ Auto-reply OFF")

@client.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    global is_away
    if event.is_private and event.out:
        is_away = True
        await event.reply("🤖 Auto-reply ON")

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌐 Web server started on port {port}")
    server.serve_forever()

async def main():
    await client.start()
    me = await client.get_me()
    print("=" * 55)
    print("✅ BOT RUNNING!")
    print(f"👤 {me.first_name}")
    print("🌍 Languages: English, Hindi, Burmese, Arabic, Urdu")
    print(f"📞 Contact: {OWNER_CONTACT}")
    print("=" * 55)
    await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
