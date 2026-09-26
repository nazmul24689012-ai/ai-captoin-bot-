import asyncio, random, os, json
from flask import Flask
from threading import Thread
import requests
from telegram import Bot

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = "@bdcapsoine"  # তোমার চ্যানেল ফিক্স করে দিলাম

app = Flask('')
@app.route('/')
def home(): return "Bot Alive & Buffering!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

bot = Bot(token=TOKEN)

BUFFER_FILE = "buffer.json"
POSTED_FILE = "posted.json"

def load_json(file, default):
    if os.path.exists(file):
        try: return json.load(open(file, encoding="utf-8"))
        except: return default
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

buffer = load_json(BUFFER_FILE, [])
posted = set(load_json(POSTED_FILE, []))

def deco():
    h = ["༆༒তও༊ক্যাপশন༊বক্স༒༆༒","꧁༒তও༊ক্যাপশন༊বক্স༒꧂","༺তও༊ক্যাপশন༊বক্স༻"]
    e = ["🥀😢","🌙🌌","💔🥀","🌑💫","🤍🌙","💭🥺"]
    return f"{random.choice(h)}\n{random.choice(e)}\n"

async def generate_one_caption():
    prompts = [
        "তুমি একজন বাংলা কষ্টের ক্যাপশন রাইটার। 1-8 লাইনের একদম নতুন, হৃদয় ছোঁয়া কষ্টের ক্যাপশন লেখো। শুধু ক্যাপশন দাও।",
        "একটি নতুন বাংলা sad status লেখো, 15-20 শব্দ, খুব ইমোশনাল, আনকমন।"
    ]
    try:
        p = random.choice(prompts) + f" random {random.randint(1,999999)}"
        r = requests.get(f"https://text.pollinations.ai/{p}", timeout=30)
        txt = r.text.strip()
        if len(txt) < 10 or len(txt) > 250 or "queue" in txt.lower(): return None
        if txt in posted or txt in buffer: return None
        return txt
    except: return None

async def buffer_filler():
    global buffer
    while True:
        try:
            if len(buffer) < 20:
                print(f"Buffer low ({len(buffer)}/20), generating...")
                cap = await generate_one_caption()
                if cap:
                    buffer.append(cap)
                    save_json(BUFFER_FILE, buffer)
                    print(f"✅ Buffer added | Total: {len(buffer)}")
                else:
                    await asyncio.sleep(15)
                    continue
            else:
                await asyncio.sleep(60)
        except: await asyncio.sleep(10)
        await asyncio.sleep(10)

async def auto_poster():
    global buffer, posted
    await asyncio.sleep(15)
    while True:
        try:
            if buffer:
                cap = buffer.pop(0)
                save_json(BUFFER_FILE, buffer)
                posted.add(cap)
                save_json(POSTED_FILE, list(posted)[-500:])
                final = f"{deco()}\n{cap}\n\n{random.choice(['🥀','🌙','💔'])}"
                await bot.send_message(chat_id=CHANNEL, text=final)
                print(f"🚀 POSTED: {cap[:30]} | Left: {len(buffer)}")
            else:
                print("⚠️ Buffer empty, waiting...")
                await asyncio.sleep(30)
                continue
        except Exception as e:
            print(f"Post Error: {e}")
        await asyncio.sleep(random.randint(1500, 3000))

async def main():
    await asyncio.gather(buffer_filler(), auto_poster())

try:
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
except:
    asyncio.run(main())
