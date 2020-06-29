# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-28 17:59
Desc:
https://github.com/boredbird/woe

    iv最大值分箱 【迭代依次查找（合并分箱后iv最大的两个箱)进行合并】
    连续特征值观测值过多的可以先进行等频率分箱
    1.初始化阶段：首先按照属性值的大小进行排序（对于非连续特征，需要先做数值转换，比如转为坏人率，然后排序），然后每个属性值单独作为一组。

    2、合并阶段：
    （1）对每一对相邻的组，计算iv值。
    （2）根据计算的iv值，对其中最大的一对邻组合并为一组。
    （3）不断重复（1），（2）直到分组数达到一定的条件（如最小分组数5，最大分组数8）并且每箱都包含正负多个label。
对同一个变量划分bin越多，iv越高

未完成
'''

import pandas as pd
import numpy as np
from pynovice.score_card.src.data_boxing import frequence_blocks

def calc_woe(x,y,bad_target=1, eps=1e-4):
    '''
    :param x:
    :param y:
    :param bad_target:
    :param eps:
    :return:
        woe字典和此特征的iv值
    '''
    bin = np.unique(x)
    prob_bad = np.array([np.logical_and(x==val,y==bad_target).sum() for val in bin])/float(np.sum(y==bad_target))
    prob_good = np.array([np.logical_and(x==val,y!=bad_target).sum() for val in bin])/float(np.sum(y!=bad_target))
    woe = np.log(np.maximum(prob_good,eps)/np.maximum(prob_bad,eps))
    iv = (prob_good-prob_bad)*woe
    woe_dict = dict(zip(bin,woe))
    return woe_dict,iv

def iv_split(df_field, df_label,bad_target=1):
    df_field = df_field.sort_values()
    df_label = df_label[df_field.index]


    init_iv = calc_woe(df_field,df_label,bad_target)


    init_split = 0.5 * (df_field[1:] + df_field[:-1])



    def find_best_split(_df,init_split):
        # 找出最大iv的分割点
        max_iv = -1
        for i in init_split:
            df_left = _df[_df < i]
            df_right = _df[_df >= i]
            _df[df_left.index] = 0
            _df[df_right.index] = 1
            _,tmp_iv = calc_woe(_df, df_label, bad_target)
            if tmp_iv>max_iv:
                max_iv = tmp_iv
                best_idx = i
        return best_idx



def iv_blocks(df_field, df_label, maxCases=5, max_iterations=100):
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
    iterations_bins = maxCases + max_iterations
    if len(set(df_field)) > iterations_bins:  # 连续特征太多，进行初步分bins
        init_bins = frequence_blocks(x=df_field.to_list(), bins=iterations_bins)
        _bins = init_bins[1:-1]+[init_bins[-2]+10]
        df_field = pd.cut(df_field,bins=init_bins,labels=_bins)

    sample_threshold = df_field.shape[0] / 20  # 总体的5%(bins要大于5%)
    pass
    print('......')

    woe_dict,iv = calc_woe(df_field, df_label, bad_target=1)


if __name__ == '__main__':
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 3, 3, 3, 2, 1, 5, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field', 'label']
    df_field, df_label = df['field'], df['label']


    import lightgbm as lgb
    params = {
        'task': 'train',  # 执行的任务类型
        'boosting_type': 'gbrt',  # 基学习器
        'objective': 'lambdarank',  # 排序任务(目标函数)
        'metric': 'ndcg',  # 度量的指标(评估函数)
        'max_position': 10,  # @NDCG 位置优化
        'metric_freq': 1,  # 每隔多少次输出一次度量结果
        'train_metric': True,  # 训练时就输出度量结果
        'ndcg_at': [10],
        'max_bin': 255,  # 一个整数，表示最大的桶的数量。默认值为 255。lightgbm 会根据它来自动压缩内存。如max_bin=255 时，则lightgbm 将使用uint8 来表示特征的每一个值。
        'num_iterations': 200,  # 迭代次数，即生成的树的棵数
        'learning_rate': 0.01,  # 学习率
        'num_leaves': 31,  # 叶子数
        # 'max_depth':6,
        'tree_learner': 'serial',  # 用于并行学习，‘serial’： 单台机器的tree learner
        'min_data_in_leaf': 30,  # 一个叶子节点上包含的最少样本数量
        'verbose': 2  # 显示训练时的信息
    }
    train_data = lgb.Dataset(df_field,df_label)
    gbm = lgb.train(params, train_data, valid_sets=[train_data])

