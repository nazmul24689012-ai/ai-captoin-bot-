import asyncio
import random
import requests
import os
import threading
from flask import Flask
from telegram import Bot

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running for @bdcapsoine"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

CHANNEL_ID = "@bdcapsoine"
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

MOOD_EMOJI = {
    "কষ্ট": ["💔", "🥀", "😢", "🌧️"],
    "ভালোবাসা": ["❤️", "🥰", "💌", "✨"],
    "একাকিত্ব": ["🌙", "🖤", "🍂", "🌌"],
    "অভিমান": ["😔", "💭", "🥀", "🙂"],
    "অপেক্ষা": ["⏳", "🌙", "💫", "🤍"]
}

# যদি AI ফেইল করে, এখান থেকে পোস্ট করবে, তাই Error আর চ্যানেলে যাবে না
FALLBACK_CAPTIONS = [
    "তোমাকে ভুলে যাওয়া সহজ না,\nভুলে থাকার অভিনয়টা কঠিন।\nরোজ রাতে নিজের সাথে যুদ্ধ করি,\nআর দিনের বেলায় হাসি।",
    "কিছু মানুষ থাকে,\nযারা চলে গিয়েও থেকে যায়।\nকথায় নয়, অভ্যাসে।\nমনে নয়, নিঃশ্বাসে।",
    "অপেক্ষাটা খারাপ না,\nখারাপ হলো যার জন্য অপেক্ষা করছি\nসে বুঝতেই পারে না\nআমি তার জন্য থেমে আছি।",
    "সবাই বলে ভালো আছি,\nকেউ জিজ্ঞেস করে না\nভালো থাকার অভিনয়টা\nকতটা কঠিন হচ্ছে।",
    "তুমি চলে গেছো ঠিকই,\nকিন্তু তোমার স্মৃতি\nআমার প্রতিটা রাতের\nঘুম কেড়ে নেয়।",
    "ভালোবাসা সুন্দর,\nযদি মানুষটা সঠিক হয়।\nআর ভালোবাসা সবচেয়ে কষ্টের,\nযদি মানুষটা ভুল হয়।",
    "মধ্যরাতে ঘুম ভেঙে গেলে\nবুঝি, তুমি এখনো\nআমার কোথাও\nরয়ে গেছো।"
]

async def generate_ai_caption():
    try:
        line_choice = random.choice(["5-7", "12-14"])
        topics = [
            ("না পাওয়ার কষ্ট", "কষ্ট"),
            ("আবেগী ভালোবাসা", "ভালোবাসা"),
            ("মধ্যরাতের একাকিত্ব", "একাকিত্ব"),
            ("অভিমানী ভালোবাসা", "অভিমান"),
            ("তার অপেক্ষায়", "অপেক্ষা")
        ]
        topic, mood = random.choice(topics)
        styles = ["কবিতার মতো ছোট লাইনে", "গল্পের মতো করে", "প্রশ্ন দিয়ে শুরু", "শেষ লাইনে চমক"]
        style = random.choice(styles)
        prompt = f"'{topic}' niye {line_choice} liner abegi bangla caption lekho. Style: {style}. Hashtag, emoji chara sudhu caption."

        print(f"AI try: {line_choice} line | {topic}")

        # নতুন লিংক, সাথে User-Agent যাতে ব্লক না করে
        url = f"https://text.pollinations.ai/{prompt}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=40)

        text = res.text.strip()

        # যদি Error JSON আসে, তাহলে এখানেই আটকে দেবে, চ্যানেলে যাবে না
        if "error" in text.lower() or "queue full" in text.lower() or "429" in text or len(text) < 20:
            raise Exception(f"Pollinations busy: {text[:50]}")

        emojis = random.sample(MOOD_EMOJI[mood], 2)
        return f"{text}\n\n{''.join(emojis)}"

    except Exception as e:
        print(f"AI Fail, fallback dicchi: {e}")
        caption = random.choice(FALLBACK_CAPTIONS)
        mood = random.choice(list(MOOD_EMOJI.keys()))
        emojis = random.sample(MOOD_EMOJI[mood], 2)
        return f"{caption}\n\n{''.join(emojis)}"

async def auto_job():
    print(f"✅ Bot চালু -> {CHANNEL_ID}")
    try:
        caption = await generate_ai_caption()
        await bot.send_message(chat_id=CHANNEL_ID, text=caption)
        print("✅ প্রথম পোস্ট হয়েছে!")
    except Exception as e:
        print(f"Telegram Error: {e}")

    while True:
        wait = random.randint(20, 50)
        print(f"পরের পোস্ট {wait} মিনিট পর...")
        await asyncio.sleep(wait * 60)
        try:
            caption = await generate_ai_caption()
            await bot.send_message(chat_id=CHANNEL_ID, text=caption)
            print("✅ পোস্ট হয়েছে")
        except Exception as e:
            print(f"Telegram Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(auto_job())
