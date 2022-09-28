# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/10/26 14:17
Desc:
'''
import pandas as pd
import woe as g7_woe
from pynovice.util.util import progress_bar

def get_woe_card(df_data,fields_bins):
    '''

    :param df_data:
    :param fields_bins: 特征的分箱字典
    :return: 构建woe字典
    '''
    assert 'label' in df_data.columns
    # assert 'fee_got' in df_data.columns
    # assert 'report_fee' in df_data.columns

    woe_list = []
    print("get woe card ....\n")
    len_=len(fields_bins)
    for i,(col, bins) in enumerate(fields_bins.items()):
        progress_bar(i,len_)
        bin_data = pd.cut(df_data[col].fillna(0), bins=bins)

        # label1：是否出险
        woe1 = g7_woe.WeightOfEvidence()
        woe1.fit(bin_data, df_data["label"])
        card = woe1.woe_card
        card.columns = ['特征字段', '分箱', '无出险车辆数', '出险车辆数',
                        '无出险占比', '出险占比', 'woe1', 'iv1']
        card['车辆总数'] = card['无出险车辆数'] + card['出险车辆数']

        # label2：赔付率
        if ('fee_got' in df_data.columns) and ('report_fee' in df_data.columns):
            woe2 = g7_woe.WeightOfFeeEvidence()
            woe2.fit(bin_data, df_data["fee_got"], df_data["report_fee"])
            card2 = woe2.woe_card
            card[["已赚保费", "赔付金额", "已赚保费占比", "赔付金额占比", "woe0", "iv0"]] = card2[
                ['get_fee', 'report_fee', 'get_fee_prob', 'report_fee_prob', 'woe', 'iv']]
        else:
            print("input data have no 'fee_got & report_fee' info!")

        # label3：是否有过赔付2k+
        if 'label_ordinary' in df_data.columns:
            woe3 = g7_woe.WeightOfEvidence()
            woe3.fit(bin_data, df_data["label_ordinary"])
            card3 = woe3.woe_card
            card[["赔付车辆数", "无赔付车辆数", "赔付车辆占比", "无赔付车辆占比", "woe2", "iv2"]] = card3[
                ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]
        else:
            print("input data have no 'label_ordinary' info! eg:>2k")

        # label4：是否大事故1w+
        if 'label_serious' in df_data.columns:
            woe4 = g7_woe.WeightOfEvidence()
            woe4.fit(bin_data, df_data["label_serious"])
            card4 = woe4.woe_card
            card[["重大事故车辆数", "非重大事故车辆数", "重大事故占比", "非重大事故占比", "woe3", "iv3"]] = card4[
                ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]
        else:
            print("input data have no 'label_serious' info! eg:>1W")

        # label5：是否重大事故5w+
        if 'label_major' in df_data.columns:
            woe5 = g7_woe.WeightOfEvidence()
            woe5.fit(bin_data, df_data["label_major"])
            card5 = woe5.woe_card
            card[["特大事故车辆数", "非特大事故车辆数", "特大事故占比", "非特大事故占比", "woe4", "iv4"]] = card5[
                ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]
        else:
            print("input data have no 'label_major' info! eg:>5W")

        # label6：是否特大事故20W'+
        if 'label_devastating' in df_data.columns:
            woe5 = g7_woe.WeightOfEvidence()
            woe5.fit(bin_data, df_data["label_devastating"])
            card5 = woe5.woe_card
            card[["特大事故车辆数", "非特大事故车辆数", "特大事故占比", "非特大事故占比", "woe5", "iv5"]] = card5[
                ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]
        else:
            print("input data have no 'label_devastating' info! eg:>20W")

        woe_list.append(card)
    woe_dict = pd.concat(woe_list).reset_index(drop=True)
    woe_dict.columns.name = 'idx'
    col = ['特征字段', '分箱', '车辆总数'] + [i for i in woe_dict if 'woe' in i]+ [i for i in woe_dict if 'iv' in i]

    return woe_dict[col]

def get_woe_features(df_data,df_card,dict_blocks):
    '''
    有问题，需修正。。。。
    :param df_data:
    :param df_card:
    :param dict_blocks:
    :return:
    '''
    df_x = pd.DataFrame()
    print("\nget woe features ......\n")
    len_ = len(dict_blocks)
    for i, (_field, _bin) in enumerate(dict_blocks.items()):
        progress_bar(i, len_)
        _card = df_card[df_card.特征字段 == _field]
        _card['分箱'] = _card['分箱'].astype(str)
        _data = pd.cut(df_data[_field].fillna(0), bins=_bin)
        out = pd.DataFrame(_data).astype(str).join(_card.set_index('分箱'), on=_data.name, how='left')
        col = [i for i in out.columns if 'woe' in i]
        col2 = [_field + "_" + i for i in col]
        df_x[col2] = out[col]
    return df_x


if __name__ == '__main__':
    import numpy as np
    df_data = pd.DataFrame([[1, 2, 3, 4, 5, 5, 5, 6, 8, 3, 2, 1, 5, 7], [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]).T
    df_data.columns = ['field', 'label']
    df_data['fee_got']=10000
    df_data['report_fee']=1000
    bins_dict={'field':[-np.inf,3,np.inf]}

    df_woe = get_woe_card(df_data, bins_dict)
    df_x = get_woe_features(df_data, df_woe, bins_dict)
    print(df_x.head())