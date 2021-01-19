#!/bin/bash

#PYTHONHTTPSVERIFY=0
#twine==3.2.0
# 1.删除已有包
#rm -rf ./build
#rm -rf ./dist
#rm -rf ./pynovice.egg-info

#git push origin --tags

# 2. add tag
# git tag v0.2.39 -m 'update feature_pre'

python setup.py sdist bdist_wheel
python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
