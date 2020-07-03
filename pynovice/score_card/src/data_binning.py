# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-22 16:58
Desc:
    1.数据分箱(离散化数据)
    代优化
'''
from collections import Sequence

import pandas as pd
import numpy as np
from pynovice.score_card.src.data_boxing import *

DISCRETIZATION_FUNCTION = {
    'frequence_blocks':
        lambda df_x, df_y, box_num: frequence_blocks(df_x, box_num),
    'distince_blocks':
        lambda df_x, df_y, box_num: distince_blocks(df_x, box_num),
    'kmeans_blocks':
        lambda df_x, df_y, box_num: kmeans_blocks(df_x, box_num),
    'bayesian_blocks':
        lambda df_x, df_y, box_num: bayesian_blocks(t=df_x, x=None, sigma=None, fitness='events'),
    'ks_blocks':
        lambda df_x, df_y, box_num: ks_blocks(df_x, df_y, box_num=box_num, bad_target=1),
    'chi_blocks':
        lambda df_x, df_y, box_num: chi_blocks(df_x, df_y, box_num=box_num, dfree=4, cf=0.1,max_iterations=100),
    'tree_blocks':
        lambda df_x, df_y, box_num: tree_blocks(df_x, df_y, box_num=box_num, criterion='entropy')
}

class DataBinning:
    """离散化连续数据
    Attributes:
         bins (Sequence): - 用于分段的列表,第一位为下限,最后一位为上限
    """

    def __init__(self, box_num=5, _func='tree_blocks'):
        self.box_num = box_num
        self.func = self.check_func(_func)
        # _out
        self.bins = None

    def fit(self, df_x, df_y=None):
        '''
        数据分箱
        :param x:
        :param y:
        :param _func: 分箱采用的方法，默认为二叉树分箱
        :return: 分箱切割点
        '''
        blocks = self.func(df_x,df_y,self.box_num)
        self.bins = blocks

    def transform(self, x):
        if not x:
            return [-np.inf,np.inf]
        s = pd.cut([x], bins=self.bins)[0]
        return s

    def fit_transform(self, df_x, df_y=None):
        self.fit(df_x, df_y)
        out = pd.cut(df_x, bins=self.bins)
        return out

    def check_func(self,_func):
        if isinstance(_func,str):
            _key = DISCRETIZATION_FUNCTION.keys()
            assert _func in _key, "func_list: {}".format(_key)
            _func = DISCRETIZATION_FUNCTION.get(_func)
        return _func

if __name__ == '__main__':
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 3, 3, 3, 2, 1, 5, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field', 'label']
    df_field, df_label = df['field'], df['label']

    binning = DataBinning(box_num=2, _func='tree_blocks')
    bb=binning.fit_transform(df_x=df['field'],df_y=df_label)
    cc= binning.transform(3)
    print(bb)
    print(binning.bins)

    print(cc)

