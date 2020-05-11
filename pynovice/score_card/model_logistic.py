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

from pynovice.score_card.score_card import ScoreCardModel
from sklearn.linear_model import LogisticRegression

class LRModel(ScoreCardModel):
    '''
        用于预测某一条预处理过的特征向量得分的方法
    :return:
        score_label: 最终预测的评分
        score_feature: 各个特征的得分字典
    '''

    def __init__(self):
        super().__init__()
        self.model_ = None
        self.woe_score = None

    def train(self,df_field,df_label,eval=False):
        self.model_ = LogisticRegression()
        self.model_.fit(df_field, df_label)
        if eval:
            self.woe_score = self.transform(df_field)
            print(self.woe_score)

    def predict(self,x):
        proba = self.model_.predict_proba([x])
        score_label = self.probability_to_score(bad_prob=proba[0][-1])
        return score_label

    def predict_detail(self,x):
        coef_ = self.model_.coef_[0]
        intercept_ = self.model_.intercept_[0]

        base_score = round(self.score_offset + self.score_factor * intercept_,2)  # 基础分
        field_score = [round(self.score_factor*coef_[i]*xi,2) for i,xi in enumerate(x)]  # 特征的分值
        final_score = int(base_score+sum(field_score))
        return final_score, base_score, field_score

    def transform(self,df_field):
        '''
        计算评分卡模型详细分数信息
        :param df_field:
        :return:
        '''
        df_eval = df_field.drop_duplicates()
        _out = []
        base_score = None
        for i, iter in df_eval.iterrows():
            _, base_score, field_score = self.predict_detail(x=iter)
            # 变量评分
            df_iter = pd.DataFrame(iter)
            df_iter.columns = ['value_']
            df_iter['score_'] = field_score
            _out.append(df_iter)
        df_score = pd.concat(_out, axis=0)
        df_score.loc['_base'] = [None, base_score]
        df_score.sort_index(inplace=True)
        return df_score


if __name__ == '__main__':
    import pandas as pd
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 6, 8, 3, 2, 1, 5, 7],[10, 2, 3, 42, 534, 5, 53, 6, 83, 3, 42, 21, 25, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field1', 'field2', 'label']
    df_fields, df_label = df[['field1','field2']], df['label']
    print(df_fields)
    lr = LRModel()
    lr.train(df_fields,df_label,eval=True)
    print(lr.predict_detail([2,8]))
