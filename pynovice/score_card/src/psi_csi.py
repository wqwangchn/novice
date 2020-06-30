# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-06-29 11:14
Desc:
监控评分卡开发样本和现有样本分数分布的差异程度，关注样本人群的稳定性。
1. Population Stability Index (PSI)：群体稳定性指标，用来衡量分数分布的变化
2. Characteristic Stability Index (CSI)：特征稳定性指标，用来衡量特征层面的变化
'''
import pickle
import pandas as pd
import numpy as np
from pynovice.score_card.src.data_binning import DataBinning

class StabilityIndex:
    def __init__(self):
        '''
        计算模型分的稳定性psi：
            需要加载bins&bins_statistic_dict，可计算calc_expect_bins_statistic函数
        计算入模特征的稳定性csi：
            需要加载bins&bins_statistic_dict和bins_statistic_dict，可计算calc_expect_bins_statistic和load_expect_bins_score函数
        或者直接加载保存到本地的数据load_bins_statistic()/load_bins_score()
        '''
        self.bins_statistic_dict = {}  # 各箱的count数量
        self.bins_score_dict = {}  # 各箱的对应贡献分
        self.bins=[]

    def calc_expect_bins_statistic(self,expect_array,bins=10.0,bins_func='frequence_blocks'):
        '''
          对expect数组进行分箱统计
        :param expect_array:
        :param bins: bins_list或者bins数
        :param bins_func: bins为整数时使用bins_func进行分箱
        :return:
        '''
        df = pd.Series(expect_array).dropna()
        if isinstance(bins,list):
            self.bins=bins
            df_bins = pd.cut(df, bins=bins)
        else:
            binning = DataBinning(box_num=bins, _func=bins_func)
            df_bins = binning.fit_transform(df_x=df)
            self.bins = binning.bins
        self.bins_statistic_dict = df_bins.value_counts().to_dict()

    def calc_expect_bins_score(self,bins_score_dict):
        '''

        :param bins_score_dict:  各分bin对应的模型分值
        :return:
        '''
        self.bins_score_dict = bins_score_dict

    def load_bins_statistic(self,file_name):
        with open(file_name, "rb") as f:
            self.bins, self.bins_statistic_dict = pickle.load(f)

    def load_bins_score(self,file_name):
        with open(file_name, "rb") as f:
            self.bins_score_dict = pickle.load(f)

    def dump_bins_statistic(self,file_name):
        # json not suppert Interval type
        bins_info = [self.bins, self.bins_statistic_dict]
        with open(file_name, "wb") as f:
            pickle.dump(bins_info, f)

    def get_psi(self,actual_array,eps=1e-4):
        '''
        psi = (实际占比-预期占比)/LN(实际占比/预期占比)
        :param actual_array:
        :param eps:
        :return:
        '''
        df_expect = pd.DataFrame.from_dict(self.bins_statistic_dict,orient='index',columns=['expected_samples'])
        df_actual = pd.DataFrame(pd.cut(actual_array,self.bins).value_counts(),columns=['actual_samples'])
        df_out = pd.concat([df_expect, df_actual], axis=1)
        df_out['expected_rate'] = df_out['expected_samples']/max(eps,df_out['expected_samples'].sum())
        df_out['actual_rate'] = df_out['actual_samples'] / max(eps,df_out['actual_samples'].sum())
        df_out['rate_change'] = df_out['actual_rate']-df_out['expected_rate']
        df_out['ln(actual/expect)'] = (df_out['actual_rate'] / df_out['expected_rate']).map(
            lambda x: np.log(max(eps, x)))
        df_out['psi'] = df_out['rate_change']*df_out['ln(actual/expect)']
        columns_round = ['expected_rate', 'actual_rate', 'rate_change', 'ln(actual/expect)', 'psi']
        df_out[columns_round] = df_out[columns_round].round(4)
        return df_out

    def get_csi(self,actual_array,eps=1e-4):
        '''
         csi = (实际占比-预期占比)*每箱得分
        :param actual_array:
        :param eps:
        :return:
        '''
        df_psi = self.get_psi(actual_array)
        df_score_attribute = pd.DataFrame.from_dict(self.bins_score_dict, orient='index',
                                                    columns=['score_attribute']).round(4)
        df_out = pd.concat([df_psi, df_score_attribute], axis=1)
        df_out['csi'] = (df_out['rate_change'] * df_out['score_attribute']).round(4)
        return df_out

if __name__ == '__main__':
    expected_array, actual_array=[20,13,14,1,16,1,1,1,1],[20,15,17,15,16,1,1,1,1]

    # 1.psi:
    stab_index = StabilityIndex()
    stab_index.calc_expect_bins_statistic(expect_array=expected_array,bins=3)
    #stab_index.dump_bins_statistic('./model_score_bins_statistic.pkl')
    aa = stab_index.get_psi(actual_array)
    print(aa)
    bins_score_dict=dict(zip(aa.index,[20.0,30.0,40.0]))
    # 2.csi:
    stab_index = StabilityIndex()
    stab_index.calc_expect_bins_statistic(expect_array=expected_array, bins=3)
    stab_index.calc_expect_bins_score(bins_score_dict)
    bb = stab_index.get_csi(actual_array)
    print(bb)
