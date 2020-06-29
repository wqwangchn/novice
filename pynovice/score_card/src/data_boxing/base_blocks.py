# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-23 14:45
Desc:
    等频分箱 & 等距分箱
    >>> frequence_blocks(x=[1,2,3,4,5,6,3],box_num=3)
    [-inf, 2.0, 4.5, inf]
    >>> distince_blocks(x=[1,2,3,4,5,6,3],box_num=5)
    [-inf, 2.0, 3.0, 4.0, 5.0, inf]
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
    if box_num<1:
        return [-np.inf,np.inf]
    blocks = np.linspace(min(x), max(x), box_num+1)
    blocks[0] = -np.inf
    blocks[-1] = np.inf
    return blocks.tolist()

if __name__ == '__main__':
    aa = frequence_blocks(x=[1, 2, 3, 4, 5, 6, 3], box_num=3)
    bb = distince_blocks(x=[1, 2, 3, 4, 5, 6, 3], box_num=5)
    print(aa,bb)