# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-22 10:56
Desc:
评分卡全流程：
    1.数据预处理  字符型变量，数值型变量
    2.变量分箱
    3.变量筛选
    4.模型开发
    5.模型评估
    6.模型监控
    + 互关联特征(DNN)

    模型校准
    1.基于违约率的评分
    2.传统lr评分卡
    3.xgboost评分卡
    4.xgboost评分卡（额度激进）


    基于IV值的变量筛选
    基于stepwise的变量筛选
    基于特征重要度的变量筛选：RF, GBDT…
    基于LASSO正则化的变量筛选
'''

from .feature_preprocessing import FeatureGenerator
from .model_base import BaseModel
from .model_logistic import LRModel
from .model_xgboost import XGBModel
from .src.psi_csi import StabilityIndex