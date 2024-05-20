import sys
sys.path.append('./I2C_LCD_driver')
import I2C_LCD_driver  # Import the module
from datetime import datetime
from time import sleep

mylcd = I2C_LCD_driver.lcd()

while True:
    # Get current date and time
    now = datetime.now()
    month_abbr = now.strftime("%b")  # Abbreviated month name
    date_str = f"{month_abbr} {now.day}, {now.year}"
    time_str = now.strftime("%I:%M:%S %p")  # 12-hour time format with seconds and AM/PM

    # Print to terminal window
    print(date_str.center(16))
    print(time_str.center(16))

    # Update LCD display
    mylcd.lcd_clear()
    mylcd.lcd_display_string(date_str.center(16), 1)
    mylcd.lcd_display_string(time_str.center(16), 2)

    # Sleep for a while before updating again
    sleep(1)
