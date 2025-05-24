from machine import Pin, I2C, Timer
import utime as time
KEYS = [
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D'] ]
COLUMN_BITS = [0b01111111,0b10111111,0b11011111,0b11101111]
class KEYPAD():
    _id = -10 # static variable
    def __init__(self,i2c,addr):
        self._i2c = i2c
        self._addr = addr
        self._timer = Timer(KEYPAD._id)
        KEYPAD._id -= 1
        self._timer.init(mode=Timer.PERIODIC,
                         period=100,
                         callback=self.scan_keypad)
        self._keys = []
        
    def read(self):
        return list(self._keys)
    
    def deinit(self):
        self._timer.deinit() # stop timer
        
    def scan_keypad(self,t):
        self._keys = []
        buf = bytearray(1)
        for row in range(4): # scan each row
            # write one byte to PCF8574 (for row scanning)
            buf[0] = COLUMN_BITS[ row ]
            try:
                self._i2c.writeto(self._addr, buf)
            except OSError:
                return
            # read one byte from PCF8574
            x = self._i2c.readfrom(self._addr,1)[0] & 0xf
            if (~x & 0xf) not in [1,2,4,8]:
                # no keypress or multiple keypress
                continue
            col = -1
            # check the i-th column for key press
            for i in range(4): 
                # the key at this column is pressed
                if (x>>i) & 1 == 0:
                    col = (3-i) # save column index
                    break
            if col >= 0:
                self._keys.append( KEYS[row][col] )