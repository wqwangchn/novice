# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-28 11:17
Desc:
    best_ks 分箱 分割
'''
import pandas as pd
import numpy as np

def calc_ks(df_field, df_label):
    '''
        计算ks值
    :param df_field:
    :param df_label:
    :return:
    '''
    # 好坏的个数
    label_statue = df_label.value_counts()
    good_cnt, bad_cnt = label_statue[0], label_statue[1]
    # 每个段不同的好坏数量
    data_cro = pd.crosstab(df_field, df_label)
    # 计算不同段的好坏百分比
    data_cro[0] = data_cro[0] / good_cnt
    data_cro[1] = data_cro[1] / bad_cnt
    # 数值进行累加
    data_cro_cum = data_cro.cumsum()
    # 计算不同段的好坏比差别
    ks_list = abs(data_cro_cum[1] - data_cro_cum[0])
    return ks_list

def ks_bin(df_field, df_label, limit):
    '''
        找到满足条件的最大的ks值划分位置
    :param df_field:
    :param df_label:
    :param limit:
    :return:ks_i 满足条件的分割点，最大的ks值
    '''
    ks_list = calc_ks(df_field, df_label)
    ks_i = None
    # 按照最大差别进行排序并且变成列表
    ks_list_index = ks_list.nlargest(len(ks_list)).index.tolist()
    for ks_i in ks_list_index:
        data_1 = df_field[df_field <= ks_i]
        data_2 = df_field[df_field > ks_i]
        if len(data_1) >= limit and len(data_2) >= limit:
            break
    return ks_i

def get_max_block(df_field, list_):
    list_zone = list()
    list_.sort()
    n = 0
    for i in list_:
        m = sum(df_field <= i) - n
        n = sum(df_field <= i)
        list_zone.append(m)
    list_zone.append(len(df_field) - sum(list_zone))
    max_index = list_zone.index(max(list_zone))
    if max_index == 0:
        rst = [df_field.min(), list_[0]]
    elif max_index == len(list_):
        # 选取项 最大项
        rst = [list_[-1], df_field.max()]
    else:
        rst = [list_[max_index - 1], list_[max_index]]
    return rst


def ks_blocks(df_field, df_label,box_num=5 ,bad_target=1):
    '''
    best_ks 分箱：找到最大ks分割点后，之后循环从数量最多的bins中找ks分隔点
    :param df_field:
    :param df_label:
    :param box_num: 分箱数量
    :param bad_target:
    :return:
    '''
    df_field.reset_index(drop=True, inplace=True)
    df_label.reset_index(drop=True, inplace=True)
    df_label.apply(lambda x:1 if x==bad_target else 0)

    limit_ = df_field.shape[0] / 20  # 总体的5%(bins要大于5%)
    ks_list = list()
    for i in range(box_num - 1):
        ks_ = ks_bin(df_field, df_label, limit_)
        if not ks_:
            break
        ks_list.append(ks_)
        border = get_max_block(df_field, ks_list)
        df_field = df_field[(df_field > border[0]) & (df_field <= border[1])]
        df_label = df_label[df_field.index]
    blocks = np.concatenate([[-np.inf],ks_list[1:-1],[np.inf]])

    return blocks

if __name__ == '__main__':
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 3, 3, 3, 2, 1, 5, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field', 'label']
    df_field, df_label = df['field'], df['label']
    aa = ks_blocks(df_field, df_label,box_num=5, bad_target=1)
    print(aa)

