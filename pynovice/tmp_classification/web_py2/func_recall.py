# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-06-05 15:18
Desc: 风控用户召回
'''
import subprocess
import signal

def set_timeout(seconds, callback_func):
    '''

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

#@set_timeout(300, None)
def risk_recall(from_product, into_product, risk_rules, start_time, end_time, dump_file):
    p_status = subprocess.Popen(
        '. /home/develop_admin/wqwang/venv36/bin/activate '
        '&& python /home/wqw/1.PyRule/Online/recall_v01.py {} {} {} {} {} {}'.format(
            from_product,into_product,risk_rules,start_time,end_time,dump_file))
    return p_status

def risk_recall(from_product, into_product, risk_rules, start_time, end_time, dump_file):
    p = subprocess.Popen('python tmp1.py & python tmp1.py',shell=True)
    return p

if __name__ == '__main__':
    p_status = risk_recall('opesa','mhela','new','20200602000000','20200602010000','recall_mhela')
    while True:
        import time
        time.sleep(1)
        aa = p_status.stdout
        _out = subprocess.Popen.poll(p_status)
        print('--',aa)
        print(_out)
        if _out==0:
            break
