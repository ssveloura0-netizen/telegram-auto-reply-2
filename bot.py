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

INACTIVITY_MINUTES = 3
is_away = True
last_activity = time.time()

GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"
CONTACT_GIF_URL = "https://media.giphy.com/media/z4lwT4QTkK3sYITR7Z/giphy.gif"

GROUP_LINK = "https://t.me/rovixbyultimate"
GROUP_USERNAME = "rovixbyultimate"

OFFLINE_MESSAGES = {
    "en": """Hello,

Thank you for reaching out. I am currently away from my desk and unable to respond right away.

I have received your message and will get back to you at the earliest opportunity.

Best regards,
[Your Name]""",
    "hi": """नमस्ते,

संपर्क करने के लिए धन्यवाद। मैं अभी अपने डेस्क से दूर हूँ और तुरंत जवाब नहीं दे सकता।

मुझे आपका संदेश मिल गया है और मैं जल्द से जल्द जवाब दूँगा।

सादर,
[आपका नाम]""",
    "my": """မင်္ဂလာပါ၊

ဆက်သွယ်ပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။ ကျွန်တော် အခု စားပွဲကနေ ဝေးနေတာမို့ ချက်ချင်း ပြန်လည်ဖြေကြားနိုင်မှာ မဟုတ်ပါဘူး။

သင့်စာ ရောက်ပါပြီ၊ အတတ်နိုင်ဆုံး အမြန်ဆုံး ပြန်လည်ဖြေကြားပါမယ်။

လေးစားစွာဖြင့်၊
[သင့်နာမည်]""",
    "ar": """مرحباً،

شكراً لتواصلك معي. أنا حالياً بعيد عن مكتبي ولا أستطيع الرد فوراً.

لقد استلمت رسالتك وسأرد عليك في أقرب فرصة ممكنة.

مع خالص التحية،
[اسمك]"""
}

# 🌐 Language menu text (numbered)
LANG_MENU = {
    "en": "🌐 **Please select your language:**\n\n1️⃣ English\n2️⃣ हिन्दी\n3️⃣ မြန်မာ\n4️⃣ العربية\n\n**Reply with 1, 2, 3, or 4**",
}

ACTION_MESSAGES = {
    "en": {
        "prompt": "👇 **Reply with:**\n\n1️⃣ Contact with Owner\n2️⃣ HACK",
        "contact": "⏳ **Please be patient.**\n\nThe owner is currently away and will get back to you as soon as possible. Thank you for your understanding!",
        "join_first": f"🚀 **Join our official group first to unlock the password:**\n\n🔗 {GROUP_LINK}\n\nAfter joining, reply with **YES** to get the password.",
        "not_joined": f"❌ **You haven't joined yet!**\n\n🔗 {GROUP_LINK}\n\nJoin first, then reply **YES** again.",
        "welcome": "🎉 **WELCOME@TO@CLN** 🎉\n\n✅ You are now verified!\n\n🔐 **Your secret password is:** `WELCOME@TO@CLN`\n\nKeep it safe!"
    },
    "hi": {
        "prompt": "👇 **Reply karo:**\n\n1️⃣ Contact with Owner\n2️⃣ HACK",
        "contact": "⏳ **कृपया धैर्य रखें।**\n\nमालिक जल्द ही आपसे संपर्क करेंगे।",
        "join_first": f"🚀 **पहले हमारे ग्रुप में शामिल हों:**\n\n🔗 {GROUP_LINK}\n\nजॉइन करने के बाद **YES** reply करें।",
        "not_joined": f"❌ **आपने जॉइन नहीं किया!**\n\n🔗 {GROUP_LINK}\n\nपहले जॉइन करें, फिर **YES** reply करें।",
        "welcome": "🎉 **WELCOME@TO@CLN** 🎉\n\n✅ आप वेरिफाइड हो गए!\n\n🔐 **पासवर्ड:** `WELCOME@TO@CLN`"
    },
    "my": {
        "prompt": "👇 **Reply လုပ်ပါ:**\n\n1️⃣ Contact with Owner\n2️⃣ HACK",
        "contact": "⏳ **ခဏစောင့်ပါ။**",
        "join_first": f"🚀 **အုပ်စုသို့ ဦးစွာဝင်ပါ:**\n\n🔗 {GROUP_LINK}\n\nဝင်ပြီးပါက **YES** reply လုပ်ပါ။",
        "not_joined": f"❌ **မဝင်ရသေးပါ!**\n\n🔗 {GROUP_LINK}\n\nဦးစွာဝင်ပါ၊ ပြီးနောက် **YES** reply လုပ်ပါ။",
        "welcome": "🎉 **WELCOME@TO@CLN** 🎉\n\n✅ အတည်ပြုပြီးပါပြီ!\n\n🔐 **စကားဝှက်:** `WELCOME@TO@CLN`"
    },
    "ar": {
        "prompt": "👇 **الرد على:**\n\n1️⃣ Contact with Owner\n2️⃣ HACK",
        "contact": "⏳ **يرجى التحلي بالصبر.**",
        "join_first": f"🚀 **انضم للمجموعة أولاً:**\n\n🔗 {GROUP_LINK}\n\nثم الرد بـ **YES**.",
        "not_joined": f"❌ **لم تنضم بعد!**\n\n🔗 {GROUP_LINK}\n\nانضم أولاً، ثم الرد بـ **YES**.",
        "welcome": "🎉 **WELCOME@TO@CLN** 🎉\n\n✅ تم التحقق!\n\n🔐 **كلمة المرور:** `WELCOME@TO@CLN`"
    }
}

user_langs = {}
bot_messages = {}
waiting_for_lang = set()      # Jin users ne language menu dekha
waiting_for_choice = set()    # Jin users ne action menu dekha
waiting_for_yes = set()       # Jin users ne group link dekha

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

        # === LANGUAGE SELECTION (1, 2, 3, 4) ===
        if user_id in waiting_for_lang:
            lang_map = {"1": "en", "2": "hi", "3": "my", "4": "ar"}
            if text in lang_map:
                user_langs[user_id] = lang_map[text]
                waiting_for_lang.discard(user_id)
                confirm = {
                    "en": "✅ Language set to **English**.\n\nNow send me your message.",
                    "hi": "✅ भाषा **हिन्दी** सेट हो गई।\n\nअब अपना संदेश भेजें।",
                    "my": "✅ ဘာသာစကား **မြန်မာ** သတ်မှတ်ပြီးပါပြီ။",
                    "ar": "✅ تم تعيين اللغة إلى **العربية**."
                }
                msg = await client.send_message(event.chat_id, confirm[lang_map[text]])
                track_message(user_id, msg)
                return
            else:
                await client.send_message(event.chat_id, "❌ Please reply with **1, 2, 3, or 4**")
                return

        # === ACTION CHOICE (1 = Contact, 2 = HACK) ===
        if user_id in waiting_for_choice:
            user_lang = user_langs.get(user_id, "en")
            if text == "1":
                waiting_for_choice.discard(user_id)
                msg = await client.send_file(event.chat_id, CONTACT_GIF_URL, caption=ACTION_MESSAGES[user_lang]["contact"])
                track_message(user_id, msg)
                print(f"📞 Contact clicked by {user_id}")
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

        # === YES (after joining group) ===
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

        # === FIRST TIME USER → Language menu ===
        if user_id not in user_langs:
            waiting_for_lang.add(user_id)
            msg = await client.send_file(event.chat_id, GIF_URL, caption=LANG_MENU["en"])
            track_message(user_id, msg)
            return

        # === AUTO-REPLY (3 min inactive) ===
        user_lang = user_langs[user_id]
        minutes_inactive = (time.time() - last_activity) / 60
        if minutes_inactive >= INACTIVITY_MINUTES:
            msg1 = await client.send_file(event.chat_id, GIF_URL, caption=OFFLINE_MESSAGES.get(user_lang, OFFLINE_MESSAGES["en"]))
            track_message(user_id, msg1)

            waiting_for_choice.add(user_id)
            msg2 = await client.send_message(event.chat_id, ACTION_MESSAGES[user_lang]["prompt"])
            track_message(user_id, msg2)
            print(f"📩 Auto-reply sent ({user_lang})")

        # === TRANSLATE ===
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
    print("=" * 55)
    await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
