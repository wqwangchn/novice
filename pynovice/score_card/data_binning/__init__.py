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
        聚类分箱: clustering_blocks.kmeans_blocks  (自下而上 合并)
        贝叶斯分箱: bayesian_blocks.bayesian_blocks   (自下而上 合并)
    有监督分箱：
        best-ks分箱: ks_blocks.ks_blocks  (自上而下 分割)
        卡方分箱: chi_blocks.chi_blocks  (自下而上 合并)
        -- iv最大分箱: iv_blocks.iv_blocks  (类卡方，自下而上 合并) 略
        单变量决策树算法（ID3、C4.5、CART）
        lightgbm分箱 （略 https://zhuanlan.zhihu.com/p/85053333?utm_source=wechat_session）

    类别特征分箱转换: transform_categray.CateCoder[cate_coding,blocks_2_catedict]
'''