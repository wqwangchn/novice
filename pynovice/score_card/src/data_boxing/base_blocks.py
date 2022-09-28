# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/10/26 10:53
Desc:
'''

import numpy as np

def frequence_blocks(x, box_num=10):
    '''
        等频分箱
    :param x: dtype=[]
    :param bins: 分箱数量
    :return: 箱边界
    '''
    x=np.sort(x)
    len_clocks = int(min(len(x),box_num))
    ind = np.linspace(0, len(x)-1, len_clocks).astype(int)
    tb=np.array(x)[ind]
    tb = np.unique(tb)
    if len(tb)<2:
        return [-np.inf,np.inf]
    blocks = np.concatenate([[-np.inf],
                            0.5 * (tb[1:] + tb[:-1]),
                            [np.inf]])
    return blocks.tolist()

def distince_blocks(x, box_num=5):
    '''
        等距分箱
    :param x: dtype=[]
    :param bins: 分箱数量
    :return: 箱边界
    '''
    blocks = np.linspace(min(x), max(x), box_num+1)
    blocks = np.unique(blocks)
    if len(blocks)<2:
        return [-np.inf,np.inf]
    blocks[0] = -np.inf
    blocks[-1] = np.inf
    return blocks.tolist()

if __name__ == '__main__':
    aa = frequence_blocks(x=[1, 2, 2, 3, 2, 6, 3], box_num=10)
    bb = distince_blocks(x=[1, 2, 2, 3, 2, 6, 3], box_num=2)
    print(aa,bb)