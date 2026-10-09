from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from deep_translator import GoogleTranslator
import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))

GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"
CONTACT_GIF_URL = "https://media.giphy.com/media/z4lwT4QTkK3sYITR7Z/giphy.gif"
MLBB_GIF_URL = "https://media.giphy.com/media/8c02kRLsiC8VgH77yJ/giphy.gif"

GROUP_LINK = "https://t.me/rovixbyultimate"
GROUP_USERNAME = "rovixbyultimate"
OWNER_CONTACT = "@MG1SHWE"

# ==========================================
# 🌍 OFFLINE MESSAGES
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
# 🌐 LANGUAGE MENU
# ==========================================
LANG_MENU = """╔══════════════════════╗
   🌐  LANGUAGE SELECTION
╚══════════════════════╝

Welcome! Please select your preferred language.

━━━━━━━━━━━━━━━━━━━━━━
👇 **Tap a button below to continue**
━━━━━━━━━━━━━━━━━━━━━━

_Your messages will be auto-translated to English._"""

# ==========================================
# 🎯 ACTION MESSAGES
# ==========================================
ACTION_MESSAGES = {
    "en": {
        "prompt": "👇 **Choose an option below:**",
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

✅ After joining, tap **"I've Joined"** to verify.""",
        "not_joined": f"""╔══════════════════════╗
   ❌  NOT VERIFIED
╚══════════════════════╝

You haven't joined our group yet.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

Please join first, then tap **"I've Joined"** again.""",
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
        "prompt": "👇 **नीचे एक विकल्प चुनें:**",
        "contact": f"""╔══════════════════════╗
   ⏳  कृपया धैर्य रखें
╚══════════════════════╝

आपके धैर्य के लिए धन्यवाद।

मालिक अभी **अनुपलब्ध** हैं और जल्द ही आपसे संपर्क करेंगे।

━━━━━━━━━━━━━━━━━━━━━━
📞  **वैकल्पिक संपर्क:**
   👤 {OWNER_CONTACT}
━━━━━━━━━━━━━━━━━━━━━━""",
        "join_first": f"""╔══════════════════════╗
   🚀  पासवर्ड अनलॉक करें
╚══════════════════════╝

गुप्त पासवर्ड प्राप्त करने के लिए पहले हमारे आधिकारिक ग्रुप में शामिल हों।

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

✅ जॉइन करने के बाद **"I've Joined"** दबाएं।""",
        "not_joined": f"""╔══════════════════════╗
   ❌  वेरिफाई नहीं हुआ
╚══════════════════════╝

आपने अभी तक ग्रुप जॉइन नहीं किया।

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

पहले जॉइन करें, फिर **"I've Joined"** दबाएं।""",
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
        "prompt": "👇 **အောက်တွင် ရွေးချယ်ပါ-**",
        "contact": f"""╔══════════════════════╗
   ⏳  ခဏစောင့်ပါ
╚══════════════════════╝

စောင့်ဆိုင်းပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။

ပိုင်ရှင်က **မရှိပါ**၊ မကြာမီ ပြန်လည်ဆက်သွယ်ပါမယ်။

━━━━━━━━━━━━━━━━━━━━━━
📞  **အခြားဆက်သွယ်ရန်:**
   👤 {OWNER_CONTACT}
━━━━━━━━━━━━━━━━━━━━━━""",
        "join_first": f"""╔══════════════════════╗
   🚀  စကားဝှက် ဖွင့်ပါ
╚══════════════════════╝

လျှို့ဝှက်စကားဝှက် ရရှိရန် ကျွန်ုပ်တို့၏ တရားဝင်အုပ်စုသို့ ဦးစွာဝင်ပါ။

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

✅ ဝင်ပြီးပါက **"I've Joined"** ကို နှိပ်ပါ။""",
        "not_joined": f"""╔══════════════════════╗
   ❌  အတည်ပြုမရသေးပါ
╚══════════════════════╝

သင်သည် အုပ်စုသို့ မဝင်ရောက်ရသေးပါ။

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

ဦးစွာဝင်ပါ၊ ပြီးနောက် **"I've Joined"** ကို နှိပ်ပါ။""",
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
        "prompt": "👇 **اختر خياراً من الأسفل:**",
        "contact": f"""╔══════════════════════╗
   ⏳  يرجى الانتظار
╚══════════════════════╝

شكراً لصبرك.

المالك **غير متوفر** حالياً وسيتواصل معك في أقرب وقت ممكن.

━━━━━━━━━━━━━━━━━━━━━━
📞  **جهة اتصال بديلة:**
   👤 {OWNER_CONTACT}
━━━━━━━━━━━━━━━━━━━━━━""",
        "join_first": f"""╔══════════════════════╗
   🚀  فتح كلمة المرور
╚══════════════════════╝

للحصول على كلمة المرور، انضم إلى مجموعتنا الرسمية أولاً.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

✅ بعد الانضمام، اضغط **"I've Joined"**.""",
        "not_joined": f"""╔══════════════════════╗
   ❌  لم يتم التحقق
╚══════════════════════╝

لم تنضم إلى مجموعتنا بعد.

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

انضم أولاً، ثم اضغط **"I've Joined"** مرة أخرى.""",
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
        "prompt": "👇 **نیچے ایک آپشن منتخب کریں:**",
        "contact": f"""╔══════════════════════╗
   ⏳  براہ کرم صبر کریں
╚══════════════════════╝

آپ کے صبر کا شکریہ۔

مالک اس وقت **دستیاب نہیں** ہیں اور جلد از جلد رابطہ کریں گے۔

━━━━━━━━━━━━━━━━━━━━━━
📞  **متبادل رابطہ:**
   👤 {OWNER_CONTACT}
━━━━━━━━━━━━━━━━━━━━━━""",
        "join_first": f"""╔══════════════════════╗
   🚀  پاس ورڈ حاصل کریں
╚══════════════════════╝

خفیہ پاس ورڈ حاصل کرنے کے لیے پہلے ہمارے آفیشل گروپ میں شامل ہوں۔

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

✅ شامل ہونے کے بعد **"I've Joined"** دبائیں۔""",
        "not_joined": f"""╔══════════════════════╗
   ❌  تصدیق نہیں ہوئی
╚══════════════════════╝

آپ نے ابھی تک گروپ میں شمولیت نہیں کی۔

━━━━━━━━━━━━━━━━━━━━━━
🔗 {GROUP_LINK}
━━━━━━━━━━━━━━━━━━━━━━

پہلے شامل ہوں، پھر **"I've Joined"** دبائیں۔""",
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

# ==========================================
# TELEGRAM BOT CLIENT
# ==========================================
client = TelegramClient('bot_session', API_ID, API_HASH)

async def is_user_in_group(user_id):
    try:
        await client(GetParticipantRequest(channel=GROUP_USERNAME, participant=user_id))
        return True
    except UserNotParticipantError:
        return False
    except Exception as e:
        print(f"⚠️ Group check error: {e}")
        return False

# ==========================================
# 🎯 INCOMING MESSAGE HANDLER
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def auto_reply_handler(event):
    try:
        if not event.is_private:
            return
        user_id = event.sender_id

        # Owner ke messages ignore
        if user_id == OWNER_ID:
            return

        # Pehli baar → Language buttons
        if user_id not in user_langs:
            buttons = [
                [Button.inline("🇬🇧 English", b"lang_en")],
                [Button.inline("🇮🇳 हिन्दी (Hindi)", b"lang_hi")],
                [Button.inline("🇲🇲 မြန်မာ (Burmese)", b"lang_my")],
                [Button.inline("🇸🇦 العربية (Arabic)", b"lang_ar")],
                [Button.inline("🇵🇰 اردو (Urdu)", b"lang_ur")],
            ]
            await client.send_file(event.chat_id, GIF_URL, caption=LANG_MENU, buttons=buttons)
            return

        # User ka message aaya → translation owner ko bhejo
        user_lang = user_langs[user_id]
        if event.text and user_lang != "en":
            try:
                translated = GoogleTranslator(source='auto', target='en').translate(event.text)
                await client.send_message(
                    OWNER_ID,
                    f"📩 **From** `{user_id}` [{user_lang.upper()}]\n\n**Original:** {event.text}\n**English:** {translated}"
                )
            except Exception as e:
                print(f"⚠️ Translation error: {e}")

        # Auto reply with buttons
        await client.send_file(event.chat_id, GIF_URL, caption=OFFLINE_MESSAGES[user_lang])
        option_buttons = [
            [Button.inline("📞 Contact with Owner", b"opt_contact")],
            [Button.inline("🚀 PUBG HACK", b"opt_pubg")],
            [Button.inline("🎮 MOBILE LEGENDS BANG", b"opt_mlbb")],
        ]
        await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["prompt"], buttons=option_buttons)
    except Exception as e:
        print(f"⚠️ Error: {e}")

# ==========================================
# 🎯 LANGUAGE BUTTON HANDLER
# ==========================================
@client.on(events.CallbackQuery(data=lambda d: d.startswith(b"lang_")))
async def lang_callback(event):
    try:
        lang = event.data.decode().replace("lang_", "")
        user_id = event.sender_id

        if lang not in OFFLINE_MESSAGES:
            return

        user_langs[user_id] = lang

        # Purana message delete
        await event.delete()

        confirm = {
            "en": "✅ Language set to **English**",
            "hi": "✅ भाषा **हिन्दी** सेट हो गई",
            "my": "✅ ဘာသာစကား **မြန်မာ** သတ်မှတ်ပြီးပါပြီ",
            "ar": "✅ تم تعيين اللغة إلى **العربية**",
            "ur": "✅ زبان **اردو** منتخب ہو گئی"
        }
        await client.send_message(event.chat_id, confirm[lang])

        # Turant offline message + buttons
        await asyncio.sleep(0.5)
        await client.send_file(event.chat_id, GIF_URL, caption=OFFLINE_MESSAGES[lang])
        option_buttons = [
            [Button.inline("📞 Contact with Owner", b"opt_contact")],
            [Button.inline("🚀 PUBG HACK", b"opt_pubg")],
            [Button.inline("🎮 MOBILE LEGENDS BANG", b"opt_mlbb")],
        ]
        await client.send_message(event.chat_id, ACTION_MESSAGES[lang]["prompt"], buttons=option_buttons)
    except Exception as e:
        print(f"⚠️ Lang Error: {e}")

# ==========================================
# 🎯 OPTION BUTTON HANDLER
# ==========================================
@client.on(events.CallbackQuery(data=lambda d: d.startswith(b"opt_")))
async def option_callback(event):
    try:
        data = event.data.decode()
        user_id = event.sender_id
        user_lang = user_langs.get(user_id, "en")
        await event.delete()

        # === CONTACT ===
        if data == "opt_contact":
            await client.send_file(event.chat_id, CONTACT_GIF_URL, caption=ACTION_MESSAGES[user_lang]["contact"])

        # === PUBG HACK ===
        elif data == "opt_pubg":
            joined = await is_user_in_group(user_id)
            if joined:
                await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["welcome"])
            else:
                verify_buttons = [
                    [Button.url("🔗 Join Group", GROUP_LINK)],
                    [Button.inline("✅ I've Joined", b"verify_join")],
                ]
                await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["join_first"], buttons=verify_buttons)

        # === MOBILE LEGENDS BANG ===
        elif data == "opt_mlbb":
            await client.send_file(event.chat_id, MLBB_GIF_URL, caption=ACTION_MESSAGES[user_lang]["contact"])
    except Exception as e:
        print(f"⚠️ Option Error: {e}")

# ==========================================
# 🎯 VERIFY JOIN HANDLER
# ==========================================
@client.on(events.CallbackQuery(data=b"verify_join"))
async def verify_handler(event):
    try:
        user_id = event.sender_id
        user_lang = user_langs.get(user_id, "en")
        joined = await is_user_in_group(user_id)

        if joined:
            await event.delete()
            await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["welcome"])
        else:
            await event.answer("❌ You haven't joined the group yet!", alert=True)
    except Exception as e:
        print(f"⚠️ Verify Error: {e}")

# ==========================================
# 🌐 WEB SERVER
# ==========================================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌐 Web server started on port {port}")
    server.serve_forever()

# ==========================================
# MAIN
# ==========================================
async def main():
    await client.start(bot_token=BOT_TOKEN)
    me = await client.get_me()
    print("=" * 55)
    print("✅ BOT RUNNING!")
    print(f"🤖 @{me.username}")
    print(f"👤 Owner ID: {OWNER_ID}")
    print("=" * 55)
    await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
