# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-05-04 15:34
Desc:
    特征生成（预处理，转换，编码）
'''
from pynovice.score_card.src.category_coder import CateCoder
from pynovice.score_card.src.data_binning import DataBinning
from pynovice.score_card.src.data_woe import WeightOfEvidence
import pandas as pd
from pynovice.util import progress_bar
import logging

class FeatureGenerator:
    def __init__(self,auto_fill_missing=True,missing=None):
        self.cate_coder_dict = {}
        self.binning_dict = {}
        self.woe_dict = {}
        self.woe_defalut = {}
        self.fields = None #特征字段
        self.category_fields = None
        self.digital_fields = None
        if missing:
            self.missing = missing
            self.auto_fill_missing = False
        else:
            self.missing = -999
            self.auto_fill_missing = auto_fill_missing
        self.binning_woe_info = None
        self.cate_fields_info = None

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
        df_fields = df_fields.copy()
        df_fields=df_fields.reset_index(drop=True)
        df_label = df_label.reset_index(drop=True)
        self.fields = df_fields.columns.to_list()
        if category_fields is None:
            self.category_fields = list()
        else:
            self.category_fields = category_fields
        self.digital_fields = list(set(self.fields)-set(self.category_fields))

        # 1.预处理
        df_fields = self.preprocessing(df_fields)

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
            self.woe_defalut.update({field:df_field.mode()[0]})## 众数

            df_fields.loc[:, field] = df_field

        self.binning_woe_info = self.get_binning_woe()
        self.cate_fields_info = self.get_cate_info()
        return df_fields

    def transform(self,fields_jsons):
        if isinstance(fields_jsons,pd.DataFrame):
            return self.transform_for_dataframe(fields_jsons)
        if not isinstance(fields_jsons,list):
            fields_jsons = [fields_jsons]
        features=[]
        len_data = len(fields_jsons)
        for i,fields_json in enumerate(fields_jsons):
            progress_bar(i,len_data)
            feature = []
            for field_name in self.fields:
                # 主逻辑
                # 默认值
                if self.auto_fill_missing:
                    _missing = self.woe_defalut.get(field_name)
                else:
                    _missing = self.missing
                # 取数据
                field_value = fields_json.get(field_name)
                if not field_value:
                    feature.append(_missing)
                    continue
                # 类别编码
                cate_coder = self.cate_coder_dict.get(field_name)
                if cate_coder:
                    field_value = cate_coder.transform(field_value)
                if not isinstance(field_value,(float,int)):
                    logging.error("{} is not a number type[index:{}]".format(field_name,i))  # 数值类型
                    feature.append(_missing)
                    continue
                # data分箱
                binning = self.binning_dict.get(field_name)
                if binning:
                    field_value = binning.transform(field_value)
                # woe编码
                woe = self.woe_dict.get(field_name)
                if woe:
                    field_value = woe.transform(field_value)
                    if not field_value:
                        field_value = _missing
                else:
                    field_value = _missing
                feature.append(field_value)
            features.append(feature)
        return features

    def transform_for_dataframe(self,df_fields):
        df_in = self.preprocessing(df_fields)
        feature_columns=[]
        for field_name in self.fields:
            feature_columns.append(field_name)
            # 默认值
            if self.auto_fill_missing:
                _missing = self.woe_defalut.get(field_name)
            else:
                _missing = self.missing
            # 取数据
            if field_name not in df_in.columns:
                df_in[field_name]=_missing
                continue
            # 类别编码
            cate_coder = self.cate_coder_dict.get(field_name)
            if cate_coder:
                df_in[field_name] = df_in[field_name].apply(lambda x:cate_coder.transform(x))
            # data分箱
            binning = self.binning_dict.get(field_name)
            if binning:
                df_in[field_name] = pd.cut(df_in[field_name], bins=binning.bins)
            # woe编码
            woe = self.woe_dict.get(field_name)
            if woe:
                df_in[field_name] = df_in[field_name].apply(lambda x: woe.transform(x)).fillna(_missing)
            else:
                df_in[field_name] = _missing
        features = df_in[feature_columns]
        return features

    def preprocessing(self, df_fields):
        _columns = list(set(df_fields.columns)&set(self.digital_fields))
        if _columns:
            df_fields[_columns] = df_fields[_columns].fillna(self.missing).astype(float)
        return df_fields

    def get_binning_woe(self):
        field_woe = [woe.woe_info for woe in self.woe_dict.values()]
        df_woe = pd.concat(field_woe,axis=0)
        return df_woe

    def get_cate_info(self):
        cate_fields_info = {field:cate.cate_dict for field,cate in self.cate_coder_dict.items()}
        return cate_fields_info

if __name__ == '__main__':
    # dump
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 6, 8, 3, 2, 1, 5, 7], [10, 2, 3, 42, 534, 5, 53, 6, 83, 3, 42, 21, 25, 7],
                       [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field1', 'field2', 'label']
    df_fields, df_label = df[['field1', 'field2']], df['label']

    feature_generator = FeatureGenerator()
    feature_generator.fit_transform(df_fields,df_label,category_fields=['field1'])
    print(feature_generator.cate_fields_info)
    print(feature_generator.binning_woe_info)

    # file_name = '../data/feature_generater.pkl'
    # pickle.dump(feature_generator, open(file_name, "wb"),protocol=3)
    #
    # # load
    # feature_generator= pickle.load(open(file_name, "rb"))
    fields_json = [{'field1':'4a', 'field2':'5a', 'aa':9},{'field1':4, 'field2':5, 'aa':9}]
    df_fields = pd.DataFrame(fields_json)
    feature = feature_generator.transform(df_fields)
    print(feature)