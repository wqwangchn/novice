# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-28 17:26
Desc:
    于sklearn决策树的最优分箱

'''

from sklearn.tree import DecisionTreeClassifier
import numpy as np

def tree_blocks(df_field,df_label,box_num=5,criterion='entropy'):
    '''
        利用决策树获得最优分箱的边界值列表
    '''
    if box_num<2:
        return [-np.inf,np.inf]
    internal_nodes = box_num - 1

    boundary = [
    x = df_field.fillna(-999).values  # 填充缺失值
    y = df_label.values
    clf = DecisionTreeClassifier(criterion=criterion,  # “信息熵”最小化准则划分,gini,选择信息熵更合理。Gini 指数更偏向于连续属性，熵更偏向于离散属性。
                                 max_leaf_nodes=internal_nodes+1,  # 最大叶子节点数 = 非叶子结点+1
                                 min_samples_leaf=0.05)  # 叶子节点样本数量最小占比

    clf.fit(x.reshape(-1, 1), y)  # 训练决策树

    n_nodes = clf.tree_.node_count
    children_left = clf.tree_.children_left
    children_right = clf.tree_.children_right
    threshold = clf.tree_.threshold

    for i in range(n_nodes):
        if children_left[i] != children_right[i]:  # 获得决策树节点上的划分边界值(除叶子结点)
            boundary.append(threshold[i])
    boundary.sort()

    blocks = np.concatenate([[-np.inf], boundary, [np.inf]])

    return blocks.tolist()

# CRITERIA_CLF = {"gini": _criterion.Gini, "entropy": _criterion.Entropy}
# CRITERIA_REG = {"mse": _criterion.MSE, "friedman_mse": _criterion.FriedmanMSE,
#                 "mae": _criterion.MAE}

if __name__ == '__main__':
    import pandas as pd
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 6, 8, 3, 2, 1, 5, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field', 'label']
    df_field, df_label = df['field'], df['label']
    aa = tree_blocks(df_field, df_label,box_num=2)
    print(aa)