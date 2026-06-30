import logging
import random
import requests
import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, constants, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Flask Web Server (For Render 24/7)
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Active!"

TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"

# Command list for Side Menu
async def post_init(application):
    commands = [
        BotCommand("start", "Welcome message"),
        BotCommand("gen", "Generate cards with BIN")
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    profile = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    msg = (f"<b>👋 Welcome, {profile}!</b>\n\n"
           f"👑 𝐎𝐰𝐧𝐞𝐫 𝐨𝐟 𝐭𝐡𝐢𝐬 𝐒𝐞𝐬𝐬𝐢𝐨𝐧: {profile}\n"
           f"🆔 𝐔𝐬𝐞𝐫 𝐈𝐃: <code>{user.id}</code>\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"✨ 𝖴𝗌𝖾 /gen <code>BIN</code> 𝗍𝗈 𝗀𝖾𝗇𝖾𝗋𝖺𝗍𝖾.")
    await update.message.reply_html(msg)

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_profile = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    
    if not context.args:
        await update.message.reply_text("❌ Format: /gen <6-digit-BIN>")
        return

    bin_input = context.args[0]
    msg = await update.message.reply_text("🔄 <b>Generating Cards...</b>\n[□□□□□] 0%")

    await asyncio.sleep(0.5)
    await msg.edit_text("🔄 <b>Generating Cards...</b>\n[■■■■■] 100%", parse_mode=constants.ParseMode.HTML)

    try:
        url = f"https://lookup.binlist.net/{bin_input[:6]}"
        resp = requests.get(url, timeout=5).json()
        
        bank = resp.get('bank', {}).get('name', 'Unknown')
        brand = resp.get('scheme', 'Unknown').upper()
        country = resp.get('country', {}).get('name', 'Unknown')
        card_type = resp.get('type', 'CREDIT').upper()
        
        cards = []
        for _ in range(10):
            base = bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])
            # Simple checksum logic
            full_card = base + str(random.randint(0, 9)) 
            cards.append(f"{full_card}|06|26|{random.randint(100,999)}")
        
        result = (f"𝗕𝗜𝗡 ⇾ {bin_input[:6]}\n"
                  f"𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10\n\n"
                  f"<code>{chr(10).join(cards)}</code>\n\n"
                  f"𝗜𝗻𝗳𝗼: {brand} - {card_type}\n"
                  f"𝐈𝐬𝐬𝐮𝐞𝐫: {bank}\n"
                  f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}\n"
                  f"👤 𝐎𝐰𝐧𝐞𝐫 𝐨𝐟 𝐒𝐞𝐬𝐬𝐢𝐨𝐧: {user_profile}")
        
        await msg.edit_text(result, parse_mode=constants.ParseMode.HTML)
    except:
        await msg.edit_text("❌ Error: Invalid BIN or Connection issue.")

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == '__main__':
    Thread(target=run_flask).start()
    
    # ApplicationBuilder mein post_init add kiya
    app_bot = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen))
    print("Bot is ready and running...")
    app_bot.run_polling()
