# lcd_screen_raspi

Overview of What This Code Does:
Imports and Setup:

Imports necessary modules.
Loads environment variables and ensures they are set.
Data Loading:

Loads positive messages and stock symbols from files.
API Interaction:

Fetches weather data from OpenWeatherMap API.
Fetches stock prices from Alpha Vantage and RapidAPI.
LCD Display Functions:

Functions to display date, stock information, and weather on an LCD screen.
Initializes the LCD display and sets up custom characters.
Logging and Deletion:

Logs displayed information to a file.
Deletes the log file every two days at 2 AM CST.
Display Loop:

Main loop to update the display with date, stock prices, and weather at appropriate intervals.
Execution:

Entry point to run the main function when the script is executed.

File structure:
    lcd_screen_raspi/
    |-- I2C_LCD_driver/
    |   |-- I2C_LCD_driver.py
    |-- lcd_utils.py
    |-- lcdtimedate.py
    |-- positive_messages.txt
    |-- stock_symbols.txt
    |-- log_lcd_screen.txt
    |-- last_deletion.txt
    |-- stock_cache.json
    |-- .env

UPDATE 06-10-2024
Alpha Vantage API Calls:

Calls are scheduled between 8:30 AM to 1:00 PM CST.
No more than 25 calls are made in this time frame.
Each call is spaced by at least 20 minutes.
RapidAPI Calls:

Calls are scheduled between 1:10 PM to 10:00 PM CST.
No more than 30 calls are made in this time frame.
Each call is spaced by at least 20 minutes.
Positive Messages:

Positive messages are displayed for 25 seconds to fill in time where no stock API call is due.
The display cycle ensures a positive message is shown if the stock API calls are within the cooldown period.
Weather API Calls:

The weather API call scheduling remains unchanged to respect the original code's rate-limiting logic.