import telebot
import time
import requests
import os
import yt_dlp
import subprocess

# Bot Token & Channel Username
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_USERNAME = "YOUR_CHANNEL_USERNAME"  # Without @

# exe.io API Key
EXE_IO_API = "2609d5781b9a3698ef25348ca37403479c55569a"

bot = telebot.TeleBot(BOT_TOKEN)

# Function to check if the user is in the channel
def is_user_joined(user_id):
    try:
        chat_member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False

# Function to update yt-dlp
def update_yt_dlp():
    try:
        subprocess.run(["yt-dlp", "-U"], capture_output=True, text=True)
    except Exception as e:
        print(f"Error updating yt-dlp: {e}")

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    # Force join check
    if not is_user_joined(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        join_button = telebot.types.InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
        check_button = telebot.types.InlineKeyboardButton("✅ Check", callback_data="check")
        markup.add(join_button)
        markup.add(check_button)

        bot.send_message(user_id, "You must join our channel to use this bot!", reply_markup=markup)
    else:
        ask_for_link(user_id)

# Callback for "Check" button
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_subscription(call):
    user_id = call.from_user.id
    
    if is_user_joined(user_id):
        bot.send_message(user_id, "✅ You have joined! Please wait...")
        time.sleep(2)
        ask_for_link(user_id)
    else:
        start(call.message)  # Resend the join message

# Ask user for the social media link
def ask_for_link(user_id):
    bot.send_message(user_id, "Send me the social media link to get the short download link.")

# Function to download video & generate short link
def download_and_shorten(url):
    try:
        # yt-dlp options to extract direct download link
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'noplaylist': True,
            'extract_flat': False,
            'skip_download': True,
            'force_generic_extractor': False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info.get("url", None)  # Extract direct video URL
        
        if not download_url:
            return None
        
        # Generate short link
        short_link = f"https://exe.io/st?api={EXE_IO_API}&url={download_url}"
        return short_link

    except Exception as e:
        print(f"Error: {e}")
        return None

# Process user's link
@bot.message_handler(func=lambda message: message.text.startswith("http"))
def process_link(message):
    user_id = message.from_user.id
    original_link = message.text

    bot.send_message(user_id, "⏳ Processing your request, please wait...")

    short_link = download_and_shorten(original_link)
    
    if short_link:
        markup = telebot.types.InlineKeyboardMarkup()
        download_button = telebot.types.InlineKeyboardButton("📥 Download Content", url=short_link)
        markup.add(download_button)

        bot.send_message(user_id, "Here is your download link:", reply_markup=markup)
    else:
        bot.send_message(user_id, "❌ Failed to process the link. Please try another.")

# Start polling
update_yt_dlp()  # Auto-update yt-dlp on startup
bot.infinity_polling()
