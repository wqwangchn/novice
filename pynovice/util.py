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
