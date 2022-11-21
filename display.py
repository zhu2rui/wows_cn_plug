import json
import os
import threading
import time
import tkinter as tk
from itertools import cycle
from numpy import *
import keyboard
import psutil
import win32gui
import win32process
import yaml
from concurrent.futures import ThreadPoolExecutor
import file
import network


class zaWindow(tk.Tk):

    def __init__(self):
        """
        :param side: 1为显示友方数据 2为显示敌方数据
        """
        tk.Tk.__init__(self)
        self.config_yaml = file.load_config()
        self.bgList=cycle(self.config_yaml.get('bg_color_list'))
        self.bg="#000000"
        self.x_=10
        self.y_=10
        self.geometry('+{}+{}'.format(self.x_,self.y_))
        self.title("hello tkinter")
        self.wm_attributes("-topmost", True)
        # 就是点击无效
        self.wm_attributes("-disabled", True)
        self.wm_attributes("-transparentcolor", "#fffffe")
        self.attributes("-alpha",self.config_yaml.get('bg_color_transparency'))
        self.config(bg=self.bg)
        self.overrideredirect(True)
        self.previousUpdateTime=0.0
        self.dataTitle=['昵称', '总胜率', '舰船', '船胜率','船场均']
        # self.shipNameCol=['鹬','君主','东约特兰','','','','','','','','','',]
        # self.playerNameCol = ['为什么不办猛犸', 'sarfm', '墨韵线缆', '', '', '', '', '', '', '', '', '', ]
        # self.winRateCol = ['58%', '58%', '58%', '', '', '', '', '', '', '', '', '', ]
        # self.shipWinRateCol = ['59%', '59%', '59%', '', '', '', '', '', '', '', '', '', ]
        self.titleLabelList=[]
        self.dataLabelList=[]

        self.data = [['舰船', '昵称', '整体胜率', '舰船胜率']
            , ['<鹬>', '为什么不办猛犸', '58%', '59%']
            , ['<君主>', 'sarfm', '58%', '59%']
            , ['<东约特兰>', '墨韵线缆', '58%', '59%']
            , ['<犬>', '逆之强袭', '58%', '59%']
            , ['<印第安纳波利斯>', '笑死小猪', '58%', '59%']
            , ['<抹香鲸>', '的积分开发大姐夫的京东方', '58%', '59%']]
        for index,i in enumerate(self.dataTitle):
            l=tk.Label(self, text=i, font=('System', '10'), bg=self.bg,fg='yellow',width=7,anchor='w')
            l.grid(row=0,column=index,padx=4)
            self.titleLabelList.append(l)
        self.initShortKeys()
        #self.updater1(self)
        threading.Thread(target=self.updater1, args=()).start()
        self.mainloop()
    def initShortKeys(self):
        '''
        设定所有快捷键
        :return:
        '''
        keyboard.add_hotkey(self.config_yaml.get('move_right'), self.move,('right',10))
        keyboard.add_hotkey(self.config_yaml.get('move_left'), self.move, ('left', 10))
        keyboard.add_hotkey(self.config_yaml.get('move_up'), self.move, ('up', 10))
        keyboard.add_hotkey(self.config_yaml.get('move_down'), self.move, ('down', 10))
        keyboard.add_hotkey(self.config_yaml.get('change_bg'), self.change_bg)
        #keyboard.add_hotkey(y.get('hide_hotkey'), self.withdraw)
        keyboard.add_hotkey(self.config_yaml.get('quit'),os._exit,(0,))
        def deiconify_():
            #time.sleep(0.05)
            try:
                pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
                if psutil.Process(pid[-1]).name()=='WorldOfWarships64.exe':
                    self.deiconify()
                else:
                    self.withdraw()
            except Exception as e:
                print(e)
                self.withdraw()
        def withdraw_():
            try:
                pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
                if psutil.Process(pid[-1]).name() == 'WorldOfWarships64.exe':
                    self.withdraw()
            except Exception as e:
                print(e)
                self.withdraw()
        keyboard.on_press_key('tab',lambda _:deiconify_())
        keyboard.on_release_key('tab',lambda _:withdraw_())
    def change_bg(self):
        color=next(self.bgList)
        self.config(bg=color)
        for i in self.dataLabelList:
            i.config(bg=color)
        for j in self.titleLabelList:
            j.config(bg=color)
    def clear(self):
        for i in self.dataLabelList:
            i.destroy()
    def move(self,toward,distance):
        assert toward in ['up','down','left','right']
        if toward=='up':
            self.y_-=distance
        if toward=='down':
            self.y_+=distance
        if toward == 'left':
            self.x_ -= distance
        if toward == 'right':
            self.x_ += distance
        self.geometry("+{}+{}".format(self.x_,self.y_))
    def updater1(self):
        print("helloworld")
        def getShipNameByShipId(shipId):
            with open("outdated/shipName.json", "r", encoding='utf-8') as f:
                shipDict=json.load(f)
                shipName=shipDict.get(shipId)
                return "NA" if  shipName is None else shipName
        # vehiclesInfo中封装shipId,playerName,和side信息，jsonMTime作为标志 如果记录中的self.previousUpdateTime和这个时间相同，则说明已经加载过这个文件了不用再次加载
        while True:
            try:
                pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
                if psutil.Process(pid[-1]).name() != 'WorldOfWarships64.exe':
                    self.withdraw()
            except Exception as e:
                print(e)
            time.sleep(0.5)
            #从json提取游戏数据
            vehiclesInfo, jsonMTime,matchGroup = file.load_tempArenaInfo()
            #两个条件同时满足才能进入request获取数据的逻辑
            #1.json文件存在————获取到的json文件创建时间不为0（获取函数定义 如果文件不存在，会返回0.0）
            #2.json文件创建时间 与上次循环不一样（只有新json文件来的时候才进行request解析）
            if jsonMTime!=0.0 and self.previousUpdateTime != jsonMTime:

                # if matchGroup not in ["pvp","ranked"]:
                #     self.clear()
                #     continue
                #1.多线程获取每个用户的数据
                self.previousUpdateTime=jsonMTime
                futureList=[]
                with ThreadPoolExecutor(psutil.cpu_count(logical=True)) as tpe:
                    for i in vehiclesInfo:
                        futureList.append(tpe.submit(network.getPlayerEverything_lite,i.get('name'),i.get('shipId'),i.get('relation')))
                    for i in futureList:
                        i.done()
                datalist=list(map(lambda x:x.result(),futureList))
                #2.删除过期数据
                self.clear()
                def getAvgWinRate(l,mode=0):
                    """
                    获取一个list中的平均整体胜率
                    :param l:放入的list
                    :param mode：0的时候是整体胜率，1的时候是舰船胜率
                    :return: 平均整体胜率.
                    """
                    assert mode in [0,1]
                    index=2 if mode==0 else 4

                    l_=filter(lambda x:"%" in x[index],l)
                    wrList=list(map(lambda x:float(x[index][:-1]),l_))
                    return str(round(mean(wrList),1))+"%"

                def keyFn(elem):
                    if elem[2]=="NA":
                        return -1
                    else:
                        return float(elem[2][:-1])
                #3.敌我数据按照胜率排序
                datalist_allies=list(filter(lambda x:x[0]<2,datalist))
                datalist_allies.sort(key=keyFn,reverse=True)
                datalist_enemies = list(filter(lambda x: x[0] == 2, datalist))
                datalist_enemies.sort(key=keyFn, reverse=True)
                #print(getAvgWinRate(datalist_allies))

                #循环添加我方数据label
                for i_index,i in enumerate(datalist_allies):
                    for j_index,j in enumerate(i[1:]):
                        color='#ccffff'
                        if len(j)>0:
                            if j[-1]=='%':
                                try:
                                    if float(j[:-1]) >= 60:
                                        color='orange'
                                    if float(j[:-1]) < 45:
                                        color='red'
                                except Exception as e:
                                    print(e)
                        lbl = tk.Label(self,text=j if len(j)>0 else 'NA', font=('System', '10'), bg=self.bg, fg=color,width=7,anchor='w')
                        lbl.grid(row=i_index+1,column=j_index,padx=0)
                        self.dataLabelList.append(lbl)

                #添加平均数据行
                avgWinRate_allies = tk.Label(self, text=getAvgWinRate(datalist_allies), font=('System', '10'), bg=self.bg, fg='white')
                avgWinRate_allies.grid(row=1+len(datalist_allies),column=1)
                avgShipWinRate_allies = tk.Label(self, text=getAvgWinRate(datalist_allies,1), font=('System', '10'),bg=self.bg, fg='white')
                avgShipWinRate_allies.grid(row=1+len(datalist_allies),column=3)
                self.dataLabelList.append(avgWinRate_allies)
                self.dataLabelList.append(avgShipWinRate_allies)
                #添加敌我中间的隔断
                for i in range(5):
                    lbl = tk.Label(self, text="", font=('System', '10'), bg=self.bg, fg='blue')
                    lbl.grid( column=i)
                    self.dataLabelList.append(lbl)
                # 循环添加敌方数据label
                for i_index, i in enumerate(datalist_enemies):
                    for j_index, j in enumerate(i[1:]):
                        color = '#ccffff'
                        if len(j) > 0:
                            if j[-1] == '%':
                                if float(j[:-1]) > 60:
                                    color = 'orange'
                                if float(j[:-1]) < 45:
                                    color = 'red'
                        lbl = tk.Label(self, text=j if len(j)>0 else 'NA', font=('System', '10'), bg=self.bg, fg=color,width=7,anchor='w')
                        lbl.grid(row=i_index + 4+len(datalist_allies), column=j_index,padx=4)
                        self.dataLabelList.append(lbl)

                # 添加平均数据行
                avgWinRate_enemies = tk.Label(self, text=getAvgWinRate(datalist_enemies), font=('System', '10'),
                                             bg=self.bg, fg='white')
                avgWinRate_enemies.grid(row=4+len(datalist_allies)+len(datalist_enemies), column=1)
                avgShipWinRate_enemies = tk.Label(self, text=getAvgWinRate(datalist_enemies, 1),
                                                 font=('System', '10'), bg=self.bg, fg='white')
                avgShipWinRate_enemies.grid(row=4+len(datalist_allies)+len(datalist_enemies), column=3)
                self.dataLabelList.append(avgWinRate_enemies)
                self.dataLabelList.append(avgShipWinRate_enemies)



