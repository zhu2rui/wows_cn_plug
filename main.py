import os
import time

import display

if __name__ == '__main__':
    os.environ['NO_PROXY'] = 'wowsgame.cn'
    if not time.time() < 1658332800:
        w = display.zaWindow().mainloop()
                    