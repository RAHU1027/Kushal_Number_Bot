import logging
import random
import asyncio
import httpx
import os
import time
from flask import Flask
from threading import Thread
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- CONFIGURATION ---
TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"
CHANNEL_ID = "@kushal_igcc_chats"
IMAGE_URL = "https://i.ibb.co/your-image-link.jpg" 
OWNER_NAME = "Kushal"

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

# Animation ID nikalne ka handler
async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.animation:
        await update.message.reply_text(f"Animation ID: `{update.message.animation.file_id}`")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Animation
    anim = await update.message.reply_animation("YOUR_ANIMATION_ID_HERE")
    await asyncio.sleep(3)
    try: await anim.delete()
    except: pass

    # 2. Sticker
    sticker = await update.message.reply_sticker("CAACAgUAAxkBAAEf8IxqRIAwOovDJ8k8sDOrnxq-M31FIwACTA4AAoNyEVW11UDSBGNxizwE")
    await asyncio.sleep(2)
    try: await sticker.delete()
    except: pass

    # 3. Welcome Message
    if await check_access(update, context):
        caption = f"👋 Hello <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>!\n\n✨ Welcome to {OWNER_NAME}'s Generator.\nUse /gen <code>bin</code> to start."
        msg = await update.message.reply_photo(photo=IMAGE_URL, caption=caption, parse_mode=constants.ParseMode.HTML)
    else:
        keyboard = [[InlineKeyboardButton("🔗 Join Channel", url="https://t.me/kushal_igcc_chats")],
                    [InlineKeyboardButton("✅ Check Join", callback_data="check_join")]]
        caption = f"👋 Hello {update.effective_user.first_name}!\n\n✨ Welcome to {OWNER_NAME}'s Generator.\n\n<b>Please join the channel to access:</b>"
        msg = await update.message.reply_photo(photo=IMAGE_URL, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=constants.ParseMode.HTML)
    
    await asyncio.sleep(30)
    try: await msg.delete()
    except: pass

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

    custom_name = "Kushal's User"
    mention = f"<a href='tg://user?id={update.effective_user.id}'>{custom_name}</a>"

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
    
    # Yahan .format() use kiya hai taaki error na aaye
    final_text = (
        "👤 <b>User:</b> {mention}\n\n{owner}\n<b>𝗕𝗜𝗡 ⇾ {bin}</b>\n<b>𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10</b>\n\n"
        "{cards}\n\n"
        "<b>𝗜𝗻𝗳𝗼: {brand} - {type_cc}</b>\n"
        "<b>𝐈𝐬𝐬𝐮𝐞𝐫: {bank}</b>\n"
        "<b>𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}</b>\n"
        "<b>𝗧𝗶𝗺𝗲: {time} (Generated {duration}s ago)</b>\n"
        "╚━━━━━━「𝒁𝒆𝒓𝒐𝑻𝘅𝒐𝑪𝒉𝒌」━━━━━━╝"
    ).format(
        mention=mention, owner=OWNER_NAME, bin=bin_input, cards="\n".join(cc_list),
        brand=brand.upper(), type_cc=type_cc.upper(), bank=bank, country=country,
        time=time.strftime("%H:%M:%S"), duration=round(time.time() - start_t, 2)
    )
    
    await msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)

if __name__ == '__main__':
    Thread(target=run_web).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen))
    app_bot.add_handler(MessageHandler(filters.ANIMATION, get_file_id))
    app_bot.add_handler(CallbackQueryHandler(check_join_callback, pattern="check_join"))
    app_bot.run_polling()
