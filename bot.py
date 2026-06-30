from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8673033967:AAGvnuf3SGgtZWX0HhzsSVlvetqFaEcDA6c"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Yahan apne GitHub Pages ka link replace kar dena
    web_url = "https://kushal-bot.github.io/index.html" 
    
    keyboard = [
        [InlineKeyboardButton("📱 Open Kushal Credit Shop", web_app=WebAppInfo(url=web_url))]
    ]
    await update.message.reply_text(
        "Welcome to Kushal Shop! 🚀\nSelect your platform to view available numbers:", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot Active!")
    app.run_polling()
