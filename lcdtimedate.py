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

# Load API key and city from environment variables
API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
CITY = os.getenv('CITY_NAME')
API_URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial'

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
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        temperature = data['main']['temp']
        weather = f"{temperature:.1f} F"
        return weather
    except requests.RequestException as e:
        # Handle request error
        print(f"Error fetching weather data: {e}")
        return "N/A"

# Function to display the date on the LCD
def display_date(lcd):
    now = datetime.now()
    month_abbr = now.strftime("%b")
    date_str = f"{month_abbr} {now.day}, {now.year}"
    
    # Display the date for 40 seconds
    for _ in range(40):
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

# Function to display the weather on the LCD
def display_weather(lcd, weather_str):
    # Display the weather for 20 seconds
    for _ in range(20):
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
        # Display the date for 40 seconds
        display_date(lcd)
        # Fetch weather data
        weather_str = get_weather()
        # Display the weather for 20 seconds
        display_weather(lcd, weather_str)

if __name__ == "__main__":
    main()
