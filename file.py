import json
import os
import yaml
import psutil


def getWowsReplayPath():
    '''
    通过游戏进程名获得游戏 replay文件夹所在的路径
    :return: string replay文件夹所在的路径
    '''
    wowsReplayPath=""
    for proc in psutil.process_iter ():
        n=proc.name()
        if n=='WorldOfWarships64.exe':
            wowsReplayPath=proc.exe()[:-21]+'..\\..\\..\\replays'
            break
    return wowsReplayPath
def load_tempArenaInfo():
    """
    按照yaml config中的replay路径地址加载 tempArenaInfo.json文件
    :return:dict 实例化后的战斗信息,文件创建时间
    """
    # with open("config.yaml",'r',encoding='utf-8') as f:
    #     y=yaml.full_load(f)
        #path="{}\\tempArenaInfo.json".format(y.get('replayPath'))
    path = "{}\\tempArenaInfo.json".format(getWowsReplayPath())
    if os.path.exists(path):
        #在界面上显示正在载入
        #print("ok")
        try:
            with open(path,'r',encoding='utf-8') as f_:
                tempArenaInfo = json.load(f_)
                return tempArenaInfo['vehicles'], os.path.getmtime(path),tempArenaInfo['matchGroup']
        except OSError:
            print("fuck")
            return load_tempArenaInfo()
    else:
        #在界面上显示未进入游戏
        print("没找到json文件")
        return None,0.0,None
def shipId_to_shipName(f,shipId):
    '''
    输入shipId 在ships_zh-cn.json中查询shipName并返回
    :param shipId: 舰船id str
    :return: 舰船名 str
    '''
    assert type(shipId)==str
    ships=json.load(f)
    ship=ships.get(shipId)
    ship_level,ship_type,ship_name,ship_nation="","","",""
    if ship is not None:
        ship_level=ship.get("tier")
        ship_type = ship.get("type")
        ship_name = ship.get("name")
        ship_nation = ship.get("nation")

    return ship_level,ship_type,ship_name,ship_nation
def load_config():
    with open("config/config.yaml", 'r', encoding='utf-8') as f:
        y = yaml.full_load(f)
        return y