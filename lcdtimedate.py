import sys
import requests
from datetime import datetime
from time import sleep

sys.path.append('./I2C_LCD_driver')
import I2C_LCD_driver

# Initialize the LCD
mylcd = I2C_LCD_driver.lcd()

# Your OpenWeatherMap API key and city
API_KEY = 'YOUR_API_KEY'
CITY = 'YOUR_CITY'
API_URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial'

def get_weather():
    try:
        response = requests.get(API_URL)
        data = response.json()
        temperature = data['main']['temp']
        weather = f"{temperature:.1f} F"
        return weather
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return "N/A"

while True:
    # Show the date for 30 seconds
    now = datetime.now()
    month_abbr = now.strftime("%b")  # Abbreviated month name
    date_str = f"{month_abbr} {now.day}, {now.year}"
    
    for _ in range(30):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")  # 12-hour time format with seconds and AM/PM

        # Print to terminal window
        print(date_str.center(16))
        print(time_str.center(16))

        # Update LCD display
        mylcd.lcd_clear()
        mylcd.lcd_display_string(date_str.center(16), 1)
        mylcd.lcd_display_string(time_str.center(16), 2)

        sleep(1)

    # Show the weather for 30 seconds
    weather_str = get_weather()
    
    for _ in range(30):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")  # 12-hour time format with seconds and AM/PM

        # Print to terminal window
        print(weather_str.center(16))
        print(time_str.center(16))

        # Update LCD display
        mylcd.lcd_clear()
        mylcd.lcd_display_string(weather_str.center(16), 1)
        mylcd.lcd_display_string(time_str.center(16), 2)

        sleep(1)
