import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from openai import OpenAI

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API Keys from Environment Variables (Render Dashboard ထဲက ယူပါမည်)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize Gemini AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

# Initialize OpenAI (Optional)
if OPENAI_API_KEY and OPENAI_API_KEY.lower() != "none":
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "မင်္ဂလာပါ! ကျွန်တော်က သင့်ရဲ့ Personal Assistant Bot ပါ။\n\n"
        "လက်ရှိတွင် Gemini AI ကို အဓိက အသုံးပြုထားပါသည်။\n"
        "စာတိုများကို တိုက်ရိုက်ပို့၍ မေးမြန်းနိုင်ပါသည်။\n\n"
        "အသုံးပြုနိုင်သော Command များ -\n"
        "/gemini [မေးခွန်း] - Gemini AI နှင့် စကားပြောရန်\n"
        "/start - Bot ကို ပြန်လည်စတင်ရန်"
    )
    await update.message.reply_text(welcome_msg)

async def get_gemini_response(prompt):
    if not gemini_model:
        return "Gemini API Key မရှိသေးပါ။ Render Environment မှာ GEMINI_API_KEY ကို စစ်ဆေးပေးပါ။"
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
    
    await update.message.reply_chat_action("typing")
    response = await get_gemini_response(text)
    await update.message.reply_text(response)

async def gemini_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("မေးခွန်းလေးပါ တစ်ခါတည်း ရိုက်ပေးပါဦး။ ဥပမာ - /gemini နေကောင်းလား")
        return
    await update.message.reply_chat_action("typing")
    response = await get_gemini_response(prompt)
    await update.message.reply_text(response)

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in Environment Variables!")
    else:
        # Create the application with the token from Environment Variables
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("gemini", gemini_command))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Bot is starting with Token from Environment...")
        application.run_polling()
