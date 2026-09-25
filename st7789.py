from machine import Pin, SPI
import time


class ST7789:
    def __init__(
        self,
        width=128,
        height=160,
        spi_id=0,
        sck=18,
        mosi=19,
        dc=16,
        rst=17,
        cs=20,
        bl=21
    ):
        self.width = width
        self.height = height

        self.spi = SPI(
            spi_id,
            baudrate=40000000,
            polarity=0,
            phase=0,
            sck=Pin(sck),
            mosi=Pin(mosi)
        )

        self.dc = Pin(dc, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.cs = Pin(cs, Pin.OUT)

        self.bl = Pin(bl, Pin.OUT)

        self.cs.value(1)
        self.dc.value(1)
        self.bl.value(1)

        self.reset()
        self.init_display()

    # ========================================
    # 基本通信
    # ========================================

    def write_cmd(self, cmd):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes([cmd]))
        self.cs.value(1)

    def write_data(self, data):
        self.cs.value(0)
        self.dc.value(1)

        if isinstance(data, int):
            data = bytes([data])

        self.spi.write(data)

        self.cs.value(1)

    # ========================================
    # リセット
    # ========================================

    def reset(self):
        self.rst.value(1)
        time.sleep_ms(50)

        self.rst.value(0)
        time.sleep_ms(50)

        self.rst.value(1)
        time.sleep_ms(150)

    # ========================================
    # 初期化
    # ========================================

    def init_display(self):

        self.write_cmd(0x01)
        time.sleep_ms(150)

        self.write_cmd(0x11)
        time.sleep_ms(120)

        # RGB565
        self.write_cmd(0x3A)
        self.write_data(0x05)

        # Memory Access Control
        self.write_cmd(0x36)
        self.write_data(0x00)

        # Frame Rate
        self.write_cmd(0xB1)
        self.write_data(bytes([
            0x01,
            0x2C,
            0x2D
        ]))

        # Display inversion
        self.write_cmd(0x21)

        # Normal display mode
        self.write_cmd(0x13)

        # Display ON
        self.write_cmd(0x29)
        time.sleep_ms(100)

        self.fill(0x0000)

    # ========================================
    # アドレス設定
    # ========================================

    def set_window(self, x0, y0, x1, y1):

        # Column Address Set
        self.write_cmd(0x2A)

        self.write_data(bytes([
            (x0 >> 8) & 0xFF,
            x0 & 0xFF,
            (x1 >> 8) & 0xFF,
            x1 & 0xFF
        ]))

        # Row Address Set
        self.write_cmd(0x2B)

        self.write_data(bytes([
            (y0 >> 8) & 0xFF,
            y0 & 0xFF,
            (y1 >> 8) & 0xFF,
            y1 & 0xFF
        ]))

        # Memory Write
        self.write_cmd(0x2C)

    # ========================================
    # 画面全体
    # ========================================

    def fill(self, color):

        hi = (color >> 8) & 0xFF
        lo = color & 0xFF

        data = bytes([hi, lo]) * (
            self.width * self.height
        )

        self.set_window(
            0,
            0,
            self.width - 1,
            self.height - 1
        )

        self.cs.value(0)
        self.dc.value(1)

        self.spi.write(data)

        self.cs.value(1)

    # ========================================
    # 1ピクセル
    # ========================================

    def pixel(self, x, y, color):

        if x < 0 or x >= self.width:
            return

        if y < 0 or y >= self.height:
            return

        self.set_window(
            x,
            y,
            x,
            y
        )

        self.write_data(bytes([
            (color >> 8) & 0xFF,
            color & 0xFF
        ]))

    # ========================================
    # 長方形
    # ========================================

    def fill_rect(self, x, y, w, h, color):

        if w <= 0 or h <= 0:
            return

        if x < 0:
            w += x
            x = 0

        if y < 0:
            h += y
            y = 0

        if x + w > self.width:
            w = self.width - x

        if y + h > self.height:
            h = self.height - y

        if w <= 0 or h <= 0:
            return

        hi = (color >> 8) & 0xFF
        lo = color & 0xFF

        data = bytes([hi, lo]) * (w * h)

        self.set_window(
            x,
            y,
            x + w - 1,
            y + h - 1
        )

        self.cs.value(0)
        self.dc.value(1)

        self.spi.write(data)

        self.cs.value(1)

    # ========================================
    # 長方形の枠
    # ========================================

    def rect(self, x, y, w, h, color):

        self.fill_rect(x, y, w, 1, color)
        self.fill_rect(
            x,
            y + h - 1,
            w,
            1,
            color
        )

        self.fill_rect(
            x,
            y,
            1,
            h,
            color
        )

        self.fill_rect(
            x + w - 1,
            y,
            1,
            h,
            color
        )

    # ========================================
    # 横線
    # ========================================

    def hline(self, x, y, w, color):
        self.fill_rect(
            x,
            y,
            w,
            1,
            color
        )

    # ========================================
    # 縦線
    # ========================================

    def vline(self, x, y, h, color):
        self.fill_rect(
            x,
            y,
            1,
            h,
            color
        )

    # ========================================
    # 画面回転
    # ========================================

    def rotation(self, mode):

        if mode == 0:
            madctl = 0x00
            self.width = 128
            self.height = 160

        elif mode == 1:
            madctl = 0x60
            self.width = 160
            self.height = 128

        elif mode == 2:
            madctl = 0xC0
            self.width = 128
            self.height = 160

        elif mode == 3:
            madctl = 0xA0
            self.width = 160
            self.height = 128

        else:
            return

        self.write_cmd(0x36)
        self.write_data(madctl)

    # ========================================
    # バックライト
    # ========================================

    def backlight(self, on=True):

        if on:
            self.bl.value(1)
        else:
            self.bl.value(0)

    # ========================================
    # 5×7フォント
    # ========================================

    FONT = {

        "A": [
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b10001,
            0b10001
        ],

        "B": [
            0b11110,
            0b10001,
            0b10001,
            0b11110,
            0b10001,
            0b10001,
            0b11110
        ],

        "C": [
            0b01111,
            0b10000,
            0b10000,
            0b10000,
            0b10000,
            0b10000,
            0b01111
        ],

        "D": [
            0b11110,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b11110
        ],

        "E": [
            0b11111,
            0b10000,
            0b10000,
            0b11110,
            0b10000,
            0b10000,
            0b11111
        ],

        "F": [
            0b11111,
            0b10000,
            0b10000,
            0b11110,
            0b10000,
            0b10000,
            0b10000
        ],

        "G": [
            0b01111,
            0b10000,
            0b10000,
            0b10111,
            0b10001,
            0b10001,
            0b01111
        ],

        "H": [
            0b10001,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b10001,
            0b10001
        ],

        "I": [
            0b11111,
            0b00100,
            0b00100,
            0b00100,
            0b00100,
            0b00100,
            0b11111
        ],

        "J": [
            0b00111,
            0b00010,
            0b00010,
            0b00010,
            0b10010,
            0b10010,
            0b01100
        ],

        "K": [
            0b10001,
            0b10010,
            0b10100,
            0b11000,
            0b10100,
            0b10010,
            0b10001
        ],

        "L": [
            0b10000,
            0b10000,
            0b10000,
            0b10000,
            0b10000,
            0b10000,
            0b11111
        ],

        "M": [
            0b10001,
            0b11011,
            0b10101,
            0b10101,
            0b10001,
            0b10001,
            0b10001
        ],

        "N": [
            0b10001,
            0b11001,
            0b10101,
            0b10011,
            0b10001,
            0b10001,
            0b10001
        ],

        "O": [
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],

        "P": [
            0b11110,
            0b10001,
            0b10001,
            0b11110,
            0b10000,
            0b10000,
            0b10000
        ],

        "Q": [
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b10101,
            0b10010,
            0b01101
        ],

        "R": [
            0b11110,
            0b10001,
            0b10001,
            0b11110,
            0b10100,
            0b10010,
            0b10001
        ],

        "S": [
            0b01111,
            0b10000,
            0b10000,
            0b01110,
            0b00001,
            0b00001,
            0b11110
        ],

        "T": [
            0b11111,
            0b00100,
            0b00100,
            0b00100,
            0b00100,
            0b00100,
            0b00100
        ],

        "U": [
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],

        "V": [
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01010,
            0b00100
        ],

        "W": [
            0b10001,
            0b10001,
            0b10001,
            0b10101,
            0b10101,
            0b11011,
            0b10001
        ],

        "X": [
            0b10001,
            0b10001,
            0b01010,
            0b00100,
            0b01010,
            0b10001,
            0b10001
        ],

        "Y": [
            0b10001,
            0b10001,
            0b01010,
            0b00100,
            0b00100,
            0b00100,
            0b00100
        ],

        "Z": [
            0b11111,
            0b00001,
            0b00010,
            0b00100,
            0b01000,
            0b10000,
            0b11111
        ],

        "0": [
            0b01110,
            0b10001,
            0b10011,
            0b10101,
            0b11001,
            0b10001,
            0b01110
        ],

        "1": [
            0b00100,
            0b01100,
            0b00100,
            0b00100,
            0b00100,
            0b00100,
            0b01110
        ],

        "2": [
            0b01110,
            0b10001,
            0b00001,
            0b00010,
            0b00100,
            0b01000,
            0b11111
        ],

        "3": [
            0b11110,
            0b00001,
            0b00001,
            0b01110,
            0b00001,
            0b00001,
            0b11110
        ],

        "4": [
            0b00010,
            0b00110,
            0b01010,
            0b10010,
            0b11111,
            0b00010,
            0b00010
        ],

        "5": [
            0b11111,
            0b10000,
            0b10000,
            0b11110,
            0b00001,
            0b00001,
            0b11110
        ],

        "6": [
            0b01110,
            0b10000,
            0b10000,
            0b11110,
            0b10001,
            0b10001,
            0b01110
        ],

        "7": [
            0b11111,
            0b00001,
            0b00010,
            0b00100,
            0b01000,
            0b01000,
            0b01000
        ],

        "8": [
            0b01110,
            0b10001,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b01110
        ],

        "9": [
            0b01110,
            0b10001,
            0b10001,
            0b01111,
            0b00001,
            0b00001,
            0b01110
        ],

        " ": [
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00000
        ],

        "!": [
            0b00100,
            0b00100,
            0b00100,
            0b00100,
            0b00100,
            0b00000,
            0b00100
        ],

        ".": [
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00110,
            0b00110
        ],

        "-": [
            0b00000,
            0b00000,
            0b00000,
            0b11111,
            0b00000,
            0b00000,
            0b00000
        ]
    }

    # ========================================
    # 1文字描画
    # ========================================

    def char(self, char, x, y, color, scale=1):

        char = char.upper()

        if char not in self.FONT:
            return

        bitmap = self.FONT[char]

        for row in range(7):

            line = bitmap[row]

            for col in range(5):

                if line & (1 << (4 - col)):

                    if scale == 1:
                        self.pixel(
                            x + col,
                            y + row,
                            color
                        )

                    else:
                        self.fill_rect(
                            x + col * scale,
                            y + row * scale,
                            scale,
                            scale,
                            color
                        )

    # ========================================
    # 文字列描画
    # ========================================

    def text(
        self,
        text,
        x,
        y,
        color,
        scale=1,
        spacing=1
    ):

        start_x = x

        for char in text:

            # 改行
            if char == "\n":
                y += 8 * scale
                x = start_x
                continue

            self.char(
                char,
                x,
                y,
                color,
                scale
            )

            # 5px + spacing
            x += (5 + spacing) * scale