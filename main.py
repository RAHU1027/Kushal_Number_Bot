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
CHANNEL_ID = "@kushal_igcc_chats"
IMAGE_URL = "https://i.ibb.co/your-image-link.jpg" 
OWNER_NAME = "mention"

# --- RENDER PUBLIC SERVER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Live!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- BOT LOGIC ---
async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type in [constants.ChatType.GROUP, constants.ChatType.SUPERGROUP]:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=update.effective_user.id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("✨ <b>Initializing...</b>", parse_mode=constants.ParseMode.HTML)
    await asyncio.sleep(0.5)
    
    if await check_access(update, context):
        await msg.delete()
        caption = f"👋 Hello <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>!\n\n✨ Welcome to {OWNER_NAME}'s Generator.\nUse /gen <code>bin</code> to start."
        await update.message.reply_photo(photo=IMAGE_URL, caption=caption, parse_mode=constants.ParseMode.HTML)
        return

    keyboard = [[InlineKeyboardButton("🔗 Join Channel", url="https://t.me/kushal_igcc_chats")],
                [InlineKeyboardButton("✅ Check Join", callback_data="check_join")]]
    
    caption = f"👋 Hello {update.effective_user.first_name}!\n\n✨ Welcome to {OWNER_NAME}'s Generator.\n\n<b>Please join the channel to access:</b>"
    await msg.delete()
    await update.message.reply_photo(photo=IMAGE_URL, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=constants.ParseMode.HTML)

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await check_access(update, context):
        await query.message.delete()
        await query.message.reply_text("✅ <b>Verified!</b> You are now allowed to use /gen.", parse_mode=constants.ParseMode.HTML)
    else:
        await query.answer("❌ Please join the channel first!", show_alert=True)

def luhn_checksum(card_number):
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        n = digits[i] * 2
        digits[i] = n if n < 10 else n - 9
    return (10 - (sum(digits) % 10)) % 10

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context):
        await update.message.reply_text("❌ Please join @kushal_igcc_chats first!")
        return

    if not context.args:
        await update.message.reply_text("❌ Use: /gen 451245")
        return

    bin_input = context.args[0]
    msg = await update.message.reply_text("🔄 <b>Generating...</b> [■□□□□] 20%", parse_mode=constants.ParseMode.HTML)
    await asyncio.sleep(0.5)
    await msg.edit_text("🔄 <b>Generating...</b> [■■■■■] 100%", parse_mode=constants.ParseMode.HTML)
    
    start_t = time.time()
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"https://lookup.binlist.net/{bin_input[:6]}")
            data = resp.json()
            bank, brand, type_cc, country = data.get('bank', {}).get('name', 'Unknown'), data.get('scheme', 'Unknown'), data.get('type', 'Unknown'), data.get('country', {}).get('name', 'Unknown')
        except:
            bank, brand, type_cc, country = "Unknown", "Unknown", "Unknown", "Unknown"

    cc_list = []
    for _ in range(10):
        partial = bin_input[:6] + "".join([str(random.randint(0, 9)) for _ in range(9)])
        full_card = partial + str(luhn_checksum(partial))
        exp_m = str(random.randint(1, 12)).zfill(2)
        exp_y = random.randint(2026, 2036)
        cvv = str(random.randint(100, 999))
        cc_list.append(f"<code>{full_card}|{exp_m}|{exp_y}|{cvv}</code>")
    
    final_text = f"""{OWNER_NAME}
<b>𝗕𝗜𝗡 ⇾ {bin_input}</b>
<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10</b>

{"\n".join(cc_list)}

<b>𝗜𝗻𝗳𝗼: {brand.upper()} - {type_cc.upper()}</b>
<b>𝐈𝐬𝐬𝐮𝐞𝐫: {bank}</b>
<b>𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}</b>
<b>𝗧𝗶𝗺𝗲: {time.strftime("%H:%M:%S")} (Generated {round(time.time() - start_t, 2)}s ago)</b>
╚━━━━━━「𝒁𝒆𝒓𝒐𝑻𝒘𝒐𝑪𝒉𝒌」━━━━━━╝"""
    
    await msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)

if __name__ == '__main__':
    Thread(target=run_web).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen))
    app_bot.add_handler(CallbackQueryHandler(check_join_callback, pattern="check_join"))
    app_bot.run_polling()
