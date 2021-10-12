# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/8/19 16:52
Desc:
'''
from pynovice.score_card import card_explanations
import numpy as np


class shap_values:
    pass

shap_values.base_values=10
shap_values.feature_names=['年龄','性别','身高']
shap_values.data=[30,'女',167]
shap_values.values=np.array([2,4,-3])
# pl.rcParams['font.sans-serif'] = ['SimSun']

# 1.单特征
# card_explanations.waterfall(base_value=10, shap_values=np.array([2,4,-3]), features=np.array([30,'女',167]),
#                                         feature_names=['年龄','性别','身高'])


# 2.单特征
# card_explanations.force(
#     base_value=10, shap_values=np.array([2,4,-3]), features=[30,'女',167],
#                                         feature_names=['年龄','性别','身高'],matplotlib=True)

# # 3.数据集特征贡献
card_explanations.beeswarm(base_values=561,shap_values=np.array([[2,4,-3]]), features=[[30,'女',167]],
                                        feature_names=['年龄','性别','身高'])