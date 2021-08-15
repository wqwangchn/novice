# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 11:16:25 2020

@author: wangwenhao
"""

import pynovice.multi_process_step_wise_regression as mpmr
from sklearn.datasets import make_classification,make_regression
import pandas as pd


def get_X_y(data_type):
    if data_type == 'logistic':
        #含有信息的变量个数：4个
        #冗余变量个数：2。 冗余变量是有信息变量的线性组合
        #无用变量个数=10-4-2=4。

        #number of informative features = 4
        #number of redundant features = 2.redundant feature is linear combinations of the informative features
        #number of useless features = 10-4-2=4
        X, y = make_classification(n_samples=200,n_features=10,n_informative=4,n_redundant=2,shuffle=False,random_state=0,class_sep=2)
        X = pd.DataFrame(X,columns=['informative_1','informative_2','informative_3','informative_4','redundant_1','redundant_2','useless_1','useless_2','useless_3','useless_4']).sample(frac=1)
        y=pd.Series(y).loc[X.index]

    if data_type == 'linear':
        # 含有信息的变量个数：6个
        # 特征矩阵的秩：2个（说明含有信息量的6个变量中存在共线性）

        # number of informative features = 6
        # matrix rank = 2 (implying collinearity between six informative features)
        X, y = make_regression(n_samples=200,n_features=10,n_informative=6,effective_rank=2,shuffle=False,random_state=0)#
        X = pd.DataFrame(X,columns=['informative_1','informative_2','informative_3','informative_4','informative_5','informative_6','useless_1','useless_2','useless_3','useless_4']).sample(frac=1)
        y=pd.Series(y).loc[X.index]
    return X, y

def test_logit(X,y):
  #   从结果可以看出：
  #   1.算法选出了全部有效变量。
  #   2.排除了所有线性组合变量，而且排除的理由是超出VIF或相关系数的设置或系数不显著。
  #   3.排除了所有无效变量，排除的原因是模型性能没有提升或系数不显著

  #   As can be seen:
  #   1.All informative features are picked up by this algorithm
  #   2.All linear combinations features are excluded and the reasons are over the max_vif_limit or  max_corr_limit or max_pvalue_limit
  #   3.All useless features are excluded and the reasons are no lift on the perfermance of model or over max_pvalue_limit

  #   return
  #    in_vars = ['informative_3', 'informative_4', 'informative_2', 'informative_1']
  #
  #    dr = {'redundant_1': (['模型性能=0.956100,小于等于最终模型的性能=0.956100',
  #   '最大VIF=inf,大于设置的阈值=3.000000',
  #   '最大相关系数=0.925277,大于设置的阈值=0.600000',
  #   '有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['the performance index of model=0.956100,less or equals than the performance index of final model=0.956100',
  #   'the max VIF=inf,more than the setting of max_vif_limit=3.000000',
  #   'the max correlation coefficient=0.925277,more than the setting of max_corr_limit=0.600000',
  #   'some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000']),
  # 'redundant_2': (['模型性能=0.956100,小于等于最终模型的性能=0.956100',
  #   '最大VIF=inf,大于设置的阈值=3.000000',
  #   '最大相关系数=0.676772,大于设置的阈值=0.600000',
  #   '有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['the performance index of model=0.956100,less or equals than the performance index of final model=0.956100',
  #   'the max VIF=inf,more than the setting of max_vif_limit=3.000000',
  #   'the max correlation coefficient=0.676772,more than the setting of max_corr_limit=0.600000',
  #   'some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000']),
  # 'useless_1': (['模型性能=0.955200,小于等于最终模型的性能=0.956100',
  #   '有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['the performance index of model=0.955200,less or equals than the performance index of final model=0.956100',
  #   'some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000']),
  # 'useless_2': (['有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000']),
  # 'useless_3': (['有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000']),
  # 'useless_4': (['模型性能=0.955800,小于等于最终模型的性能=0.956100',
  #   '有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['the performance index of model=0.955800,less or equals than the performance index of final model=0.956100',
  #   'some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000'])}
    lr  =  mpmr.LogisticReg(X,y,measure='roc_auc',iter_num=20,logger_file_EN=None,logger_file_CH=None)
    in_vars,clf_final,dr = lr.fit()
    return in_vars,clf_final,dr


def test_linear(X,y):
 #    从结果可以看出：
 #    选出的变量来自有信息量的变量
 #    选出变量的个数等于特征矩阵秩的个数

 #    As can be seen:
 #    The picked features is from informative features
 #    The number of picked features equals matrix rank

 #    return
 #    ['informative_2', 'informative_6']
 #    dr = {'informative_1': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'informative_3': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'informative_4': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'informative_5': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'useless_1': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'useless_2': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'useless_3': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'useless_4': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000'])}
    lr  =  mpmr.LinearReg(X,y,iter_num=20,max_pvalue_limit=0.1,logger_file_EN=None,logger_file_CH=None)
    in_vars,clf_final,dr = lr.fit()
    return in_vars,clf_final,dr


if __name__ == '__main__':
    X_logit, y_logit = get_X_y('logistic')
    in_vars_logit,clf_final_logit,dr_logit = test_logit(X_logit,y_logit)

    X_linear, y_linear = get_X_y('linear')
    in_vars_linear,clf_final_linear,dr_linear = test_linear(X_linear,y_linear)
    print(in_vars_linear)
