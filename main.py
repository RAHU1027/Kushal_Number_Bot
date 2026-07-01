import logging
import random
import asyncio
import httpx
import os
import time
from flask import Flask
from threading import Thread
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# --- CONFIGURATION ---
TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"
CHANNEL_ID = "@kushal_igcc_chats"
OWNER_NAME = "Kushal"

# --- PREMIUM EMOJI LOGIC ---
def get_premium_entities():
    ids = [
        "6138595008674009570", "6138522591230431210", "6138530760258228554",
        "6136580196565782691", "5873204392429096339", "6089110457073801038",
        "6098287664019018219", "6071319615907041401", "6073454283372630712",
        "4956612582816351459", "4956436416142771580", "6296577138615125756",
        "6296367896398399651", "6255890170390775841", "6088958101698909879",
        "6098064720856617194", "6129580830097410852", "6131847262864675499",
        "6129580830097410852", "6132043212157619800", "6131969566353395110",
        "6129448347536198680", "6131940510899638481", "6129589660550171485"
    ]
    offsets = [0, 1, 3, 4, 6, 7, 9, 10, 12, 14, 15, 16, 17, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38]
    lengths = [1, 2, 1, 2, 1, 2, 1, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    # Emojis dikhane ke liye sirf invisible character space use kiya hai
    return [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=offsets[i], length=lengths[i], custom_emoji_id=ids[i]) for i in range(len(ids))]

async def send_with_premium(update, text, reply_markup=None):
    # Emojis ko invisible characters par apply kiya hai taaki text na dikhe
    await update.message.reply_text("‎" * 40 + "\n" + text, entities=get_premium_entities(), reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)

# --- SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- BOT LOGIC ---
async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type in [constants.ChatType.GROUP, constants.ChatType.SUPERGROUP]: return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=update.effective_user.id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reactions = ["🔥", "✨", "🚀", "💎", "⚡", "🤖", "🛡️"]
    r_emoji = random.choice(reactions)
    msg = await update.message.reply_text(f"{r_emoji} 𝗜𝗡𝗜𝗧𝗜𝗔𝗟𝗜𝗭𝗜𝗡𝗚 𝗦𝗬𝗦𝗧𝗘𝗠...")
    await asyncio.sleep(0.5)
    await msg.edit_text(f"{r_emoji} 𝗟𝗢𝗔𝗗𝗜𝗡𝗚: [■■■■■■■■■■] 100%")
    await msg.delete()

    user = update.effective_user
    caption = (f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n👤 <b>User:</b> {user.first_name}\n🆔 <b>User ID:</b> <code>{user.id}</code>\n📛 <b>Username:</b> @{user.username if user.username else 'None'}\n✨ <b>Owner:</b> {OWNER_NAME}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n📢 <b>Please join our channel to access:</b>\n\n⚡ <b>Use command:</b> <code>/gen 451245</code>")
    keyboard = [[InlineKeyboardButton("🔗 Join Channel", url="https://t.me/kushal_igcc_chats")], [InlineKeyboardButton("✅ Check Join", callback_data="check_join")]]
    await send_with_premium(update, caption, reply_markup=InlineKeyboardMarkup(keyboard))

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await check_access(update, context):
        await query.message.delete()
        await send_with_premium(update, "✅ <b>Verified!</b> You are now allowed to use /gen.")
    else: await query.answer("❌ Please join the channel first!", show_alert=True)

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
    msg = await update.message.reply_text("🔄 <b>Generating...</b>", parse_mode=constants.ParseMode.HTML)
    start_t = time.time()
    
    # Original Generator Logic
    cc_list = [f"<code>{bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)]) + str(luhn_checksum(bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])))}|{str(random.randint(1, 12)).zfill(2)}|{random.randint(2026, 2036)}|{random.randint(100, 999)}</code>" for _ in range(10)]
    final_text = f"<b>[+] 𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙀𝘿 𝘾𝘼𝙍𝘿𝙎</b>\n\n"+"\n".join(cc_list)+f"\n\n<b>──────────────</b>\n<b>💳 𝘽𝙄𝙉:</b> <code>{bin_input}</code>\n<b>⏰ 𝙏𝙄𝙈𝙀:</b> {round(time.time() - start_t, 2)}s\n<b>👤 𝙊𝙒𝙉𝙀𝙍:</b> {OWNER_NAME}"
    
    # Updated message with entities
    await msg.edit_text("‎" * 40 + "\n" + final_text, entities=get_premium_entities(), parse_mode=constants.ParseMode.HTML)

if __name__ == '__main__':
    Thread(target=run_web).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen))
    app_bot.add_handler(CallbackQueryHandler(check_join_callback, pattern="check_join"))
    app_bot.run_polling()
