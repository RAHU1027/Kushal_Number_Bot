import logging
import random
import requests
import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, constants, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Active!"

TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"

async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Welcome"),
        BotCommand("gen", "Generate cards")
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    profile = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    msg = (f"<b>👋 Welcome, {profile}!</b>\n\n"
           f"👑 𝐎𝐰𝐧𝐞𝐫 𝐨𝐟 𝐭𝐡𝐢𝐬 𝐒𝐞𝐬𝐬𝐢𝐨𝐧: {profile}\n"
           f"✨ 𝖴𝗌𝖾 /gen <code>BIN</code>")
    await update.message.reply_html(msg)

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_profile = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    
    if not context.args:
        await update.message.reply_text("❌ Format: /gen <BIN>")
        return

    bin_input = context.args[0]
    msg = await update.message.reply_text("🔄 Processing...")

    try:
        # API 1: Binlist (Main)
        url = f"https://lookup.binlist.net/{bin_input[:6]}"
        resp = requests.get(url, timeout=5)
        
        if resp.status_code != 200:
            # API 2: Backup (agar pehli fail ho)
            url = f"https://data.handyapi.com/bin/{bin_input[:6]}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            bank = data.get('Bank', {}).get('Name', 'Unknown')
            brand = data.get('Card', {}).get('Scheme', 'Unknown')
            country = data.get('Country', {}).get('Name', 'Unknown')
        else:
            data = resp.json()
            bank = data.get('bank', {}).get('name', 'Unknown')
            brand = data.get('scheme', 'Unknown')
            country = data.get('country', {}).get('name', 'Unknown')

        # Generate 10 unique cards
        cards = []
        for _ in range(10):
            base = bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])
            full = base + str(random.randint(0, 9))
            cards.append(f"{full}|06|26|{random.randint(100,999)}")
        
        result = (f"𝗕𝗜𝗡 ⇾ {bin_input[:6]}\n"
                  f"𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10\n\n"
                  f"<code>{chr(10).join(cards)}</code>\n\n"
                  f"𝗜𝗻𝗳𝗼: {brand.upper()}\n"
                  f"𝐈𝐬𝐬𝐮𝐞𝐫: {bank}\n"
                  f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n"
                  f"👤 𝐎𝐰𝐧𝐞𝐫: {user_profile}")
        
        await msg.edit_text(result, parse_mode=constants.ParseMode.HTML)
    except Exception as e:
        await msg.edit_text(f"❌ Error: BIN data fetch failed. Try another BIN.")

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == '__main__':
    Thread(target=run_flask).start()
    app_bot = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen))
    app_bot.run_polling()
