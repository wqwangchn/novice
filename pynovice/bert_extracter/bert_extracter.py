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

CUR_PASTH = os.path.dirname(os.path.abspath(__file__))

class ExtractBertFeatures:
    def __init__(self):
        bert_model_dir = os.path.join(CUR_PASTH,'data','uncased_L-2_H-128_A-2')
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
    def __init__(self,url='https://storage.googleapis.com/bert_models/2020_02_20/uncased_L-2_H-128_A-2.zip'):
        self.model_dir = url
        name = url.split('/')[-1].split('.')[0]
        self.save_parh = os.path.join(CUR_PASTH, 'data', name)

    def dump(self,save_parh=''):
        if not save_parh:
            save_parh = self.save_parh
        if not os.path.exists(save_parh):
            os.makedirs(save_parh)

        r = requests.get(self.model_dir)
        with open("_tmp.zip", "wb") as code:
            code.write(r.content)

        f = zipfile.ZipFile('_tmp.zip', 'r')
        for file in f.namelist():
            f.extract(file,save_parh)
        os.remove("_tmp.zip")


if __name__ == '__main__':
    aa=DownloadBertModel()
    aa.dump()
    print(CUR_PASTH)
    bb=ExtractBertFeatures()
    print(bb.predict('你好啊'))
