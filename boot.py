from machine import UART
import time

# Set up UART1 with the desired baud rate
uart1 = UART(1, baudrate=115200, tx=17, rx=16)  # UART1 on TX=17, RX=16
print("UART1 initialized with baud rate 115200")

# Add any initialization code here
time.sleep(2)  # Optional: Delay to ensure everything is set up

# Start main.py
exec(open('main.py').read())

