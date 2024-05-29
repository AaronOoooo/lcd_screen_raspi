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

def initialize_lcd():
    try:
        lcd = I2C_LCD_driver.lcd()
        
        # Define custom character for degree symbol
        degree_symbol = [
            0b01100,
            0b10010,
            0b10010,
            0b01100,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
        ]
        lcd.lcd_load_custom_chars([degree_symbol])
        return lcd
    except Exception as e:
        print(f"Error initializing LCD: {e}")
        sys.exit(1)

def get_weather():
    try:
        response = requests.get(WEATHER_API_URL)
        response.raise_for_status()
        data = response.json()
        
        temperature = int(data['main']['temp'])
        weather_main = data['weather'][0]['main']
        
        weather = f"{temperature}\x00F {weather_main}"
        return weather
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return "N/A"

def get_stock_price(symbol):
    STOCK_API_URL = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
    try:
        response = requests.get(STOCK_API_URL)
        response.raise_for_status()
        data = response.json()
        if 'Global Quote' not in data:
            raise KeyError("Global Quote not found in response")
        global_quote = data['Global Quote']
        price = float(global_quote['05. price'])
        price_change = float(global_quote['09. change'])
        stock_info = f"{symbol}: {price:.2f} ({price_change:+.2f})"
        return stock_info
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching stock data: {e}")
        return random.choice(positive_messages)

def display_date(lcd):
    now = datetime.now()
    month_abbr = now.strftime("%b")
    date_str = f"{month_abbr} {now.day}, {now.year}"
    
    for _ in range(30):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")

        print(date_str.center(16))
        print(time_str.center(16))

        lcd.lcd_clear()
        lcd.lcd_display_string(date_str.center(16), 1)
        lcd.lcd_display_string(time_str.center(16), 2)

        sleep(1)

def display_stock(lcd, stock_str):
    for _ in range(15):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")

        print(stock_str.center(16))
        print(time_str.center(16))

        lcd.lcd_clear()
        lcd.lcd_display_string(stock_str.center(16), 1)
        lcd.lcd_display_string(time_str.center(16), 2)

        sleep(1)

def display_weather(lcd, weather_str):
    for _ in range(15):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")

        print(weather_str.center(16))
        print(time_str.center(16))

        lcd.lcd_clear()
        lcd.lcd_display_string(weather_str.center(16), 1)
        lcd.lcd_display_string(time_str.center(16), 2)

        sleep(1)

def is_within_allowed_hours():
    now = datetime.now()
    start_time = time(8, 30)  # 8:30 AM CST
    end_time = time(15, 0)    # 3:00 PM CST
    return start_time <= now.time() <= end_time

def main():
    lcd = initialize_lcd()
    api_call_count = 0
    max_api_calls = 25
    
    start_time = datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
    end_time = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
    total_duration = (end_time - start_time).seconds
    api_call_interval = total_duration // max_api_calls  # Interval in seconds
    
    last_api_call_time = None
    
    while True:
        current_time = datetime.now()

        # Reset the API call count at the start of each day
        if current_time >= start_time + timedelta(days=1):
            api_call_count = 0
            start_time += timedelta(days=1)
            end_time += timedelta(days=1)

        display_date(lcd)

        if is_within_allowed_hours() and api_call_count < max_api_calls:
            if last_api_call_time is None or (current_time - last_api_call_time).seconds >= api_call_interval:
                stock_symbol = random.choice(stock_symbols)
                stock_str = get_stock_price(stock_symbol)
                api_call_count += 1
                last_api_call_time = current_time
            else:
                stock_str = random.choice(positive_messages)
        else:
            stock_str = random.choice(positive_messages)

        display_stock(lcd, stock_str)

        weather_str = get_weather()
        display_weather(lcd, weather_str)

if __name__ == "__main__":
    main()
