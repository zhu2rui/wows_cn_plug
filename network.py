import json

import requests
import file
from fake_useragent import UserAgent # 这个包是随机UA,需要安装,也可以不用这个

def get_player_id(name):
    '''
    通过玩家姓名去查询玩家id
    :param name: 玩家姓名 str
    :return: 玩家id str
    '''
    response_getPlayerId=requests.get('https://vortex.wowsgame.cn/api/accounts/search/{}'.format(name),headers={'User-Agent': UserAgent(verify_ssl=False).random, 'X-Requested-With': "XMLHttpRequest"})
    dict_response=json.loads(response_getPlayerId.text)
    data=dict_response.get('data')
    playerId='-1' if data is None else data[0].get('spa_id')
    return str(playerId)

def mode_to_str(mode):
    modeStr='未知模式'
    if mode=='pvp_solo':
        modeStr='随机单野'
    elif mode=='pvp':
        modeStr='随机整体'
    elif mode=='rank_solo':
        modeStr='排位单野'
    elif mode=='rank':
        modeStr='排位整体'
    elif mode == 'pvp_div2':
        modeStr = '随机两轮车'
    elif mode == 'pvp_div3':
        modeStr = '随机三轮车'
    return modeStr
def get_player_overall_performance(playerId):
    '''
    通过玩家id 去查询玩家的整体数据 包括pvp rank pve
    :param playerId:
    :return:
    '''
    url='https://vortex.wowsgame.cn/api/accounts/{}/'.format(playerId)
    #print(url)
    response = requests.get(url,headers={'User-Agent': UserAgent(verify_ssl=False).random,'X-Requested-With': "XMLHttpRequest"})
    dict_response = json.loads(response.text)
    performance_data = dict_response.get('data')
    assert performance_data is not None
    name=performance_data.get(playerId).get("name")
    statistics = performance_data.get(playerId).get("statistics")
    pvp,pvp_solo,pve,rank_solo,rank_info=None,None,None,None,None
    if statistics is not None:
        pvp = statistics.get("pvp")
        pvp_solo = statistics.get("pvp_solo")
        pve = statistics.get("pve")
        rank_solo = statistics.get("rank_solo")
        rank_info = statistics.get("rank_info")
    else:
        print('statistics is None')
    return name,pvp_solo,rank_solo
def get_ship_performance(playerId,shipId,mode):
    '''
    通过玩家id 和舰船id 获取 该玩家使用该舰船的表现数据
    :param playerId:玩家id str
    :param shipId:舰船id str
    :param mode:模式 str——pve、rank_solo、pvp、pvp_solo、pvp_div2、pvp_div3，分别对应人机、排位、随机整体、随机单野、随机二轮车、随机三轮车
    :return:
    '''
    assert mode in ['pve','rank_solo','pvp_solo','pvp_div2','pvp_div3']
    url='https://vortex.wowsgame.cn/api/accounts/{}/ships/{}/{}/'.format(playerId,shipId,mode)
    response = requests.get(url,headers={'User-Agent': UserAgent(verify_ssl=False).random, 'X-Requested-With': "XMLHttpRequest"})
    dict_response = json.loads(response.text)
    ship_performance_data = dict_response.get('data')
    assert ship_performance_data is not None
    ship_data=ship_performance_data.get(playerId).get('statistics').get(shipId)
    ship_mode_winrate_str, ship_mode_avg_dmg_str='-1','-1'
    if ship_data is not None:
        mode_data=ship_data.get(mode)
        ship_mode_wins=mode_data.get("wins")
        ship_mode_battles_count=mode_data.get("battles_count")
        ship_mode_winrate_str,ship_mode_avg_dmg_str="NA","NA"
        if ship_mode_wins is not None and ship_mode_battles_count is not None:
            ship_mode_winrate=mode_data['wins']/mode_data['battles_count']
            ship_mode_winrate_str=str(round(ship_mode_winrate*100,1))+'%'
            ship_mode_avg_dmg=mode_data['damage_dealt']/mode_data['battles_count']
            ship_mode_avg_dmg_str = str(int(ship_mode_avg_dmg))


    return ship_mode_winrate_str,ship_mode_avg_dmg_str
def get_display_data(playerName,shipId,mode,f):
    '''
    通过用户名和shipid 得到所有需要显示在界面上的数据
    :param playerName: 用户名
    :param shipId: 舰船id
    :param mode: 游戏模式
    :param f:储存舰船名称的json文件
    :return: 用户名，pvp_solo的胜率，rank_solo的胜率，舰船在对应模式的胜率，舰船在对应模式场均
    '''
    playerId = get_player_id(playerName)
    ship_level, ship_type, ship_name, ship_nation = file.shipId_to_shipName(f, shipId)
    modeStr = mode_to_str(mode)
    if playerId == '-1':
        return (playerName, ship_name, "NA", "NA", "NA", "NA", modeStr)
    name, pvp_solo, rank_solo = get_player_overall_performance(playerId)

    # 最终要显示 昵称|整体胜率 分pvp或rank|舰船|舰船胜率 分pvp或rank|舰船场均
    print(name,pvp_solo)

    if pvp_solo is not None:
        pvp_solo_battles_count=pvp_solo.get('battles_count')
        pvp_solo_wins=pvp_solo.get('wins')
        pvp_solo_winrate_str="NA"
        if pvp_solo_battles_count is not None and pvp_solo_wins is not None:
            pvp_solo_winrate = pvp_solo_wins/ pvp_solo_battles_count
            pvp_solo_winrate_str = str(round(pvp_solo_winrate * 100, 1)) + '%'

        rank_solo_battles_count = rank_solo.get('battles_count')
        rank_solo_wins = rank_solo.get('wins')
        rank_solo_winrate_str = "NA"
        if rank_solo_battles_count is not None and rank_solo_wins is not None:
            rank_solo_winrate = rank_solo_wins / rank_solo_battles_count
            rank_solo_winrate_str = str(round(rank_solo_winrate * 100, 1)) + '%'
        ship_mode_winrate_str, ship_mode_avg_dmg_str = get_ship_performance(playerId, shipId, mode)


        if ship_name=="":
            print("发现未收录船只 船只id:{},用户:{}".format(shipId,playerName))
        return (name,ship_name,pvp_solo_winrate_str,rank_solo_winrate_str,ship_mode_winrate_str,ship_mode_avg_dmg_str,modeStr)
    else:
        return (name,ship_name,"NA","NA","NA","NA",modeStr)


def getPlayerEverything_lite(userName,shipId,side):
    shipId=str(shipId)
    (name,shipName,pvp_solo_winrate_str,rank_solo_winrate_str,ship_mode_winrate_str,ship_mode_avg_dmg_str,modeStr)=get_display_data(userName, shipId,"pvp_solo", open(
        "config/ships_zh-cn.json", 'r', encoding='utf-8'))
    return (side,userName,pvp_solo_winrate_str,shipName,ship_mode_winrate_str,ship_mode_avg_dmg_str)