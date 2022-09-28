# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/11/5 12:23
Desc:
'''

import numpy as np

def get_randomforest_blocks(clf_rf):
    '''
        利用随机森林获得最优分箱的边界值列表
    '''
    rf_boundary = []
    for i, treei in enumerate(clf_rf.estimators_):
        n_nodes = treei.tree_.node_count
        feature = treei.tree_.feature
        threshold = treei.tree_.threshold
        children_left = treei.tree_.children_left
        children_right = treei.tree_.children_right

        tree_boundary = {}
        for i in range(n_nodes):
            if children_left[i] != children_right[i]:  # 获得决策树节点上的划分边界值(除叶子结点)
                if feature[i] in tree_boundary:
                    boundary = tree_boundary.get(feature[i])
                    boundary.append(threshold[i])
                else:
                    boundary = [-np.inf, np.inf]
                    boundary.append(threshold[i])
                tree_boundary.update({feature[i]: boundary})
        for k, v in tree_boundary.items():
            sv = list(set([round(i, 4) for i in v]))
            sv.sort()
            tree_boundary.update({k: sv})

        rf_boundary.append(tree_boundary)
    return rf_boundary
