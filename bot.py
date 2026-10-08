from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from deep_translator import GoogleTranslator
import asyncio
import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# RENDER ENVIRONMENT VARIABLES
# ==========================================
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

# ==========================================
# ⏱️ TIME SETTING
# ==========================================
INACTIVITY_MINUTES = 3
is_away = True
last_activity = time.time()

# ==========================================
# 🎬 GIF LINKS
# ==========================================
GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"
CONTACT_GIF_URL = "https://media.giphy.com/media/z4lwT4QTkK3sYITR7Z/giphy.gif"

# ==========================================
# 🔗 GROUP LINK + 🎁 SECRET PASSWORD
# ==========================================
GROUP_LINK = "https://t.me/rovixbyultimate"
GROUP_USERNAME = "rovixbyultimate"
SECRET_PASSWORD = "WELCOME@TO@CLN"

# ==========================================
# 🌍 OFFLINE MESSAGES
# ==========================================
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

# ==========================================
# 🎯 ACTION MESSAGES
# ==========================================
ACTION_MESSAGES = {
    "en": {
        "prompt": "👇 **Choose an option below:**",
        "contact": "⏳ **Please be patient.**\n\nThe owner is currently away and will get back to you as soon as possible. Thank you for your understanding!",
        "join_first": f"🚀 **Join our official group first to unlock the password:**\n\n🔗 {GROUP_LINK}\n\nAfter joining, tap the button below 👇",
        "not_joined": f"❌ **You haven't joined yet!**\n\n🔗 {GROUP_LINK}\n\nJoin the group first, then tap '✅ I've Joined' again.",
        "welcome": f"🎉 **WELCOME@TO@CLN** 🎉\n\n✅ You are now verified!\n\n🔐 **Your secret password is:** `WELCOME@TO@CLN`\n\nKeep it safe!"
    },
    "hi": {
        "prompt": "👇 **नीचे एक विकल्प चुनें:**",
        "contact": "⏳ **कृपया धैर्य रखें।**\n\nमालिक अभी व्यस्त हैं और जल्द ही आपसे संपर्क करेंगे। आपकी समझ के लिए धन्यवाद!",
        "join_first": f"🚀 **पासवर्ड अनलॉक करने के लिए पहले हमारे आधिकारिक ग्रुप में शामिल हों:**\n\n🔗 {GROUP_LINK}\n\nजॉइन करने के बाद नीचे वाला बटन दबाएं 👇",
        "not_joined": f"❌ **आपने अभी तक जॉइन नहीं किया!**\n\n🔗 {GROUP_LINK}\n\nपहले ग्रुप जॉइन करें, फिर '✅ I've Joined' दबाएं।",
        "welcome": f"🎉 **WELCOME@TO@CLN** 🎉\n\n✅ आप वेरिफाइड हो गए हैं!\n\n🔐 **आपका सीक्रेट पासवर्ड है:** `WELCOME@TO@CLN`\n\nइसे संभाल कर रखें!"
    },
    "my": {
        "prompt": "👇 **အောက်တွင် ရွေးချယ်မှုတစ်ခုကို ရွေးပါ-**",
        "contact": "⏳ **ခဏစောင့်ပါ။**\n\nပိုင်ရှင်က အခု အလုပ်များနေလို့ မကြာမီ ပြန်လည်ဆက်သွယ်ပါမယ်။ နားလည်ပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။",
        "join_first": f"🚀 **စကားဝှက်ရရှိရန် ကျွန်ုပ်တို့၏ တရားဝင်အုပ်စုသို့ ဦးစွာဝင်ရောက်ပါ:**\n\n🔗 {GROUP_LINK}\n\nဝင်ရောက်ပြီးပါက အောက်ရှိခလုတ်ကို နှိပ်ပါ 👇",
        "not_joined": f"❌ **သင်မဝင်ရောက်ရသေးပါ!**\n\n🔗 {GROUP_LINK}\n\nအုပ်စုသို့ ဦးစွာဝင်ရောက်ပါ၊ ပြီးနောက် '✅ I've Joined' ကို ထပ်နှိပ်ပါ။",
        "welcome": f"🎉 **WELCOME@TO@CLN** 🎉\n\n✅ အတည်ပြုပြီးပါပြီ!\n\n🔐 **သင့်လျှို့ဝှက်စကားဝှက်:** `WELCOME@TO@CLN`\n\nလုံခြုံစွာ သိမ်းဆည်းထားပါ!"
    },
    "ar": {
        "prompt": "👇 **اختر أحد الخيارات أدناه:**",
        "contact": "⏳ **يرجى التحلي بالصبر.**\n\nالمالك مشغول حالياً وسيتواصل معك في أقرب وقت ممكن. شكراً لتفهمك!",
        "join_first": f"🚀 **انضم أولاً إلى مجموعتنا الرسمية لفتح كلمة المرور:**\n\n🔗 {GROUP_LINK}\n\nبعد الانضمام، اضغط على الزر أدناه 👇",
        "not_joined": f"❌ **لم تنضم بعد!**\n\n🔗 {GROUP_LINK}\n\nانضم أولاً، ثم اضغط على '✅ I've Joined' مرة أخرى.",
        "welcome": f"🎉 **WELCOME@TO@CLN** 🎉\n\n✅ تم التحقق منك!\n\n🔐 **كلمة المرور السرية الخاصة بك:** `WELCOME@TO@CLN`\n\nاحتفظ بها بأمان!"
    }
}

user_langs = {}

# 🗑️ Har user ke bot ke bheje messages ka record (delete karne ke liye)
bot_messages = {}   # {user_id: [message_id1, message_id2, ...]}

# ==========================================
# TELEGRAM CLIENT
# ==========================================
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ==========================================
# 🔍 GROUP MEMBERSHIP CHECK
# ==========================================
async def is_user_in_group(user_id):
    try:
        await client(GetParticipantRequest(
            channel=GROUP_USERNAME,
            participant=user_id
        ))
        return True
    except UserNotParticipantError:
        return False
    except Exception as e:
        print(f"⚠️ Group check error: {e}")
        return False

# ==========================================
# 🗑️ DELETE ALL BOT MESSAGES FUNCTION
# ==========================================
async def delete_bot_messages(user_id):
    """User ke chat se bot ke saare messages delete karo"""
    try:
        if user_id in bot_messages:
            for msg_id in bot_messages[user_id]:
                try:
                    await client.delete_messages(user_id, msg_id)
                except Exception:
                    pass
            bot_messages[user_id] = []
            print(f"🗑️ Deleted bot messages for {user_id}")
    except Exception as e:
        print(f"⚠️ Delete error: {e}")

def track_message(user_id, message):
    """Bot ke bheje message ko track karo"""
    if user_id not in bot_messages:
        bot_messages[user_id] = []
    bot_messages[user_id].append(message.id)

# ==========================================
# 🎯 INCOMING MESSAGE HANDLER (From User)
# ==========================================
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

        # Language select
        if user_id not in user_langs:
            buttons = [
                [Button.inline("🇬🇧 English", b"lang_en")],
                [Button.inline("🇮🇳 हिन्दी", b"lang_hi")],
                [Button.inline("🇲🇲 မြန်မာ", b"lang_my")],
                [Button.inline("🇸🇦 العربية", b"lang_ar")],
            ]
            msg = await client.send_file(
                event.chat_id,
                GIF_URL,
                caption="🌐 **Please select your language:**\n\n_Choose the language you speak. Your messages will be translated to English for me._",
                buttons=buttons
            )
            track_message(user_id, msg)
            return

        user_lang = user_langs[user_id]

        # Auto-reply (3 min inactive)
        minutes_inactive = (time.time() - last_activity) / 60
        if minutes_inactive >= INACTIVITY_MINUTES:
            msg1 = await client.send_file(
                event.chat_id,
                GIF_URL,
                caption=OFFLINE_MESSAGES.get(user_lang, OFFLINE_MESSAGES["en"])
            )
            track_message(user_id, msg1)
            
            action_buttons = [
                [Button.inline("📞 Contact with Owner", b"action_contact")],
                [Button.inline("🚀 HACK", b"action_hack")]
            ]
            msg2 = await client.send_message(
                event.chat_id,
                ACTION_MESSAGES[user_lang]["prompt"],
                buttons=action_buttons
            )
            track_message(user_id, msg2)
            print(f"📩 Auto-reply + Choices sent ({user_lang})")

        # Translate
        if event.text and user_lang != "en":
            try:
                translated = GoogleTranslator(source='auto', target='en').translate(event.text)
                await client.send_message(
                    "me",
                    f"📩 **New message from** `{user_id}`\n"
                    f"**Language:** {user_lang.upper()}\n"
                    f"**Original:** {event.text}\n"
                    f"**English:** {translated}"
                )
            except Exception as e:
                print(f"⚠️ Translation error: {e}")

    except Exception as e:
        print(f"⚠️ Error: {e}")

# ==========================================
# 🎯 OUTGOING MESSAGE HANDLER (From YOU - Owner)
# ==========================================
@client.on(events.NewMessage(outgoing=True))
async def outgoing_handler(event):
    global last_activity
    try:
        # Activity update karo
        last_activity = time.time()

        # Sirf private chats me
        if not event.is_private:
            return

        # Command messages skip karo
        if event.text and event.text.startswith("/"):
            return

        user_id = event.chat_id

        # 🗑️ Agar tumne user ko reply kiya → bot ke saare messages delete karo
        if user_id in bot_messages and bot_messages[user_id]:
            await delete_bot_messages(user_id)

    except Exception as e:
        print(f"⚠️ Outgoing Error: {e}")

# ==========================================
# 🎯 LANGUAGE SELECTION HANDLER
# ==========================================
@client.on(events.CallbackQuery(data=lambda d: d.startswith(b"lang_")))
async def lang_callback(event):
    try:
        data = event.data.decode()
        user_id = event.sender_id
        lang = data.replace("lang_", "")

        if lang in OFFLINE_MESSAGES:
            user_langs[user_id] = lang
            await event.delete()

            confirm_msg = {
                "en": "✅ Language set to **English**.\n\nNow send me your message.",
                "hi": "✅ भाषा **हिन्दी** सेट हो गई।\n\nअब अपना संदेश भेजें।",
                "my": "✅ ဘာသာစကား **မြန်မာ** သတ်မှတ်ပြီးပါပြီ။\n\nအခု သင့်စာ ပို့ပါ။",
                "ar": "✅ تم تعيين اللغة إلى **العربية**.\n\nالآن أرسل رسالتك."
            }
            msg = await client.send_message(event.chat_id, confirm_msg[lang])
            track_message(user_id, msg)
    except Exception as e:
        print(f"⚠️ Callback Error: {e}")

# ==========================================
# 🎯 ACTION BUTTONS HANDLER
# ==========================================
@client.on(events.CallbackQuery(data=lambda d: d.startswith(b"action_")))
async def action_callback(event):
    try:
        data = event.data.decode()
        user_id = event.sender_id
        user_lang = user_langs.get(user_id, "en")

        if data == "action_contact":
            await event.delete()
            msg = await client.send_file(
                event.chat_id,
                CONTACT_GIF_URL,
                caption=ACTION_MESSAGES[user_lang]["contact"]
            )
            track_message(user_id, msg)
            print(f"📞 Contact owner clicked by {user_id}")

        elif data == "action_hack":
            await event.delete()
            joined = await is_user_in_group(user_id)

            if joined:
                msg = await client.send_message(
                    event.chat_id,
                    ACTION_MESSAGES[user_lang]["welcome"]
                )
                track_message(user_id, msg)
                print(f"🎉 Password given to {user_id}")
            else:
                verify_buttons = [
                    [Button.url("🔗 Join Group", GROUP_LINK)],
                    [Button.inline("✅ I've Joined", b"verify_join")]
                ]
                msg = await client.send_message(
                    event.chat_id,
                    ACTION_MESSAGES[user_lang]["join_first"],
                    buttons=verify_buttons
                )
                track_message(user_id, msg)
                print(f"🔗 Group link sent to {user_id}")

    except Exception as e:
        print(f"⚠️ Action Error: {e}")

# ==========================================
# 🎯 VERIFY JOIN HANDLER
# ==========================================
@client.on(events.CallbackQuery(data=b"verify_join"))
async def verify_join_handler(event):
    try:
        user_id = event.sender_id
        user_lang = user_langs.get(user_id, "en")

        joined = await is_user_in_group(user_id)

        if joined:
            await event.delete()
            msg = await client.send_message(
                event.chat_id,
                ACTION_MESSAGES[user_lang]["welcome"]
            )
            track_message(user_id, msg)
            print(f"🎉 Verified & password given to {user_id}")
        else:
            await event.answer(
                "❌ You haven't joined the group yet!",
                alert=True
            )
            verify_buttons = [
                [Button.url("🔗 Join Group", GROUP_LINK)],
                [Button.inline("✅ I've Joined", b"verify_join")]
            ]
            msg = await client.send_message(
                event.chat_id,
                ACTION_MESSAGES[user_lang]["not_joined"],
                buttons=verify_buttons
            )
            track_message(user_id, msg)
            print(f"❌ User {user_id} not joined yet")

    except Exception as e:
        print(f"⚠️ Verify Error: {e}")

# ==========================================
# COMMANDS
# ==========================================
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

# ==========================================
# 🌐 WEB SERVER (Render ke liye)
# ==========================================
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

# ==========================================
# MAIN
# ==========================================
async def main():
    await client.start()
    me = await client.get_me()
    print("=" * 55)
    print("✅ VERIFY BOT RUNNING!")
    print(f"👤 {me.first_name}")
    print(f"⏱️  Inactivity: {INACTIVITY_MINUTES} min")
    print(f"🔗 Group: {GROUP_LINK}")
    print(f"🗑️  Auto-delete on owner reply: ON")
    print("=" * 55)
    await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
