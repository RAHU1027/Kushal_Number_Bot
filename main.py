import random, requests, os, asyncio
from flask import Flask
from threading import Thread
from telegram import Update, constants, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is VIP Active!"

TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"
CHANNEL_ID = "@YOUR_CHANNEL_USERNAME" 

PREMIUM_EMOJIS = [
    "6120898777046847624", "6269285159774720688", "6138793380328510194", "6138595008674009570",
    "6138522591230431210", "5864127571754489150", "6269014138748408445", "6118397435338296885",
    "6138530760258228554", "4958489311726011319", "6086919156169448008", "6088958101698909879",
    "6129589660550171485", "6131847262864675499", "6131969566353395110", "6129448347536198680",
    "6131940510899638481", "6129497520616771484", "6129580830097410852", "6132043212157619800"
]

def get_e(): return f"<emoji document_id='{random.choice(PREMIUM_EMOJIS)}'>✨</emoji>"

async def is_member(update, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=update.effective_user.id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

async def post_init(application):
    await application.bot.set_my_commands([BotCommand("start", "Welcome"), BotCommand("gen", "Generate Cards")])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_member(update, context):
        kbd = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_ID.replace('@','')}"), 
                InlineKeyboardButton("✅ Check Join", callback_data="check")]]
        await update.message.reply_html(f"{get_e()} <b>Please join our channel first!</b>", reply_markup=InlineKeyboardMarkup(kbd))
    else:
        user = update.effective_user
        msg = f"{get_e()} <b>Welcome, <a href='tg://user?id={user.id}'>{user.first_name}</a>!</b>\n\n👑 𝐎𝐰𝐧𝐞𝐫: 𝐊𝐔𝐒𝐇𝐀𝐋 𝐎𝐖𝐍𝐄𝐑\n{get_e()} 𝖴𝗌𝖾 /gen <code>BIN</code>"
        await update.message.reply_html(msg)

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_member(update, context):
        await update.callback_query.answer("✅ Welcome Back!")
        await start(update, context)
    else:
        await update.callback_query.answer("❌ Please join first!", show_alert=True)

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_member(update, context):
        await update.message.reply_text("❌ Join channel to use this!")
        return
    
    bin_input = context.args[0] if context.args else None
    if not bin_input:
        await update.message.reply_text("❌ Use: /gen <BIN>")
        return

    msg = await update.message.reply_html(f"{get_e()} <b>Generating...</b>")
    for i in range(2):
        await asyncio.sleep(0.5)
        await msg.edit_text(f"{get_e()} <b>Processing...</b> [■■■■■] {50*(i+1)}%", parse_mode="HTML")

    try:
        # API Check
        url = f"https://lookup.binlist.net/{bin_input[:6]}"
        resp = requests.get(url, timeout=5)
        data = resp.json() if resp.status_code == 200 else {}
        
        bank = data.get('bank', {}).get('name', 'Unknown')
        brand = data.get('scheme', 'Unknown').upper()
        country = data.get('country', {}).get('name', 'Unknown')

        cards = []
        for _ in range(10):
            base = bin_input[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])
            full_card = base + str(random.randint(0, 9))
            month = f"{random.randint(1, 12):02d}"
            year = f"{random.randint(26, 31)}"
            cvv = f"{random.randint(100, 999)}"
            cards.append(f"{full_card}|{month}|{year}|{cvv}")
            
        result = (f"{get_e()} 𝗕𝗜𝗡 ⇾ <code>{bin_input[:6]}</code>\n{get_e()} 𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10\n\n<code>{chr(10).join(cards)}</code>\n\n"
                  f"{get_e()} 𝗜𝗻𝗳𝗼: {brand}\n{get_e()} 𝐈𝐬𝐬𝐮𝐞𝐫: {bank}\n"
                  f"{get_e()} 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country}")
        await msg.edit_text(result, parse_mode="HTML")
    except Exception as e: 
        await msg.edit_text(f"❌ Error: {str(e)}")

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == '__main__':
    # Flask thread start
    Thread(target=run_flask, daemon=True).start()
    
    # Bot start
    app_bot = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("gen", gen))
    app_bot.add_handler(CallbackQueryHandler(check_join, pattern="check"))
    app_bot.run_polling()
