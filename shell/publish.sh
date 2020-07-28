#!/bin/bash

#PYTHONHTTPSVERIFY=0
# git tag v0.2.13 -m 'update feature_pre'

# 删除已有包
rm -rf ./build
rm -rf ./dist
rm -rf ./pynovice.egg-info

python setup.py sdist bdist_wheel
python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
