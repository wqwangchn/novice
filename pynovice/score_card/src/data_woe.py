# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-28 16:23
Desc:
    针对离散数据,我们需要将离散的枚举值替换成数值才可以用于计算.这些数值就是各个枚举值的权重.
    广义上讲,woe可以算是一种编码方式.
    IV	预测能力
    <0.03	无预测能力
    0.03~0.09	低
    0.1~0.29	中
    0.3~0.49	高
    >=0.5	极高
'''
import numpy as np
import pandas as pd


class WeightOfEvidence:
    def __init__(self,bad_target=1):
        self.bad_target = bad_target
        self.eps = 1e-4
        self.woe_dict = None
        self.iv = None
        self.woe_info = None

    def fit(self,df_x,df_y):
        '''
        :param x:
        :param y:
        :return:
            woe字典和此特征的iv值
        '''
        df_info = self.calc_woe(df_x,df_y)
        self.woe_dict = dict(zip(df_info['bin'].values,df_info['woe'].values.astype(float)))
        self.iv = sum(df_info['iv'])
        self.woe_info = df_info

    def transform(self,x):
        return self.woe_dict.get(x)

    def fit_transform(self,df_x,df_y):
        self.fit(df_x,df_y)
        out = df_x.apply(lambda x:self.transform(x))
        return out

    def calc_woe(self,df_x,df_y):
        '''
        :param df_x:
        :param df_y:
        :return:
            返回woe详细信息
        '''
        # |fields |bins |bad |good |bad_prob |good_prob |woe |iv

        bin = np.unique(df_x)
        good = np.array([np.logical_and(df_x == val, df_y != self.bad_target).sum() for val in bin])
        bad = np.array([np.logical_and(df_x == val, df_y == self.bad_target).sum() for val in bin])
        prob_good = good / float(np.sum(df_y != self.bad_target))
        prob_bad = bad / float(np.sum(df_y==self.bad_target))
        woe = np.log(np.maximum(prob_good,self.eps)/np.maximum(prob_bad,self.eps))
        iv = (prob_good-prob_bad)*woe
        df_info = pd.DataFrame(data=np.array([bin,good,bad,prob_good,prob_bad,woe,iv]).T,
                               columns=['bin','good','bad','good_prob','bad_prob','woe','iv'])
        df_info.insert(0, 'fields', df_x.name)
        return df_info



if __name__ == '__main__':
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 3, 3, 3, 2, 1, 5, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field', 'label']
    df_field, df_label = df['field'], df['label']

    df_field = pd.cut(df_field,bins=3)
    print(df_field)
    woe = WeightOfEvidence()
    aa = woe.fit_transform(df_field, df_label)
    bb = woe.transform(df_field[0])
    print(aa)
    print(bb)
    print(woe.woe_info)





