import asyncio
import random
import json
import os
import threading
from flask import Flask
from telegram import Bot
from google import genai

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running for @bdcapsoine"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# তোমার চ্যানেল - ঠিক করে দিলাম
CHANNEL_ID = "@bdcapsoine"

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    print("❌ Render এ BOT_TOKEN আর GEMINI_API_KEY বসাওনি!")
    exit()

client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=BOT_TOKEN)

USED_FILE = "used_captions.json"

def load_used():
    if os.path.exists(USED_FILE):
        try:
            with open(USED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_used(s):
    with open(USED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(s), f, ensure_ascii=False)

used_captions = load_used()

async def generate_ai_caption():
    topics = ["আবেগী ভালোবাসা", "না পাওয়ার কষ্ট", "একাকিত্ব", "অভিমান", "মধ্যরাতের অনুভূতি"]
    topic = random.choice(topics)
    prompt = f"'{topic}' বিষয়ে 5-7 লাইনের আবেগী, কাব্যিক বাংলা ক্যাপশন লেখো। একটু ডিজাইন দিবে, শেষে 2টা ইমোজি দিবে। হ্যাশট্যাগ দিবে না।"
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        caption = response.text.strip()
        if caption in used_captions or len(caption) < 20:
            return await generate_ai_caption()
        used_captions.add(caption)
        save_used(used_captions)
        return caption
    except Exception as e:
        print(f"AI Error: {e}")
        return "তাকে ভালোবাসাটা ছিল আমার নীরব অভ্যাস,\nযেটা সে কখনো বুঝতেই পারেনি।\nআজ আমি কষ্ট পেতে শিখে গেছি,\nআর সে থাকতে ভুলে গেছে।\n\n💔 🥀"

async def auto_job():
    print(f"✅ Bot চালু -> {CHANNEL_ID}")
    # চালু হওয়ার সাথে সাথেই প্রথম পোস্ট
    try:
        caption = await generate_ai_caption()
        await bot.send_message(chat_id=CHANNEL_ID, text=caption)
        print("✅ প্রথম পোস্ট হয়েছে @bdcapsoine এ!")
    except Exception as e:
        print(f"Telegram Error: {e}")

    while True:
        wait_minutes = random.randint(20, 50)
        print(f"পরের পোস্ট {wait_minutes} মিনিট পর...")
        await asyncio.sleep(wait_minutes * 60)
        caption = await generate_ai_caption()
        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=caption)
            print("✅ পোস্ট হয়েছে")
        except Exception as e:
            print(f"Telegram Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(auto_job())
