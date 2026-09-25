import os, random, asyncio, threading
from flask import Flask
from google import genai
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_ID = -1003159703637

# নতুন Gemini SDK
client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Running - bdcapsoine is Alive!"

TOPICS_18 = [
    "না পাওয়া ভালোবাসা", "ছেড়ে যাওয়া / ধোঁকা", "একতরফা ভালোবাসা",
    "রাত জাগা কষ্ট", "মনে পড়া / মিস করা", "একাকিত্ব",
    "অপেক্ষা", "অভিমান", "হারিয়ে যাওয়া মানুষ",
    "মিথ্যে হাসি", "কাউকে ভুলতে না পারা", "ভালোবাসার আফসোস",
    "বেকারত্বের কষ্টে প্রেম হারানো", "পরিবারের চাপে বিচ্ছেদ",
    "পুরনো স্মৃতি", "নিজেকে ভালোবাসা", "মাঝরাতের চিন্তা", "ভালো থাকার অভিনয়"
]

posted_history = set()

async def generate_caption():
    topic = random.choice(TOPICS_18)
    prompt = f"তুমি @bdcapsoine চ্যানেলের জন্য লিখছো। বিষয়: {topic}\nএই বিষয়ে একটি নতুন, ভাইরাল, ইমোশনাল বাংলা ক্যাপশন লেখো। শর্ত: 1. আগে পোস্ট করেছো {list(posted_history)[-5:]} - রিপিট করবে না। 2. ডিজাইন সহ লাইনে লাইনে সাজানো। 3. শেষে মুড অনুযায়ী 2-3 টা ইমোজি 🥀💔😊 4. 30-60 শব্দ। 5. শেষে #bdcapsoine"
    res = await client.aio.models.generate_content(model='gemini-2.0-flash', contents=prompt)
    return res.text

async def generate_story():
    prompt = f"তুমি ফেসবুকে ভাইরাল হওয়া বাস্তব জীবনের গল্প লেখক। @bdcapsoine এর জন্য একটি বড় গল্প লেখো। গল্পের ধরন: ছেড়ে যাওয়া / ধোঁকা / ভালোবাসার কষ্ট। শর্ত: 1. প্রথম ব্যক্তিতে (আমি) লেখো, বাস্তব মনে হবে। 2. আগে পোস্ট করা {list(posted_history)[-5:]} রিপিট না। 3. টাইটেল সহ 200-350 শব্দ, ইমোজি সহ। 4. ইমোশনাল। 5. শেষে #bdcapsoine"
    res = await client.aio.models.generate_content(model='gemini-2.0-flash', contents=prompt)
    return res.text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যাঁ ভাই, আমি চালু আছি ✅\n@bdcapsoine এ পোস্ট চলছে...")

async def hi_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.lower()
    if any(x in txt for x in ["hi", "হাই", "bot", "চালু", "hello"]):
        await update.message.reply_text("হ্যাঁ ভাই, আমি চালু আছি আর পোস্ট করতে প্রস্তুত আছি! 🚀")

async def posting_loop(bot: Bot):
    await asyncio.sleep(20)
    while True:
        try:
            is_story = random.random() < 0.25
            content = await generate_story() if is_story else await generate_caption()
            if content[:60] not in posted_history:
                await bot.send_message(chat_id=CHANNEL_ID, text=content)
                posted_history.add(content[:60])
                print("Posted:", "Story" if is_story else "Caption")
                wait = random.randint(6*3600, 12*3600) if is_story else random.randint(1800, 10800)
                await asyncio.sleep(wait)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(60)

async def main_async():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hi_reply))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # একই application এর bot ব্যবহার করলে কনফ্লিক্ট হবে না
    await posting_loop(application.bot)

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main_async())
