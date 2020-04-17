# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-03-25 14:40
Desc:
'''

from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
import numpy as np
import os
import requests
import zipfile
from pynovice.util import progress_bar

CUR_PASTH = os.path.dirname(os.path.abspath(__file__))

class ExtractBertFeatures:
    def __init__(self,model_name = 'uncased_L-4_H-256_A-4'):
        bert_model_dir = os.path.join(CUR_PASTH,'data',model_name)
        self.load_model(model_dir=bert_model_dir)
        pass

    def load_model(self,model_dir):
        config_name = os.path.join(model_dir, 'bert_config.json')
        checkpoint_name = os.path.join(model_dir, 'bert_model.ckpt')
        vocab_name = os.path.join(model_dir, 'vocab.txt')
        self.tokenizer = Tokenizer(vocab_name, do_lower_case=True)  # 建立分词器
        self.model = build_transformer_model(config_name, checkpoint_name)  # 建立模型，加载权重

    def predict(self,x,second_text=None,max_length=None,first_length=None,second_length=None,use_multiprocessing=False):
        token_ids, segment_ids = self.tokenizer.encode(x,second_text,max_length,first_length,second_length)
        features = self.model.predict([np.array([token_ids]), np.array([segment_ids])])
        return features

class DownloadBertModel:
    def __init__(self,url='https://storage.googleapis.com/bert_models/2020_02_20/uncased_L-4_H-256_A-4.zip'):
        self.model_url = url
        self.name = url.split('/')[-1].split('.')[0]
        self.save_parh = os.path.join(CUR_PASTH, 'data', self.name)

    def dump(self, save_parh=''):
        if not save_parh:
            save_parh = self.save_parh
        if not os.path.exists(save_parh):
            os.makedirs(save_parh)
        # 模型下载
        url = self.model_url
        with requests.get(url, stream=True) as r:
            filesize = r.headers["Content-Length"]
            chunk_size = 1024
            times = int(filesize) // chunk_size
            print("模型文件大小:", filesize, "bytes")
            print("下载地址:", url)
            print('-' * 30)
            print("开始下载")
            with open("_tmp.zip", "wb") as fw:
                start = 0
                for chunk in r.iter_content(chunk_size):
                    fw.write(chunk)
                    start += 1
                    progress_bar(start, times)
        # 解压文件
        f = zipfile.ZipFile('_tmp.zip', 'r')
        for file in f.namelist():
            f.extract(file,save_parh)
        os.remove("_tmp.zip")

if __name__ == '__main__':
    # aa=DownloadBertModel()
    # aa.dump()
    print(CUR_PASTH)
    bb=ExtractBertFeatures()
    print(bb.predict('你好啊'))
