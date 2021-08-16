# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 11:16:25 2020

@author: wangwenhao
"""

import pynovice.step_wise as mpmr
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
    lr  =  mpmr.Regression(X,y,measure='roc_auc',iter_num=20,logger_file=None)
    in_vars,dr = lr.fit()
    return in_vars,dr


if __name__ == '__main__':
    X_logit, y_logit = get_X_y('logistic')
    in_vars_logit,dr_logit = test_logit(X_logit,y_logit)

    print(in_vars_logit)
