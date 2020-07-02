# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-30 14:42
Desc:
    xgboost 模型评分卡
    xgboost 参数 https://blog.csdn.net/zc02051126/article/details/46711047
    score = self.score_offset + self.score_factor * np.log(odds)
'''

from pynovice.score_card.src.score_card import ScoreCardModel
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

class XGBModel(ScoreCardModel):
    '''
        用于预测某一条预处理过的特征向量得分的方法
    :return:
        score_label: 最终预测的评分
        score_feature: 各个特征的得分字典
    '''
    missing_value: float

    def __init__(self,missing_value=-999.0,**kwargs):
        super().__init__()
        self.missing_value = missing_value
        self.param = self.load_xgb_param(kwargs)
        self.feature_columns = None
        self.model_ = None

    def load_xgb_param(self,kwargs):
        param={}
        # 1.一般参数:  这些参数用来控制XGBoost的整体通用功能，
        general_param={
            'booster': 'gbtree',  # [默认gbtree] 有两中模型可以选择gbtree和gblinear。gbtree使用基于树的模型进行提升计算，gblinear使用线性模型进行提升计算。
            'silent': 1, # [默认0]	是否开启静默模式，0为不开启，1为开启，开启后不打印运行时信息。
            'nthread': 1,  # [默认取最大线程数] 这个参数用来控制最大并行的线程数
        }
        # 2.booster的参数,取决于使用哪种booster, 这些参数是要重点调整的。
        booster_tree_param = {
            'eta': 0.1,  # [default=0.3] 学习率参数，就是原理中说的缩减，保证每一颗树对于结果的影响不太大，从而保证模型的效果。更新叶子节点权重时，乘以该系数，避免步长过大。参数值越大，越可能无法收敛。把学习率 eta 设置的小一些，小学习率可以使得后面的学习更加仔细。 典型值为0.01-0.2。
            'gamma': 0,  # [default=0] 一听这种希腊字母就知道是个系数，在树的叶子节点上作进一步分区所需的最小损失减少。越大，算法越保守。取值在[0,∞] 。通俗点讲就是，这个节点还划不划分，先看看损失减不减少了再说。同样需要cv调优。
            'max_depth': 3,  # [default=6] 这个没啥好说的，每棵树的最大深度，也是用来避免过拟合的，max_depth越大，模型会学到更具体更局部的样本，典型值3-10，要用cv调优。
            'min_child_weight': 1,  # [default=1] 大家对他的解释是决定最小叶子节点样本权重和，不太好理解。看了一些解释的文章，这个值可以理解为H值，还记得H值吗，就是损失函数对y(t-1)的二阶导数和，那么如果损失函数是平方函数（回归问题），这个就是1，如果是对数损失函数（分类问题），导数是a(1-a)的形式，a代表sigmoid函数，这样的话当y预测值非常大的时候，这个式子的值接近于0，这当然是不好的，因此你要给他设定一个阈值，小于这个阈值就不分裂了。现在可以解释了，这个值代表所有样本二阶导数的和，和上边说的叶子得分不是一个事，如果是回归问题实际代表样本个数，如果是分类问题实际代表a(1-a)所有样本计算值的加和。明白这个参数是啥以后，来看他是干嘛的，这个参数用于避免过拟合，当它的值较大时，可以避免模型学习到局部的特殊样本。举个栗子来说，对正负样本不均衡时的 0-1 分类而言，假设 h 在 0.01 附近，min_child_weight 为 1 意味着叶子节点中最少需要包含 100 个样本，实际是通过控制样本数来控制过拟合的。你们应该看出来这个值越小越容易过拟合，需要通过cv进行调整优化。
            # max_leaf_nodes 树上最大节点的数量，和上面的那个参数一样，如果定义了这个参数就会忽略掉max_depth参数，我们调优还是以max_depth为主吧。
            'max_delta_step': 0,  # [default=0] 这参数限制每棵树权重改变的最大步长。如果这个参数的值为0，那就意味着没有约束。如果它被赋予了某个正值，那么它会让这个算法更加保守。通常，这个参数不需要设置。但是当各类别的样本十分不平衡时，它对逻辑回归是很有帮助的。也就是说这个参数不用管啊。
            'subsample': 1,  # [default=1] 样本采样用的，用于训练模型的子样本占整个样本集合的比例,减小这个参数的值，算法会更加保守，避免过拟合，但是如果这个值设置得过小，它可能会导致欠拟合。典型值：0.5-1。既然有个范围，给他个面子cv调优一把吧。
            'colsample_bytree': 1,  # [default=1] 列采样，在建立树时对特征采样的比例，前面介绍过了，和设置缩减率一样是为了干嘛来着，是为了防止过拟合的，一般设置为： 0.5-1 ，也要用cv拟合。
            'tree_method': 'auto',  # [default=’auto’] 还记得我说过树的生成方法，有三个可选的值， {‘auto’, ‘exact’, ‘approx’} ，分别对应 贪心算法(小数据集)/近似算法(大数据集) 。
            #'scale_pos_weight': # 是用来调节正负样本不均衡问题的，用助于样本不平衡时训练的收敛（应该是增大了少数样本的学习率）。- 如何你仅仅关注预测问题的排序或者AUC指标，那么你尽管可以调节此参数。如果你希望得到真正的预测概率则不能够通过此参数来平衡样本
        }
        booster_linear_param = {
            'lambda': 1,   # [default=1] 又是个系数，这个是控制L2正则的，就是目标函数里的那个叶子节点得分前边的系数，用不用看你自己了。
            'alpha': 0,  # [default=0] 在建立树时对特征采样的比例有L2就有L1，用不用全凭自己了。
            'lambda_bias': 0,  # [default=0] 在偏置上的L2正则。缺省值为0（在L1上没有偏置项的正则，因为L1时偏置不重要）
        }
        # 学习目标参数,跟目标函数有关,控制学习的场景，例如在回归问题中会使用不同的参数控制排序
        object_param = {
            'objective': 'binary:logistic',  # [ default=reg:linear ] 定义学习任务及相应的学习目标，可选的目标函数如下,包含的函数还挺多，默认是线形的。此外你还可以选择：binary:logistic 二分类的逻辑回归，返回预测的概率(不是类别).
            'eval_metric':['error','auc'],  # [默认值取决于objective参数的取值] 也就是说怎么计算目标函数值，根据你目标函数的形式来，对于回归问题，默认值是rmse，对于分类问题，默认值是error。
            'base_score': 0.5,  # [ default=0.5 ]
            'seed':666,  # [ default=0 ] 随机数的种子。缺省值为0
        }
        param.update(general_param)
        param.update(booster_tree_param)
        param.update(object_param)
        param.update(kwargs)
        return param

    def train(self,train_feature, train_label, test_feature=pd.DataFrame(), test_label=pd.DataFrame(),eval=True,
              eval_plot=False,num_boost_round=200,early_stopping_rounds=50):
        '''

        :param train_feature: pd.DataFrame
        :param train_label:
        :param test_feature:
        :param test_label:
        :return:
        '''
        self.feature_columns = train_feature.columns
        if (test_feature.empty or test_label.empty):
            train_feature, test_feature, train_label, test_label = \
                train_test_split(train_feature, train_label, test_size=0.2, random_state=0)
        dtrain = xgb.DMatrix(data=train_feature, label=train_label, missing=self.missing_value)
        dtest = xgb.DMatrix(data=test_feature, label=test_label, missing=self.missing_value)
        evallist = [(dtrain, 'train'), (dtest, 'test')]  # 如果说eval_metric有很多个指标(evals)，那就以最后一个指标为准
        # 当logloss在设置early_stopping_rounds轮迭代之内，都没有提升的话，就stop。
        self.model_ = xgb.train(self.param, dtrain, num_boost_round=num_boost_round, evals=evallist,
                                early_stopping_rounds=early_stopping_rounds)
        if eval:
            # 模型评估
            print("training eval:")
            df_pre, _ = self.predict(train_feature)
            auc, _ = self.get_auc(df_pre,train_label)
            ks, _ = self.get_ks(df_pre, train_label)
            lift, _ = self.get_lift(df_pre, train_label)
            print("auc={}, ks={}, lift={}".format(auc, ks['gap'].values[0],lift))

            print('testing eval:')
            df_pre, _ = self.predict(test_feature)
            auc, _ = self.get_auc(df_pre, test_label)
            ks, _ = self.get_ks(df_pre, test_label)
            lift,_ = self.get_lift(df_pre, test_label)
            print("auc={}, ks={}, lift={}".format(auc, ks['gap'].values[0],lift))

        if eval_plot:
            df_pre, _ = self.predict(test_feature)
            self.plot_roc(df_pre, test_label, pre_target=1, save_path='.')
            self.plot_ks(df_pre, test_label, pre_target=1, save_path='.')
            self.plot_lift(df_pre, test_label, pre_target=1, save_path='.')

    def predict(self,x):
        '''
        :param x: list/datafame
        :return: array([proba]),array([score_label])
        '''
        dmatrix = xgb.DMatrix(np.array(x), feature_names=self.feature_columns, missing=self.missing_value)
        predict = self.model_.predict(dmatrix)
        score_label = np.array([self.probability_to_score(bad_prob=proba_i) for proba_i in predict])
        return predict, score_label


if __name__ == '__main__':
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 6, 8, 3, 2, 1, 5, 7],[10, 2, 3, 42, 534, 5, 53, 6, 83, 3, 42, 21, 25, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field1', 'field2', 'label']
    df_fields, df_label = df[['field1','field2']], df['label']
    lf = XGBModel(aa=34,missing_value=99)
    lf.train(df_fields,df_label,eval=True)
    print(lf.predict([[2,3]]))
    print(lf.predict(df_fields.head()))
