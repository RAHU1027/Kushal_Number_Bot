import random, asyncio, aiohttp, logging, traceback
from flask import Flask
from threading import Thread
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# Logging setup
logging.basicConfig(level=logging.INFO)

# --- NETWORK FIX: Connection timeouts and pool size ---
request_config = HTTPXRequest(
    connection_pool_size=10,
    connect_timeout=30.0,
    read_timeout=30.0,
    write_timeout=30.0
)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Fully Operational!"

TOKEN = "8410119226:AAEDaMjNEmPINLbJc26RsPVNKgGjVNH_fSk"
CHANNEL_ID = "@kushal_igcc_chats"

PREMIUM_EMOJIS = [
    "6120898777046847624", "6269285159774720688", "6138793380328510194", "6138595008674009570",
    "6138522591230431210", "5864127571754489150", "6269014138748408445", "6118397435338296885",
    "6138530760258228554", "4958489311726011319", "6086919156169448008", "6088958101698909879",
    "6129589660550171485", "6131847262864675499", "6131969566353395110", "6129448347536198680",
    "6131940510899638481", "6129497520616771484", "6129580830097410852", "6132043212157619800"
]

def get_e(): return f"<emoji document_id='{random.choice(PREMIUM_EMOJIS)}'>✨</emoji>"

# --- AI-STYLE AUTO-RECOVERY DECORATOR ---
def auto_recover(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            logging.error(f"Error in {func.__name__}: {traceback.format_exc()}")
    return wrapper

@auto_recover
async def is_member(update, context):
    if update.effective_chat.type != 'private': return True
    member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=update.effective_user.id)
    return member.status in ['member', 'administrator', 'creator']

@auto_recover
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sticker = await update.message.reply_sticker(sticker="CAACAgIAAxkBAAEX2Ntm8-y5a6y5a6y5a6y5a6y5a6y5AAJvAAOtZ9UAAAAy-z963_4uEwQ")
        await asyncio.sleep(1.5)
        await sticker.delete()
    except: pass

    if not await is_member(update, context):
        kbd = [[InlineKeyboardButton(f"{get_e()} Join Channel", url="https://t.me/kushal_igcc_chats")],
               [InlineKeyboardButton(f"{get_e()} Check Join", callback_data="check")]]
        await update.message.reply_html(f"{get_e()} <b>Please join our channel first!</b>", reply_markup=InlineKeyboardMarkup(kbd))
    else:
        await send_welcome(update, context)

@auto_recover
async def send_welcome(update, context):
    user = update.effective_user
    load = await update.message.reply_html(f"{get_e()} <b>Loading...</b>")
    photos = await context.bot.get_user_profile_photos(user_id=user.id, limit=1)
    msg = (f"{get_e()} 👋 Welcome, <a href='tg://user?id={user.id}'>{user.first_name}</a>\n\n"
           f"{get_e()} 👑 𝐎𝐰𝐧𝐞𝐫: 𝐊𝐔𝐒𝐇𝐀𝐋 𝐎𝐖𝐍𝐄𝐑\n"
           f"{get_e()} 🆔 𝐔𝐬𝐞𝐫 𝐈𝐃: <code>{user.id}</code>\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"{get_e()} ✨ 𝖴𝗌𝖾 /gen <code>BIN</code>.")
    await load.delete()
    if photos.photos:
        try: await update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=msg, parse_mode="HTML")
        except: await update.message.reply_html(msg)
    else: await update.message.reply_html(msg)

@auto_recover
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🔄 Checking...", show_alert=False)
    if await is_member(update, context):
        try: await query.message.delete()
        except: pass
        await send_welcome(update, context)
    else: await query.answer("❌ Please join @kushal_igcc_chats first!", show_alert=True)

@auto_recover
async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_member(update, context): return
    if not context.args: await update.message.reply_text("❌ Use: /gen <BIN>"); return
    msg = await update.message.reply_html(f"{get_e()} <b>Analyzing...</b>")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://lookup.binlist.net/{context.args[0][:6]}", timeout=10) as resp:
                data = await resp.json() if resp.status == 200 else {}
        except: data = {}
    cards = [f"{context.args[0][:6]}{random.randint(1000000000,9999999999)}|{random.randint(1,12):02d}|{random.randint(26,31)}|{random.randint(100,999)}" for _ in range(10)]
    res = (f"{get_e()} 𝗕𝗜𝗡 ⇾ <code>{context.args[0][:6]}</code>\n\n<code>{chr(10).join(cards)}</code>\n\n"
           f"{get_e()} 👤 𝐃𝐨𝐧𝐞 𝐛𝐲 𝐊𝐮𝐬𝐡𝐚𝐋")
    await msg.edit_text(res, parse_mode="HTML")

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    bot_app = ApplicationBuilder().token(TOKEN).request(request_config).post_init(lambda app: app.bot.set_my_commands([BotCommand("start", "Welcome"), BotCommand("gen", "Generate")])).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("gen", gen))
    bot_app.add_handler(CallbackQueryHandler(check_join, pattern="check"))
    print("Bot is running with Auto-Recovery...")
    bot_app.run_polling(drop_pending_updates=True)
