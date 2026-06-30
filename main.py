import logging
import random
import time
import requests
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

TOKEN = "8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo"
OWNER_NAME = "𝐊𝐔𝐒𝐇𝐀𝐋 𝐎𝐖𝐍𝐄𝐑"

logging.basicConfig(level=logging.INFO)

def luhn_checksum(card_number):
    digits = [int(d) for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return (10 - (total % 10)) % 10

def generate_cc(bin_num):
    # BIN ke saath valid random numbers
    partial = bin_num[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])
    full_card = partial + str(luhn_checksum(partial))
    cvv = str(random.randint(100, 999))
    return f"<code>{full_card}|06|2028|{cvv}</code>"

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /gen <6-digit-BIN>")
        return

    bin_input = context.args[0]
    if len(bin_input) < 6:
        await update.message.reply_text("❌ Invalid BIN! 6 digit ka BIN dalen.")
        return

    user = update.effective_user
    msg = await update.message.reply_text("🔍 Checking real-time data...")

    try:
        # Better API for accuracy
        url = f"https://lookup.binlist.net/{bin_input[:6]}"
        resp = requests.get(url, timeout=5).json()

        if 'scheme' not in resp:
            await msg.edit_text("❌ Invalid BIN! System mein nahi mila.")
            return

        bank = resp.get('bank', {}).get('name', 'Unknown')
        brand = resp.get('scheme', 'Unknown').upper()
        type_cc = resp.get('type', 'Unknown').upper()
        country = resp.get('country', {}).get('name', 'Unknown')
        flag = resp.get('country', {}).get('emoji', '🏳️')

        # CC Generation
        cards = "\n".join([generate_cc(bin_input) for _ in range(5)])

        final_text = f"""👤 <b>User:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>
<b>.gen {bin_input}</b>

╚━━━━━━「𝐊𝐔𝐒𝐇𝐀𝐋」━━━━━━╝
⚜️ 𝑰𝒏𝒑𝒖𝒕: <code>{bin_input}</code>
╚━━━━━━「 𝑪𝑪𝒔 ♻️ 」━━━━━━╝
{cards}
╚━━━━━━「 𝑫𝑬𝑻𝑨𝑰𝑳𝑺 」━━━━━━╝
⚜️ 𝑩𝒂𝒏𝒌: {bank}
⚜️ 𝑵𝒆𝒕𝒘𝒐𝒓𝒌: {brand}
⚜️ 𝑻𝒚𝒑𝒆: {type_cc}
⚜️ 𝑪𝒐𝒖𝒏𝒕𝒓𝒚: {country} {flag}
⚜️ 𝑶𝒘𝒏𝒆𝒓: {OWNER_NAME}
╚━━━━━━「𝒁𝒆𝒓𝒐𝑻𝒘𝒐𝑪𝒉𝒌」━━━━━━╝"""
        
        await msg.edit_text(final_text, parse_mode=constants.ParseMode.HTML)

    except Exception:
        await msg.edit_text("❌ Error: API Connection Failed. Try again.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("gen", gen))
    print("Bot Running...")
    app.run_polling()
