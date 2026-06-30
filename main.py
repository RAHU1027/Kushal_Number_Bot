import logging
import random
import asyncio
import httpx
import os
import time
from flask import Flask
from threading import Thread
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# --- CONFIGURATION ---
TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"
CHANNEL_ID = "@your_channel_username" # Apna channel ID yahan daalein
OWNER_NAME = "🦋💸 ⃪♔‌⃟𝐊𝐔𝐒𝐇𝐀𝐋 🇴‌𝐖𝐍𝐄𝐑≛⃝❛🚩"

# --- RENDER PUBLIC SERVER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Kushal Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- BOT LOGIC ---
async def is_user_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def luhn_checksum(card_number):
    digits = [int(d) for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return (10 - (total % 10)) % 10

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("✨ <b>Initializing...</b>", parse_mode=constants.ParseMode.HTML)
    await asyncio.sleep(0.5)
    
    keyboard = [
        [InlineKeyboardButton("🔗 Join Channel", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")],
        [InlineKeyboardButton("✅ Check Join", callback_data="check_join")]
    ]
    await msg.edit_text(
        f"👋 Hello <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>!\n\n"
        f"✨ Welcome to {OWNER_NAME}'s Generator.\nUse /gen <code>bin</code> to start.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=constants.ParseMode.HTML
    )

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await is_user_member(context, query.from_user.id):
        await query.answer("✅ Verified! Use /gen.", show_alert=True)
    else:
        await query.answer("❌ Pehle Channel Join Karo!", show_alert=True)

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(context, update.effective_user.id):
        await update.message.reply_text("❌ Please join our channel first!")
        return

    if not context.args:
        await update.message.reply_text("❌ Use: /gen 557501")
        return

    bin_input = context.args[0]
    msg = await update.message.reply_text("🔄 <b>Fetching Real-time Data...</b>", parse_mode=constants.ParseMode.HTML)
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"https://lookup.binlist.net/{bin_input[:6]}")
            data = resp.json()
            bank = data.get('bank', {}).get('name', 'Unknown')
            brand = data.get('scheme', 'Unknown')
            type_cc = data.get('type', 'Unknown')
            country = data.get('country', {}).get('name', 'Unknown')
            emoji = data.get('country', {}).get('emoji', '🌍')
        except:
            bank, brand, type_cc, country, emoji = "Unknown", "Unknown", "Unknown", "Unknown", "🌍"

    cc_list = []
    for _ in range(10):
        partial = bin_input[:6].ljust(6, '0') + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        full_card = partial + str(luhn_checksum(partial))
        cvv = str(random.randint(100, 999))
        cc_list.append(f"<code>{full_card}|06|26|{cvv}</code>")

    spent_time = round(time.time() - start_time, 2)
    final_text = f"""<b>𝗕𝗜𝗡 ⇾ {bin_input}</b>
<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10</b>

{"\n".join(cc_list)}

<b>𝗜𝗻𝗳𝗼: {brand.upper()} - {type_cc.upper()}</b>
<b>𝐈𝐬𝐬𝐮𝐞𝐫: {bank}</b>
<b>𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {emoji} {country}</b>
<b>𝗧𝗶𝗺𝗲: {spent_time}s</b>"""
    
    await msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)

# --- EXECUTION ---
if __name__ == '__main__':
    Thread(target=run_web).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen))
    app_bot.add_handler(CallbackQueryHandler(check_join_callback, pattern="check_join"))
    app_bot.run_polling()
