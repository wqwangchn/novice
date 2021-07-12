# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-22 14:26
Desc:
    评分卡流程(计算得分及各种评估)

    TPR = TP / (TP+FN);
    FPR = FP / (FP + TN);
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class ScoreCardModel:
    def __init__(self):
        self.load_score_alpha()

    def load_score_alpha(self, odds=1 / 2, bScore=650, addScore=-20):
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

    def probability_to_score(self, bad_prob, eps=1e-4):
        '''
            逾期概率转换为评分
        :param bad_prob: 逾期概率
        :return: bScore = offset - factor*ln(odds)
        '''

        odds = max(bad_prob, eps) / max(1 - bad_prob, eps)
        score = self.score_offset + self.score_factor * np.log(odds)
        return int(score)

    def score_to_probability(self, score, eps=1e-4):
        '''
            评分转换为逾期概率
        :param score: 信用评分
        :return: bScore = offset - factor*ln(odds) -->bad_prob
        '''
        score_factor = eps if self.score_factor==0 else self.score_factor
        odds = np.e**((score - self.score_offset)/(score_factor))
        odds = -1+eps if odds == -1 else odds
        bad_prob = 1.00*odds/(1+odds)
        return bad_prob

    @classmethod
    def get_auc(cls, df_pre, df_label, pre_target=1):
        '''
        功能: 计算KS值，输出对应分割点和累计分布函数曲线图
        :param df_pre: 一维数组或series，代表模型得分
        :param df_label: 一维数组或series，代表真实的标签{0,1}
        :return: 'auc': auc值，'crossdens': TPR&FPR
        '''
        df_label = df_label.apply(lambda x: 1 if x == pre_target else 0)
        crossfreq = pd.crosstab(df_pre, df_label).sort_index(ascending=False)  # 按照预测概率从大到小排序作为阈值
        crossdens = crossfreq.cumsum(axis=0) / crossfreq.sum()
        crossdens.columns = ['fpr', 'tpr']
        crossdens.name = 'pre_threshold'
        fpr = crossdens.loc[:, 'fpr']
        tpr = crossdens.loc[:, 'tpr']
        auc = np.trapz(y=tpr, x=fpr)
        return auc, crossdens

    @classmethod
    def get_g7_auc(cls, df_pre, df_got_fee, df_report_fee):
        '''
        功能: 计算auc值，输出对应分割点和累计分布函数曲线图
        :param df_pre: 一维数组或series，代表模型得分
        :param df_got_fee: 一维数组或series，代表已赚保费
        :param df_report_fee: 一维数组或series，代表赔付额
        :return: 'auc': auc值，'crossdens': TPR&FPR
        '''
        df_data = pd.concat([df_pre.reset_index(drop=True), df_got_fee.reset_index(drop=True), df_report_fee.reset_index(drop=True)],axis=1,ignore_index=True)
        df_data.columns=['pre','got_fee','report_fee']
        df_data=df_data.set_index('pre').sort_index(ascending=False)  # 按照预测概率从大到小排序作为阈值
        crossdens = df_data.cumsum(axis=0) / df_data.sum()
        crossdens.columns = ['fpr', 'tpr']
        crossdens.name = 'pre_threshold'
        fpr = crossdens.loc[:, 'fpr']
        tpr = crossdens.loc[:, 'tpr']
        auc = np.trapz(y=tpr, x=fpr)
        return auc, crossdens

    @classmethod
    def get_ks(cls, df_pre, df_label, pre_target=1):
        '''
        功能: 计算KS值，输出对应分割点和累计分布函数曲线图
        :param df_pre: 一维数组或series，代表模型得分
        :param df_label: 一维数组或series，代表真实的标签
        :return:
            'ks': KS值
            'crossdens': 好坏客户累积概率分布以及其差值gap
        '''
        df_label = df_label.apply(lambda x: 1 if x == pre_target else 0)
        crossfreq = pd.crosstab(df_pre, df_label).sort_index(ascending=False)  # 按概率降序排序
        crossdens = crossfreq.cumsum(axis=0) / crossfreq.sum()
        crossdens.columns = ['fpr', 'tpr']
        crossdens.name = 'pre_threshold'
        crossdens['gap'] = abs(crossdens['fpr'] - crossdens['tpr'])
        ks = crossdens[crossdens['gap'] == crossdens['gap'].max()]
        return ks, crossdens

    @classmethod
    def get_g7_ks(cls, df_pre, df_got_fee, df_report_fee):
        '''
        功能: 计算auc值，输出对应分割点和累计分布函数曲线图
        :param df_pre: 一维数组或series，代表模型得分
        :param df_got_fee: 一维数组或series，代表已赚保费
        :param df_report_fee: 一维数组或series，代表赔付额
        :return: 'auc': auc值，'crossdens': TPR&FPR
        '''
        df_data = pd.concat([df_pre.reset_index(drop=True), df_got_fee.reset_index(drop=True), df_report_fee.reset_index(drop=True)],axis=1,ignore_index=True)
        df_data.columns=['pre','got_fee','report_fee']
        df_data=df_data.set_index('pre').sort_index(ascending=False)  # 按照预测概率从大到小排序作为阈值
        crossdens = df_data.cumsum(axis=0) / df_data.sum()
        crossdens.columns = ['fpr', 'tpr']
        crossdens.name = 'pre_threshold'
        crossdens['gap'] = abs(crossdens['fpr'] - crossdens['tpr'])
        ks = crossdens[crossdens['gap'] == crossdens['gap'].max()]
        return ks, crossdens

    @classmethod
    def get_lift(cls, df_pre, df_label, pre_target=1, judg_threshold=0.5):
        '''
        功能: 计算KS值，输出对应分割点和累计分布函数曲线图
        :param df_pre: 一维数组或series，代表模型得分
        :param df_label: 一维数组或series，代表真实的标签{0,1}
        :return: 'auc': auc值，'crossdens': TPR&FPR
        '''
        df_label = df_label.apply(lambda x: 1 if x == pre_target else 0)
        crossfreq = pd.crosstab(df_pre, df_label).sort_index(ascending=False)
        crossdens = crossfreq.cumsum(axis=0)
        crossdens = crossdens.apply(lambda x: x / crossdens.sum(axis=1), axis=0)
        crossdens.columns = ['acc_false', 'acc_true']
        crossdens.name = 'pre_threshold'
        crossdens['acc_random'] = df_label.sum() / df_label.size  # 随机情况下的准确率
        crossdens['lift'] = crossdens['acc_true'] / crossdens['acc_random']
        # 预测阈值
        lift = crossdens[crossdens.index >= judg_threshold]['lift'].values
        if len(lift)>0:
            lift =lift[-1]
        else:
            lift = crossdens['lift'].mean()
        return lift, crossdens

    @classmethod
    def plot_roc(cls, df_pre, df_label, pre_target=1, save_path='./'):
        auc, crossdens = cls.get_auc(df_pre, df_label, pre_target)
        fpr = crossdens.loc[:, 'fpr']
        tpr = crossdens.loc[:, 'tpr']

        print('auc=%0.5f' % auc)
        fig = plt.figure(figsize=(10, 10))
        plt.plot(fpr, tpr, 'r--', linewidth=2.0, aa=False, label='ROC (area=%0.2f)' % (auc))
        plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6))
        plt.xlim([0.0, 1.00])
        plt.ylim([0.0, 1.00])
        plt.xlabel('False Postive Rate')
        plt.ylabel('True Postive Rate')
        plt.title('ROC Curve')
        plt.legend(loc="lower right")
        fig.savefig('%s/roc_curve_v1.png' % (save_path,), dpi=180)
        plt.close(fig)
        return auc

    @classmethod
    def plot_ks(cls, df_pre, df_label, pre_target=1, save_path='./'):
        ks, crossdens = cls.get_ks(df_pre, df_label, pre_target)
        max_ks_gap_index = str(ks.index[0])
        max_ks_gap_good_value = ks['tpr'].values[0]
        max_ks_gap_bad_value = ks['fpr'].values[0]
        max_ks_gap_value = ks['gap'].values[0]
        annotate_xtext = max_ks_gap_index
        annotate_ytext = str(round(max_ks_gap_value, 3))
        annotate_text_y_index = max_ks_gap_value / 2 + min(max_ks_gap_good_value, max_ks_gap_bad_value)

        fpr = crossdens.loc[:, 'fpr']
        tpr = crossdens.loc[:, 'tpr']
        axes_x = [str(i) for i in fpr.index]

        print('ks=%s' % max_ks_gap_value)
        fig = plt.figure(figsize=(10, 10))
        axes = fig.gca()
        axes.plot(axes_x, tpr, 'g', linewidth=2, label='tpr')
        axes.plot(axes_x, fpr, 'r', linewidth=2, label='fpr')
        axes.annotate(annotate_xtext, xy=(max_ks_gap_index, 0), xytext=(max_ks_gap_index, 0.05),
                      arrowprops=dict(facecolor='red', shrink=0.05))
        axes.plot([max_ks_gap_index, max_ks_gap_index],
                  [max_ks_gap_bad_value, max_ks_gap_good_value],
                  linestyle='--', linewidth=2.5)
        axes.annotate(annotate_ytext, xy=(max_ks_gap_index, annotate_text_y_index))
        axes.legend()
        axes.set_title('KS Curve')
        fig.savefig('%s/ks_curve_v1.png' % (save_path), dpi=180)
        plt.close(fig)
        return max_ks_gap_value

    @classmethod
    def plot_lift(cls, df_pre, df_label, pre_target=1, save_path='./'):
        lift, crossdens = cls.get_lift(df_pre, df_label, pre_target)
        crossdens['acc_random'] = 1
        acc_random = crossdens.loc[:, 'acc_random']
        acc_lift = crossdens.loc[:, 'lift']
        axis_x = [str(i) for i in acc_lift.index]

        print('lift=%0.5f' % lift)
        fig = plt.figure(figsize=(10, 10))
        plt.plot(axis_x, acc_random, 'g', linewidth=2.0, aa=False, label='random')
        plt.plot(axis_x, acc_lift, 'r', linewidth=2.0, aa=False, label='model(lift_threshold): %0.2f' % lift)

        plt.xlabel('Pre Rate')
        plt.title('Lift Curve')
        plt.legend(loc="lower right")
        fig.savefig('%s/lift_curve_v1.png' % (save_path,), dpi=180)
        plt.close(fig)
        return lift




if __name__ == '__main__':
    score_card_model = ScoreCardModel()
    score_card_model.load_score_alpha()
    for i in range(0, 11):
        score = score_card_model.probability_to_score(0.1 * i)
        print('overdue prob: {}, score: {}'.format(round(0.1 * i, 2), score))

    print('2343',score_card_model.score_to_probability(660))
    print(score_card_model.probability_to_score(0.3))

    # 评分卡模型评估
    df_raw = pd.DataFrame([[0.42, 0.73, 0.55, 0.37, 0.57, 0.70, 0.25, 0.23, 0.46, 0.62, 0.76, 0.46, 0.55, 0.56, 0.56,
                            0.38, 0.37, 0.73, 0.77, 0.21],
                           [1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0]]).T
    df_pre = df_raw[0]
    df_label = df_raw[1]

    aa,bb=score_card_model.get_lift(df_pre, df_label)

    # score_card_model.plot_roc(df_pre, df_label, pre_target=1, save_path='../data')
    # score_card_model.plot_ks(df_pre, df_label, pre_target=1, save_path='../data')
    # score_card_model.plot_lift(df_pre, df_label, pre_target=1, save_path='../data')