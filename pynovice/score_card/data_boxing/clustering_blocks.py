# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-23 16:10
Desc:
    聚类分箱(k-means) 合并
    >>> kmeans_blocks(x=[1,2,3],bins=3)
    >>> print(aa)
'''

from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabaz_score
import numpy as np

def kmeans_blocks(x,box_num=3):
    '''
        聚类分箱
    :param x: dtype=[]
    :param bins: 分箱数量
    :return: 箱边界
    '''
    len_clocks = min(box_num,len(x),len(set(x))+1)
    if len_clocks<=1:
        return [-np.inf,np.inf]
    X = np.array(x).reshape([-1, 1])
    km = KMeans(n_clusters=len_clocks-1, random_state=666)
    y_pre = km.fit_predict(X)
    # 使用Calinski-Harabasz Index评估的聚类分数: 分数越高，表示聚类的效果越好
    if km.cluster_centers_.size > 1:  # 聚类类别大于1
        kmeans_score = calinski_harabaz_score(X, y_pre)
        print("聚类效果评分：{}".format(kmeans_score))
    tb = km.cluster_centers_.reshape([-1])
    tb.sort()
    blocks = np.concatenate([[-np.inf],tb,[np.inf]])
    return blocks.tolist()

if __name__ == '__main__':
    aa = kmeans_blocks(x=[1, 2, 3], box_num=3)
    print(aa)