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