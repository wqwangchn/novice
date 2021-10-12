# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/8/16 14:47
Desc:
'''

import numpy as np
import pandas as pd
from sklearn.metrics import explained_variance_score
from sklearn.metrics import r2_score
from sklearn.metrics import max_error
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import average_precision_score
from statsmodels.stats.outliers_influence import variance_inflation_factor
import logging


class _Tool():
    def KS(y_true, y_hat, sample_weight=None):
        if isinstance(y_true, np.ndarray):
            y_true = pd.Series(y_true)
        if sample_weight is None:
            sample_weight = pd.Series(np.ones_like(y_true), index=y_true.index)
        if isinstance(y_hat, np.ndarray):
            y_hat = pd.Series(y_hat, index=y_true.index)
        sample_weight.name = 'sample_weight'
        y_true.name = 'y'
        y_hat.name = 'score'
        df = pd.concat([y_hat, y_true, sample_weight], axis=1)
        df['y_mutli_w'] = df['y'] * df['sample_weight']
        total = df.groupby(['score'])['sample_weight'].sum()
        bad = df.groupby(['score'])['y_mutli_w'].sum()
        all_df = pd.DataFrame({'total': total, 'bad': bad})
        all_df['good'] = all_df['total'] - all_df['bad']
        all_df.reset_index(inplace=True)
        all_df = all_df.sort_values(by='score', ascending=False)
        all_df['badCumRate'] = all_df['bad'].cumsum() / all_df['bad'].sum()
        all_df['goodCumRate'] = all_df['good'].cumsum() / all_df['good'].sum()
        ks = all_df.apply(lambda x: x.goodCumRate - x.badCumRate, axis=1)
        return np.abs(ks).max()

    def vif(df):
        vif = pd.DataFrame()
        vif['features'] = df.columns
        if df.shape[1] > 1:
            vif['VIF Factor'] = [variance_inflation_factor(df.values, i) for i in range(df.shape[1])]
        else:
            vif['VIF Factor'] = 0
        vif = vif.sort_values('VIF Factor', ascending=False)
        return vif

    def make_logger(is_logger, logger_file):
        logger_level = logging.INFO if is_logger else logging.DEBUG
        logging.getLogger().setLevel(logger_level)
        fh = None
        if logger_file is not None:
            fh = logging.FileHandler(logger_file, mode='w')
            fh.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '[%(name)s]-[%(filename)s-%(lineno)d]-[%(processName)s]-[%(asctime)s]-[%(levelname)s]: %(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        return logging, fh

SCORERS = dict(
    r2=r2_score,
    explained_variance_score=explained_variance_score,
    max_error=max_error,
    accuracy=accuracy_score,
    roc_auc=roc_auc_score,
    balanced_accuracy=balanced_accuracy_score,
    average_precision=average_precision_score,
    ks=_Tool.KS)