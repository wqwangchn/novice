# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-28 11:17
Desc:
    best_ks 分箱 分割
    将特征值值进行从小到大的排序。
    计算出KS最大的那个值(或者是bin size最大的)，即为切点，记为D。然后把数据切分成两部分。
    重复步骤2，进行递归，D左右的数据进一步切割。直到KS的箱体数达到我们的预设阈值即可。

    这里实现的是 ks最大和bin size 最大进行交替寻找
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
    data_cro.sort_index(inplace=True)
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
    if np.unique(df_label).size<2:
        return None,-np.inf
    ks_list = calc_ks(df_field, df_label)

    ks_sorted = ks_list.sort_values(ascending=False, inplace=False)
    for ks_i, ks in ks_sorted.items():
        data_1 = df_field[df_field <= ks_i]
        data_2 = df_field[df_field > ks_i]
        if len(data_1) >= limit and len(data_2) >= limit:
            break

    if len(ks_list)>1:
        ks_index = ks_list.index.astype(float).to_list()
        ks_index.sort()
        pos_i = ks_index.index(ks_i)
        if pos_i==len(ks_index)-1:
            ks_i=sum(ks_index[-2:])/2.0
        else:
            ks_i = sum(ks_index[pos_i:pos_i+2]) / 2.0
    return ks_i,ks

def get_best_split(ks_measure, _focus='ks'):
    ks_measure = np.array(ks_measure)  # 分割点，ks值，binsize
    ks_i = ks_measure[:,0]
    ind = 2 if _focus == 'bin_size' else 1
    idx = ks_measure[:,ind].argmax()
    return ks_i[idx]

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
    df_concat = pd.concat([df_field, df_label], axis=1)
    df_concat.columns = ['field', 'label']
    df_concat.sort_values(by='field', ascending=True, inplace=True)

    limit_ = df_concat.shape[0] / 20  # 总体的5%(bins要大于5%)

    ks_i,ks = ks_bin(df_concat['field'],df_concat['label'], limit_)
    df_set={ks_i:(df_concat,ks,len(df_concat))}

    ks_list = list()
    for i in range(box_num - 1):
        ks_measure = [[ks_i, v[1], v[2]] for ks_i, v in df_set.items()] # 分割点，ks值，binsize
        _focus = 'ks' if i%2==0 else 'bin_size' ## ks值和bin_size交叉寻找最大切分点
        ks_i = get_best_split(ks_measure,_focus)  # 找到最佳分割点
        if not ks_i:
            continue
        ks_list.append(ks_i)
        df_tmp,ks,bin_size = df_set.pop(ks_i)
        df_data1 = df_tmp[df_tmp['field'] > ks_i]
        df_data2 = df_tmp[df_tmp['field'] <= ks_i]
        ks_i_1, ks_1 = ks_bin(df_data1['field'], df_data1['label'], limit_)
        ks_i_2, ks_2 = ks_bin(df_data2['field'], df_data2['label'], limit_)
        df_set.update({ks_i_1:(df_data1,ks_1,len(df_data1))}) #{分割点：(data,ks,bin_size)}
        df_set.update({ks_i_2: (df_data1, ks_2,len(df_data2))})

    ks_list.sort()
    blocks = np.concatenate([[-np.inf],ks_list,[np.inf]])

    return blocks

if __name__ == '__main__':
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 3, 3, 3, 2, 1, 5, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    #df = pd.DataFrame([[3, 4, 0, 1, 2, 2, 2, 5, 7, 4, 7, 7, 7, 6], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field', 'label']
    df_field, df_label = df['field'], df['label']
    aa = ks_blocks(df_field, df_label,box_num=5, bad_target=1)
    print(aa)
