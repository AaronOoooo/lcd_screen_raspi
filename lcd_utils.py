import sys
import os

sys.path.append('./I2C_LCD_driver')
import I2C_LCD_driver

def initialize_lcd():
    try:
        lcd = I2C_LCD_driver.lcd()  # Assuming the correct class name is 'lcd'
        
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
