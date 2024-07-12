import telebot
import re
import requests
from datetime import datetime
import logging
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode

# Initialize the bot with your Telegram Bot Token
BOT_TOKEN = '7419453703:AAEnyaVTt5hfLgG7xWKJ_i-_M_vt2KCATFs'

bot = telebot.TeleBot(BOT_TOKEN)

# API configuration
DOMAIN = 'Main.tozuck.store'
PORT = 443
ADMIN_USERNAME = 'tomk'
ADMIN_PASSWORD = 'steam'

# Set up logging
logging.basicConfig(filename='bot_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_access_token():
    url = f'https://{DOMAIN}:{PORT}/api/admin/token'
    data = {
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        logging.error(f'Error occurred while obtaining access token: {e}')
        return None

def get_user_data(access_token, username):
    url = f'https://{DOMAIN}:{PORT}/api/user/{username}'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error occurred while retrieving user data: {e}')
        return None

def calculate_remaining(user_data):
    now = datetime.now().timestamp()
    expire_time = user_data['expire']
    days_left = max(0, int((expire_time - now) / 86400))
    
    data_limit = user_data['data_limit']
    used_traffic = user_data['used_traffic']
    data_left = max(0, data_limit - used_traffic)
    
    return days_left, data_left

def extract_username_from_qr(file_path):
    try:
        img = Image.open(file_path)
        decoded_objects = decode(img)
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            print(f"Decoded data: {data}")  # For debugging
            # Check if it's a VLESS link
            if data.startswith('vless://'):
                # Extract the username from the end of the link
                match = re.search(r'#(.+)$', data)
                if match:
                    return match.group(1)
        logging.error(f'No valid VLESS link found in QR code')
    except Exception as e:
        logging.error(f'Error decoding QR code: {e}')
    return None

@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message):
    user_id = message.from_user.id
    username = None

    if message.content_type == 'text':
        vless_link = message.text
        match = re.search(r'#(.+)$', vless_link)
        if match:
            username = match.group(1)
        else:
            bot.reply_to(message, "Invalid VLESS link format.")
            logging.info(f"User {user_id} sent an invalid VLESS link")
            return
    elif message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("temp_qr.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
        username = extract_username_from_qr("temp_qr.jpg")
        if not username:
            bot.reply_to(message, "Could not extract username from QR code.")
            logging.info(f"User {user_id} sent an invalid QR code")
            return

    logging.info(f"User {user_id} requested info for username: {username}")
    
    access_token = get_access_token()
    if not access_token:
        bot.reply_to(message, "Failed to authenticate with the server.")
        logging.error("Failed to obtain access token")
        return

    user_data = get_user_data(access_token, username)
    if user_data:
        days_left, data_left = calculate_remaining(user_data)
        gb_left = data_left / (1024 * 1024 * 1024)
        response = f"Username: {username}\nDays left: {days_left}\nData left: {gb_left:.2f} GB"
        bot.reply_to(message, response)
        logging.info(f"Successfully provided info for username: {username}")
    else:
        bot.reply_to(message, f"Username '{username}' not found.")
        logging.warning(f"Username not found: {username}")

# Start the bot
if __name__ == "__main__":
    logging.info("Bot started")
    bot.polling()
