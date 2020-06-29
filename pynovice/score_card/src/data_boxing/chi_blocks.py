# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-23 17:59
Desc:
    卡方分箱 【迭代依次查找（合并分箱后卡方最小的两个箱)进行合并】
    连续特征值观测值过多的可以先进行等频率分箱
    from https://zhuanlan.zhihu.com/p/115267395
    1.初始化阶段：首先按照属性值的大小进行排序（对于非连续特征，需要先做数值转换，比如转为坏人率，然后排序），然后每个属性值单独作为一组。

    2、合并阶段：
    （1）对每一对相邻的组，计算卡方值。
    （2）根据计算的卡方值，对其中最小的一对邻组合并为一组。
    （3）不断重复（1），（2）直到计算出的卡方值都不低于事先设定的阈值，或者分组数达到一定的条件（如最小分组数5，最大分组数8）并且每箱都包含正负多个label。

    >>> df = pd.DataFrame([[1,2,3,4,5,5,5,3,3,3,2,1,5,7],[1,1,0,0,0,0,0,1,1,0,1,1,1,1]]).T
    >>> df.columns=['field','label']
    >>> df_field, df_label = df['field'],df['label']
    >>> aa = chi_blocks(df_field, df_label, box_num=5, dfree=4, cf=0.1)
    >>> print(aa)
    [-inf, 4.0, 5.0, inf]

'''

import pandas as pd
import numpy as np
from scipy.stats import chi2
from pynovice.score_card.src.data_boxing import frequence_blocks

def get_chi2(df_field,df_label):
    '''
    计算卡方统计量
    :param df_field: 需分箱的字段 Series
    :param df_label: 样本的标签 Series
    :return:
        各箱样本频率,期望频率,卡发值
    '''

    df_field.reset_index(drop=True,inplace=True)
    df_label.reset_index(drop=True,inplace=True)
    df_concat = pd.concat([df_field,df_label],axis=1)
    df_concat.columns = ['field','label']
    df_concat.sort_values(by='field',ascending= True,inplace=True)

    dict_label_ratio = dict(df_label.value_counts() / df_label.count())
    _group = df_concat.groupby('field')

    group_cnt = []
    group_except_cnt = []
    for i,j in dict_label_ratio.items():
        iterm = _group.agg([(i, lambda x: sum(x == i))])
        group_cnt.append(iterm)
        iterm_expect = _group.agg([(i, lambda x: len(x)*j)])
        group_except_cnt.append(iterm_expect)
    df_pos_cnt = pd.concat(group_cnt,axis=1).droplevel(level=0,axis=1)  # 样本频率
    df_except_cnt = pd.concat(group_except_cnt,axis=1).droplevel(level=0,axis=1)  # 样本期望频率
    df_chi_square = (df_pos_cnt - df_except_cnt) ** 2 / df_except_cnt  # 卡方值

    return df_pos_cnt,df_except_cnt,df_chi_square


def cal_chisqure_threshold(dfree=4, cf=0.1):
    '''
    根据给定的自由度和显著性水平, 计算卡方阈值
    '''
    percents = [0.95, 0.90, 0.5, 0.1, 0.05, 0.025, 0.01, 0.005]

    ## 计算每个自由度，在每个显著性水平下的卡方阈值
    df = pd.DataFrame(np.array([chi2.isf(percents, df=i) for i in range(1, 30)]))
    df.columns = percents
    df.index = df.index + 1

    pd.set_option('precision', 3)
    return df.loc[dfree, cf]

def chi_merge(_pos_cnt, _except_cnt, window=2):
    '''
    合并相邻两bins，并计算合并后的卡方值，得到合并后最小卡方值和分箱位置索引
    :param _pos_cnt:
    :param _except_cnt:
    :param window:
    :return:
        合并分箱后的数据及对应的最小卡方值
    '''
    df_pos_cnt = _pos_cnt.sort_index().copy()
    df_except_cnt = _except_cnt.sort_index().copy()

    df_bins_init = df_pos_cnt.rolling(window=window).sum()[1:]
    df_expect_bins_init = df_except_cnt.rolling(window=window).sum()[1:]
    chi_bins = ((df_bins_init-df_expect_bins_init)**2/df_expect_bins_init).sum(axis=1).reset_index(drop=True)
    min_chi = chi_bins.min()
    idx_chi = chi_bins.idxmin()

    # merge
    index = df_pos_cnt.index
    df_pos_cnt.iloc[idx_chi+1,:] = df_pos_cnt.iloc[idx_chi,:]+df_pos_cnt.iloc[idx_chi+1,:]
    df_pos_cnt.drop(index=index[idx_chi],inplace=True)

    df_except_cnt.iloc[idx_chi+1,:] = df_except_cnt.iloc[idx_chi,:]+df_except_cnt.iloc[idx_chi+1,:]
    df_except_cnt.drop(index=index[idx_chi],inplace=True)

    return  df_pos_cnt,df_except_cnt,min_chi


def oneclass_merge(df_pos_cnt, df_except_cnt,sample_threshold=2):
    '''
    检查是否有箱没有好或者坏样本或者只有一类的。如果有，需要跟相邻的箱进行合并，直到每箱同时包含多类别样本
    :param df_pos_cnt:
    :param df_except_cnt:
    :param sample_threshold:bins中至少含有样本阈值
    :return:

    '''
    raw_index = df_pos_cnt.index
    df_pos_cnt.reset_index(drop=True,inplace=True)
    df_except_cnt.reset_index(drop=True,inplace=True)
    df_oneclass = df_pos_cnt[df_pos_cnt.apply(lambda x: (1==sum(x > 0)) or (sum(x)<sample_threshold), axis=1)]
    idx_oneclass = df_oneclass.index.to_list()

    if len(idx_oneclass)>0&(len(df_pos_cnt)>1):
        icur = idx_oneclass[0]
        if icur == 0:  # 如果分箱区间在最前,则向下合并
            df_pos_cnt.loc[icur + 1, :] = df_pos_cnt.loc[icur + 1, :] + \
                                          df_pos_cnt.loc[icur, :]
            df_except_cnt.loc[icur + 1, :] = df_except_cnt.loc[icur + 1, :] + \
                                             df_except_cnt.loc[icur, :]
            drop_index = icur
        elif icur == len(raw_index) - 1:  # 如果分箱区间在最后，则向上合并
            df_pos_cnt.loc[icur - 1, :] = df_pos_cnt.loc[icur - 1, :] + \
                                          df_pos_cnt.loc[icur, :]
            df_except_cnt.loc[icur - 1, :] = df_except_cnt.loc[icur - 1, :] + \
                                             df_except_cnt.loc[icur, :]
            drop_index = icur
        else:  # 如果分箱区间在中间，则判断与其相邻的最小卡方的区间，然后进行合并
            select_idx = [icur - 1, icur, icur + 1]
            pos_cnt, except_cnt, _ = chi_merge(df_pos_cnt.loc[select_idx, :], df_except_cnt.loc[select_idx, :], window=2)
            df_pos_cnt.loc[pos_cnt.index, :] = pos_cnt
            df_except_cnt.loc[pos_cnt.index, :] = except_cnt
            if max(pos_cnt.index) < icur + 1:
                drop_index = icur + 1
            elif min(pos_cnt.index) > icur - 1:
                drop_index = icur - 1
            else:
                drop_index = icur
        df_pos_cnt.drop(index=drop_index, inplace=True)
        df_except_cnt.drop(index=drop_index, inplace=True)
    df_pos_cnt.index = raw_index[df_pos_cnt.index]
    df_except_cnt.index = raw_index[df_except_cnt.index]
    if len(idx_oneclass) > 1:
        return oneclass_merge(df_pos_cnt, df_except_cnt)
    return df_pos_cnt,df_except_cnt

def chi_blocks(df_field, df_label, box_num=5, dfree=4, cf=0.1,max_iterations=100):
    '''
    卡方分箱
    :param df_field: 需分箱的字段 Series
    :param df_label: 样本的标签 Series
    :param dfree: 卡方分布的自由度
    :param cf: 卡方分布的显著性水平
    :param box_num: 最大分箱数
    :param sample_threshold:  bins中最少样本数
    :param _type:  number|category
    :return:
        分箱的eges
    '''
    if box_num<2:
        return [-np.inf,np.inf]
    chi_threshold = cal_chisqure_threshold(dfree, cf)  # 卡方阈值
    sample_threshold = df_field.shape[0] / 20  # 总体的5%(bins要大于5%)
    iterations_bins = box_num+max_iterations
    if len(set(df_field))>iterations_bins: #连续特征太多，进行初步分bins
        init_bins = frequence_blocks(x=df_field.to_list(), bins=iterations_bins)
        _bins = init_bins[1:-1]+[init_bins[-2]+10]
        df_field = pd.cut(df_field,bins=init_bins,labels=_bins)

    pos_cnt, except_cnt,_ = get_chi2(df_field, df_label)  # 各箱样本频率和期望频率
    df_pos_cnt, df_except_cnt = oneclass_merge(pos_cnt, except_cnt,sample_threshold)
    min_chi = -np.inf
    # 如果变量区间的最小卡方值小于阈值，则继续合并直到最小值大于等于阈值
    while (min_chi<chi_threshold and len(df_pos_cnt) >= box_num):
        _pos_cnt, _except_cnt, min_chi = chi_merge(df_pos_cnt, df_except_cnt, window=2)
        df_pos_cnt, df_except_cnt = oneclass_merge(_pos_cnt, _except_cnt,sample_threshold)

    blocks = np.concatenate([[-np.inf],df_pos_cnt.index,[np.inf]])
    return blocks.tolist()

if __name__ == '__main__':
    df = pd.DataFrame([[1,2,3,4,5,5,5,3,3,3,2,1,5,7],[1,1,0,0,0,0,0,1,1,0,1,1,1,1]]).T
    df.columns=['field','label']
    df_field, df_label = df['field'],df['label']
    aa = chi_blocks(df_field, df_label, box_num=5, dfree=4, cf=0.1)
    print(aa)
