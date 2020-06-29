# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-29 15:48
Desc:
'''
import pandas as pd
import dill as pickle
from pynovice.score_card.src.data_boxing import frequence_blocks,distince_blocks, kmeans_blocks, bayesian_blocks, \
    ks_blocks, chi_blocks, tree_blocks

from pynovice.score_card.feature_preprocessing import FeatureGenerator

def test_data_binning():
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 6, 8, 3, 2, 1, 5, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field', 'label']
    df_field, df_label = df['field'], df['label']

    # frequence_blocks
    fre_blocks = frequence_blocks(x=df_field, box_num=4)
    print("frequence_blocks: {}".format(fre_blocks))

    # distince_blocks
    dist_blocks = distince_blocks(x=df_field, box_num=4)
    print("distince_blocks: {}".format(dist_blocks))

    # kmeans_blocks
    km_blocks = kmeans_blocks(x=df_field, box_num=4)
    print("kmeans_blocks: {}".format(km_blocks))

    # bayesian_blocks
    bay_blocks = bayesian_blocks(df_field, fitness='events', p0=0.01)
    print("bayesian_blocks: {}".format(bay_blocks))

    # ks_blocks
    k_blocks = ks_blocks(df_field, df_label, box_num=4)
    print("ks_blocks: {}".format(k_blocks))

    # chi_blocks
    ch_blocks = chi_blocks(df_field, df_label, box_num=4)
    print("chi_blocks: {}".format(ch_blocks))

    # cart_blocks
    cart_blocks = tree_blocks(df_field, df_label, box_num=4)
    print("tree_blocks: {}".format(cart_blocks))
    aa=pd.cut(df_field,cart_blocks)
    print(aa)
    # bb,cc=calc_woe(aa, df_label, bad_target=1, eps=1e-4)
    # print(bb,cc)



    # ## 类别变量转换
    # print("-----类别-----")
    # cate_coder = CateCoder()
    # df_field = cate_coder.cate_coding(df_field, df_label, target_label=1)
    # def get_blocks(df_field,df_label):
    #     fre_blocks = frequence_blocks(x=df_field, bins=4)
    #     dist_blocks = distince_blocks(x=df_field, bins=4)
    #     km_blocks = kmeans_blocks(x=df_field, bins=4)
    #     bay_blocks = bayesian_blocks(df_field, fitness='events', p0=0.01)
    #     k_blocks = ks_blocks(df_field, df_label, box_num=4)
    #     ch_blocks = chi_blocks(df_field, df_label, box_num=4)
    #     cart_blocks = tree_blocks(df_field, df_label, box_num=4)
    #     return (fre_blocks,dist_blocks,km_blocks,bay_blocks,k_blocks,ch_blocks,cart_blocks)
    # set_blocks = get_blocks(df_field,df_label)
    # for i,block in enumerate(set_blocks):
    #     block_dict = cate_coder.blocks_2_catedict(block)
    #     print(i,block_dict)

def test_feature_procprocessing():
    df = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 6, 8, 3, 2, 1, 5, 7], [10, 2, 3, 42, 534, 5, 53, 6, 83, 3, 42, 21, 25, 7],
                       [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df.columns = ['field1', 'field2', 'label']
    df_fields, df_label = df[['field1', 'field2']], df['label']

    feature_generator = FeatureGenerator()
    feature_generator.fit_transform(df_fields, df_label)
    print(feature_generator.binning_woe_info)
    file_name = '../data/feature_generater.pkl'
    pickle.dump(feature_generator, open(file_name, "wb"),protocol=3)

    # load
    feature_generator= pickle.load(open(file_name, "rb"))
    fields_json = {'field1': 4, 'field22': 5, 'aa': 9}
    feature = feature_generator.transform(fields_json)
    print(feature)

if __name__ == '__main__':
    # 分箱
    test_data_binning()
    test_feature_procprocessing()