# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 14:53:31 2020

@author: 王文皓(wangwenhao)

"""
import statsmodels.api as sm
import os

import numpy as np
import pandas as pd
from itertools import repeat
from .Tool import _Tool
from .Tool import SCORERS
from multiprocessing import Pool
import math

class Regression():
    def __init__(self,X,y,fit_weight=None,measure='ks',measure_weight=None,kw_measure_args=None,max_pvalue_limit=0.05,max_vif_limit=3,max_corr_limit=0.6,coef_sign=None,iter_num=20,kw_algorithm_class_args=None,n_core=None,logger_file_CH=None,logger_file_EN=None):
        self.X = X
        self.y = y
        self.fit_weight=np.ones(len(X))#fit_weight
        self.measure = measure
        self.kw_measure_args = {'sample_weight':measure_weight}
        if kw_measure_args is not None:
            self.kw_measure_args.update(kw_measure_args)
        self.max_pvalue_limit = max_pvalue_limit
        self.max_vif_limit = max_vif_limit
        self.max_corr_limit = max_corr_limit
        self.coef_sign = coef_sign
        self.iter_num = iter_num
        self.kw_algorithm_class_args = kw_algorithm_class_args
        self.logger_file_CH = logger_file_CH
        self.logger_file_EN = logger_file_EN
        if n_core is None:
            self.n_core = os.cpu_count()-1
        elif n_core >=1:
            self.n_core = n_core
        else:
            self.n_core = math.ceil(os.cpu_count() * n_core)
    
    def _check(self,clf,in_vars,current_perf):
        X = self.X[in_vars]
        check_param=True
        if isinstance(self.coef_sign,dict):
            coef_pos = {k: v for k, v in self.coef_sign.items() if v == '+'}
            if len(coef_pos)>0:
                check_param = (clf.params[clf.params.index.isin(coef_pos)]> 0).all()
                if check_param:
                    coef_neg = {k: v for k, v in self.coef_sign.items() if v == '-'}
                    if len(coef_neg) > 0:
                        check_param = (clf.params[clf.params.index.isin(coef_neg)]< 0).all()
        elif self.coef_sign == '+':
            check_param = (clf.params[1:] > 0).all()
        elif self.coef_sign == '-':
            check_param = (clf.params[1:] < 0).all()
        
        check_pvalue = (clf.pvalues < self.max_pvalue_limit).all()
        y_hat=pd.Series(clf.predict(sm.add_constant(X)),index=self.y.index,name='score')     
        perf = SCORERS[self.measure](self.y,y_hat,**self.kw_measure_args)
        check_perf = perf > current_perf 
        if X.shape[1] <2:
            corr_max = 0
            vif = 0
        else:
            vif = _Tool.vif(X).iloc[0,1]
            df_corr = X.corr()
            t = np.arange(df_corr.shape[1])
            df_corr.values[t,t] = np.nan
            corr_max = df_corr.max().max()
        check_vif = vif < self.max_vif_limit
        check_corr = corr_max < self.max_corr_limit
        
        return check_param,check_pvalue,check_perf,perf,check_vif,vif,check_corr,corr_max 

    def _add_var(self,args):
        col = args[0]
        in_vars,current_perf = args[1]
        add_rm_var=(None,None,current_perf)
        tmp_cols=[col]
        tmp_cols.extend(in_vars)
        clf = self._regression(tmp_cols)
        check_param,check_pvalue,check_perf,perf,check_vif,vif,check_corr,corr_max = self._check(clf,tmp_cols,current_perf)
        if check_perf: 
            if check_param and check_pvalue and check_vif and check_corr:
                add_rm_var=(col,None,perf)
            else:
                if len(in_vars) > 0:
                    rm_var_arr =  map(self._rm_var,zip(in_vars,repeat((tmp_cols,current_perf))))
                    rm_var,perf = sorted(rm_var_arr, key=lambda x:x[1])[-1]
                    if rm_var:
                        add_rm_var=(col,rm_var,perf)
        return add_rm_var    
    
    def _rm_var(self,args):
        col = args[0]
        in_vars,current_perf = args[1]
        rm_var=(None,current_perf)
        X_tmp=self.X[in_vars]
        X_tmp=X_tmp.loc[:,X_tmp.columns!=col]
        clf = self._regression(list(X_tmp.columns))
        check_param,check_pvalue,check_perf,perf,check_vif,vif,check_corr,corr_max = self._check(clf,list(X_tmp.columns),current_perf)
        check_pass=(check_param and check_pvalue and check_vif and check_corr and check_perf)
        if check_pass:
            rm_var=(col,perf)     
        return rm_var
    
    def _del_reason(self,args):
        col = args[0]
        in_vars,current_perf = args[1]
        tmp_cols = [col]
        tmp_cols.extend(in_vars)

        clf = self._regression(tmp_cols)
        check_param,check_pvalue,check_perf,perf,check_vif,vif,check_corr,corr_max = self._check(clf,tmp_cols,current_perf)
        
        reasons = []
        reasons_en = []
        if not check_perf:
            reasons.append('模型性能=%f,小于等于最终模型的性能=%f'%(perf,current_perf))
            reasons_en.append('the performance index of model=%f,less or equals than the performance index of final model=%f'%(perf,current_perf))
        if not check_vif:
            reasons.append('最大VIF=%f,大于设置的阈值=%f'%(vif,self.max_vif_limit))
            reasons_en.append('the max VIF=%f,more than the setting of max_vif_limit=%f'%(vif,self.max_vif_limit))
        if not check_corr:
            reasons.append('最大相关系数=%f,大于设置的阈值=%f'%(corr_max,self.max_corr_limit))
            reasons_en.append('the max correlation coefficient=%f,more than the setting of max_corr_limit=%f'%(corr_max,self.max_corr_limit))
        if not check_pvalue: 
            reasons.append('有些系数不显著，P_VALUE大于设置的阈值=%f'%(self.max_pvalue_limit))
            reasons_en.append('some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=%f'%(self.max_pvalue_limit))
        if not check_param:
            reasons.append('有些系数不符合coef_sign的设置')
            reasons_en.append('some setting of coef_sign are unreachable')
        return (col,reasons,reasons_en)
    
    def fit(self):
        '''
        中文版 
        训练模型
        
        
        Returns
        -------
        in_vars : list
        所有的入模变量列表，列表中的顺序即为加入时的顺序
            
        clf_final : statsmodels.genmod.generalized_linear_model.GLMResultsWrapper
        最终的逐步回归的模型
            
        dr : dict
        删除原因，其结构为:{'变量名称':([...],[...])}
        每个dr的value是一个含有两个元素的tuple，第一个为中文给出的删除原因，第二个为英文给出的删除原因。每个元素是一个list，记录了对应变量(key)的所有删除原因。如果某一个特征对应的list里没有任何元素，则应考虑将这个特征手工的加入到模型中去。
        
        English Document
        Fitting a model
        
        
        Returns
        -------
        in_vars : list
        All variables to be picked up by model.The order in list is same with the order of to be added
            
        clf_final : statsmodels.genmod.generalized_linear_model.GLMResultsWrapper
        A final step-wise model
        
        dr : dict
        deletion reason.It`s format is {'var_name':([...],[...])}
        Every value in dr contains a tuple including two elements.The first element is reason in Chinese and the second in English.Every element is a list and record all deletion reason of variable(matching key).Some features should be added into model manually,if a list corresponding these features has no any element.
        '''
        c=0
        in_vars = []
        current_perf = -np.inf
        logger_ch = None
        logger_en = None
        if self.logger_file_CH is not None:
            logger_ch,fh_ch = _Tool.make_logger('LogisticReg_Step_Wise_MP_CH',self.logger_file_CH)
        
        if self.logger_file_EN is not None:
            logger_en,fh_en = _Tool.make_logger('LogisticReg_Step_Wise_MP_EN',self.logger_file_EN)
            
        while(True):
            c+=1
            if c > self.iter_num:
                break            
            if logger_ch:
                logger_ch.info('****************迭代轮数：%d********************'%c)
            if logger_en:
                logger_en.info('****************Iterate Number:%d********************'%c) 
            
            out_vars = self.X.columns[~self.X.columns.isin(in_vars)]
            if len(out_vars) == 0:
                if logger_ch:
                    logger_ch.info('变量全部进入模型，建模结束')
                if logger_en:
                    logger_en.info('All variables are picked by step model. Modeling is completed!')
                break
            with Pool(self.n_core) as pool:
                result = pool.map_async(self._add_var, zip(out_vars,repeat((in_vars,current_perf))))
                add_rm_var_arr = result.get()
            add_var,rm_var_0,perf = sorted(add_rm_var_arr, key=lambda x:x[2])[-1]
            if add_var is not None:
                in_vars.append(add_var)
                current_perf=perf
                if rm_var_0:
                    in_vars.remove(rm_var_0)
            if len(in_vars)==0:
                if logger_ch:
                    logger_ch.info('没有变量能够进入模型，建模结束')
                if logger_en:
                    logger_en.info('All variables can`t be picked by step model. Modeling is completed!')
                break
            with Pool(self.n_core) as pool:
                result =  pool.map_async(self._rm_var,zip(in_vars,repeat((in_vars,current_perf))))
                rm_var_arr = result.get()
            rm_var,perf = sorted(rm_var_arr, key=lambda x:x[1])[-1]
            if rm_var is not None:
                in_vars.remove(rm_var)
                current_perf=perf
            if (add_var is None) and (rm_var is None): 
                if logger_ch:
                    logger_ch.info('在此轮迭代中，在满足使用者所设置条件的前提下，已经不能通过增加或删除变量来进一步提升模型的指标，建模结束')
                if logger_en:
                    logger_en.info('At this iteration,it`s not reachable under conditions you set that promoting performance index of model by adding or removing any variable. Modeling is completed!')
                break
            if logger_ch:
                logger_ch.info('此轮迭代完成，当前入模变量为：%s。 当前模型性能%s为:%f'%(in_vars,self.measure,current_perf))
            if logger_en:
                logger_en.info('This iteration is end.Current variables in model are %s.The performance of model is %s=%f'%(in_vars,self.measure,current_perf))
                
        clf_final = self._regression(in_vars)
        out_vars = self.X.columns[~self.X.columns.isin(in_vars)]
        with Pool(self.n_core) as pool:
            result = pool.map_async(self._del_reason,zip(out_vars,repeat((in_vars,current_perf))))
            del_var_arr = result.get()
        dr=dict((col,(reasons,reasons_en)) for col,reasons,reasons_en in del_var_arr)
        if logger_ch:
            fh_ch.close()
            logger_ch.removeHandler(fh_ch)
        if logger_en:
            fh_en.close()
            logger_en.removeHandler(fh_en)
        return in_vars,clf_final,dr