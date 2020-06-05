# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-24 10:54
Desc:
    简易的风控规则引擎

    待系统化：（单量预警系统）
    |当前进件单量| 当前进件通过率| 当前通过单量| - |预测剩余进件量| 预测剩余进件通过率(7天同时段同规则)| 预测剩余通过单量|- |预测今日总计通过单量
    单量预测可靠性 = 当天已进件通过率 - 7天进件通过率(同时段同规则) 可靠性评分
'''

from .rule_parser import RuleParser