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

# তোমার বলা মতো মুড অনুযায়ী ইমোজি
MOOD_EMOJI = {
    "কষ্ট": ["💔", "🥀", "😢", "🌧️"],
    "ভালোবাসা": ["❤️", "🥰", "💌", "✨"],
    "একাকিত্ব": ["🌙", "🖤", "🍂", "🌌"],
    "অভিমান": ["😔", "💭", "🥀", "🙂"],
    "অপেক্ষা": ["⏳", "🌙", "💫", "🤍"]
}

async def generate_ai_caption():
    try:
        # 1. এলোমেলো লাইন সিলেক্ট - তোমার বলা মতো
        line_choice = random.choice(["5-7", "12-14"])

        # 2. টপিক আর মুড
        topics = [
            ("না পাওয়ার কষ্ট", "কষ্ট"),
            ("আবেগী ভালোবাসা", "ভালোবাসা"),
            ("মধ্যরাতের একাকিত্ব", "একাকিত্ব"),
            ("অভিমানী ভালোবাসা", "অভিমান"),
            ("তার অপেক্ষায়", "অপেক্ষা")
        ]
        topic, mood = random.choice(topics)

        # 3. বিভিন্ন স্টাইল যাতে নজর কাড়ে
        styles = [
            "প্রতি লাইন ছোট কবিতার মতো",
            "গল্পের মতো করে",
            "প্রশ্ন দিয়ে শুরু করবে",
            "শেষ লাইনে একটা চমক থাকবে"
        ]
        style = random.choice(styles)

        prompt = f"'{topic}' niye {line_choice} liner abegi bangla caption lekho. Style: {style}. Bhasha khub sundor hobe, manush er mon chuye jabe. Kono hashtag dio na, emoji dio na, sudhu caption dio."

        print(f"বানাচ্ছি: {line_choice} লাইন | {topic} | {style}")

        url = f"https://text.pollinations.ai/{prompt}"
        res = requests.get(url, timeout=30)
        caption = res.text.strip()

        # 4. শেষে মুড অনুযায়ী ইমোজি যোগ করা - তোমার বলা মতো
        emojis = random.sample(MOOD_EMOJI[mood], 2)
        final_caption = f"{caption}\n\n{''.join(emojis)}"

        return final_caption

    except Exception as e:
        print(f"AI Error: {e}")
        return "ভুলে গেছো বললেই কি ভোলা যায়?\nকিছু মানুষ স্মৃতিতে নয়,\nঅভ্যাসে থেকে যায়।\nতাকে ছাড়া সব আছে,\nশুধু ভালো থাকাটা নেই।\n\n💔🥀"

async def auto_job():
    print(f"✅ Bot চালু -> {CHANNEL_ID}")
    try:
        caption = await generate_ai_caption()
        await bot.send_message(chat_id=CHANNEL_ID, text=caption)
        print("✅ প্রথম পোস্ট হয়েছে!")
    except Exception as e:
        print(f"Telegram Error: {e}")

    while True:
        # তোমার বলা মতো ২০-৫০ মিনিট এলোমেলো টাইমে
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
