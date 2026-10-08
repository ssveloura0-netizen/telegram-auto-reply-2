from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

INACTIVITY_MINUTES = 2
is_away = True
last_activity = time.time()

AWAY_MESSAGE = """╔══════════════════════╗
   💤  OFFLINE MODE  💤
╚══════════════════════╝

Hey there! 👋

I'm currently **offline** right now —
away from my phone, busy with something. 😅

Your message has been received,
and I'll reply as soon as I'm back online. ✅

━━━━━━━━━━━━━━━━━━━━━━
⏳ *Please wait a little while*
━━━━━━━━━━━━━━━━━━━━━━

— Sent automatically 🤖"""

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
                await event.reply(AWAY_MESSAGE)
                print(f"📩 Reply sent")
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
