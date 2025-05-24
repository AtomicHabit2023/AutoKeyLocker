from time import sleep_ms
from machine import I2C, Pin
from i2c_lcd import I2cLcd
from i2c_keypad import KEYPAD
import uasyncio as asyncio
import ujson
#import uos

# I2C setup
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
keypads = KEYPAD(i2c, 0x21)

CODE = "345678"

class Password:
    
    def __init__(self):
        self.code_map = {str(floor * 100 + room): CODE for floor in range(1, 6) for room in range(1, 10)}
        self.load_passwords()  # Load passwords from file on startup
    
    def save_passwords(self):
        with open('passwords.json', 'w') as f:
            ujson.dump(self.code_map, f)

    def load_passwords(self):
        try:
            with open('passwords.json', 'r') as f:
                self.code_map = ujson.load(f)
        except OSError:
            print("Password file not found, using default passwords.")
    
    async def check(self):
        try:
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr('Room: ')
            lcd.move_to(6, 0)
            
            self.room_num = await self._read_input(3, display_char=True)
            if self.room_num in self.code_map:
                lcd.move_to(0, 1)
                lcd.putstr('Password: ')
                lcd.move_to(10, 1)
                
                self.room_pwd = await self._read_input(6, display_char=False)
                if self.room_pwd == self.code_map[self.room_num]:
                    self._display_message('Success')
                    return self.room_num
                else:
                    self._display_message('Failure')
                    return '000'
            else:
                return '000'
        except KeyboardInterrupt:
            for keypad in keypads:
                keypad.deinit()    
      
    async def _read_input(self, length, display_char):
        input_str = ''
        while len(input_str) < length:
            key = keypads.read()
            if len(key) == 1:
                if display_char:
                    lcd.putchar(key[0])
                else:
                    lcd.putchar('X')
                input_str += key[0]
                key.clear()
                await asyncio.sleep(0.5)
            await asyncio.sleep(0.1)  # Non-blocking sleep to allow other tasks to run
        return input_str

    def _display_message(self, message):
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(message)
        sleep_ms(3000)
        