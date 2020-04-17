# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-16 16:51
Desc:
'''
from pynovice.bert_extracter import DownloadBertModel,ExtractBertFeatures

if __name__ == '__main__':
    # aa=DownloadBertModel()
    # aa.dump()
    bb=ExtractBertFeatures()
    print(bb.predict('你好啊'))