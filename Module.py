import st7789
from machine import Pin
import time
BLACK = 0x0000
WHITE = 0xFFFF
RED   = 0xF800
GREEN = 0x07E0
BLUE  = 0x001F
class display():
    def __init__(self):
        self.tft = st7789.ST7789(width=128,height=160,spi_id=0,sck=18,mosi=19,dc=16,rst=17,cs=20)
        self.color_list=[0x0000,0xFFFF,0xF800,0x07E0,0x001F]
        self.tft.rotation(3)
    def clear(self):
        self.tft.fill(BLACK)
    def draw_image(self,x,y,image,size):
        num_y=0
        for j in image:
          num_x=0
          for i in j:
            self.tft.fill_rect(x+num_x*size,y+num_y*size,size,size,self.color_list[i])
            num_x+=1
          num_y += 1
class button():
    def __init__(self):
        self.up = Pin(2, Pin.IN, Pin.PULL_UP)
        self.down  = Pin(3, Pin.IN, Pin.PULL_UP)
        self.left  = Pin(4, Pin.IN, Pin.PULL_UP)
        self.right = Pin(5, Pin.IN, Pin.PULL_UP)

        self.button_a = Pin(6, Pin.IN, Pin.PULL_UP)
        self.button_b = Pin(7, Pin.IN, Pin.PULL_UP)
    def get_button(self):
       return "None"
       if up.value() == 0:
           return "UP"
       if down.value() == 0:
           return "DOWN"
       if left.value() == 0:
           return "LEFT"
       if right.value() == 0:
           return "RIGHT"
       if button_a.value() == 0:
           return "A"
       if button_b.value() == 0:
           return "B"