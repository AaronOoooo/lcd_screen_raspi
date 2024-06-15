# Signally LCD / Aaron O Hall
import sys
import os
import requests
from datetime import datetime, time, timedelta
from time import sleep
from dotenv import load_dotenv
import random
import json

# Import the LCD driver module
sys.path.append('./I2C_LCD_driver')
import I2C_LCD_driver

# Load environment variables from .env file
load_dotenv()

# Load API keys and city from environment variables
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
CITY = os.getenv('CITY_NAME')

# Ensure required environment variables are set
if not all([OPENWEATHERMAP_API_KEY, ALPHA_VANTAGE_API_KEY, RAPIDAPI_KEY, CITY]):
    print("Missing required environment variables.")
    sys.exit(1)

# Load data from files
POSITIVE_MESSAGES_FILE = 'positive_messages.txt'
WELLNESS_MESSAGES_FILE = 'wellness_messages.txt'
HISTORICAL_MESSAGES_FILE = 'historical_messages.txt'
STOCK_SYMBOLS_FILE = 'stock_symbols.txt'
LOG_FILE = 'log_lcd_screen.txt'
HTML_LOG_FILE = 'log_lcd_screen.html'
LAST_DELETION_FILE = 'last_deletion.txt'
STOCK_CACHE_FILE = 'stock_cache.json'

# Function to load messages from a file
def load_messages(filename):
    try:
        with open(filename, 'r') as file:
            messages = [line.strip() for line in file if line.strip()]
        return messages
    except Exception as e:
        print(f"Error loading messages from {filename}: {e}")
        return []

# Load positive, wellness, and historical messages
positive_messages = load_messages(POSITIVE_MESSAGES_FILE)
wellness_messages = load_messages(WELLNESS_MESSAGES_FILE)
historical_messages = load_messages(HISTORICAL_MESSAGES_FILE)

# Function to load stock symbols from a file
def load_stock_symbols(filename):
    try:
        with open(filename, 'r') as file:
            symbols = [line.strip() for line in file if line.strip()]
        return symbols
    except Exception as e:
        print(f"Error loading stock symbols: {e}")
        return []

# Load stock symbols
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
def get_stock_price_alpha_vantage(symbol):
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
        stock_info = f"{symbol}: {price:.2f} {price_change:+.2f}"
        return stock_info
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching stock data: {e}")
        return random.choice(positive_messages)

# Function to fetch stock data from RapidAPI with caching and rate limiting
def get_stock_price_rapidapi(symbol):
    now = datetime.now()
    stock_cache = load_stock_cache()
    
    # Check if the stock data is in the cache and is still valid
    if symbol in stock_cache and (now - datetime.fromisoformat(stock_cache[symbol]['timestamp'])).seconds < 1800:
        return stock_cache[symbol]['stock_info']

    url = f"https://yahoo-finance127.p.rapidapi.com/price/{symbol}"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "yahoo-finance127.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        price = data['regularMarketPrice']['raw']
        price_change = data['regularMarketChange']['raw']
        stock_info = f"{symbol}: {price:.2f} {price_change:+.2f}"
        
        # Cache the stock data
        stock_cache[symbol] = {
            'stock_info': stock_info,
            'timestamp': now.isoformat()
        }
        save_stock_cache(stock_cache)
        
        return stock_info
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching stock data from RapidAPI: {e}")
        return random.choice(positive_messages)

# Function to load stock cache from a file
def load_stock_cache():
    try:
        if os.path.exists(STOCK_CACHE_FILE):
            with open(STOCK_CACHE_FILE, 'r') as file:
                return json.load(file)
        else:
            return {}
    except Exception as e:
        print(f"Error loading stock cache: {e}")
        return {}

# Function to save stock cache to a file
def save_stock_cache(cache):
    try:
        with open(STOCK_CACHE_FILE, 'w') as file:
            json.dump(cache, file)
    except Exception as e:
        print(f"Error saving stock cache: {e}")

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
    for _ in range(30):  # Display for 30 seconds
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

# Function to display positive or wellness messages on the LCD
def display_message(lcd, message):
    for _ in range(25):  # Display for 25 seconds
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")

        print(message.center(16))
        print(time_str.center(16))

        lcd.lcd_clear()
        lcd.lcd_display_string(message.center(16), 1)
        lcd.lcd_display_string(time_str.center(16), 2)

        log_to_file(message, time_str)

        sleep(1)

# Function to display historical messages on the LCD
def display_historical_message(lcd, message):
    lines = message.split('\n')
    if len(lines) == 2:
        line1, line2 = lines
        for _ in range(25):  # Display for 25 seconds
            now = datetime.now()
            time_str = now.strftime("%I:%M:%S %p")

            print(f"Displaying historical message: {line1} | {line2}")  # Debug: Print message being displayed

            lcd.lcd_clear()
            lcd.lcd_display_string(line1.center(16), 1)
            lcd.lcd_display_string(line2.center(16), 2)

            log_to_file(f"{line1} | {line2}", time_str)

            sleep(1)
    else:
        print(f"Invalid historical message format: {message}")

# Function to log displayed information to a file
def log_to_file(line1, line2):
    try:
        # Log to text file
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"{datetime.now()}: {line1} | {line2}\n")
        
        # Log to HTML file
        ensure_html_format()
        
        log_entry = f"<div class='log-entry'><strong>{datetime.now()}</strong>: {line1} | {line2}</div>\n"
        
        with open(HTML_LOG_FILE, 'r') as html_file:
            content = html_file.read()
        
        new_content = content.replace("</div></body></html>", log_entry + "</div></body></html>")
        
        with open(HTML_LOG_FILE, 'w') as html_file:
            html_file.write(new_content)
        
    except Exception as e:
        print(f"Error logging to file: {e}")

# Function to ensure the HTML file has a proper structure
def ensure_html_format():
    now = datetime.now()
    created_date = now.strftime("%B %d, %Y | %I:%M %p")
    
    if not os.path.exists(HTML_LOG_FILE):
        with open(HTML_LOG_FILE, 'w') as html_file:
            with open('style_log_template.html', 'r') as template_file:
                template = template_file.read()
            html_content = template.replace("{created_date}", created_date).replace("{log_entries}", "")
            html_file.write(html_content)
    else:
        with open(HTML_LOG_FILE, 'r') as html_file:
            content = html_file.read()
        if not content.startswith("<!DOCTYPE html>"):
            with open(HTML_LOG_FILE, 'w') as html_file:
                with open('style_log_template.html', 'r') as template_file:
                    template = template_file.read()
                html_content = template.replace("{created_date}", created_date).replace("{log_entries}", "")
                html_file.write(html_content)
        if not content.endswith("</div></body></html>"):
            with open(HTML_LOG_FILE, 'a') as html_file:
                html_file.write("</div></body></html>\n")


# Function to check if current time is within Alpha Vantage API call hours
def is_within_alpha_vantage_hours():
    now = datetime.now().time()
    start_time = time(8, 30)  # 8:30 AM CST
    end_time = time(13, 0)    # 1:00 PM CST
    return start_time <= now <= end_time

# Function to check if current time is within RapidAPI call hours
def is_within_rapidapi_hours():
    now = datetime.now().time()
    start_time = time(13, 10)  # 1:10 PM CST
    end_time = time(22, 0)     # 10:00 PM CST
    return start_time <= now <= end_time

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
            if os.path.exists(HTML_LOG_FILE):
                os.remove(HTML_LOG_FILE)
                print("HTML log file deleted.")

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

    # Simulate fade out by replacing characters with spaces, keeping text centered
    for i in range(len(message_line1)):
        lcd.lcd_clear()
        fade_line1 = message_line1[:len(message_line1) - i].ljust(len(message_line1))
        fade_line2 = message_line2[:len(message_line2) - i].ljust(len(message_line2))
        lcd.lcd_display_string(fade_line1.center(total_length), 1)
        lcd.lcd_display_string(fade_line2.center(total_length), 2)
        sleep(0.1)

# Main function that runs the display loop
def main():
    lcd = initialize_lcd()
    display_opening_message(lcd)

    alpha_vantage_call_count = 0
    rapidapi_call_count = 0
    max_alpha_vantage_calls = 25
    max_rapidapi_calls = 30
    alpha_vantage_interval = 20 * 60  # 20 minutes in seconds
    rapidapi_interval = 20 * 60  # 20 minutes in seconds
    last_alpha_vantage_call_time = None
    last_rapidapi_call_time = None

    while True:
        current_time = datetime.now()
        display_date(lcd)

        # Reset API call counts at midnight
        if current_time.hour == 0 and current_time.minute == 0:
            alpha_vantage_call_count = 0
            rapidapi_call_count = 0

        if is_within_alpha_vantage_hours() and alpha_vantage_call_count < max_alpha_vantage_calls:
            if last_alpha_vantage_call_time is None or (current_time - last_alpha_vantage_call_time).seconds >= alpha_vantage_interval:
                stock_symbol = random.choice(stock_symbols)
                stock_str = get_stock_price_alpha_vantage(stock_symbol)
                alpha_vantage_call_count += 1
                last_alpha_vantage_call_time = current_time
                display_stock(lcd, stock_str)
            else:
                message = random.choice(positive_messages + wellness_messages)
                display_message(lcd, message)
        elif is_within_rapidapi_hours() and rapidapi_call_count < max_rapidapi_calls:
            if last_rapidapi_call_time is None or (current_time - last_rapidapi_call_time).seconds >= rapidapi_interval:
                stock_symbol = random.choice(stock_symbols)
                stock_str = get_stock_price_rapidapi(stock_symbol)
                rapidapi_call_count += 1
                last_rapidapi_call_time = current_time
                display_stock(lcd, stock_str)
            else:
                message = random.choice(positive_messages + wellness_messages)
                display_message(lcd, message)
        else:
            message = random.choice(positive_messages + wellness_messages + historical_messages)
            print(f"Selected message: {message}")  # Debug: Print selected message
            if message in historical_messages:
                display_historical_message(lcd, message)
            else:
                display_message(lcd, message)

        weather_str = get_weather()
        display_weather(lcd, weather_str)
        delete_log_file()


# Entry point of the program
if __name__ == "__main__":
    main()
