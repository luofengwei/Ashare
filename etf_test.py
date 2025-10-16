import random
import math
#股市行情数据获取和作图 -2
from  Ashare import *          #股票数据库    https://github.com/mpquant/Ashare
from  MyTT import *            #myTT麦语言工具函数指标库  https://github.com/mpquant/MyTT

def get_real_data(num_days):
    df=get_price('sh510760',frequency='1d',count=num_days)      #默认获取今天往前5天的日线行情
    #ddf=get_price('sh510980',frequency='1d',count=num_days)      #默认获取今天往前5天的日线行情
    # print('上证指数etf日线行情\n',df)
    
    #-------有数据了，下面开始正题 -------------
    CLOSE=df.close.values;         OPEN=df.open.values           #基础数据定义，只要传入的是序列都可以  Close=df.close.values 
    HIGH=df.high.values;           LOW=df.low.values             #例如  CLOSE=list(df.close) 都是一样
    # #打印K线数据
    # for i, openLine in enumerate(OPEN):
    #     print(f"Day {i+1}: Open={df.open.values[i]}, High={df.high.values[i]}, Low={df.low.values[i]}, CLOSE={df.close.values[i]}")
    return df, CLOSE, OPEN, HIGH, LOW

def get_bond_etf_data(num_days):
    df=get_price('sh511260',frequency='1d',count=num_days)      #默认获取今天往前5天的日线行情
    #ddf=get_price('sh510980',frequency='1d',count=num_days)      #默认获取今天往前5天的日线行情
    # print('十年国债etf日线行情\n',df)
    
    #-------有数据了，下面开始正题 -------------
    CLOSE=df.close.values;         OPEN=df.open.values           #基础数据定义，只要传入的是序列都可以  Close=df.close.values 
    HIGH=df.high.values;           LOW=df.low.values             #例如  CLOSE=list(df.close) 都是一样
    # #打印K线数据
    # for i, openLine in enumerate(OPEN):
    #     print(f"Day {i+1}: Open={df.open.values[i]}, High={df.high.values[i]}, Low={df.low.values[i]}, CLOSE={df.close.values[i]}")
    return df, CLOSE, OPEN, HIGH, LOW

def generate_kline_data(num_days):
    kline_data = []
    const_price = 3000.0  # 实际价值
    current_price = const_price  # 初始股价

    for _ in range(num_days):
        # 随机生成当日的最高价、最低价和收盘价
        k = (const_price - current_price) / 1000 * 0.01 # [2000,4000] -> [0.02, -0.02]
        high = current_price * random.uniform(max(0.9, 0.98 + k), min(1.02 + k, 1.1))
        low = current_price * random.uniform(max(0.9, 0.98 + k), min(1.02 + k, 1.1))
        close = random.uniform(low, high)
        if high < low:
            temp = high
            high = low
            low = temp
        # 生成开盘价（取前一日的收盘价）
        open = current_price
        # 更新当前股价为当日收盘价
        current_price = close
        
        kline_data.append((open, high, low, close, k))
    # #打印K线数据
    # for i, kline in enumerate(kline_data):
    #     print(f"Day {i+1}: Open={kline[0]}, High={kline[1]}, Low={kline[2]}, Close={kline[3]}, K = {kline[4]}")

    return kline_data

def etf_strage(num_days):
    # 上证综指etf 510760 历史数据
    df, CLOSE, OPEN, HIGH, LOW = get_real_data(num_days)
    const_price = 1.044  # 实际价值
    sell_profit = 0.03  # 卖出时的利润
    buy_discount = 0.015       # 指数降低多少买入

    bond_df, Bond_CLOSE, Bond_OPEN, Bond_HIGH, Bond_LOW = get_bond_etf_data(num_days)
    useBoneStrategy = True # 是否购买债券
    
    # 模拟k线数据 指数均值3000
    useSimulatorData = False # 是否使用模拟数据
    if useSimulatorData:
        kline_data = generate_kline_data(num_days)
        const_price = 3000.0  # 实际价值
        sell_profit = 100.0  # 卖出时的利润
        buy_discount = 50       # 指数降低多少买入

    my_total_money = 200000
    my_buy_money_perday = 35000
    trade_log = []
    my_ticket_num = []
    my_ticket_price = []
    buy_times = 0
    sell_times = 0
    const_buy_price = const_price + buy_discount * 1  # 最高买入价
    target_buy_price = const_buy_price  # 目标买入价
    my_bond_num = 0               # 买入债券etf的数量
    for _ in range(num_days):
        # 更新当前股价
        open = OPEN[_]
        high = HIGH[_]
        low = LOW[_]
        close = CLOSE[_]
        if useSimulatorData:
            open = kline_data[_][0]
            high = kline_data[_][1]
            low = kline_data[_][2]
            close = kline_data[_][3]

        buy_price = 0.0
        sell_price = 0.0
        # 将当日K线数据添加到列表中
        # T + 1
        # strategy: 买入条件：当日最低价低于目标买入价，且有足够的钱买入
        #           卖出条件：当日最高价高于目标卖出价，且有足够的股票卖出
        if len(my_ticket_num) > 0 and high > (my_ticket_price[-1] + sell_profit):
            my_total_money += my_ticket_num[-1] * (my_ticket_price[-1] + sell_profit) * 0.99969 # 税： 0.031%
            sell_price = (my_ticket_price[-1] + sell_profit)
            my_ticket_num.pop(-1)
            my_ticket_price.pop(-1)
            sell_times += 1
        if low < target_buy_price and my_total_money > 0:
            buy_price = target_buy_price
            if target_buy_price > high:
                buy_price = high
            if my_total_money > my_buy_money_perday:
                my_ticket_num.append(my_buy_money_perday / buy_price)
                my_total_money -= my_buy_money_perday
            else:
                my_ticket_num.append(my_total_money / buy_price)
                my_total_money -= my_total_money
            my_ticket_price.append(buy_price)
            buy_times += 1
        if len(my_ticket_price) > 0:
            target_buy_price = my_ticket_price[-1] - buy_discount
        else:
            target_buy_price = const_buy_price

        bond_close = Bond_CLOSE[_]
        if useBoneStrategy:
            if my_total_money > my_buy_money_perday * 2:
                buy_money = my_total_money - my_buy_money_perday
                my_bond_num += buy_money / bond_close
                my_total_money -= buy_money
            elif my_total_money < my_buy_money_perday:
                sell_num = my_buy_money_perday / bond_close
                if sell_num > my_bond_num:
                    sell_num = my_bond_num
                my_bond_num -= sell_num
                my_total_money += sell_num * bond_close - 5 # 交易费用
        my_total_asset = my_total_money + my_bond_num * bond_close
        for i in range(len(my_ticket_num)):
            my_total_asset += my_ticket_num[i] * close
        trade_log.append((open, high, low, close, buy_price, sell_price, bond_close, my_bond_num, my_total_asset, my_total_money))

    return trade_log,my_ticket_num,my_ticket_price,buy_times,sell_times


# 生成10天的K线数据
days = 21 * 12 * 3
# do strage
trade_log,my_ticket_num,my_ticket_price,buy_times,sell_times = etf_strage(days)


# 打印K线数据
max = 0
min = 10000
for i, kline in enumerate(trade_log):
    if kline[1] > max:
        max = kline[1]
    if kline[2] < min:
        min = kline[2]
    print(f"Day {i+1}: ETF Price Change ({kline[0]}, {kline[1]}, {kline[2]}),   buy_price = {kline[4]}, sell_price = {kline[5]},    My Bonds ({kline[6]}, {kline[7]}), Total Asset = {kline[8]}, Cash = {kline[9]}")
print(f"max = {max}, min = {min}, buy_times = {buy_times}, sell_times = {sell_times}")
print(f"my_ticket_num = {my_ticket_num}")
print(f"my_ticket_price = {my_ticket_price}")