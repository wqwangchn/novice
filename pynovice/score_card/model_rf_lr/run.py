# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/11/5 12:28
Desc:
'''

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
def load_data(indices=False):
    data = load_iris()

    x, y = data.data, data.target
    if indices:
        x = x[:, 2:4]
    x_train, x_test, y_train, y_test = \
        train_test_split(x, y, test_size=0.3,
                         shuffle=True, random_state=20)
    return x_train, x_test, y_train, y_test

def frc2(x_train, x_test, y_train, y_test):
    forest = RandomForestClassifier(
        n_estimators=100,
        criterion="gini",
        max_depth=3,
        min_samples_leaf=0.05,
        bootstrap=False,
        random_state=666,
    )
    forest.fit(x_train, y_train)
    print("仅包含两个维度时的准确率：", forest.score(x_test, y_test))
    return forest

if __name__ == '__main__':
    # 1.load data
    x_train, x_test, y_train, y_test = load_data()
    # 2.随机森林获取分箱
    rf = frc2(x_train, x_test, y_train, y_test)
    blocks_set = get_randomforest_blocks(rf)
    # 3.woe特征
