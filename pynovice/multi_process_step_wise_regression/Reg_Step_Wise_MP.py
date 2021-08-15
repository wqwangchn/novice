# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 14:53:31 2020

@author: 王文皓(wangwenhao)

一个python版本的逐步回归，提供了逐步逻辑回归和逐步线性回归
在添加特征和删除特征时使用多进程来并行计算来决定每个特征是否应该加入或删除模型
支持多进程,Windows系统的多进程版本也被支持

A step-wise regression with python.It has step-wise logstic regression and step-wise linear regression.
It uses multiprocessing when deciding to add or remove features.
It works with multi-processing.Supporting Windows system multi-processing too.

usage:

import MultiProcessMStepRegression as mpmr
from sklearn.datasets import make_classification,make_regression
import pandas as pd

def get_X_y(data_type):
    if data_type == 'logistic':
        #含有信息的变量个数：4个
        #冗余变量个数：2。 冗余变量是有信息变量的线性组合
        #无用变量个数=10-4-2=4。
        
        #number of informative features = 4
        #number of redundant features = 2.redundant feature is linear combinations of the informative features
        #number of useless features = 10-4-2=4
        X, y = make_classification(n_samples=200,n_features=10,n_informative=4,n_redundant=2,shuffle=False,random_state=0,class_sep=2)
        X = pd.DataFrame(X,columns=['informative_1','informative_2','informative_3','informative_4','redundant_1','redundant_2','useless_1','useless_2','useless_3','useless_4']).sample(frac=1)
        y=pd.Series(y).loc[X.index]
        
    if data_type == 'linear':
        # 含有信息的变量个数：6个
        # 特征矩阵的秩：2个（说明含有信息量的6个变量中存在共线性）
        
        # number of informative features = 6
        # matrix rank = 2 (implying collinearity between six informative features)
        X, y = make_regression(n_samples=200,n_features=10,n_informative=6,effective_rank=2,shuffle=False,random_state=0)#
        X = pd.DataFrame(X,columns=['informative_1','informative_2','informative_3','informative_4','informative_5','informative_6','useless_1','useless_2','useless_3','useless_4']).sample(frac=1)
        y=pd.Series(y).loc[X.index]
    return X, y
    
def test_logit(X,y):
  #   从结果可以看出：
  #   1.算法选出了全部有效变量。
  #   2.排除了所有线性组合变量，而且排除的理由是超出VIF或相关系数的设置或系数不显著。
  #   3.排除了所有无效变量，排除的原因是模型性能没有提升或系数不显著
    
  #   As can be seen:
  #   1.All informative features are picked up by this algorithm
  #   2.All linear combinations features are excluded and the reasons are over the max_vif_limit or  max_corr_limit or max_pvalue_limit
  #   3.All useless features are excluded and the reasons are no lift on the perfermance of model or over max_pvalue_limit
    
  #   return
  #    in_vars = ['informative_3', 'informative_4', 'informative_2', 'informative_1']
  #
  #    dr = {'redundant_1': (['模型性能=0.956100,小于等于最终模型的性能=0.956100',
  #   '最大VIF=inf,大于设置的阈值=3.000000',
  #   '最大相关系数=0.925277,大于设置的阈值=0.600000',
  #   '有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['the performance index of model=0.956100,less or equals than the performance index of final model=0.956100',
  #   'the max VIF=inf,more than the setting of max_vif_limit=3.000000',
  #   'the max correlation coefficient=0.925277,more than the setting of max_corr_limit=0.600000',
  #   'some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000']),
  # 'redundant_2': (['模型性能=0.956100,小于等于最终模型的性能=0.956100',
  #   '最大VIF=inf,大于设置的阈值=3.000000',
  #   '最大相关系数=0.676772,大于设置的阈值=0.600000',
  #   '有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['the performance index of model=0.956100,less or equals than the performance index of final model=0.956100',
  #   'the max VIF=inf,more than the setting of max_vif_limit=3.000000',
  #   'the max correlation coefficient=0.676772,more than the setting of max_corr_limit=0.600000',
  #   'some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000']),
  # 'useless_1': (['模型性能=0.955200,小于等于最终模型的性能=0.956100',
  #   '有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['the performance index of model=0.955200,less or equals than the performance index of final model=0.956100',
  #   'some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000']),
  # 'useless_2': (['有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000']),
  # 'useless_3': (['有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000']),
  # 'useless_4': (['模型性能=0.955800,小于等于最终模型的性能=0.956100',
  #   '有些系数不显著，P_VALUE大于设置的阈值=0.050000'],
  #  ['the performance index of model=0.955800,less or equals than the performance index of final model=0.956100',
  #   'some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.050000'])}
    lr  =  mpmr.LogisticReg(X,y,measure='roc_auc',iter_num=20,logger_file_EN='c:/temp/mstep_en.log',logger_file_CH='c:/temp/mstep_ch.log')
    in_vars,clf_final,dr = lr.fit()
    return in_vars,clf_final,dr
    

def test_linear(X,y):
 #    从结果可以看出：
 #    选出的变量来自有信息量的变量
 #    选出变量的个数等于特征矩阵秩的个数
    
 #    As can be seen:
 #    The picked features is from informative features
 #    The number of picked features equals matrix rank
    
 #    return 
 #    ['informative_2', 'informative_6']
 #    dr = {'informative_1': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'informative_3': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'informative_4': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'informative_5': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'useless_1': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'useless_2': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'useless_3': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000']),
 # 'useless_4': (['有些系数不显著，P_VALUE大于设置的阈值=0.100000'],
 #  ['some coefficients are not significant,P_VALUE is more than the setting of max_pvalue_limit=0.100000'])}
    lr  =  mpmr.LinearReg(X,y,iter_num=20,max_pvalue_limit=0.1,logger_file_EN='c:/temp/mstep_en.log',logger_file_CH='c:/temp/mstep_ch.log')
    in_vars,clf_final,dr = lr.fit()
    return in_vars,clf_final,dr

#在windows中必须使用__main__才能使多进程被执行
#In windows,must use __main__ to make multi-processing running
if __name__ == '__main__':    
    X_logit, y_logit = get_X_y('logistic')
    in_vars_logit,clf_final_logit,dr_logit = test_logit(X_logit,y_logit)
    
    X_linear, y_linear = get_X_y('linear')
    in_vars_linear,clf_final_linear,dr_linear = test_linear(X_linear,y_linear)
"""
from statsmodels.genmod.generalized_linear_model import GLM
from statsmodels.genmod.families import Binomial
from statsmodels.genmod.families.links import logit
import statsmodels.api as sm
from .Reg_Sup_Step_Wise_MP import Regression

class LogisticReg(Regression):
    '''
    中文版文档(Document in English is in the next.）
    MultiProcessMStepRegression.LogisticReg:多进程逐步逻辑回归，其底层的逻辑回归算法使用的是statsmodels.genmod.generalized_linear_model.GLM。
    每一次向前添加过程中都会使用多进程来同时遍历多个解释变量，然后选取其中符合使用者设定的条件且能给逻辑回归带来最大性能提升的解释变量加入到模型中，如果所有变量都不能在满足使用者设置条件的前提下提升模型性能，则此次添加过程不加入任何变量。
    每一次的向后删除过程中也使用与向前添加过程同样的原则来决定删除哪个变量。
    在添加过程中模型性能有提升，但是部分条件不被满足，此时会额外触发一轮向后删除的过程，如果删除的变量与正要添加的变量为同一个，则此变量不被加入，添加流程结束。如果删除的变量与正要添加的变量不是同一个，则添加当前的变量，并将需要删除的变量从当前选中变量列表中排除。额外触发的向后删除过程与正常的向后删除过程的流程一致。
    在建模结束后，会将没有入选的解释变量分别加入到现有模型变量中，通过重新建模，会给出一个准确的没有入选该变量的原因。

    支持的功能点如下：
    1.支持双向逐步回归(Step_Wise)
    2.支持多进程，在每步增加变量或删除变量时，使用多进程来遍历每个候选变量。Windows系统也支持多进程。
    3.支持使用者指定的指标来作为变量添加或删除的依据，而不是使用AIC或BIC，在处理不平衡数据时可以让使用者选择衡量不平衡数据的指标
    4.支持使用者指定P-VALUE的阈值，如果超过该阈值，即使指标有提升，也不会被加入到变量中
    5.支持使用者指定VIF的阈值，如果超过该阈值，即使指标有提升，也不会被加入到变量中
    6.支持使用者指定相关系数的阈值，如果超过该阈值，即使指标有提升，也不会被加入到变量中
    7.支持使用者指定回归系数的正负号，在某些业务中，有些特征有明显的业务含义，例如WOE转换后的数据，就会要求回归系数均为正或均为负，加入对系数正负号的限制，如果回归系数不满足符号要求，则当前变量不会被加入到变量中
    8.上述4，5，6，7均在逐步回归中完成，挑选变量的同时校验各类阈值与符号
    9.会给出每一个没有入模变量被剔除的原因，如加入后指标下降，P-VALUE超出指定阈值，正负号与使用者的预期不符等等。
    10.支持中英文双语的日志，会将逐步回归中的每一轮迭代的情况记录到中文日志和英文日志中
    
    注意：因为该类会将数据X和y作为该类一个实例的属性，所以实例会比较大，因此非必要时，尽量不要保存MultiProcessMStepRegression.LogisticReg的实例。而是保存其返回的模型和删除原因等信息。
    
    
    Parameters    
    ----------
    X:DataFrame
    features
    
    y:Series
    target
    
    fit_weight:Series
    长度与样本量相同，为训练模型时的weight，如果取值为None（默认），则认为各个样本的训练权重相同。不要与模型性能评价的measure_weight混淆，二者可以一样也可以不一样，需要看使用者样本的抽样设计。例如：在建模时为了减少大类样本的影响，可以提高小类样本的权重，而在计算KS或者ROC_AUC等指标时，又将大类样本与小类样本的权重还原回实际样本的权重值，这么做是由于逻辑回归的损失函数是大类样本敏感的，所以需要通过训练权重来人为的做调整。而KS或ROC_AUC等指标的计算方式不会受到不平衡样本的影响，因此无需调整衡量指标的样本权重，除非使用者认为样本之间损失的惩罚力度不一样。
    注：在MultiProcessMStepRegression.LogisticReg中即使使用KS或ROC_AUC等衡量非平衡数据的指标来挑选特征，但是其底层还是标准的逻辑回归算法，因此MultiProcessMStepRegression.LogisticReg仍是大类样本敏感的。
    
    measure:str ks(默认) | accuracy | roc_auc | balanced_accuracy | average_precision
    计算逻辑回归模型性能的函数，y_true,y_hat和measure_weight会被自动传递进指定measure函数中，其余参数会由kw_measure_args传入
    
    measure_weight:Series
    长度与样本量相同，为度量模型性能时的weight，如果取值为None（默认），则认为各个样本的度量权重相同。
    参看 fit_weight
    
    kw_measure_args:dict | None(默认)
    measure函数除y_true,y_hat,measure_weight外，其余需要传入的参数都写入该dict里。None意味着不需要传入额外的参数
    
    max_pvalue_limit:float
    允许的P-VALUE的最大值。0.05（默认）

    max_vif_limit:float
    允许的VIF的最大值。3（默认）
    
    max_corr_limit:float
    允许的相关系数的最大值。0.6（默认）
    
    coef_sign:'+','-',dict,None（默认）
        如果知道X对y的影响关系--正相关或负相关，则可以对变量的符号进行约束。
        '+':所有X的系数都应为正数
        '-':所有X的系数都应为负数
        dict:格式如{'x_name1':'+','x_name2':'-'}，将已知的X的系数符号配置在dict中，以对回归结果中X的系数的正负号进行约束。没有被包含在dict中的变量，不对其系数进行约束
        None:所有X的系数的正负号都不被约束
        
    iter_num:int 
    挑选变量的轮数，默认为20。np.inf表示不限制轮数，当变量很多时，需要较长的运行时间。如果所有的变量都已经被选入到模型，或者不能通过增加或删除变量来进一步提升模型性能，则实际迭代轮数可能小于iter_num。每一轮挑选变量包含如下步骤：1.尝试将每一个还未被加入到模型中的变量加入到当前模型中，选出一个满足使用者设置的条件且使模型性能提升最多的变量加入到模型中。2.在当前模型中的每一个变量尝试删除，选出一个满足使用者设置的条件且使模型性能提升最多的变量移出模型。完成1，2两步即为完成一轮迭代。如果步骤1和2均未能挑选出变量，则迭代提前终止，无论是否达到了iter_num。
        
    kw_algorithm_class_args:dict
    除X，y，fit_weight外，其它需要传入逻辑回归算法（statsmodels.genmod.generalized_linear_model.GLM）的参数。
    注意：在statsmodels.genmod.generalized_linear_model.GLM中的y和X分别被叫做endog和exog
    
    n_core:int | float | None
    CPU的进程数。如果是int类型，则为使用CPU的进程数。如果是float类型，则为CPU全部进程数的百分比所对应的进程数（向上取整）。如果为None，则为使用全部CPU进程数-1
    
    logger_file_CH:str
    使用者指定的用于记录逐步回归过程的文件名，日志为中文日志。如果为None（默认）则不记录中文日志
    
    logger_file_EN:str
    使用者指定的用于记录逐步回归过程的文件名，日志为英文日志。如果为None（默认）则不记录英文日志



    Document in English
    MultiProcessMStepRegression.LogisticReg:A Step-Wise Logistic Regression handling with multi-processing.It bases on statsmodels.genmod.generalized_linear_model.GLM supplying a logistic regression algorithm
    In adding feature process,multi-processing is used to traversal several features concurrently.The feature which meets the conditions which the user set and get a max lift on measure index is added in the model.If any feature can`t improve the performance of model undering the conditions set by user ,no feature is added in current iteration. 
    The removing feature process has same policy with adding feature process to decide which feature should be removed.
    When adding process, if there is improving on performance of model but some conditions user set are missed,a additional removing process will start to run.If the feature to remove is same with the feature to add,the feature will not be added and the adding process is over.If They are not same,the feature to add is added in and the feature to remove is excluded from current list in which the picked features stay.The additional removing process has same procedure with removing process. 
    When modeling is compeleted,the features not picked up will respectively be added in picked features list. And then by rebuilding model with those features,a exact deletion reasons will return. 
    
    The characteristics are listed below:
    1.Supporting forward-backward Step-Wise.
    2.Supporting multi-processing.When adding or removing features,multi-processing is used to traversal all candidate features.
    3.Supporting that user could point the index instead of AIC/BIC for measuring model performance when adding or removing feaures.That is benifit when user`s data is unbalanced.
    4.Supporting that user could point p-value threshold.If max p-value is more than this threshold,the current features will not be added,although getting a lift on performance of model.
    5.Supporting that user could point VIF threshold.If max VIF is more than this threshold,the current features will not be added,although getting a lift on performance of model.
    6.Supporting that user could point coefficient of correlation threshold.If max coefficient of correlation is more than this threshold,the current features will not be added,although getting a lift on performance of model.
    7.Supporting that user could point sign to coefficients of regression. A part of features have sense in some business like woe transfer which require that all coefficients of regression are postive or negtive.If the signs requirement is not met,the current features will not be added,although getting a lift on performance of model.
    8.[4,5,6,7] above are completed in step-wise procedure.Picking features and verifing those thresholds and signs are simultaneous.
    9.Users will get reasons of which features isn`t picked up,as performance is fall or p-value is more than threshold or signs is not in accord with user`s expect and so on after adding this feature 
    10.Supporting the Chinese and English log in whcih user can get record of every iteration
    
    Note:As X and y is a property in a instance of MultiProcessMStepRegression.LogisticReg class,so that instance will be very large.Saving that instance is not recommended instead of saving the returned model and remove reasons.
    
    
    Parameters    
    ----------
    X:DataFrame
    features
    
    y:Series
    target
    
    fit_weight:Series
    The length of fit_weight is same with length of y.The fit_weight is for trainning data.If None(default),every sample has a same trainning weight.Don`t confuse fit_weight with measure_weight(mentioned below) that is for measuring model.It depends on user`s design on sample whether fit_weight is same with measure_weight or not.For example,for reducing effect from large class sample,it`s a good way to improve weights of small class sample when trainning model but the weight between large class sample and small class sample returns back to original weight value when measuring with some index like KS or ROC_AUC.Why doing like this is that the lost function of regression is large class sensitive.So the user need adjust sample weights.Some index like KS or ROC_AUC,their calculate way is non-sensitive in unbalanced sample situation,so the user need not adjust sample weights unless the user thinks that the loss penalty between samples is different.  
    note:Although the user set measure='KS' or 'ROC_AUC' to measure performance and pick features,but the MultiProcessMStepRegression.LogisticReg is still large class sensitive,due to the base algorithm is standard logistic regression yet. 
    
    
    measure:str ks(默认) | accuracy | roc_auc | balanced_accuracy | average_precision
    Performance evaluate function.The y_true,y_hat and measure_weight will be put into measure function automatically and the other parameters will be put into measure function with kw_measure_args
    
    measure_weight:Series
    The length of measure_weight is same with length of y.The measure_weight is for measuring function.If None(default),every sample has a same measuring weight.
    See also fit_weight
    
    kw_measure_args:dict | None(默认)
    Except y_true,y_hat and measure_weight,the other parameters need be put in kw_measure_args to deliver into measure function.
    None means that no other parameters delivers into measure function.
    
    max_pvalue_limit:float
    The max P-VALUE limit.
    0.05(default)

    max_vif_limit:float
    The max VIF limit.
    3(default)
    
    max_corr_limit:float
    The max coefficient of correlation limit. 
    0.6(default)
    
    coef_sign:'+','-',dict,None（默认）
    If the user have a priori knowledge on relation between X and y,like positive correlation or negtive correlation,user can make a constraint restriction on sign of resression coefficient by this parameter.
    '+':all signs of resression coefficients are positive
    '-':all signs of resression coefficients are negtive
    dict:the format is as {'x_name1':'+','x_name2':'-'}.Put coefficient and coefficient`s sign on which you have a priori knowledge into a dict and then constraint these signs that are in this dict. The coefficients not included in this dict will not be constrainted.
    None:all coefficients are not constrainted.
        
    iter_num:int 
    The iteration num for picking features.Default is 20.When np.inf,no limit to iteration num,if features are many,then the running time is long.If all features are already picked in model or no imporve on perfermance by adding/removing any feature,the actual iteration num should be samller than iter_num.The steps inclueed in every iteration is:1.Try adding feature which is not added in current model yet and then pick up one feature that makes most promotion for performance of model with satisfying user`s setting. 2.Try removing feature and then remove out one feature that makes most promotion for performance of model with satisfying user`s setting.It is means finshing one time iteration that step 1 and step 2 is completed.If all step 1 and step 2 can`t pick up any feature then iteration is pre-terminated,no matter whether iter_num is reached.
        
    kw_algorithm_class_args:dict
    Except X，y，fit_weight,the other parameters that are delivered into logistic regression algorithm is in kw_algorithm_class_args
    Note:y,X is called endog and exog in statsmodels.genmod.generalized_linear_model.GLM
    
    n_core:int | float | None
    Count of CPU processing.If int,user point the count.If float,the count is as percentage of all count transfered to int(ceil).If None(default),all count of CPU processing -1.
    
    logger_file_CH:str
    A log file name where log for step-wise procedure is recorded in Chinese.If None(default),not recording Chinese log.
    
    logger_file_EN:str
    A log file name where log for step-wise procedure is recorded in English.If None(default),not recording English log.
    
    '''
    def __init__(self,X,y,fit_weight=None,measure='ks',measure_weight=None,kw_measure_args=None,max_pvalue_limit=0.05,max_vif_limit=3,max_corr_limit=0.6,coef_sign=None,iter_num=20,kw_algorithm_class_args=None,n_core=None,logger_file_CH=None,logger_file_EN=None):
        Regression.__init__(self,X,y,fit_weight,measure,measure_weight,kw_measure_args,max_pvalue_limit,max_vif_limit,max_corr_limit,coef_sign,iter_num,kw_algorithm_class_args,n_core,logger_file_CH,logger_file_EN) 
            
    def _regression(self,in_vars):
        X = self.X[in_vars]
        if self.fit_weight is None:
            if self.kw_algorithm_class_args is not None:
                glm = GLM(self.y,sm.add_constant(X),family = Binomial(link=logit),**self.kw_algorithm_class_args)
            else:
                glm = GLM(self.y,sm.add_constant(X),family = Binomial(link=logit))
        else:
            if self.kw_algorithm_class_args is not None:
                glm = GLM(self.y,sm.add_constant(X),family = Binomial(link=logit),freq_weights = self.fit_weight,**self.kw_algorithm_class_args)
            else:
                glm = GLM(self.y,sm.add_constant(X),family = Binomial(link=logit),freq_weights = self.fit_weight)         
        clf = glm.fit()      
        clf.intercept_=[clf.params.const]
        clf.coef_=[clf.params[1:]]
        return clf

class LinearReg(Regression):
    '''
    中文版文档(Document in English is in the next.）
    MultiProcessMStepRegression.LinearReg:多进程逐步线性回归，其底层的线性回归算法使用的是statsmodels.api.OLS或statsmodels.api.WLS，依据用户是否使用训练样本权重来绝定。
    每一次向前添加过程中都会使用多进程来同时遍历多个解释变量，然后选取其中符合使用者设定的条件且能给线性回归带来最大性能提升的解释变量加入到模型中，如果所有变量都不能在满足使用者设置条件的前提下提升模型性能，则此次添加过程不加入任何变量。
    每一次的向后删除过程中也使用与向前添加过程同样的原则来决定删除哪个变量。
    在添加过程中模型性能有提升，但是部分条件不被满足，此时会额外触发一轮向后删除的过程，如果删除的变量与正要添加的变量为同一个，则此变量不被加入，添加流程结束。如果删除的变量与正要添加的变量不是同一个，则添加当前的变量，并将需要删除的变量从当前选中变量列表中排除。额外触发的向后删除过程与正常的向后删除过程的流程一致。
    在建模结束后，会将没有入选的解释变量分别加入到现有模型变量中，通过重新建模，会给出一个准确的没有入选该变量的原因。

    支持的功能点如下：
    1.支持双向逐步回归(Step_Wise)
    2.支持多进程，在每步增加变量或删除变量时，使用多进程来遍历每个候选变量。Windows系统也支持多进程。
    3.支持使用者指定的指标来作为变量添加或删除的依据，而不是使用AIC或BIC，在处理不平衡数据时可以让使用者选择衡量不平衡数据的指标
    4.支持使用者指定P-VALUE的阈值，如果超过该阈值，即使指标有提升，也不会被加入到变量中
    5.支持使用者指定VIF的阈值，如果超过该阈值，即使指标有提升，也不会被加入到变量中
    6.支持使用者指定相关系数的阈值，如果超过该阈值，即使指标有提升，也不会被加入到变量中
    7.支持使用者指定回归系数的正负号，在某些业务中，有些特征有明显的业务含义，例如WOE转换后的数据，就会要求回归系数均为正或均为负，加入对系数正负号的限制，如果回归系数不满足符号要求，则当前变量不会被加入到变量中
    8.上述4，5，6，7均在逐步回归中完成，挑选变量的同时校验各类阈值与符号
    9.会给出每一个没有入模变量被剔除的原因，如加入后指标下降，P-VALUE超出指定阈值，正负号与使用者的预期不符等等。
    10.支持中英文双语的日志，会将逐步回归中的每一轮迭代的情况记录到中文日志和英文日志中
    
    注意：因为该类会将数据X和y作为该类一个实例的属性，所以实例会比较大，因此非必要时，尽量不要保存MultiProcessMStepRegression.LinearReg的实例。而是保存其返回的模型和删除原因等信息。
    
    
    Parameters    
    ----------
    X:DataFrame
    features
    
    y:Series
    target
    
    fit_weight:Series
    长度与样本量相同，为训练模型时的weight，如果取值为None（默认），则认为各个样本的训练权重相同，选用statsmodels.api.OLS做为底层的实现算法。如果不为空，则会选用statsmodels.api.WLS做为底层的实现算法。在线性回归中设置权重的目的是，在异方差的情况下，训练出稳定的模型。
    
    measure:str r2(默认) | explained_variance_score | max_error
    计算线性回归模型性能的函数，y_true,y_hat和measure_weight会被自动传递进指定measure函数中，其余参数会由kw_measure_args传入
    
    measure_weight:Series
    长度与样本量相同，为度量模型性能时的weight，如果取值为None（默认），则认为各个样本的度量权重相同。
    
    kw_measure_args:dict | None(默认)
    measure函数除y_true,y_hat,measure_weight外，其余需要传入的参数都写入该dict里。None意味着不需要传入额外的参数
    
    max_pvalue_limit:float
    允许的P-VALUE的最大值。0.05（默认）

    max_vif_limit:float
    允许的VIF的最大值。3（默认）
    
    max_corr_limit:float
    允许的相关系数的最大值。0.6（默认）
    
    coef_sign:'+','-',dict,None（默认）
        如果知道X对y的影响关系--正相关或负相关，则可以对变量的符号进行约束。
        '+':所有X的系数都应为正数
        '-':所有X的系数都应为负数
        dict:格式如{'x_name1':'+','x_name2':'-'}，将已知的X的系数符号配置在dict中，以对回归结果中X的系数的正负号进行约束。没有被包含在dict中的变量，不对其系数进行约束
        None:所有X的系数的正负号都不被约束
        
    iter_num:int 
    挑选变量的轮数，默认为20。np.inf表示不限制轮数，当变量很多时，需要较长的运行时间。如果所有的变量都已经被选入到模型，或者不能通过增加或删除变量来进一步提升模型性能，则实际迭代轮数可能小于iter_num。每一轮挑选变量包含如下步骤：1.尝试将每一个还未被加入到模型中的变量加入到当前模型中，选出一个满足使用者设置的条件且使模型性能提升最多的变量加入到模型中。2.在当前模型中的每一个变量尝试删除，选出一个满足使用者设置的条件且使模型性能提升最多的变量移出模型。完成1，2两步即为完成一轮迭代。如果步骤1和2均未能挑选出变量，则迭代提前终止，无论是否达到了iter_num。
        
    kw_algorithm_class_args:dict
    除X，y，fit_weight外，其它需要传入线性回归算法（OLS，WLS）的参数。
    
    
    n_core:int | float | None
    CPU的进程数。如果是int类型，则为使用CPU的进程数。如果是float类型，则为CPU全部进程数的百分比所对应的进程数（向上取整）。如果为None，则为使用全部CPU进程数-1
    
    logger_file_CH:str
    使用者指定的用于记录逐步回归过程的文件名，日志为中文日志。如果为None（默认）则不记录中文日志
    
    logger_file_EN:str
    使用者指定的用于记录逐步回归过程的文件名，日志为英文日志。如果为None（默认）则不记录英文日志



    Document in English
    MultiProcessMStepRegression.LinearReg:A Step-Wise Linear Regression handling with multi-processing.It bases on statsmodels.api.OLS or statsmodels.api.WLS supplying a linear regression algorithm.Which algorithm should be used depends on the setting of train sample weight. 
    In adding feature process,multi-processing is used to traversal several features concurrently.The feature which meets the conditions which the user set and get a max lift on measure index is added in the model.If any feature can`t improve the performance of model undering the conditions set by user ,no feature is added in current iteration. 
    The removing feature process has same policy with adding feature process to decide which feature should be removed.
    When adding process, if there is improving on performance of model but some conditions user set are missed,a additional removing process will start to run.If the feature to remove is same with the feature to add,the feature will not be added and the adding process is over.If They are not same,the feature to add is added in and the feature to remove is excluded from current list in which the picked features stay.The additional removing process has same procedure with removing process. 
    When modeling is compeleted,the features not picked up will respectively be added in picked features list. And then by rebuilding model with those features,a exact deletion reasons will return. 
    
    The characteristics are listed below:
    1.Supporting forward-backward Step-Wise.
    2.Supporting multi-processing.When adding or removing features,multi-processing is used to traversal all candidate features.
    3.Supporting that user could point the index instead of AIC/BIC for measuring model performance when adding or removing feaures.That is benifit when user`s data is unbalanced.
    4.Supporting that user could point p-value threshold.If max p-value is more than this threshold,the current features will not be added,although getting a lift on performance of model.
    5.Supporting that user could point VIF threshold.If max VIF is more than this threshold,the current features will not be added,although getting a lift on performance of model.
    6.Supporting that user could point coefficient of correlation threshold.If max coefficient of correlation is more than this threshold,the current features will not be added,although getting a lift on performance of model.
    7.Supporting that user could point sign to coefficients of regression. A part of features have sense in some business like woe transfer which require that all coefficients of regression are postive or negtive.If the signs requirement is not met,the current features will not be added,although getting a lift on performance of model.
    8.[4,5,6,7] above are completed in step-wise procedure.Picking features and verifing those thresholds and signs are simultaneous.
    9.Users will get reasons of which features isn`t picked up,as performance is fall or p-value is more than threshold or signs is not in accord with user`s expect and so on after adding this feature 
    10.Supporting the Chinese and English log in whcih user can get record of every iteration
    
    Note:As X and y is a property in a instance of MultiProcessMStepRegression.LinearReg class,so that instance will be very large.Saving that instance is not recommended instead of saving the returned model and remove reasons.
    
    
    Parameters    
    ----------
    X:DataFrame
    features
    
    y:Series
    target
    
    fit_weight:Series
    The length of fit_weight is same with length of y.The fit_weight is for trainning data.If None(default),every sample has a same trainning weight and statsmodels.api.OLS is used as base linear algorithm.If not None,statsmodels.api.WLS is used as base linear algorithm.In linear regression,the goal of setting weight is for getting a stable model with Heteroscedasticity.
    
    
    measure:str r2(默认) | explained_variance_score | max_error
    Performance evaluate function.The y_true,y_hat and measure_weight will be put into measure function automatically and the other parameters will be put into measure function with kw_measure_args
    
    measure_weight:Series
    The length of measure_weight is same with length of y.The measure_weight is for measuring function.If None(default),every sample has a same measuring weight.
    See also fit_weight
    
    kw_measure_args:dict | None(默认)
    Except y_true,y_hat and measure_weight,the other parameters need be put in kw_measure_args to deliver into measure function.
    None means that no other parameters delivers into measure function.
    
    max_pvalue_limit:float
    The max P-VALUE limit.
    0.05(default)

    max_vif_limit:float
    The max VIF limit.
    3(default)
    
    max_corr_limit:float
    The max coefficient of correlation limit. 
    0.6(default)
    
    coef_sign:'+','-',dict,None（默认）
    If the user have a priori knowledge on relation between X and y,like positive correlation or negtive correlation,user can make a constraint restriction on sign of resression coefficient by this parameter.
    '+':all signs of resression coefficients are positive
    '-':all signs of resression coefficients are negtive
    dict:the format is as {'x_name1':'+','x_name2':'-'}.Put coefficient and coefficient`s sign on which you have a priori knowledge into a dict and then constraint these signs that are in this dict. The coefficients not included in this dict will not be constrainted.
    None:all coefficients are not constrainted.
        
    iter_num:int 
    The iteration num for picking features.Default is 20.When np.inf,no limit to iteration num,if features are many,then the running time is long.If all features are already picked in model or no imporve on perfermance by adding/removing any feature,the actual iteration num should be samller than iter_num.The steps inclueed in every iteration is:1.Try adding feature which is not added in current model yet and then pick up one feature that makes most promotion for performance of model with satisfying user`s setting. 2.Try removing feature and then remove out one feature that makes most promotion for performance of model with satisfying user`s setting.It is means finshing one time iteration that step 1 and step 2 is completed.If all step 1 and step 2 can`t pick up any feature then iteration is pre-terminated,no matter whether iter_num is reached.
        
    kw_algorithm_class_args:dict
    Except X，y，fit_weight,the other parameters that are delivered into linear regression algorithm is in kw_algorithm_class_args
    Note:y,X is called endog and exog in statsmodels.genmod.generalized_linear_model.GLM
    
    n_core:int | float | None
    Count of CPU processing.If int,user point the count.If float,the count is as percentage of all count transfered to int(ceil).If None(default),all count of CPU processing -1.
    
    logger_file_CH:str
    A log file name where log for step-wise procedure is recorded in Chinese.If None(default),not recording Chinese log.
    
    logger_file_EN:str
    A log file name where log for step-wise procedure is recorded in English.If None(default),not recording English log.
    
    '''
    def __init__(self,X,y,fit_weight=None,measure='r2',measure_weight=None,kw_measure_args=None,max_pvalue_limit=0.05,max_vif_limit=3,max_corr_limit=0.6,coef_sign=None,iter_num=20,kw_algorithm_class_args=None,n_core=None,logger_file_CH=None,logger_file_EN=None):
        Regression.__init__(self,X,y,fit_weight,measure,measure_weight,kw_measure_args,max_pvalue_limit,max_vif_limit,max_corr_limit,coef_sign,iter_num,kw_algorithm_class_args,n_core,logger_file_CH,logger_file_EN) 
            
    def _regression(self,in_vars):
        X = self.X[in_vars]
        if self.fit_weight is None:
            if self.kw_algorithm_class_args is not None:
                reg = sm.OLS(self.y,sm.add_constant(X),**self.kw_algorithm_class_args)
            else:
                reg = sm.OLS(self.y,sm.add_constant(X))
        else:
            if self.kw_algorithm_class_args is not None:
                reg = sm.WLS(self.y,sm.add_constant(X),weights=self.fit_weight,**self.kw_algorithm_class_args)
            else:
                reg = sm.WLS(self.y,sm.add_constant(X),weights=self.fit_weight)       
        clf = reg.fit()      
        clf.intercept_=[clf.params.const]
        clf.coef_=[clf.params[1:]]
        return clf