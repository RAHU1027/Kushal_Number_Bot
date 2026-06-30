import random, asyncio, aiohttp, os
from flask import Flask
from threading import Thread
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Fully Operational!"

TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"
CHANNEL_ID = "@kushal_igcc_chats"

PREMIUM_EMOJIS = [
    "6120898777046847624", "6269285159774720688", "6138793380328510194", "6138595008674009570",
    "6138522591230431210", "5864127571754489150", "6269014138748408445", "6118397435338296885",
    "6138530760258228554", "4958489311726011319", "6086919156169448008", "6088958101698909879",
    "6129589660550171485", "6131847262864675499", "6131969566353395110", "6129448347536198680",
    "6131940510899638481", "6129497520616771484", "6129580830097410852", "6132043212157619800",
    "6120898777046847624"
]

def get_e(): return f"<emoji document_id='{random.choice(PREMIUM_EMOJIS)}'>✨</emoji>"

# --- Validation Logic ---
async def is_member(update, context):
    if update.effective_chat.type != 'private': return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=update.effective_user.id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await is_member(update, context):
        kbd = [[InlineKeyboardButton(f"{get_e()} Join Channel", url="https://t.me/kushal_igcc_chats")],
               [InlineKeyboardButton(f"{get_e()} Check Join", callback_data="check")]]
        await update.message.reply_html(f"{get_e()} <b>Please join our channel first!</b>", reply_markup=InlineKeyboardMarkup(kbd))
        return

    photos = await context.bot.get_user_profile_photos(user_id=user.id, limit=1)
    msg = (f"{get_e()} 👋 Welcome, <a href='tg://user?id={user.id}'>{user.first_name}</a>\n\n"
           f"{get_e()} 👑 𝐎𝐰𝐧𝐞𝐫: 𝐊𝐔𝐒𝐇𝐀𝐋 𝐎𝐖𝐍𝐄𝐑\n"
           f"{get_e()} 🆔 𝐔𝐬𝐞𝐫 𝐈𝐃: <code>{user.id}</code>\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"{get_e()} ✨ 𝖴𝗌𝖾 /gen <code>BIN</code> 𝗍𝗈 𝗀𝖾𝗇𝖾𝗋𝖺𝗍𝖾.")
    
    if photos.photos:
        await update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=msg, parse_mode="HTML")
    else:
        await update.message.reply_html(msg)

# --- Join Check Callback ---
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await is_member(update, context):
        await query.message.delete()
        await start(update, context)
    else:
        await query.answer("❌ You haven't joined yet!", show_alert=True)

# --- Generator Logic (Expanded) ---
async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_member(update, context): return
    if not context.args: await update.message.reply_text("❌ Use /gen <BIN>"); return

    bin_input = context.args[0]
    # Animation Start
    msg = await update.message.reply_html(f"{get_e()} <b>Analyzing BIN...</b>")
    await asyncio.sleep(0.5)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://lookup.binlist.net/{bin_input[:6]}", timeout=5) as resp:
            data = await resp.json() if resp.status == 200 else {}
            
    await msg.edit_text(f"{get_e()} <b>Generating Premium Cards...</b>")
    
    cards = []
    for _ in range(10):
        base = bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        full = base + str(random.randint(0, 9))
        cards.append(f"{full}|{random.randint(1,12):02d}|{random.randint(26,31)}|{random.randint(100,999)}")
        
    result = (f"{get_e()} 𝗕𝗜𝗡 ⇾ <code>{bin_input[:6]}</code>\n\n"
              f"<code>{chr(10).join(cards)}</code>\n\n"
              f"{get_e()} 𝗜𝗻𝗳𝗼: {data.get('scheme','Unknown').upper()}\n"
              f"{get_e()} 🏦 𝐈𝐬𝐬𝐮𝐞𝐫: {data.get('bank',{}).get('name','Unknown')}\n"
              f"{get_e()} 🌍 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {data.get('country',{}).get('name','Unknown')}\n"
              f"{get_e()} 👤 𝐎𝐰𝐧𝐞𝐫: {update.effective_user.first_name}")
    
    await msg.edit_text(result, parse_mode="HTML")

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    app_bot = ApplicationBuilder().token(TOKEN).post_init(lambda app: app.bot.set_my_commands([BotCommand("start", "Welcome"), BotCommand("gen", "Generate")])).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen))
    app_bot.add_handler(CallbackQueryHandler(lambda u, c: asyncio.create_task(check_join(u, c)), pattern="check"))
    app_bot.run_polling()
