# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/8/16 14:17
Desc:
'''
# glm中的pvalue值??

import statsmodels.api as sm
import os
import numpy as np
import pandas as pd
from itertools import repeat
from multiprocessing import Pool
import math
from sklearn.model_selection import train_test_split
from .util import _Tool,SCORERS


class Regression():
    def __init__(self, X:pd.DataFrame, Y, model=None, sample_weight = None,iter_num=20,
                 is_train_test_split=True, test_size=0.4, split_num=10, kw_measure_args={},
                 measure = 'ks', max_pvalue_limit=0.05, max_vif_limit=3, max_corr_limit=0.6,seed=666,
                n_core=None, logger_file=None):
        # fit_weight = None, measure_weight = None, kw_measure_args = None,
        # kw_algorithm_class_args = None


        '''
        :param X: 数据特征集合,pd.DataFrame
        :param Y: 数据标签，一维list
        :param model: 评估所使用的模型
        :param iter_num: 最大迭代次数,预估筛选出多少个特征
        :param measure: 评估指标
        :param max_pvalue_limit: 错误拒绝H0的概率很低，表示H0本身(两者无关联)就是错误的。两者两者有关联，这个独立变量重要。
        :param max_vif_limit: 方差膨胀系数，是对多重共线性严重程度的一种度量。它表示回归系数估计量的方差与假设自变量间不线性相关时方差
                相比的比值。一般>5或者>10表示严重多重共线
        :param max_corr_limit: 皮尔逊相关系数。值越大表示越相关
        :param n_core: 进程数
        :param logger_file: 日志地址
        '''
        if model is None:
            self.model = self._regression
        else:
            self.model=model
        self.sample_weight=sample_weight
        self.measure = measure
        self.max_pvalue_limit = max_pvalue_limit
        self.max_vif_limit = max_vif_limit
        self.max_corr_limit = max_corr_limit
        self.is_trte_split=is_train_test_split
        self.test_size=test_size
        self.split_num=split_num
        self.kw_measure_args = kw_measure_args
        self.iter_num = iter_num
        self.logger_file = logger_file
        self.seed=seed

        if n_core is None:
            self.n_core = os.cpu_count() - 1
        elif n_core >= 1:
            self.n_core = n_core
        else:
            self.n_core = math.ceil(os.cpu_count() * n_core)

        self._check_input_data(X,Y)

    def _check_input_data(self,X,Y):
        dataset = []
        if self.is_trte_split:
            seed_state = np.random.RandomState(seed=self.seed)
            seed_set = [int(_ * 10000) for _ in seed_state.rand(self.split_num)]
            for seed_i in seed_set:
                X_train, X_valid, Y_train, Y_valid = train_test_split(X, Y, test_size=0.4,random_state=seed_i)
                dataset.append([X_train, X_valid, Y_train, Y_valid])
        else:
            X_train, X_valid, Y_train, Y_valid = X, Y, X, Y
            dataset.append([X_train, X_valid, Y_train, Y_valid])
        self.dataset=dataset
        self.columns=dataset[0][0].columns

    def _check(self, in_vars, current_perf):

        # 多次抽样
        pvalue_list=[]
        perf_list=[]
        for i in self.dataset:
            X_train, X_valid, Y_train, Y_valid =i
            X_train, X_valid=X_train[in_vars], X_valid[in_vars]
            clf = self.model(X_train,Y_train)
            Y_valid_pre = pd.Series(clf.predict(sm.add_constant(X_valid)), index=Y_valid.index, name='score')
            ipvalue = clf.pvalues ## 1.待修改
            pvalue_list.append(ipvalue)
            iperf = SCORERS[self.measure](Y_valid, Y_valid_pre, **self.kw_measure_args) ## 2.评价指标
            perf_list.append(iperf)
        df_pvalues =pd.concat(pvalue_list,axis=1).mean(1)
        perfs = np.mean(perf_list)


        X = pd.concat([X_train,X_valid],axis=0)
        if X.shape[1] < 2:
            corr_max = 0
            vif = 0
        else:
            vif = _Tool.vif(X).iloc[0, 1]
            df_corr = X.corr()
            t = np.arange(df_corr.shape[1])
            df_corr.values[t, t] = np.nan
            corr_max = df_corr.max().max()

        check_pvalue = (df_pvalues < self.max_pvalue_limit).all()
        check_perf = perfs > current_perf
        check_vif = vif < self.max_vif_limit
        check_corr = corr_max < self.max_corr_limit
        return check_pvalue, check_perf, perfs, check_vif, vif, check_corr, corr_max

    def _add_var(self, args):
        col = args[0]
        in_vars, current_perf = args[1]
        add_rm_var = (None, None, current_perf)
        tmp_cols = [col]
        tmp_cols.extend(in_vars)
        check_pvalue, check_perf, perf, check_vif, vif, check_corr, corr_max = self._check(tmp_cols,current_perf)
        if check_perf:
            if check_pvalue and check_vif and check_corr:
                add_rm_var = (col, None, perf)
            else:
                if len(in_vars) > 0:
                    rm_var_arr = map(self._rm_var, zip(in_vars, repeat((tmp_cols, current_perf))))
                    rm_var, perf = sorted(rm_var_arr, key=lambda x: x[1])[-1]
                    if rm_var:
                        add_rm_var = (col, rm_var, perf)
        return add_rm_var

    def _rm_var(self, args):
        col = args[0]
        in_vars, current_perf = args[1]
        rm_var = (None, current_perf)
        X_col = list(set(in_vars)-set([col]))
        check_pvalue, check_perf, perf, check_vif, vif, check_corr, corr_max = self._check(X_col, current_perf)
        check_pass = (check_pvalue and check_vif and check_corr and check_perf)
        if check_pass:
            rm_var = (col, perf)
        return rm_var

    def _del_reason(self, args):
        col = args[0]
        in_vars, current_perf = args[1]
        tmp_cols = [col]
        tmp_cols.extend(in_vars)
        check_pvalue, check_perf, perf, check_vif, vif, check_corr, corr_max = self._check(tmp_cols,current_perf)

        reasons = []
        if not check_perf:
            reasons.append('模型性能=%f,小于等于最终模型的性能=%f' % (perf, current_perf))
        if not check_vif:
            reasons.append('最大VIF=%f,大于设置的阈值=%f' % (vif, self.max_vif_limit))
        if not check_corr:
            reasons.append('最大相关系数=%f,大于设置的阈值=%f' % (corr_max, self.max_corr_limit))
        if not check_pvalue:
            reasons.append('有些系数不显著，P_VALUE大于设置的阈值=%f' % (self.max_pvalue_limit))
        return (col, reasons)

    def fit(self):
        '''
        :return:
            in_vars : list,所有的入模变量列表，列表中的顺序即为加入时的顺序
            out_vars : dict,剔除的变量列表及删除原因，其结构为:{'变量名称':[删除原因]}
        '''
        iter_idx = 0
        in_vars = []
        current_perf = -np.inf
        logger_ch = None
        if self.logger_file is not None:
            logger_ch, fh_ch = _Tool.make_logger('LogisticReg_Step_Wise_MP_CH', self.logger_file_CH)

        while (True):
            iter_idx += 1
            if iter_idx > self.iter_num:
                break
            if logger_ch:
                logger_ch.info('****************迭代轮数：%d********************' % c)

            out_vars = self.columns[~self.columns.isin(in_vars)]
            if len(out_vars) == 0:
                if logger_ch:
                    logger_ch.info('变量全部进入模型，建模结束')
                break

            with Pool(self.n_core) as pool:
                result = pool.map_async(self._add_var, zip(out_vars, repeat((in_vars, current_perf))))
                add_rm_var_arr = result.get()
            add_var, rm_var_0, perf = sorted(add_rm_var_arr, key=lambda x: x[2])[-1]
            if add_var is not None:
                in_vars.append(add_var)
                current_perf = perf
                if rm_var_0:
                    in_vars.remove(rm_var_0)
            if len(in_vars) == 0:
                if logger_ch:
                    logger_ch.info('没有变量能够进入模型，建模结束')
                break
            with Pool(self.n_core) as pool:
                result = pool.map_async(self._rm_var, zip(in_vars, repeat((in_vars, current_perf))))
                rm_var_arr = result.get()
            rm_var, perf = sorted(rm_var_arr, key=lambda x: x[1])[-1]
            if rm_var is not None:
                in_vars.remove(rm_var)
                current_perf = perf
            if (add_var is None) and (rm_var is None):
                if logger_ch:
                    logger_ch.info('在此轮迭代中，在满足使用者所设置条件的前提下，已经不能通过增加或删除变量来进一步提升模型的指标，建模结束')
                break
            if logger_ch:
                logger_ch.info('此轮迭代完成，当前入模变量为：%s。 当前模型性能%s为:%f' % (in_vars, self.measure, current_perf))

        out_vars = self.columns[~self.columns.isin(in_vars)]
        with Pool(self.n_core) as pool:
            result = pool.map_async(self._del_reason, zip(out_vars, repeat((in_vars, current_perf))))
            del_var_arr = result.get()
        del_vars = dict((col, reasons) for col, reasons in del_var_arr)
        if logger_ch:
            fh_ch.close()
            logger_ch.removeHandler(fh_ch)
        return in_vars, del_vars


    def _regression(self,X,Y,weights=None,**kwargs):
        if weights is None:
            weights = np.ones(len(X))
        reg = sm.WLS(Y, sm.add_constant(X), weights=weights, **kwargs)
        clf = reg.fit()
        return clf