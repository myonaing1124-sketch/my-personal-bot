 import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from openai import OpenAI

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API Keys from Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize Gemini AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

# Initialize OpenAI
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

# Default AI settings (Gemini as primary)
user_ai_preference = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "မင်္ဂလာပါ! ကျွန်တော်က သင့်ရဲ့ Personal Assistant Bot ပါ။\n\n"
        "လက်ရှိတွင် Gemini AI ကို အဓိက အသုံးပြုထားပါသည်။\n"
        "အောက်ပါ Command များကို အသုံးပြုနိုင်ပါသည် -\n"
        "/gemini [မေးခွန်း] - Gemini AI နှင့် စကားပြောရန်\n"
        "/openai [မေးခွန်း] - OpenAI နှင့် စကားပြောရန်\n"
        "/set_ai [gemini/openai] - Default AI ပြောင်းရန်\n"
        "စာတိုများကို တိုက်ရိုက်ပို့၍လည်း မေးမြန်းနိုင်ပါသည်။"
    )
    await update.message.reply_text(welcome_msg)

async def get_gemini_response(prompt):
    if not gemini_model:
        return "Gemini API Key မရှိသေးပါ။"
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

async def get_openai_response(prompt):
    if not openai_client:
        return "OpenAI API Key မရှိသေးပါ။"
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {str(e)} (Quota ကုန်နေခြင်း ဖြစ်နိုင်ပါသည်)"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Get AI preference (Default is Gemini)
    ai_choice = user_ai_preference.get(user_id, "gemini")
    
    await update.message.reply_chat_action("typing")
    
    if ai_choice == "gemini":
        response = await get_gemini_response(text)
    else:
        response = await get_openai_response(text)
        
    await update.message.reply_text(response)

async def set_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args and context.args[0].lower() in ["gemini", "openai"]:
        choice = context.args[0].lower()
        user_ai_preference[user_id] = choice
        await update.message.reply_text(f"Default AI ကို {choice.upper()} သို့ ပြောင်းလဲလိုက်ပါပြီ။")
    else:
        await update.message.reply_text("အသုံးပြုပုံ: /set_ai gemini သို့မဟုတ် /set_ai openai")

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
        print("Error: TELEGRAM_BOT_TOKEN not found!")
    else:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("gemini", gemini_command))
        application.add_handler(CommandHandler("set_ai", set_ai))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Bot is running...")
        application.run_polling()
