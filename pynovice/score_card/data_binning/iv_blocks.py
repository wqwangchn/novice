# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-28 17:59
Desc:
    iv最大值分箱 【迭代依次查找（合并分箱后iv最大的两个箱)进行合并】
    连续特征值观测值过多的可以先进行等频率分箱
    1.初始化阶段：首先按照属性值的大小进行排序（对于非连续特征，需要先做数值转换，比如转为坏人率，然后排序），然后每个属性值单独作为一组。

    2、合并阶段：
    （1）对每一对相邻的组，计算iv值。
    （2）根据计算的iv值，对其中最大的一对邻组合并为一组。
    （3）不断重复（1），（2）直到分组数达到一定的条件（如最小分组数5，最大分组数8）并且每箱都包含正负多个label。
对同一个变量划分bin越多，iv越高

'''

import pandas as pd
import numpy as np
from scipy.stats import chi2
from pynovice.score_card.data_binning.base_blocks import distince_blocks

def iv_blocks(df_field, df_label, maxCases=5, sample_threshold=2):
    '''
    best_iv 分箱
    :param df_field: 需分箱的字段 Series
    :param df_label: 样本的标签 Series
    :param maxCases: 最大分箱数
    :param sample_threshold:  bins中最少样本数
    :return:
        分箱的eges
    '''
    if maxCases<2:
        return [-np.inf,np.inf]
    if len(set(df_field))>100: #连续特征太多，进行初步分bins
        init_bins = distince_blocks(x=df_field.to_list(), bins=100)
        _bins = init_bins[1:-1]+[init_bins[-2]+10]
        df_field = pd.cut(df_field,bins=init_bins,labels=_bins)

    sample_threshold = df_field.shape[0] / 20  # 总体的5%(bins要大于5%)
    pass
    print('......')


    if len(set(df_field)) > 100:  # 连续特征太多，进行初步分bins
        init_bins = distince_blocks(x=df_field.to_list(), bins=100)
        _bins = init_bins[1:-1] + [init_bins[-2] + 10]
        df_field = pd.cut(df_field, bins=init_bins, labels=_bins)

pos_cnt, except_cnt, _ = get_chi2(df_field, df_label)  # 各箱样本频率和期望频率
df_pos_cnt, df_except_cnt = oneclass_merge(pos_cnt, except_cnt, sample_threshold)
min_chi = -np.inf
# 如果变量区间的最小卡方值小于阈值，则继续合并直到最小值大于等于阈值
while (min_chi < chi_threshold and len(df_pos_cnt) >= maxCases):
    _pos_cnt, _except_cnt, min_chi = chi_merge(df_pos_cnt, df_except_cnt, window=2)
    df_pos_cnt, df_except_cnt = oneclass_merge(_pos_cnt, _except_cnt, sample_threshold)

blocks = np.concatenate([[-np.inf], df_pos_cnt.index, [np.inf]])
return blocks.tolist()



