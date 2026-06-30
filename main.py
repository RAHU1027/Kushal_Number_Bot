import logging
import random
import requests
import threading
from flask import Flask
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Web Server (Keep Alive)
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(f"👋 Hello <a href='tg://user?id={user.id}'>{user.first_name}</a>!\n\n✨ Welcome to KUSHAL Generator.\nUse /gen <code>BIN</code> to start.")

# Command: /gen
async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    
    if not args:
        await update.message.reply_text("❌ Format: /gen 413098")
        return

    bin_input = args[0]
    msg = await update.message.reply_text("🔄 Processing...")

    try:
        # BIN Info
        resp = requests.get(f"https://lookup.binlist.net/{bin_input[:6]}", timeout=5).json()
        bank = resp.get('bank', {}).get('name', 'Unknown')
        brand = resp.get('scheme', 'Unknown').upper()
        country = resp.get('country', {}).get('name', 'Unknown')
        
        # CC Generation
        partial = bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        full_card = partial + str((10 - (sum([int(d) for d in str(partial)][-1::-2]) % 10)) % 10)
        
        result = f"""👤 <b>User:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>
╚━━━━━━「𝐊𝐔𝐒𝐇𝐀𝐋」━━━━━━╝
⚜️ 𝑰𝒏𝒑𝒖𝒕: <code>{bin_input}</code>
♻️ 𝑪𝑪: <code>{full_card}|06|2028|{random.randint(100,999)}</code>
╚━━━━━━「 𝑫𝑬𝑻𝑨𝑰𝑳𝑺 」━━━━━━╝
⚜️ 𝑩𝒂𝒏𝒌: {bank}
⚜️ 𝑵𝒆𝒕𝒘𝒐𝒓𝒌: {brand}
⚜️ 𝑪𝒐𝒖𝒏𝒕𝒓𝒚: {country}
⚜️ 𝑶𝒘𝒏𝒆𝒓: 𝐊𝐔𝐒𝐇𝐀𝐋 𝐎𝐖𝐍𝐄𝐑
╚━━━━━━「𝒁𝒆𝒓𝒐𝑻𝒘𝒐𝑪𝒉𝒌」━━━━━━╝"""
        await msg.edit_text(result, parse_mode=constants.ParseMode.HTML)
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

def run_bot():
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("gen", gen))
    bot_app.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=8080)
