# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-07-30 11:07
Desc:
@动态规划
有一些不规则的硬币。在这些硬币中，prob[i] 表示第 i 枚硬币正面朝上的概率。

请对每一枚硬币抛掷 一次，然后返回正面朝上的硬币数等于 target 的概率。

 

示例 1：

输入：prob = [0.4], target = 1
输出：0.40000
示例 2：

输入：prob = [0.5,0.5,0.5,0.5,0.5], target = 0
输出：0.03125
 

提示：

1 <= prob.length <= 1000
0 <= prob[i] <= 1
0 <= target <= prob.length
如果答案与标准答案的误差在 10^-5 内，则被视为正确答案。

'''

from typing import (
    TypeVar, Generic, Dict, overload, List, Tuple,
    Any, Type, Optional, Union
)
class Solution:
    def probabilityOfHeads(self, prob: List[float], target: int) -> float:
        pass