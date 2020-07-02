# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-30 14:42
Desc:
    标准评分卡(lr)
    log(odds)=w*x
    score = self.score_offset + self.score_factor * np.log(odds)
'''

from pynovice.score_card.src.score_card import ScoreCardModel
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

class LRModel(ScoreCardModel):
    '''
        用于预测某一条预处理过的特征向量得分的方法
    :return:
        score_label: 最终预测的评分
        score_feature: 各个特征的得分字典
    '''

    def __init__(self,**kwargs):
        super().__init__()
        self.model_ = None
        self.woe_score = None
        self.kwargs = kwargs

    def train(self,train_feature, train_label, test_feature=pd.DataFrame, test_label=pd.DataFrame,eval=True,eval_plot=False):
        if (test_feature.empty or test_label.empty):
            train_feature, test_feature, train_label, test_label = \
                train_test_split(train_feature, train_label, test_size=0.2, random_state=0)

        self.model_ = LogisticRegression(**self.kwargs)
        self.model_.fit(train_feature, train_label)
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
        proba = self.model_.predict_proba(x)[:,1]
        score_label = np.array([self.probability_to_score(bad_prob=proba_i) for proba_i in proba])
        return proba,score_label

    def predict_detail(self,x):
        '''

        :param x: list/datafame
        :return: base_score,array([field_score]),array([final_score])
        '''
        coef_ = self.model_.coef_[0]
        intercept_ = self.model_.intercept_[0]

        base_score = round(self.score_offset + self.score_factor * intercept_,2)  # 基础分
        field_score = (np.array(x)*coef_*self.score_factor).round(decimals=2)  # 特征的分值
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
    lr = LRModel(class_weight='balanced')
    lr.train(df_fields,df_label,eval=True)
    print(lr.predict_detail([[2,8]]))
    print(lr.predict_detail(df_fields.head()))

    print(lr.predict([[2,8]]))
    print(lr.predict(df_fields.head()))

