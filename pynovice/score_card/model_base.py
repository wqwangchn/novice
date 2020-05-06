# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-30 14:42
Desc:
    基于违约率的评分模型
    score = self.score_offset + self.score_factor * np.log(odds)
'''

from pynovice.score_card.score_card import ScoreCardModel
import numpy as np

class BaseModel(ScoreCardModel):
    '''
        用于预测某一条预处理过的特征向量得分的方法
    :return:
        score_label: 最终预测的评分
    '''

    def __init__(self,bad_target=1,eps=1e-4):
        super().__init__()
        self.bad_target = bad_target
        self.eps = eps
        # _out
        self.base_logodds = None
        self.fields_logodds = None

    def train(self,df_fields,df_label):
        '''
            通过训练集的odds来创建违约率模型
        :param df_fields:
        :param df_label:
        :return:
        '''
        df_fields.reset_index(drop=True, inplace=True)
        df_label.reset_index(drop=True, inplace=True)
        _bad_rate = 1.00* (df_label==self.bad_target).sum()/df_label.size
        self.base_logodds = max(_bad_rate,self.eps)/max(1-_bad_rate,self.eps)
        self.fields_logodds = []
        for iname in df_fields.columns:
            df_concat = pd.concat([df_fields[iname], df_label], axis=1)
            log_odds = df_concat.groupby(iname).agg(
                lambda x:1.00* np.log(max(sum(x==self.bad_target),self.eps)/max(sum(x!=self.bad_target),self.eps)))
            odds_dict = dict(zip(log_odds.index,log_odds.values[:,0]))
            self.fields_logodds.append(odds_dict)

    def predict_detail(self,x):
        base_score = round(self.score_offset, 2)  # 基础分
        field_score = []
        for i,v in enumerate(x):
            _logodds = self.fields_logodds[i].get(v,self.base_logodds)
            _score = round(self.score_factor * _logodds,2)  # 特征的分值
            field_score.append(_score)
        final_score = int(base_score+sum(field_score))
        return final_score, base_score, field_score


if __name__ == '__main__':
    import pandas as pd
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 6, 8, 3, 2, 1, 5, 7],[10, 2, 3, 42, 534, 5, 53, 6, 83, 3, 42, 21, 25, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field1', 'field2', 'label']
    df_fields, df_label = df[['field1','field2']], df['label']

    base = BaseModel()
    base.train(df_fields,df_label)
    print(base.predict_detail([2,10]))
