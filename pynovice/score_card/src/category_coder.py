# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-28 11:06
Desc:
    1.类别特征转换为数值，[进行分箱后]，2.再次将分箱转换为类别字典
'''
import pandas as pd

class CateCoder:
    def __init__(self):
        self.cate_dict={}

    def fit(self,df_field, df_label,target_label=1):
        '''
            类别字段按照坏样本占比排序编码
            :param df_field:
            :param df_label:
            :param target_label:
            :return:
            cate_dict: {field0:0,field1:1,field2:2}
            '''
        df_field.reset_index(drop=True, inplace=True)
        df_label.reset_index(drop=True, inplace=True)
        df_concat = pd.concat([df_field, df_label], axis=1)
        df_concat.columns = ['field', 'label']
        bad_rate_sorted = df_concat.groupby('field').agg(lambda x: sum(x == target_label) / len(x)).sort_values('label')

        rever_cate_dict = dict(enumerate(bad_rate_sorted.index))  # {0:field0,1:field1,2:field2}
        self.cate_dict = {v: k for k, v in rever_cate_dict.items()}  # {field0:0,field1:1,field2:2}

        # df_field = df_field.apply(lambda x: self.cate_dict.get(x, -1))
        # return df_field

    def transform(self,x):
        return self.cate_dict.get(x, -1)

    def fit_transform(self,df_field, df_label, target_label=1):
        self.fit(df_field, df_label, target_label)
        df_out = df_field.apply(lambda x: self.transform(x))
        return df_out

    # tmp
    def blocks_2_catedict(self,blocks):
        # 转换原始类别标签到分箱编码
        cate_code = list(self.cate_dict.values())
        block_code = pd.cut(cate_code, bins=blocks)#, labels=list(range(len(blocks) - 1)))
        block_dict = dict(zip(cate_code, block_code))
        return block_dict

if __name__ == '__main__':
    from pynovice.score_card.src.data_boxing import chi_blocks
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 3, 3, 3, 2, 1, 5, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field', 'label']
    df_field, df_label = df['field'], df['label']

    cate_coder = CateCoder()
    df_field = cate_coder.fit_transform(df_field, df_label,target_label=1)
    x = cate_coder.transform(5)
    print(df_field,x)


    block = chi_blocks(df_field, df_label, box_num=5, dfree=4, cf=0.1)
    print(block)
    block_dict=cate_coder.blocks_2_catedict(block)
    print(block_dict)



