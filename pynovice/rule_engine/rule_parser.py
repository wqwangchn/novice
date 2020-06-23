# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-24 10:55
Desc:
    简易的风控规则引擎 (仅供自己测试)
    ["操作符"，["操作符1#tag"， "参数1"， "参数2"， ...]，["操作符2"， "参数1"， "参数2"， ...]]
    >>> rules = ["and",[">#rule_10", 0, 0.05],["in#rule_20", 3, 2, 3, 4]]
    (False, [{'rule_10': False}, {'rule_20': True}, {'untag': False}])

'''
from numpy import unicode
import json

class LogicalFunctions(object):
    '''
    定义的方法集合
    '''
    def __init__(self):
        self.func_ = {
            '=': self.eq,
            '!=': self.neq,
            '>': self.gt,
            '>=': self.gte,
            '<': self.lt,
            '<=': self.lte,
            'and': self.and_,
            'in': self.in_,
            'between': self.between_,
            'or': self.or_,
            'not': self.not_,
            'str': self.str_,
            'int': self.int_,
            '+': self.plus,
            '-': self.minus,
            '*': self.multiply,
            '/': self.divide
        }

    def eq(self, *args):
        return args[0] == args[1]

    def neq(self, *args):
        return args[0] != args[1]

    def in_(self, *args):
        return args[0] in args[1:]

    def between_(self, *args):
        return (args[0] >= args[1]) and (args[0] <= args[2])

    def gt(self, *args):
        return args[0] > args[1]

    def gte(self, *args):
        return args[0] >= args[1]

    def lt(self, *args):
        return args[0] < args[1]

    def lte(self, *args):
        return args[0] <= args[1]

    def not_(self, *args):
        return not args[0]

    def or_(self, *args):
        return any(args)

    def and_(self, *args):
        return all(args)

    def int_(self, *args):
        return int(args[0])

    def str_(self, *args):
        return unicode(args[0])

    def upper(self, *args):
        return args[0].upper()

    def lower(self, *args):
        return args[0].lower()

    def plus(self, *args):
        return sum(args)

    def minus(self, *args):
        return args[0] - args[1]

    def multiply(self, *args):
        return args[0] * args[1]

    def divide(self, *args):
        return float(args[0]) / float(args[1])

    def abs(self, *args):
        return abs(args[0])

class RuleParser(object):
    def __init__(self):
        self.funcSet = LogicalFunctions().func_

    def get_func(self,_func):
        func = self.funcSet.get(_func)
        if not func:
            self.func_list()
            func = lambda _:None
        return func

    def func_list(self):
        _func_list = list(self.funcSet.keys())
        print("supported function list: {}".format(_func_list))

    def validate_check(self,rule):
        if isinstance(rule, str):
            rule = json.loads(rule)
        else:
            rule = rule
        if not isinstance(rule, list):
            raise ('Rule must be a list, got {}'.format(type(rule)))
        if len(rule) < 2:
            raise ('Must have at least one argument.')
        return rule

    def evaluate(self,_rule):
        self.whole_result = []
        rule = self.validate_check(_rule)
        result = self._evaluate(rule)
        return result,self.whole_result

    # filter hit_rule
    def get_hit_rules(self,exclude_rules=[]):
        result = self.whole_result
        filt_out = []
        for irule in result:
            for _k,_v in irule.items():
                if _k.lower() in exclude_rules:
                    continue
                if 'untag'==_k:
                    continue
                if bool(_v):
                    continue
                filt_out.append(_k)
        return filt_out

    def _evaluate(self, rule):
        """
        递归执行list内容
        """
        operate_info = rule[0].split('#') # tag操作符号[eg: or#rule_1101]
        tag = operate_info[1] if len(operate_info)>1 else 'untag'
        operate = operate_info[0].lower()
        data = rule[1:]
        for id,idata in enumerate(data):
            if isinstance(idata, list):
                data[id] = self._evaluate(idata)
        iterate_out = self.get_func(operate)(*data)
        if 'untag'!=tag:
            self.whole_result.append({tag:iterate_out})
        return iterate_out

if __name__ == '__main__':
    engine = RuleParser()
    bb= engine.evaluate(_rule = ['in',3,2,5,4])
    print(bb)
    cc = engine.evaluate(_rule = ['in', 3, 2, 3, 4])
    print(cc)
    dd = engine.evaluate(_rule = ["and#result",[">#rule_10", 0, 0.05],["In#rule_20", 3, 2, 3, 4]])
    print(dd)