
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Replace with your actual bot token and OpenAI API key
TELEGRAM_BOT_TOKEN = '8507002729:AAHs8HVCwGMnUJ02l0orfdnfV8oEtl3-4h0'
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# In-memory storage for user data (for simplicity, a real bot would use a database)
user_data = {}

async def start(update: Update, context) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot.")
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I'm your personal assistant bot. How can I help you today? Type /help to see what I can do.",
    )

async def handle_message(update: Update, context) -> None:
    """Handle normal messages (not commands) by using AI chat."""
    user_message = update.message.text
    user_id = update.effective_user.id
    logger.info(f"Received message from {user_id}: {user_message}")
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful personal assistant for a Myanmar user who is a content writer, language learner (Urdu, Thai, English), and video editor. Answer in Myanmar language unless asked otherwise."},
                {"role": "user", "content": user_message}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Error in message handler: {e}")
        await update.message.reply_text("Sorry, I couldn't process your message.")

async def help_command(update: Update, context) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "Here are the commands you can use:\n"
        "/start - Start the bot\n"
        "/help - Get help and see available commands\n"
        "/chat <your_message> - Chat with the AI assistant\n"
        "/spellcheck <myanmar_text> - Check Myanmar spelling\n"
        "/translate <lang_code> <text> - Translate text (e.g., /translate en Hello)\n"
        "/video_tips - Get video editing tips\n"
        "/add_reminder <time> <message> - Add a reminder (e.g., /add_reminder 10:00 Meeting)\n"
        "/show_reminders - Show all your reminders\n"
        "/add_todo <task> - Add a task to your to-do list\n"
        "/show_todos - Show your to-do list\n"
        "/add_note <note_text> - Add a note\n"
        "/show_notes - Show all your notes\n"
        "/search <query> - Search the web\n"
    )
    await update.message.reply_text(help_text)

async def ai_chat(update: Update, context) -> None:
    """Handle AI chat messages."""
    if not context.args:
        await update.message.reply_text("Please provide a message to chat with the AI. Example: /chat What is AI?")
        return
    
    user_message = " ".join(context.args)
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini", # Using a smaller model for efficiency
            messages=[
                {"role": "system", "content": "You are a helpful personal assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        await update.message.reply_text("Sorry, I couldn't process your request at the moment.")

async def spell_check_myanmar(update: Update, context) -> None:
    """Check Myanmar spelling using AI."""
    if not context.args:
        await update.message.reply_text("Please provide Myanmar text to spell check. Example: /spellcheck မြန်မာစာ")
        return
    
    myanmar_text = " ".join(context.args)
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a Myanmar language expert. Check the spelling and grammar of the provided Myanmar text and suggest corrections if any. If the text is correct, state that it is correct."},
                {"role": "user", "content": f"Check this Myanmar text: {myanmar_text}"}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Error in Myanmar spell check: {e}")
        await update.message.reply_text("Sorry, I couldn't check the spelling at the moment.")

async def translate_text(update: Update, context) -> None:
    """Translate text to a specified language."""
    if len(context.args) < 2:
        await update.message.reply_text("Please provide a language code and text to translate. Example: /translate en Hello")
        return
    
    target_lang = context.args[0].lower()
    text_to_translate = " ".join(context.args[1:])
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": f"You are a language translator. Translate the following text into {target_lang}."},
                {"role": "user", "content": text_to_translate}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Error in translation: {e}")
        await update.message.reply_text("Sorry, I couldn't translate the text at the moment.")

async def video_editing_tips(update: Update, context) -> None:
    """Provide video editing tips."""
    tips = [
        "Always start with a clear story or message.",
        "Use good quality audio; it's often more important than video quality.",
        "Keep your edits tight and purposeful.",
        "Learn keyboard shortcuts for your editing software.",
        "Color grade your footage to create a consistent look.",
        "Use royalty-free music and sound effects.",
        "Export in the correct format and resolution for your platform."
    ]
    await update.message.reply_text("Here are some video editing tips:\n" + "\n".join(tips))

async def add_reminder(update: Update, context) -> None:
    """Add a reminder for the user."""
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {'reminders': [], 'todos': [], 'notes': []}

    if len(context.args) < 2:
        await update.message.reply_text("Please provide a time and a message for the reminder. Example: /add_reminder 10:00 Meeting")
        return
    
    time = context.args[0]
    message = " ".join(context.args[1:])
    user_data[user_id]['reminders'].append({'time': time, 'message': message})
    await update.message.reply_text(f"Reminder '{message}' set for {time}.")

async def show_reminders(update: Update, context) -> None:
    """Show all reminders for the user."""
    user_id = update.effective_user.id
    if user_id in user_data and user_data[user_id]['reminders']:
        reminders_list = "Your reminders:\n"
        for r in user_data[user_id]['reminders']:
            reminders_list += f"- {r['time']}: {r['message']}\n"
        await update.message.reply_text(reminders_list)
    else:
        await update.message.reply_text("You have no reminders.")

async def add_todo(update: Update, context) -> None:
    """Add a task to the to-do list."""
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {'reminders': [], 'todos': [], 'notes': []}

    if not context.args:
        await update.message.reply_text("Please provide a task to add to your to-do list. Example: /add_todo Buy groceries")
        return
    
    task = " ".join(context.args)
    user_data[user_id]['todos'].append(task)
    await update.message.reply_text(f"Task '{task}' added to your to-do list.")

async def show_todos(update: Update, context) -> None:
    """Show the user's to-do list."""
    user_id = update.effective_user.id
    if user_id in user_data and user_data[user_id]['todos']:
        todo_list = "Your to-do list:\n"
        for i, task in enumerate(user_data[user_id]['todos']):
            todo_list += f"{i+1}. {task}\n"
        await update.message.reply_text(todo_list)
    else:
        await update.message.reply_text("Your to-do list is empty.")

async def add_note(update: Update, context) -> None:
    """Add a note for the user."""
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {'reminders': [], 'todos': [], 'notes': []}

    if not context.args:
        await update.message.reply_text("Please provide a note to add. Example: /add_note Remember to call mom")
        return
    
    note = " ".join(context.args)
    user_data[user_id]['notes'].append(note)
    await update.message.reply_text(f"Note '{note}' added.")

async def show_notes(update: Update, context) -> None:
    """Show all notes for the user."""
    user_id = update.effective_user.id
    if user_id in user_data and user_data[user_id]['notes']:
        notes_list = "Your notes:\n"
        for i, note in enumerate(user_data[user_id]['notes']):
            notes_list += f"{i+1}. {note}\n"
        await update.message.reply_text(notes_list)
    else:
        await update.message.reply_text("You have no notes.")

async def web_search(update: Update, context) -> None:
    """Perform a web search and return top results."""
    if not context.args:
        await update.message.reply_text("Please provide a query for web search. Example: /search latest AI news")
        return
    
    query = " ".join(context.args)
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status() # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        
        search_results = []
        for g in soup.find_all('div', class_='tF2CMy'): # This class might change over time
            title = g.find('h3')
            link = g.find('a')
            snippet = g.find('div', class_='VwiC3b')
            
            if title and link:
                search_results.append(f"**{title.text}**\n{link['href']}\n{snippet.text if snippet else ''}\n")
        
        if search_results:
            await update.message.reply_text("Top search results:\n" + "\n".join(search_results[:5]), parse_mode='Markdown')
        else:
            await update.message.reply_text("No search results found.")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during web search: {e}")
        await update.message.reply_text("Sorry, I couldn't perform the web search at the moment.")
    except Exception as e:
        logger.error(f"Error parsing search results: {e}")
        await update.message.reply_text("Sorry, I encountered an issue while processing search results.")

async def error_handler(update: Update, context) -> None:
    """Log the error and send a message to the user."""
    logger.warning(f'Update {update} caused error {context.error}')
    if update and update.effective_message:
        await update.effective_message.reply_text("An error occurred. Please try again later.")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("chat", ai_chat))
    application.add_handler(CommandHandler("spellcheck", spell_check_myanmar))
    application.add_handler(CommandHandler("translate", translate_text))
    application.add_handler(CommandHandler("video_tips", video_editing_tips))
    application.add_handler(CommandHandler("add_reminder", add_reminder))
    application.add_handler(CommandHandler("show_reminders", show_reminders))
    application.add_handler(CommandHandler("add_todo", add_todo))
    application.add_handler(CommandHandler("show_todos", show_todos))
    application.add_handler(CommandHandler("add_note", add_note))
    application.add_handler(CommandHandler("show_notes", show_notes))
    application.add_handler(CommandHandler("search", web_search))

    # Message handler for non-command text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
