import sys
import os
import requests
from datetime import datetime
from time import sleep
from dotenv import load_dotenv
import random

# Import the LCD driver module
sys.path.append('./I2C_LCD_driver')
import I2C_LCD_driver

# Load environment variables from .env file
load_dotenv()

# Load API keys and city from environment variables
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
CITY = os.getenv('CITY_NAME')

# List of stock symbols
STOCK_SYMBOLS = [
    "AAPL", "ADP", "AMZN", "BDX", "BFAM", "EMBC", "GDDY", "GOOG", "GOOGL", "INTC", "K", "KLG", "META",
    "NFLX", "PEP", "SJM", "SYK", "T", "TMUS", "V", "VTI", "WBD", "DIS", "UPS", "MSFT", "MCD", "SBUX", 
    "ASH", "WMT"
]

# Construct API URLs
WEATHER_API_URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHERMAP_API_KEY}&units=imperial'

# Array of 100 two-word positive messages
positive_messages = [
    "Stay Positive", "Be Kind", "Stay Strong", "Keep Smiling", "Be Happy", "Stay Awesome", "You Rock",
    "Be Grateful", "Stay Humble", "Keep Going", "Shine Bright", "Be Brave", "Stay Focused", "Be Yourself",
    "Stay True", "Be Inspired", "Dream Big", "Stay Calm", "Be Creative", "Stay Motivated", "Keep Growing",
    "Stay Confident", "Be Resilient", "Keep Learning", "Stay Curious", "Be Adventurous", "Stay Determined",
    "Be Generous", "Stay Healthy", "Be Mindful", "Stay Balanced", "Be Optimistic", "Stay Positive", "Keep Faith",
    "Be Honest", "Stay Loyal", "Be Compassionate", "Stay Encouraged", "Be Patient", "Stay Driven", "Be Forgiving",
    "Stay Courageous", "Be Supportive", "Stay Joyful", "Be Resourceful", "Stay Inspired", "Be Fearless", "Stay Grateful",
    "Be Thoughtful", "Stay Vibrant", "Be Authentic", "Stay Kind", "Be Energetic", "Stay Persistent", "Be Flexible",
    "Stay Focused", "Be Reliable", "Stay Peaceful", "Be Cheerful", "Stay Strong", "Be Loving", "Stay Proud", "Be Hopeful",
    "Stay Enthusiastic", "Be Friendly", "Stay Trustworthy", "Be Devoted", "Stay Content", "Be Generous", "Stay Thankful",
    "Be Selfless", "Stay Bright", "Be Positive", "Stay Passionate", "Be Humble", "Stay Blissful", "Be Charitable", "Stay Brave",
    "Be Uplifting", "Stay Kindhearted", "Be Motivated", "Stay Warmhearted", "Be Sympathetic", "Stay Empathetic", "Be Forgiving",
    "Stay Joyous", "Be Understanding", "Stay Lighthearted", "Be Supportive", "Stay Hopeful", "Be Proud", "Stay Faithful", "Be Confident",
    "Stay Radiant", "Be Playful", "Stay Unique", "Be Talented"
]

# Function to initialize the LCD display
def initialize_lcd():
    try:
        lcd = I2C_LCD_driver.lcd()
        return lcd
    except Exception as e:
        # Handle initialization error
        print(f"Error initializing LCD: {e}")
        sys.exit(1)

# Function to fetch weather data from OpenWeatherMap API
def get_weather():
    try:
        response = requests.get(WEATHER_API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        temperature = data['main']['temp']
        weather = f"{temperature:.1f} F"
        return weather
    except requests.RequestException as e:
        # Handle request error
        print(f"Error fetching weather data: {e}")
        return "N/A"

# Function to fetch stock data from Alpha Vantage API
def get_stock_price(symbol):
    STOCK_API_URL = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
    try:
        response = requests.get(STOCK_API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if 'Global Quote' not in data:
            raise KeyError("Global Quote not found in response")
        global_quote = data['Global Quote']
        price = float(global_quote['05. price'])
        price_change = float(global_quote['09. change'])
        stock_info = f"{symbol}: {price:.2f} ({price_change:+.2f})"
        return stock_info
    except (requests.RequestException, KeyError) as e:
        # Handle request error or missing key error
        print(f"Error fetching stock data: {e}")
        return random.choice(positive_messages)

# Function to display the date on the LCD
def display_date(lcd):
    now = datetime.now()
    month_abbr = now.strftime("%b")
    date_str = f"{month_abbr} {now.day}, {now.year}"
    
    # Display the date for 30 seconds
    for _ in range(30):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")

        # Print to terminal window
        print(date_str.center(16))
        print(time_str.center(16))

        # Update LCD display
        lcd.lcd_clear()
        lcd.lcd_display_string(date_str.center(16), 1)
        lcd.lcd_display_string(time_str.center(16), 2)

        sleep(1)

# Function to display the stock price on the LCD
def display_stock(lcd, stock_str):
    # Display the stock price for 15 seconds
    for _ in range(15):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")

        # Print to terminal window
        print(stock_str.center(16))
        print(time_str.center(16))

        # Update LCD display
        lcd.lcd_clear()
        lcd.lcd_display_string(stock_str.center(16), 1)
        lcd.lcd_display_string(time_str.center(16), 2)

        sleep(1)

# Function to display the weather on the LCD
def display_weather(lcd, weather_str):
    # Display the weather for 15 seconds
    for _ in range(15):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")

        # Print to terminal window
        print(weather_str.center(16))
        print(time_str.center(16))

        # Update LCD display
        lcd.lcd_clear()
        lcd.lcd_display_string(weather_str.center(16), 1)
        lcd.lcd_display_string(time_str.center(16), 2)

        sleep(1)

# Main function to control the program flow
def main():
    lcd = initialize_lcd()
    
    while True:
        # Display the date for 30 seconds
        display_date(lcd)
        # Randomly choose a stock symbol
        stock_symbol = random.choice(STOCK_SYMBOLS)
        # Fetch stock data
        stock_str = get_stock_price(stock_symbol)
        # Display the stock price for 15 seconds
        display_stock(lcd, stock_str)
        # Fetch weather data
        weather_str = get_weather()
        # Display the weather for 15 seconds
        display_weather(lcd, weather_str)

if __name__ == "__main__":
    main()
