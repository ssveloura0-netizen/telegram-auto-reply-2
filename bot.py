from telethon import TelegramClient, events
from telethon.sessions import StringSession
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
# SETTINGS
# ==========================================
# 2 minute ki jagah 15 minute kar diya hai (taaki online hote waqt galti se reply na jaye)
INACTIVITY_MINUTES = 15   
is_away = True
last_activity = time.time()

# ==========================================
# 🎬 GIF KA DIRECT LINK (Tumhara Will Smith wala GIF)
# ==========================================
GIF_URL = "https://media.giphy.com/media/OQS9HFAZuLvJEoUdR1/giphy.gif"

# ==========================================
# 💼 BUSINESS PROFESSIONAL MESSAGE
# ==========================================
AWAY_MESSAGE = """Hello,

Thank you for reaching out. I am currently away from my desk and unable to respond right away.

I have received your message and will get back to you at the earliest opportunity.

Best regards,
[ROBIXBY ULTI]"""

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def auto_reply_handler(event):
    global last_activity
    try:
        if event.is_private and is_away:
            me = await client.get_me()
            if event.sender_id == me.id:
                return
            minutes_inactive = (time.time() - last_activity) / 60
            if minutes_inactive >= INACTIVITY_MINUTES:
                # 🎬 GIF ke saath professional message bhejo
                await client.send_file(
                    event.chat_id,
                    GIF_URL,
                    caption=AWAY_MESSAGE
                )
                print(f"📩 Reply sent with GIF")
    except Exception as e:
        print(f"⚠️ Error: {e}")

@client.on(events.NewMessage(outgoing=True))
async def activity_tracker(event):
    global last_activity
    last_activity = time.time()

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
    print("✅ BOT RUNNING ON RENDER!")
    print(f"👤 {me.first_name}")
    print("=" * 55)
    await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
