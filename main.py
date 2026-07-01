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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # --- ORIGINAL ANIMATION SYSTEM ---
    reactions = ["🔥", "✨", "🚀", "💎", "⚡", "🤖", "🛡️"]
    r_emoji = random.choice(reactions)
    
    msg = await update.message.reply_text(f"{r_emoji} 𝗜𝗡𝗜𝗧𝗜𝗔𝗟𝗜𝗭𝗜𝗡𝗚 𝗦𝗬𝗦𝗧𝗘𝗠...")
    await asyncio.sleep(0.5)
    await msg.edit_text(f"{r_emoji} 𝗟𝗢𝗔𝗗𝗜𝗡𝗚: [■□□□□□□□□□] 10%")
    await asyncio.sleep(0.4)
    await msg.edit_text(f"{r_emoji} 𝗟𝗢𝗔𝗗𝗜𝗡𝗚: [■■■■■□□□□□] 50%")
    await asyncio.sleep(0.4)
    await msg.edit_text(f"{r_emoji} 𝗟𝗢𝗔𝗗𝗜𝗡𝗚: [■■■■■■■■■■] 100%")
    await msg.delete()
    # --- ANIMATION END ---

    # Welcome Text Content
    user = update.effective_user
    caption = (f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
               f"👤 <b>User:</b> {user.first_name}\n"
               f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
               f"📛 <b>Username:</b> @{user.username if user.username else 'None'}\n"
               f"✨ <b>Owner:</b> {OWNER_NAME}\n"
               f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
               f"📢 <b>Please join our channel to access:</b>\n\n"
               f"⚡ <b>Use command:</b> <code>/gen 451245</code>")

    # Buttons
    keyboard = [[InlineKeyboardButton("🔗 Join Channel", url="https://t.me/kushal_igcc_chats")],
                [InlineKeyboardButton("✅ Check Join", callback_data="check_join")]]
    
    # Send as simple text message
    await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=constants.ParseMode.HTML)

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
    msg = await update.message.reply_text("🔄 <b>Generating...</b> [■■■■■] 100%", parse_mode=constants.ParseMode.HTML)
    
    start_t = time.time()
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"https://lookup.binlist.net/{bin_input[:6]}")
            data = resp.json()
            bank, brand, type_cc, country = data.get('bank', {}).get('name', 'Unknown'), data.get('scheme', 'Unknown'), data.get('type', 'Unknown'), data.get('country', {}).get('name', 'Unknown')
        except:
            bank, brand, type_cc, country = "Unknown", "Unknown", "Unknown", "Unknown"

    cc_list = [f"<code>{bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)]) + str(luhn_checksum(bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])))}|{str(random.randint(1, 12)).zfill(2)}|{random.randint(2026, 2036)}|{random.randint(100, 999)}</code>" for _ in range(10)]
    
    final_text = f"<b>[+] 𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙀𝘿 𝘾𝘼𝙍𝘿𝙎</b>\n\n"+"\n".join(cc_list)+f"\n\n<b>──────────────</b>\n<b>💳 𝘽𝙄𝙉:</b> <code>{bin_input}</code>\n<b>🏦 𝘽𝘼𝙉𝙆:</b> {bank}\n<b>📡 𝙏𝙔𝙋𝙀:</b> {brand.upper()} - {type_cc.upper()}\n<b>🌍 𝘾𝙊𝙐𝙉𝙏𝙍𝙔:</b> {country}\n<b>──────────────</b>\n<b>⏰ 𝙏𝙄𝙈𝙀:</b> {round(time.time() - start_t, 2)}s\n<b>👤 𝙊𝙒𝙉𝙀𝙍:</b> {OWNER_NAME}"
    await msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)

if __name__ == '__main__':
    Thread(target=run_web).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen))
    app_bot.add_handler(CallbackQueryHandler(check_join_callback, pattern="check_join"))
    app_bot.run_polling()
