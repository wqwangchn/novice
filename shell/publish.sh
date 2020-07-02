#!/bin/bash

#PYTHONHTTPSVERIFY=0
# git tag v0.2.13 -m 'update feature_pre'
python setup.py sdist bdist_wheel
python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
