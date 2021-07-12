# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-03-27 15:17
Desc:
'''

import sys
import math
import inspect
import signal

# 1.进度条展示 progress_bar(1, 100)
def progress_bar(portion, total):
    """
    total 总数据大小，portion 已经传送的数据大小
    :param portion: 已经接收的数据量
    :param total: 总数据量
    :return: 接收数据完成，返回True
    """
    part = total / 50  # 1%数据的大小
    count = math.ceil(portion / part)
    sys.stdout.write('\r')
    sys.stdout.write(('[%-50s]%.2f%%' % (('>' * count), portion / total * 100)))
    sys.stdout.flush()

    if portion >= total:
        sys.stdout.write('\n')
        return True
    return False

# 2.获取变量名
def get_retrieve_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    list_name = [var_name for var_name, var_val in callers_local_vars if var_val is var]
    return list_name

# 3.函数超时退出
def set_timeout(seconds, callback_func):
    '''
    暂时不可用
    :param seconds: 超时时间秒
    :param callback_func:超时后执行的函数
    :return:
    '''
    def wrap(func):
        def handle(signum, frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
            raise RuntimeError

        def to_do(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                signal.alarm(seconds)  # 设置 num 秒的闹钟
                # print('start alarm signal.')
                r = func(*args, **kwargs)
                # print('close alarm signal.')
                signal.alarm(0)  # 关闭闹钟
                return r
            except RuntimeError as e:
                if callback_func:
                    callback_func()

        return to_do
    return wrap


## vin 校准（检验车辆识别码是否正确）
def func_check_vin(vin):
    # https://www.angelfire.com/ca/TORONTO/VIN/VDS.html#equip
    if len(vin) != 17:
        return False
    if len(set(vin[:8] + vin[9:])) < 2:
        return False
    vin_ord = [ord(i) for i in vin]

    # 1.校验位(第9位)
    if (vin_ord[8] >= 48 and vin_ord[8] <= 57):  # 0到9
        verify = vin_ord[8] - 48
    elif (vin_ord[8] == 88):  # X
        verify = 10;
    else:
        return False

    # 位置权重
    weight = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

    # 字符对应值
    def get_symbol_trans(_ord_str):
        if (_ord_str >= 48 and _ord_str <= 57):  # 0-9
            symbol = _ord_str - 48
        elif (_ord_str >= 65 and _ord_str <= 72):  # A-H
            symbol = _ord_str - 64
        elif (_ord_str >= 74 and _ord_str <= 82 and _ord_str != 79 and _ord_str != 81):  # J-R不含O,Q
            symbol = _ord_str - 73
        elif (_ord_str >= 83 and _ord_str <= 90):  # S-Z
            symbol = _ord_str - 81
        else:
            return -999
        return symbol

    total_sum = 0
    for i, iv in enumerate(vin_ord):
        _symbol = get_symbol_trans(iv)
        if _symbol < 0:
            return False
        total_sum += _symbol * weight[i]

    return verify == total_sum % 11

## 房贷利率
def get_fee_month(loan_amount, year_rates, _type=1, pay_month=360):
    '''
    :param loan_amount: 贷款金额
    :param year_rates: 年化利率=月利率*12
    :param _type: {1:'等额本息',2:'等额本金',3:'先息后本'}
    :param pay_month: 1期为1月，30年即为360期
    :return: 月还款明细
    '''
    '''
    等额本息计算公式
    每月还款额=贷款本金×[月利率×（1+月利率）^还款月数]÷[（1+月利率）^还款月数-1]
    总支付利息：总利息=还款月数×每月月供额-贷款本金
    每月应还利息=贷款本金×月利率×〔(1+月利率)^还款月数-(1+月利率)^(还款月序号-1)〕÷〔(1+月利率)^还款月数-1〕
    每月应还本金=贷款本金×月利率×(1+月利率)^(还款月序号-1)÷〔(1+月利率)^还款月数-1〕
    总利息=还款月数×每月月供额-贷款本金
    
    等额本金计算公式
    每月月供额=(贷款本金÷还款月数)+(贷款本金-已归还本金累计额)×月利率
    每月应还本金=贷款本金÷还款月数
    每月应还利息=剩余本金×月利率=(贷款本金-已归还本金累计额)×月利率。
    每月月供递减额=每月应还本金×月利率=贷款本金÷还款月数×月利率
    总利息=还款月数×(总贷款额×月利率-月利率×(总贷款额÷还款月数)*(还款月数-1)÷2+总贷款额÷还款月数)
    '''
    month_rates = year_rates / 12
    _col = ['期数', '还款总额', '还款本金', '还款利息']
    if 1 == _type:  # 等额本息
        data = []
        for month_i in range(pay_month):
            interest = loan_amount * month_rates * ((1 + month_rates) ** pay_month - (1 + month_rates) ** month_i) / (
            (1 + month_rates) ** pay_month - 1)
            principal = loan_amount * month_rates * (1 + month_rates) ** month_i / ((1 + month_rates) ** pay_month - 1)
            _data = [month_i + 1, round(interest + principal, 2), round(principal, 2), round(interest, 2)]
            data.append(_data)
        df = pd.DataFrame(data, columns=_col)
    elif 2 == _type:  # 等额本金
        data = []
        payed_fee = 0
        principal = loan_amount / pay_month
        for month_i in range(pay_month):
            payed_fee = payed_fee +  principal
            interest = (loan_amount - payed_fee) * month_rates
            _data = [month_i + 1, round(interest + principal, 2), round(principal, 2), round(interest, 2)]
            data.append(_data)
        df = pd.DataFrame(data, columns=_col)
    else:  # 先息后本
        data = []
        interest = loan_amount * month_rates
        for month_i in range(pay_month - 1):
            _data = [month_i + 1, round(interest, 2), 0, round(interest, 2)]
            data.append(_data)
        data.append([month_i + 2, round(interest + loan_amount, 2), round(loan_amount, 2), round(interest, 2)])
        df = pd.DataFrame(data, columns=_col)
    return df



## 手机号正则
mobile_rg=r'^1[3|4|5|6|7|8|9][0-9]{9}$'
ydmobile_rg=r'^1(3[4-9]|4[7]|5[012789]|7[28]|8[23478]|9[578])\d{8}$'
ltmobile_rg=r'^1(3[0-2]|4[56]|5[56]|6[6]|7[0156]|8[56]|9[6])\d{8}$'
dxmobile_rg=r'^1(3[3]|4[19]|5[3]|7[3479]|8[019]|9[0139])\d{8}$'
def re_mobile(mobile):
    if re.match(ydmobile_rg,str(mobile)):
        return "移动"
    elif re.match(ltmobile_rg,str(mobile)):
        return "联通"
    elif re.match(mobile_rg,str(mobile)):
        return "电信"
    elif re.match(mobile_rg,str(mobile)):
        return "未知"
    else:
        return "非法手机号"

if __name__ == '__main__':
    ## 1.进度条
    portion = 0
    total = 254820000
    while True:
        portion += 1024
        sum = progress_bar(portion, total)
        if sum:
           break
    print("ok")
    # or
    progress_bar(portion=32, total=100)


    ## 2.变量名
    name = "bob"
    age = "23"
    bb = (name,age)
    for i in bb:
        var = get_retrieve_name(i)
        print(var)

    ## 3.函数超时
    def aa():
        print("超时")
    @set_timeout(2, callback_func=aa)
    def tt1():
        import time
        time.sleep(3)
    tt1()
