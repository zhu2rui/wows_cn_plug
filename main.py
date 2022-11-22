import os
import time

import display

if __name__ == '__main__':
    #把数据来源的网站 强制走直连，以免用vpn时候报错
    os.environ['NO_PROXY'] = 'wowsgame.cn'
    if not time.time() < 1658332800:
        w = display.zaWindow().mainloop()
