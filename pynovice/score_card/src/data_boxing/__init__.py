# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-22 20:10
Desc:
    无监督分箱：
        等频分箱: base_blocks.frequence_blocks  (自上而下 分割)
        等距分箱: base_blocks.distince_blocks  (自上而下 分割)
        聚类分箱: clustering_blocks.kmeans_blocks  (自上而下 分割)
        贝叶斯分箱: bayesian_blocks.bayesian_blocks   (自上而下 分割)
    有监督分箱：
        best-ks分箱: ks_blocks.ks_blocks  (自上而下 分割)
        卡方分箱: chi_blocks.chi_blocks  (自底而上 合并)
        决策树分箱(cart): tree_blocks.tree_blocks (自上而下 分割)
        ----
        iv最大分箱: iv_blocks.iv_blocks  (类卡方，树方法自上而下 分割) 略
        lightgbm分箱 （略 直方图分bins
            https://zhuanlan.zhihu.com/p/85053333?utm_source=wechat_session
            https://www.hrwhisper.me/machine-learning-lightgbm/）

'''

from .base_blocks import frequence_blocks,distince_blocks
from .clustering_blocks import kmeans_blocks
from .bayesian_blocks import bayesian_blocks

from .ks_blocks import ks_blocks
from .chi_blocks import chi_blocks
from .tree_blocks import tree_blocks

