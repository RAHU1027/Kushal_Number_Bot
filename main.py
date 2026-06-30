import logging
import random
import requests
import os
from flask import Flask
from threading import Thread
from telegram import Update, constants, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Web Server for Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"

TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"
OWNER_NAME = "𝐊𝐔𝐒𝐇𝐀𝐋 𝐎𝐖𝐍𝐄𝐑"

# Automatic Side Menu Commands Set Karna
async def set_commands(bot):
    commands = [
        BotCommand("start", "Welcome message"),
        BotCommand("gen", "Generate a card")
    ]
    await bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Side Menu Update
    await set_commands(context.bot)
    
    user = update.effective_user
    text = f"👋 Hello <a href='tg://user?id={user.id}'>{user.first_name}</a>!\n\n✨ Welcome to 𝐊𝐔𝐒𝐇𝐀𝐋 Generator.\nUse /gen <code>BIN</code> to start."
    await update.message.reply_html(text)

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("❌ Use: /gen <6-digit-BIN>")
        return

    bin_input = context.args[0]
    msg = await update.message.reply_text("🔄 Processing...")

    try:
        url = f"https://lookup.binlist.net/{bin_input[:6]}"
        resp = requests.get(url, timeout=5).json()
        
        bank = resp.get('bank', {}).get('name', 'Unknown')
        brand = resp.get('scheme', 'Unknown').upper()
        country = resp.get('country', {}).get('name', 'Unknown')
        
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
⚜️ 𝑶𝒘𝒏𝒆𝒓: {OWNER_NAME}
╚━━━━━━「𝒁𝒆𝒓𝒐𝑻𝒘𝒐𝑪𝒉𝒌」━━━━━━╝"""
        await msg.edit_text(result, parse_mode=constants.ParseMode.HTML)
    except:
        await msg.edit_text("❌ Error: Invalid BIN.")

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == '__main__':
    Thread(target=run_flask).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen))
    print("Bot is ready...")
    app_bot.run_polling()
