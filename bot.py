from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8673033967:AAGvnuf3SGgtZWX0HhzsSVlvetqFaEcDA6c"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Emojis ka use karke hum waisa hi visual effect denge
    keyboard = [
        [InlineKeyboardButton("➕ ADD ME TO YOUR GROUP", callback_data='group')],
        [InlineKeyboardButton("✅ HELP", callback_data='help'), InlineKeyboardButton("❌ SOURCE", callback_data='source')],
        [InlineKeyboardButton("🌐 LANGS", callback_data='langs')],
        [InlineKeyboardButton("💬 SUPPORT", callback_data='support'), InlineKeyboardButton("📢 CHANNEL", callback_data='channel')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🚀 *Kushal Credit Shop*\nChoose your category:", parse_mode='Markdown', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Number selling ka logic
    if query.data == 'group':
        await query.edit_message_text("📱 *Instagram Numbers List:*\n+91 9876543210\n+91 9123456789")
    elif query.data == 'help':
        await query.edit_message_text("🆘 *How to buy:*\nSend payment to @Admin and get your code.")
    # Baki buttons ka logic yahan aise hi aayega...

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
