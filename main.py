import logging
import random
import time
import requests
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"
OWNER_NAME = "🦋💸 ⃪♔‌⃟𝐊𝐔𝐒𝐇𝐀𝐋 🇴‌𝐖𝐍𝐄𝐑≛⃝❛🚩"

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def luhn_checksum(card_number):
    digits = [int(d) for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return (10 - (total % 10)) % 10

def generate_cc(bin_num):
    cards = []
    for _ in range(10):
        partial = bin_num[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        full_card = partial + str(luhn_checksum(partial))
        cvv = str(random.randint(100, 999))
        cards.append(f"<code>{full_card}|06|2026|{cvv}</code>")
    return "\n".join(cards)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"👋 Hello <a href='tg://user?id={user.id}'>{user.first_name}</a>!\n\n✨ Welcome to {OWNER_NAME}'s Generator.\nUse /gen <code>bin</code> to start."
    await update.message.reply_text(text, parse_mode=constants.ParseMode.HTML)

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /gen 413098")
        return

    user = update.effective_user
    bin_input = context.args[0]
    msg = await update.message.reply_text("🔄 <b>Generating...</b> [■□□□□] 20%", parse_mode=constants.ParseMode.HTML)
    
    time.sleep(0.5)
    await msg.edit_text("🔄 <b>Generating...</b> [■■■□□] 60%", parse_mode=constants.ParseMode.HTML)
    
    start_t = time.time()
    try:
        url = f"https://lookup.binlist.net/{bin_input[:6]}"
        resp = requests.get(url, timeout=5).json()
        bank = resp.get('bank', {}).get('name', 'Unknown')
        brand = resp.get('scheme', 'Unknown')
        type_cc = resp.get('type', 'Unknown')
        country = resp.get('country', {}).get('name', 'Unknown')
    except:
        await msg.edit_text("❌ Error: Invalid BIN!")
        return

    cc_list = generate_cc(bin_input)
    spent = round(time.time() - start_t, 2)
    
    final_text = f"""{OWNER_NAME}
<b>.gen {bin_input}</b>

╚━━━━━━「kushal」━━━━━━╝
⚜️ 𝑰𝒏𝒑𝒖𝒕: {bin_input}|rnd
╚━━━━━━「 𝑪𝑪𝒔 ♻️ 」━━━━━━╝
{cc_list}
╚━━━━━━「 𝑫𝑬𝑻𝑨𝑰𝑳𝑺 」━━━━━━╝
⚜️ 𝑩𝒊𝒏 𝑰𝒏𝒇𝒐: {bank}
⚜️ {brand.upper()} - {type_cc.upper()}
⚜️ {country}
⚜️ 𝑻𝒊𝒎𝒆 𝑺𝒑𝒆𝒏𝒕 -» {spent}'s
⚜️ 𝑮𝒆𝒏𝒆𝒓𝒂𝒅𝒐 𝑩𝒚: <a href='tg://user?id={user.id}'>{user.first_name}</a>
⚜️ 𝑶𝒘𝒏𝒆𝒓: ¥JΞŦΞЯSФЛ¥
╚━━━━━━「𝒁𝒆𝒓𝒐𝑻𝒘𝒐𝑪𝒉𝒌」━━━━━━╝"""
    
    await msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    app.run_polling()
