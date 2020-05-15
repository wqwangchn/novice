# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-05-04 15:34
Desc:
    特征生成（预处理，转换，编码）
'''
from pynovice.score_card.category_coder import CateCoder
from pynovice.score_card.data_binning import DataBinning
from pynovice.score_card.data_woe import WeightOfEvidence
import pandas as pd

class FeatureGenerator:
    def __init__(self):
        self.cate_coder_dict = {}
        self.binning_dict = {}
        self.woe_dict = {}
        self.binning_woe_info = None
        self.fields = None #特征字段

    def fit_transform(self, df_fields, df_label, category_fields=None, default_boxs=5, boxs_dict={},bins_dict={}):
        '''
            预处理+类别转换+分箱+woe编码
        :param df_fields: 训练集pandas.DataFrame
        :param df_label: Series
        :param category_fields: df_fields中类别特征字段，list
        :param default_boxs: 默认分箱数量
        :param boxs_dict: 自定义分箱数量
        :param bins_dict: 自定义分箱阈值，{field:[]}
        :return:
        '''
        if category_fields is None:
            category_fields = list()

        # 1.预处理
        df_fields = df_fields.copy()
        df_fields = self.preprocessing(df_fields)
        self.fields = df_fields.columns.to_list()

        # 2.类别特征转换
        for field in category_fields:
            cate_coder = CateCoder()
            df_fields[field] = cate_coder.fit_transform(df_fields[field], df_label)
            self.cate_coder_dict.update({field:cate_coder})

        # 3.分箱&woe编码
        for field in self.fields:
            _bins = bins_dict.get(field)
            # 自定义分箱
            if bool(_bins) & isinstance(_bins,list):
                box_num = len(_bins)
                binning = DataBinning(box_num=box_num)
                binning.bins = _bins
                df_field = pd.cut(df_fields[field],bins=_bins)
            # 程序分箱
            else:
                box_num = boxs_dict.get(field,default_boxs)
                binning = DataBinning(box_num=box_num, _func='tree_blocks')
                df_field = binning.fit_transform(df_x=df_fields[field], df_y=df_label)
            self.binning_dict.update({field:binning})

            woe = WeightOfEvidence()
            df_field = woe.fit_transform(df_field, df_label)
            self.woe_dict.update({field: woe})

            df_fields.loc[:, field] = df_field

        self.binning_woe_info = self.get_binning_woe()
        return df_fields

    def transform(self,fields_json):
        feature = []
        for field_name in self.fields:
            # 取数据
            field_value = fields_json.get(field_name)
            if not field_value:
                feature.append(-999)
                continue
            # 类别编码
            cate_coder = self.cate_coder_dict.get(field_name)
            if cate_coder:
                field_value = cate_coder.transform(field_value)
            # data分箱
            binning = self.binning_dict.get(field_name)
            if binning:
                field_value = binning.transform(field_value)
            # woe编码
            woe = self.woe_dict.get(field_name)
            if woe:
                field_value = woe.transform(field_value)
            feature.append(field_value)
        return [feature]

    def preprocessing(self, df_fields):
        return df_fields

    def get_binning_woe(self):
        field_woe = [woe.woe_info for woe in self.woe_dict.values()]
        df_woe = pd.concat(field_woe,axis=0)
        return df_woe



if __name__ == '__main__':
    import dill as pickle
    # dump
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 6, 8, 3, 2, 1, 5, 7], [10, 2, 3, 42, 534, 5, 53, 6, 83, 3, 42, 21, 25, 7],
                       [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field1', 'field2', 'label']
    df_fields, df_label = df[['field1', 'field2']], df['label']

    feature_generator = FeatureGenerator()
    feature_generator.fit_transform(df_fields,df_label,category_fields=['field1'])
    print(feature_generator.binning_woe_info)

    # file_name = '../data/feature_generater.pkl'
    # pickle.dump(feature_generator, open(file_name, "wb"),protocol=3)
    #
    # # load
    # feature_generator= pickle.load(open(file_name, "rb"))
    fields_json = {'field1':4, 'field22':5, 'aa':9}
    feature = feature_generator.transform(fields_json)
    print(feature)


