import random, asyncio, aiohttp, logging
from flask import Flask
from threading import Thread
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# Logging setup
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Operational!"

TOKEN = "8410119226:AAEDaMjNEmPINLbJc26RsPVNKgGjVNH_fSk"
CHANNEL_ID = "@kushal_igcc_chats"

# --- NETWORK CONFIG ---
request_config = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0)

async def is_member(update, context):
    if update.effective_chat.type != 'private': return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=update.effective_user.id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# 1. Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sticker hata diya
    if not await is_member(update, context):
        kbd = [[InlineKeyboardButton("Join Channel", url="https://t.me/kushal_igcc_chats")],
               [InlineKeyboardButton("Check Join", callback_data="check")]]
        await update.message.reply_text("Please join our channel first!", reply_markup=InlineKeyboardMarkup(kbd))
    else:
        await send_welcome(update, context)

# 2. Welcome Sender (Photo/Emoji Removed)
async def send_welcome(update, context):
    user = update.effective_user
    msg = (f"👋 Welcome, {user.first_name}\n\n"
           f"👑 Owner: KUSHAL OWNER\n"
           f"🆔 User ID: {user.id}\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"✨ Use /gen <BIN>.")
    await update.message.reply_text(msg)

# 3. Join Check
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Checking...")
    if await is_member(update, context):
        try: await query.message.delete()
        except: pass
        await send_welcome(update, context)
    else:
        await query.answer("❌ Please join @kushal_igcc_chats first!", show_alert=True)

# 4. Gen
async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_member(update, context): return
    if not context.args: await update.message.reply_text("❌ Use: /gen <BIN>"); return
    
    msg = await update.message.reply_text("Analyzing...")
    
    # BIN Lookup
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://lookup.binlist.net/{context.args[0][:6]}", timeout=10) as resp:
            data = await resp.json() if resp.status == 200 else {}
            
    cards = [f"{context.args[0][:6]}{random.randint(1000000000,9999999999)}|{random.randint(1,12):02d}|{random.randint(26,31)}|{random.randint(100,999)}" for _ in range(10)]
    
    res = (f"BIN: {context.args[0][:6]}\n\n"
           f"{chr(10).join(cards)}\n\n"
           f"👤 Done by KushaL")
    await msg.edit_text(res)

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    
    bot_app = ApplicationBuilder().token(TOKEN).request(request_config).post_init(lambda app: app.bot.set_my_commands([BotCommand("start", "Welcome"), BotCommand("gen", "Generate")])).build()
    
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("gen", gen))
    bot_app.add_handler(CallbackQueryHandler(check_join, pattern="check"))
    
    print("Bot is running in simple mode...")
    bot_app.run_polling(drop_pending_updates=True)
