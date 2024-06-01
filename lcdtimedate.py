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

# Ensure required environment variables are set
if not all([OPENWEATHERMAP_API_KEY, ALPHA_VANTAGE_API_KEY, CITY]):
    print("Missing required environment variables.")
    sys.exit(1)

# Load data from files
POSITIVE_MESSAGES_FILE = 'positive_messages.txt'
STOCK_SYMBOLS_FILE = 'stock_symbols.txt'
LOG_FILE = 'log_lcd_screen.txt'
LAST_DELETION_FILE = 'last_deletion.txt'

# Function to load positive messages from a file
def load_positive_messages(filename):
    try:
        with open(filename, 'r') as file:
            messages = [line.strip() for line in file if line.strip()]
        return messages
    except Exception as e:
        print(f"Error loading positive messages: {e}")
        return []

# Function to load stock symbols from a file
def load_stock_symbols(filename):
    try:
        with open(filename, 'r') as file:
            symbols = [line.strip() for line in file if line.strip()]
        return symbols
    except Exception as e:
        print(f"Error loading stock symbols: {e}")
        return []

# Load positive messages and stock symbols
positive_messages = load_positive_messages(POSITIVE_MESSAGES_FILE)
stock_symbols = load_stock_symbols(STOCK_SYMBOLS_FILE)

# Function to initialize the LCD display
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

# Function to fetch weather data from OpenWeatherMap API
def get_weather():
    WEATHER_API_URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHERMAP_API_KEY}&units=imperial'
    try:
        response = requests.get(WEATHER_API_URL)
        response.raise_for_status()
        data = response.json()
        
        # Extract temperature and main weather condition
        temperature = int(data['main']['temp'])
        weather_main = data['weather'][0]['main']
        
        # Format weather information for display
        weather = f"{temperature}\x00F {weather_main}"
        return weather
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return "N/A"

# Function to fetch stock data from Alpha Vantage API
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

# Function to display the date on the LCD
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

        log_to_file(date_str, time_str)

        sleep(1)

# Function to display stock information on the LCD
def display_stock(lcd, stock_str):
    for _ in range(15):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")

        print(stock_str.center(16))
        print(time_str.center(16))

        lcd.lcd_clear()
        lcd.lcd_display_string(stock_str.center(16), 1)
        lcd.lcd_display_string(time_str.center(16), 2)

        log_to_file(stock_str, time_str)

        sleep(1)

# Function to display weather information on the LCD
def display_weather(lcd, weather_str):
    for _ in range(15):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")

        print(weather_str.center(16))
        print(time_str.center(16))

        lcd.lcd_clear()
        lcd.lcd_display_string(weather_str.center(16), 1)
        lcd.lcd_display_string(time_str.center(16), 2)

        log_to_file(weather_str, time_str)

        sleep(1)

# Function to log displayed information to a file
def log_to_file(line1, line2):
    try:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"{datetime.now()}: {line1} | {line2}\n")
    except Exception as e:
        print(f"Error logging to file: {e}")

# Function to check if current time is within allowed hours
def is_within_allowed_hours():
    now = datetime.now()
    start_time = time(8, 30)  # 8:30 AM CST
    end_time = time(15, 0)    # 3:00 PM CST
    return start_time <= now.time() <= end_time

# Function to delete the log file every two days at 2 AM CST
def delete_log_file():
    now = datetime.now()
    if os.path.exists(LAST_DELETION_FILE):
        with open(LAST_DELETION_FILE, 'r') as file:
            last_deletion_date = datetime.fromisoformat(file.read().strip())
    else:
        last_deletion_date = now - timedelta(days=3)  # Set to more than 2 days ago initially

    # Check if it's 2 AM CST and more than two days have passed since the last deletion
    if now.time() >= time(2, 0) and (now - last_deletion_date).days >= 2:
        try:
            if os.path.exists(LOG_FILE):
                os.remove(LOG_FILE)
                print("Log file deleted.")

            with open(LAST_DELETION_FILE, 'w') as file:
                file.write(now.isoformat())

        except Exception as e:
            print(f"Error deleting log file: {e}")

# Function to display the opening message
def display_opening_message(lcd):
    message_line1 = "Signally"
    message_line2 = "LCD"
    total_length = 16
    
    # Swipe in from the right to the center
    for i in range(total_length, (total_length - len(message_line1)) // 2, -1):
        lcd.lcd_clear()
        lcd.lcd_display_string(message_line1.rjust(i + len(message_line1)), 1)
        lcd.lcd_display_string(message_line2.rjust(i + len(message_line2)), 2)
        sleep(0.1)
    
    # Stay for 5 seconds
    sleep(5)
    
    # Simulate fade out by replacing characters with spaces
    for i in range(len(message_line1)):
        lcd.lcd_clear()
        lcd.lcd_display_string(" " * (i + 1) + message_line1[i + 1:], 1)
        lcd.lcd_display_string(" " * (i + 1) + message_line2[i + 1:], 2)
        sleep(0.1)

# Main function to control the program flow
def main():
    lcd = initialize_lcd()
    
    # Display the opening message with swipe in and fade out
    display_opening_message(lcd)

    api_call_count = 0
    max_api_calls = 25
    
    # Define start and end times for allowed API call period
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

        # Display the date for 30 seconds
        display_date(lcd)

        # Check if current time is within allowed hours and API call count is within the limit
        if is_within_allowed_hours() and api_call_count < max_api_calls:
            # Ensure the interval between API calls is respected
            if last_api_call_time is None or (current_time - last_api_call_time).seconds >= api_call_interval:
                stock_symbol = random.choice(stock_symbols)
                stock_str = get_stock_price(stock_symbol)
                api_call_count += 1
                last_api_call_time = current_time
            else:
                stock_str = random.choice(positive_messages)
        else:
            stock_str = random.choice(positive_messages)

        # Display the stock information or a positive message for 15 seconds
        display_stock(lcd, stock_str)

        # Fetch and display the weather information for 15 seconds
        weather_str = get_weather()
        display_weather(lcd, weather_str)

        # Delete the log file if necessary
        delete_log_file()

if __name__ == "__main__":
    main()
