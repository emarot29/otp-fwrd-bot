import requests
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import re
import pickle
import os

# Configuration
IVASMS_EMAIL = "emarotkhondkar03@gmail.com"
IVASMS_PASSWORD = "711332ee"
TELEGRAM_BOT_TOKEN = "8309700958:AAGtPo-V5McghxzyKXV7_b739jPMruKfhV4"
TELEGRAM_GROUP_ID = "-1003042524817"

# Sent messages store
SENT_MESSAGES_FILE = "sent_messages.pkl"

# Mask number
def mask_number(number):
    if len(number) > 7:
        return number[:5] + "**" + number[-3:]
    return number

# Extract OTP
def extract_otp(message):
    match = re.search(r'\b\d{4,8}\b', message)
    return match.group(0) if match else "N/A"

# Load sent messages
def load_sent_messages():
    if os.path.exists(SENT_MESSAGES_FILE):
        with open(SENT_MESSAGES_FILE, "rb") as f:
            return pickle.load(f)
    return set()

# Save sent messages
def save_sent_messages(sent_messages):
    with open(SENT_MESSAGES_FILE, "wb") as f:
        pickle.dump(sent_messages, f)

# Fetch SMS from IVASMS
def fetch_sms():
    url = "https://www.ivasms.com/api/sms"
    try:
        response = requests.post(url, json={
            "email": IVASMS_EMAIL,
            "password": IVASMS_PASSWORD
        })
        data = response.json()
        return data.get("messages", [])
    except Exception as e:
        print("Error fetching SMS:", e)
        return []

# Send OTP to Telegram Group
def send_to_telegram(sms_data):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    sent_messages = load_sent_messages()

    for sms in sms_data:
        sms_id = sms.get("id") or (sms.get("number", "") + sms.get("message", ""))
        if sms_id in sent_messages:
            continue

        sent_messages.add(sms_id)

        service = sms.get("service", "Unknown Service")
        country = sms.get("country", "Unknown Country")
        flag = sms.get("flag", "🌍")
        number = mask_number(sms.get("number", "+8801XXXXXXX"))
        full_message = sms.get("message", "")
        otp = extract_otp(full_message)
        time_received = datetime.now().strftime("%H:%M")

        message = f"""
💥 *New OTP received* 💥
🔗 *Service* ➡️ {service}
🌍 *Country* ➡️ {flag} {country}
☎️ *Number* ➡️ {number}
🔐 *OTP* ➡️ {otp}
📝 *Full message* ➡️ {full_message}
⏰ *Received at* ➡️ {time_received}
"""

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔗 Number Source", url="https://t.me/Emarotkhondokar")]]
        )

        try:
            bot.send_message(chat_id=TELEGRAM_GROUP_ID, text=message, parse_mode='Markdown', reply_markup=keyboard)
        except Exception as e:
            print("Error sending to Telegram:", e)

    save_sent_messages(sent_messages)

# Run the Bot
if name == "main":
    sms_data = fetch_sms()
    if sms_data:
        send_to_telegram(sms_data)
    else:
        print("No new messages to send.")