# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-28 16:23
Desc:
    IV	预测能力
    <0.03	无预测能力
    0.03~0.09	低
    0.1~0.29	中
    0.3~0.49	高
    >=0.5	极高
'''
import numpy as np

def calc_woe(x,y,bad_target=1, eps=1e-4):
    bin = np.unique(x)
    prob_bad = np.array([np.logical_and(x==val,y==bad_target).sum() for val in bin])/float(np.sum(y==bad_target))
    prob_good = np.array([np.logical_and(x==val,y!=bad_target).sum() for val in bin])/float(np.sum(y!=bad_target))
    woe = np.log(np.maximum(prob_good,eps)/np.maximum(prob_bad,eps))
    iv = (prob_good-prob_bad)*woe
    return woe,iv


if __name__ == '__main__':
    import pandas as pd
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 3, 3, 3, 2, 1, 5, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field', 'label']
    df_field, df_label = df['field'], df['label']
    aa = calc_woe(df_field, df_label)
    print(aa,aa[1].sum())
