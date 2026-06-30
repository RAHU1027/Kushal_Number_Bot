import logging
import random
import time
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Token ko environment variable se lein (Render setup)
TOKEN = os.environ.get('8772576350:AAHuWfDUGuFAHVfZtMwn-WquwxYzH_qRAUo')
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
        # 6 digit bin + 9 random digits = 15 digits
        partial = bin_num[:6] + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        check_digit = luhn_checksum(partial)
        full_card = partial + str(check_digit)
        cvv = str(random.randint(100, 999))
        cards.append(f"{full_card}|06|2026|{cvv}")
    return "\n".join(cards)

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    
    if not context.args:
        await update.message.reply_text("❌ Format galat hai! Use: `.gen 413098`")
        return

    bin_input = context.args[0]
    
    # 1. BIN Validation
    try:
        url = f"https://lookup.binlist.net/{bin_input[:6]}"
        resp = requests.get(url, timeout=5).json()
        
        if 'bank' not in resp:
            await update.message.reply_text("❌ Error: Invalid BIN! Ye BIN system mein exist nahi karta.")
            return
            
        bank = resp.get('bank', {}).get('name', 'Unknown')
        brand = resp.get('scheme', 'Unknown')
        type_cc = resp.get('type', 'Unknown')
        country = resp.get('country', {}).get('name', 'Unknown')
        flag = resp.get('country', {}).get('emoji', '🏳️')
    except:
        await update.message.reply_text("❌ Error: API check fail ho gaya, phir se koshish karein.")
        return

    # 2. Generation
    cc_list = generate_cc(bin_input)
    end_time = time.time()
    time_spent = round(end_time - start_time, 2)

    # 3. Final Formatted Output
    message = f"""{OWNER_NAME}
.gen {bin_input}

:
╚━━━━━━「kushal」━━━━━━╝
⚜️𝑰𝒏𝒑𝒖𝒕: 
{bin_input}|rnd
╚━━━━━━「 𝑪𝑪𝒔 ♻️ 」━━━━━━╝
{cc_list}
╚━━━━━━「 𝑫𝑬𝑻𝑨𝑰𝑳𝑺 」━━━━━━╝
⚜️ Bin Information:
{bank}
{brand.upper()} - {type_cc.upper()}
{country} {flag}
⚜️ 𝑻𝒊𝒎𝒆 𝑺𝒑𝒆𝒏𝒕 -» {time_spent}'s
⚜️ 𝑮𝒆𝒏𝒆𝒓𝒂𝒅𝒐 𝑩𝒚: {OWNER_NAME}
⚜️ 𝑶𝒘𝒏𝒆𝒓: ¥JΞŦΞЯSФЛ¥
╚━━━━━━「𝒁𝒆𝒓𝒐𝑻𝒘𝒐𝑪𝒉𝒌」━━━━━━╝"""

    await update.message.reply_text(message)

if __name__ == '__main__':
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable set nahi hai!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("gen", gen))
        print("Bot is ready...")
        app.run_polling()
