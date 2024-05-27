import sys
import os
import requests
from datetime import datetime, time, timedelta
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

# Load data from files
POSITIVE_MESSAGES_FILE = 'positive_messages.txt'
STOCK_SYMBOLS_FILE = 'stock_symbols.txt'

def load_positive_messages(filename):
    try:
        with open(filename, 'r') as file:
            messages = [line.strip() for line in file if line.strip()]
        return messages
    except Exception as e:
        print(f"Error loading positive messages: {e}")
        return []

def load_stock_symbols(filename):
    try:
        with open(filename, 'r') as file:
            symbols = [line.strip() for line in file if line.strip()]
        return symbols
    except Exception as e:
        print(f"Error loading stock symbols: {e}")
        return []

positive_messages = load_positive_messages(POSITIVE_MESSAGES_FILE)
stock_symbols = load_stock_symbols(STOCK_SYMBOLS_FILE)

# Construct API URLs
WEATHER_API_URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHERMAP_API_KEY}&units=imperial'

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

# Function to check if the current time is within the allowed hours
def is_within_allowed_hours():
    now = datetime.now()
    start_time = time(8, 30)  # 8:30 AM CST
    end_time = time(15, 0)    # 3:00 PM CST
    return start_time <= now.time() <= end_time

# Main function to control the program flow
def main():
    lcd = initialize_lcd()
    api_call_count = 0
    max_api_calls = 25
    last_api_call_time = None
    reset_time = datetime.now().replace(hour=8, minute=30, second=0, microsecond=0) + timedelta(days=1)

    while True:
        # Reset the API call count at the start of each new day
        if datetime.now() >= reset_time:
            api_call_count = 0
            reset_time += timedelta(days=1)
        
        # Display the date for 30 seconds
        display_date(lcd)

        # Check if the current time is within allowed hours and if we haven't exceeded the API call limit
        if is_within_allowed_hours() and api_call_count < max_api_calls:
            # Randomly choose a stock symbol
            stock_symbol = random.choice(stock_symbols)
            # Fetch stock data
            stock_str = get_stock_price(stock_symbol)
            api_call_count += 1
            last_api_call_time = datetime.now()
        else:
            stock_str = random.choice(positive_messages)

        # Display the stock price or positive message for 15 seconds
        display_stock(lcd, stock_str)

        # Fetch weather data
        weather_str = get_weather()
        # Display the weather for 15 seconds
        display_weather(lcd, weather_str)

if __name__ == "__main__":
    main()
