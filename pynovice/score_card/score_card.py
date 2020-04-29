# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-22 14:26
Desc:
    评分卡流程
'''
import numpy as np
class ScoreCardModel:
    def __init__(self):
        self.load_score_alpha()
        pass

    def load_score_alpha(self, odds=1/2, bScore=650, addScore=-20):
        '''
            1.坏好比odds=1:2时，对应基础评分bScore=600
            2.坏好比增加一倍时，评分减少addscore=-20
            bScore = offset - factor*ln(odds)
            bScore + addScore = offset - factor*ln(2*odds)
        :param odds: 坏好比
        :param bScore: 基础score分
        :param addScore: 评分变动值
        :return: bScore = offset - factor*ln(odds)
        '''

        self.score_factor = addScore / np.log(2)
        self.score_offset = bScore - addScore * np.log(odds) / np.log(2)

    def probability_to_score(self,bad_prob,eps=1e-4):
        '''
            逾期概率转换为评分
        :param bad_prob: 逾期概率
        :return: bScore = offset - factor*ln(odds)
        '''

        odds = max(bad_prob, eps) / max(1-bad_prob, eps)
        score = self.score_offset + self.score_factor*np.log(odds)
        return int(score)



if __name__ == '__main__':
    score_card_model=ScoreCardModel()
    score_card_model.load_score_alpha()
    for i in range(0,11):
        score=score_card_model.probability_to_score(0.1*i)
        print('overdue prob: {}, score: {}'.format(round(0.1*i,2),score))