import logging
import random
import time
import requests
import threading
from flask import Flask
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Flask App for Web Service (To keep it 24/7)
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running 24/7!"

# Telegram Bot Token
TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"
OWNER_NAME = "𝐊𝐔𝐒𝐇𝐀𝐋 𝐎𝐖𝐍𝐄𝐑"

# Bot Logic
async def gen(update, context):
    if not context.args:
        await update.message.reply_text("❌ Usage: /gen <BIN>")
        return
    
    bin_input = context.args[0]
    msg = await update.message.reply_text("🔍 Fetching data...")
    
    try:
        url = f"https://lookup.binlist.net/{bin_input[:6]}"
        resp = requests.get(url, timeout=5).json()
        
        bank = resp.get('bank', {}).get('name', 'Unknown')
        brand = resp.get('scheme', 'Unknown').upper()
        country = resp.get('country', {}).get('name', 'Unknown')
        flag = resp.get('country', {}).get('emoji', '🏳️')
        
        # Generator logic
        partial = bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        full_card = partial + str((10 - (sum([int(d) for d in str(partial)][-1::-2]) % 10)) % 10)
        
        final_text = f"""👤 <b>User:</b> {update.effective_user.first_name}
╚━━━━━━「𝐊𝐔𝐒𝐇𝐀𝐋」━━━━━━╝
⚜️ 𝑰𝒏𝒑𝒖𝒕: <code>{bin_input}</code>
♻️ 𝑪𝑪: <code>{full_card}|06|2028|{random.randint(100,999)}</code>
╚━━━━━━「 𝑫𝑬𝑻𝑨𝑰𝑳𝑺 」━━━━━━╝
⚜️ 𝑩𝒂𝒏𝒌: {bank}
⚜️ 𝑵𝒆𝒕𝒘𝒐𝒓𝒌: {brand}
⚜️ 𝑪𝒐𝒖𝒏𝒕𝒓𝒚: {country} {flag}
⚜️ 𝑶𝒘𝒏𝒆𝒓: {OWNER_NAME}
╚━━━━━━「𝒁𝒆𝒓𝒐𝑻𝒘𝒐𝑪𝒉𝒌」━━━━━━╝"""
        await msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)
    except:
        await msg.edit_text("❌ Error!")

def run_bot():
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("gen", gen))
    bot_app.run_polling()

if __name__ == '__main__':
    # Threading for bot + flask
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=8080)
