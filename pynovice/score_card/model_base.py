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

from pynovice.score_card.src.score_card import ScoreCardModel
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

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

    def train(self,train_feature, train_label, test_feature=pd.DataFrame, test_label=pd.DataFrame, eval=True,eval_plot=False):
        if (test_feature.empty or test_label.empty):
            train_feature, test_feature, train_label, test_label = \
                train_test_split(train_feature, train_label, test_size=0.2, random_state=0)

        train_feature.reset_index(drop=True, inplace=True)
        train_label.reset_index(drop=True, inplace=True)
        base_bad_rate = 1.00 * (train_label == self.bad_target).sum() / train_label.size
        self.base_logodds = max(base_bad_rate, self.eps) / max(1 - base_bad_rate, self.eps)

        fields_logodds = []
        for iname in train_feature.columns:
            df_concat = pd.concat([train_feature[iname], train_label], axis=1)
            _log_odds = df_concat.groupby(iname).agg(
                lambda x: 1.00 * np.log(
                    max(sum(x == self.bad_target), self.eps) / max(sum(x != self.bad_target), self.eps)))
            odds_dict = dict(zip(_log_odds.index, _log_odds.values[:, 0]))
            fields_logodds.append(odds_dict)
        self.fields_logodds = fields_logodds

        if eval:
            self.woe_score = self.get_card_info(train_feature)
            # 模型评估
            print("training eval:")
            df_pre, _ = self.predict(train_feature)
            auc, _ = self.get_auc(df_pre, train_label)
            ks, _ = self.get_ks(df_pre, train_label)
            lift, _ = self.get_lift(df_pre, train_label)
            print("auc={}, ks={}, lift={}".format(auc, ks['gap'].values[0], lift))

            print('testing eval:')
            df_pre, _ = self.predict(test_feature)
            auc, _ = self.get_auc(df_pre, test_label)
            ks, _ = self.get_ks(df_pre, test_label)
            lift, _ = self.get_lift(df_pre, test_label)
            print("auc={}, ks={}, lift={}".format(auc, ks['gap'].values[0], lift))

        if eval_plot:
            df_pre, _ = self.predict(test_feature)
            self.plot_roc(df_pre, test_label, pre_target=1, save_path='.')
            self.plot_ks(df_pre, test_label, pre_target=1, save_path='.')
            self.plot_lift(df_pre, test_label, pre_target=1, save_path='.')

    def predict(self,x):
        '''
        :param x: list/datafame
        :return: array([proba]),array([score_label])
        '''
        _, _, final_score = self.predict_detail(x)
        proba = np.array([self.score_to_probability(score_i) for score_i in final_score])
        return proba, final_score

    def predict_detail(self,x):
        '''

        :param x: list/datafame
        :return: base_score,array([field_score]),array([final_score])
        '''
        if isinstance(x,(pd.DataFrame,pd.Series)):
            x = x.values.tolist()

        intercept_ = 0
        logodds = np.array([list(self.fields_logodds[i].get(v,self.base_logodds) for i,v in enumerate(iterm)) for iterm in x])
        base_score = round(self.score_offset + self.score_factor * intercept_,2)  # 基础分
        field_score = (logodds*self.score_factor).round(decimals=2)  # 特征的分值
        final_score = (base_score + field_score.sum(axis=1)).astype(int)  #综合评分
        return base_score, field_score, final_score

    def get_card_info(self,df_field):
        '''
        计算评分卡模型详细分数信息
        :param df_field:
        :return:
        '''
        _out = []
        base_score = None
        for i,field in enumerate(df_field.columns):
            df_idx = df_field[field].drop_duplicates().index
            df_eval = df_field.loc[df_idx,:]
            base_score, field_score, _ = self.predict_detail(x=df_eval)
            # 变量评分
            df_iter = pd.DataFrame(df_eval[field].values,columns=['value'])
            df_iter['score'] = field_score[:,i]
            df_iter.insert(loc=0, column='fields', value=field)
            _out.append(df_iter.sort_values('value'))
        df_card = pd.concat(_out, axis=0)
        df_card.loc['__'] = ['_base',None, base_score]
        df_card = df_card.sort_values('fields').reset_index(drop=True)
        return df_card


if __name__ == '__main__':
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 6, 8, 3, 2, 1, 5, 7],[10, 2, 3, 42, 534, 5, 53, 6, 83, 3, 42, 21, 25, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field1', 'field2', 'label']
    df_fields, df_label = df[['field1','field2']], df['label']

    base = BaseModel()
    base.train(df_fields,df_label,eval=True)
    print(base.predict_detail([[2,10]]))
    print(base.predict([[2,10]]))

    print(base.predict_detail(df_fields))
    print(base.predict(df_fields))
