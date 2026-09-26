import asyncio
import random
import json
import os
from telegram import Bot
import google.generativeai as genai

# Render থেকে নেবে
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# তোমার চ্যানেল ফিক্স করে দিলাম
CHANNEL_ID = "@bdcapsoine"

if not BOT_TOKEN or not GEMINI_API_KEY:
    print("❌ Render এ BOT_TOKEN আর GEMINI_API_KEY বসাওনি!")
    exit()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
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

def save_used(used_set):
    with open(USED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(used_set), f, ensure_ascii=False)

used_captions = load_used()

async def generate_ai_caption():
    topics = ["আবেগী ভালোবাসা", "না পাওয়ার কষ্ট", "একাকিত্ব", "অভিমান", "মধ্যরাতের অনুভূতি", "অপেক্ষা"]
    topic = random.choice(topics)

    prompt = f"""
    '{topic}' বিষয়ে 5-7 লাইনের একটি আবেগী বাংলা ক্যাপশন লেখো।
    নিয়ম: 
    1. অবশ্যই 5-7 লাইন হবে।
    2. একটু ডিজাইন/বর্ডার সহকারে লিখবে।
    3. শেষে 2 টা ইমোজি দিবে।
    4. হ্যাশট্যাগ দিবে না।
    """

    try:
        response = await model.generate_content_async(prompt)
        caption = response.text.strip()
        if caption in used_captions:
            return await generate_ai_caption()
        used_captions.add(caption)
        save_used(used_captions)
        return caption
    except Exception as e:
        print(f"AI Error: {e}")
        return "তাকে ভালোবাসাটা ছিল আমার নীরব অভ্যাস,\nযেটা সে কখনো বুঝতেই পারেনি।\nআজ আমি কষ্ট পেতে শিখে গেছি,\nআর সে থাকতে ভুলে গেছে।\n\n💔 🥀"

async def auto_job():
    print(f"✅ Bot চালু হয়েছে -> {CHANNEL_ID} এ পোস্ট করবে...")
    while True:
        wait_minutes = random.randint(20, 50)
        await asyncio.sleep(wait_minutes * 60)
        caption = await generate_ai_caption()
        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=caption)
            print(f"✅ পোস্ট হয়েছে bdcapsoine এ")
        except Exception as e:
            print(f"Telegram Error: {e} - বটকে চ্যানেলে Admin করেছো তো?")

if __name__ == "__main__":
    asyncio.run(auto_job())
