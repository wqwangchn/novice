# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-06-16 16:39
Desc:
'''
from sklearn.linear_model import LogisticRegression

def explain_in_detail():
    explain_base = '''
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression(penalty='l2', dual=False, tol=1e-4, C=1.0,
                 fit_intercept=True, intercept_scaling=1, class_weight=None,
                 random_state=None, solver='liblinear', max_iter=100,
                 multi_class='ovr', verbose=0, warm_start=False, n_jobs=1)
    '''
    explain_info = {
        "penalty": '''
         penalty:正则化选择参数，参数可选值为l1和l2，分别对应l1正则化和l2正则化，默认是l2正则化。

调整该参数的目的主要是为了防止过拟合，一般penalty选择l2正则化就够啦，但是如果选择l2正则化发现依然过拟合，即预测效果还是很差的时候，就可以考虑l1正则化。如果模型的特征非常多，我们希望做一些特征选择（即把一些不重要的特征过滤掉），这个时候也可以考虑用l1正则化。

penalty参数的选择会影响我们损失函数优化算法的选择，即参数solver的选择，如果是l2正则化，可选的优化算法 {‘newton-cg’, ‘lbfgs’, ‘liblinear’, ‘sag’}都可以选择。但是如果penalty是L1正则化的话，就只能选择‘liblinear’了。这是因为L1正则化的损失函数不是连续可导的，而{‘newton-cg’, ‘lbfgs’,‘sag’}这三种优化算法时都需要损失函数的一阶或者二阶连续导数。而‘liblinear’并没有这个依赖。这几个优化方法在solver参数环节进行讲述。
        '''
    }

    return explain_base

if __name__ == '__main__':
    aa=explain_in_detail()
    print(aa)
