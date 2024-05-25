import sys
import os
import requests
from datetime import datetime
from time import sleep
from dotenv import load_dotenv

# Import the LCD driver module
sys.path.append('./I2C_LCD_driver')
import I2C_LCD_driver

# Load environment variables from .env file
load_dotenv()

# Load API keys and city from environment variables
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
CITY = os.getenv('CITY_NAME')
WMT_SYMBOL = "WMT"

# Construct API URLs
WEATHER_API_URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHERMAP_API_KEY}&units=imperial'
STOCK_API_URL = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={WMT_SYMBOL}&apikey={ALPHA_VANTAGE_API_KEY}'

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
def get_stock_price():
    try:
        response = requests.get(STOCK_API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        global_quote = data['Global Quote']
        price = float(global_quote['05. price'])
        price_change = float(global_quote['09. change'])
        stock_info = f"WMT: {price:.2f} ({price_change:+.2f})"
        return stock_info
    except requests.RequestException as e:
        # Handle request error
        print(f"Error fetching stock data: {e}")
        return "N/A"

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
        # Fetch stock data
        stock_str = get_stock_price()
        # Display the stock price for 15 seconds
        display_stock(lcd, stock_str)
        # Fetch weather data
        weather_str = get_weather()
        # Display the weather for 15 seconds
        display_weather(lcd, weather_str)

if __name__ == "__main__":
    main()
