
import telebot
import os
import logging
import requests
import yfinance as yf  
import matplotlib.pyplot as plt
import io
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiException

# Set up logging
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# Get API token from environment variable
API_TOKEN = os.environ.get("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN environment variable is not set.")

# Initialize bot
bot = telebot.TeleBot(API_TOKEN)

# Channel and support details
CHANNEL_ID = '-1002460204159'  
CHANNEL_USERNAME = "MyPyTel_MKbot"  
SUPPORT_USERNAME = "TIMCN"  

# Function to check if the user is a member of the channel
def is_member(user_id):
    try:
        user_info = bot.get_chat_member(CHANNEL_ID, user_id)
        return user_info.status in ["administrator", "creator", "member"]
    except ApiException as e:
        logging.error(f"Error checking membership for user {user_id}: {e}")
        return False  

# Function to fetch Bitcoin price using CoinGecko API
def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if "bitcoin" in data and "usd" in data["bitcoin"]:
            return f"Bitcoin Price: ${data['bitcoin']['usd']}"
        else:
            logging.error(f"Unexpected response format: {data}")
            return "Unexpected response format from CoinGecko."
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Bitcoin price: {e}")
        return "Failed to fetch Bitcoin price. Please try again later."

# Function to fetch Tesla stock price using yfinance
def get_tesla_price():
    try:
        tsla = yf.Ticker("TSLA")
        price = tsla.history(period="1d")["Close"].iloc[-1]  
        return f"Tesla Stock Price: ${price:.2f}"
    except Exception as e:
        logging.error(f"Error fetching Tesla price: {e}")
        return "Failed to fetch Tesla price. Please try again later."
    

# Function to get and send Bitcoin price chart
def get_bitcoin_chart(chat_id):
    try:
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(period="1mo")  # Last 1 month

        if hist.empty:
            bot.send_message(chat_id, "No Bitcoin price data available.")
            return

        # Plot the Bitcoin price chart
        plt.figure(figsize=(8, 4))
        plt.plot(hist.index, hist["Close"], label="BTC Price", color="orange")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.title("Bitcoin (BTC) Price Chart - Last Month")
        plt.legend()
        plt.grid()

        # Save plot to a buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        # Send the image
        bot.send_photo(chat_id, buffer)
        plt.close()

    except Exception as e:
        bot.send_message(chat_id, f"Failed to fetch Bitcoin price chart.\nError: {e}")


# Function to fetch and plot gold price
def get_gold_chart(chat_id):
    try:
        gold = yf.Ticker("GC=F")  # "GC=F" is the ticker symbol for Gold Futures
        data = gold.history(period="1mo")  # Fetch last 1 month's data

        if data.empty:
            bot.send_message(chat_id, "No gold price data available.")
            return

        plt.figure(figsize=(8, 4))
        plt.plot(data.index, data["Close"], marker="o", linestyle="-", color="gold", label="Gold Price")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.title("Gold Price Trend (Last 1 Month)")
        plt.legend()
        plt.grid()

        # Save plot to a buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        # Send the image
        bot.send_photo(chat_id, buffer)
        plt.close()

    except Exception as e:
        bot.send_message(chat_id, f"Failed to fetch gold price chart.\nError: {e}")

# Start command
@bot.message_handler(commands=["start"])
def start_command(message):
    markup = InlineKeyboardMarkup()
    services_button = InlineKeyboardButton(text="دسترسی به خدمات ما", callback_data="services")
    support_button = InlineKeyboardButton(text="ارتباط با ما", url=f"https://t.me/{SUPPORT_USERNAME}")
    
    markup.add(services_button)
    markup.add(support_button)

    bot.send_message(
        message.chat.id,
        "به بات ما خوش آمدید! 🎉\n\n"
        "با کلیک روی هریک از دکمه های زیر به خدمات ما دسترسی پیدا می کنید.\n"
        " ",
        reply_markup=markup,
    )

# Help command
@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Use /start to access services. You must be a member of our channel to proceed."
    )

# Callback query handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "services":
        if is_member(call.from_user.id):
            markup = InlineKeyboardMarkup()
            service_a_button = InlineKeyboardButton(text="دریافت قیمت بیتکوین", callback_data="service_a")
            service_b_button = InlineKeyboardButton(text="دریافت قیمت سهام تسلا", callback_data="service_b")
            service_c_button = InlineKeyboardButton(text="چارت تغییرات بیتکوین", callback_data="service_c")  
            service_d_button = InlineKeyboardButton(text="چارت تغییرات قیمت طلا", callback_data="service_d")  # New button for Gold Chart

            markup.add(service_a_button)
            markup.add(service_b_button)
            markup.add(service_c_button)
            markup.add(service_d_button)

            bot.send_message(
                call.message.chat.id,
                "✅   شما عضو کانال هستید و می توانید به خدمات ما دسترسی داشته باشید.  \n   لطفا یکی از خدمات زیر را انتخاب کنید.",
                reply_markup=markup,
            )
        else:
            markup = InlineKeyboardMarkup()
            join_button = InlineKeyboardButton(text="Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
            markup.add(join_button)

            bot.send_message(
                call.message.chat.id,
                "❌ شما عضو کانال ما نیستید.\n"
                " لطفا برای دسترسی به خدمات ما عضو کانال ما شوید. ",
                reply_markup=markup,
            )

    elif call.data == "service_a":
        bot.send_message(call.message.chat.id, get_bitcoin_price())
    elif call.data == "service_b":
        bot.send_message(call.message.chat.id, get_tesla_price())
    elif call.data == "service_c":
        get_bitcoin_chart(call.message.chat.id)
    elif call.data == "service_d":  # New case for Gold price chart
        get_gold_chart(call.message.chat.id)

# Handle all other messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    bot.send_message(
        message.chat.id,
        "Sorry, I don't understand that command. Use /start to see available options.",
    )

# Start the bot
bot.infinity_polling()