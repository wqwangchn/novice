# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-24 15:40
Desc:
'''
from pynovice.rule_engine import RuleParser

def rule_pattern(_iterm):
    age = _iterm.get('age',0)
    sms_len = _iterm.get('sms_len',0)
    micro_loan_len = _iterm.get('micro_loan_len', 0)
    endBillsLen = _iterm.get('endBillsLen', 0)
    maxDueday = _iterm.get('maxDueday', 0)
    this_apply_dueday_predicted_score = _iterm.get('this_apply_dueday_predicted_score', 0)

    _pattern = [
        'OR',
            ['between#rule_10',age,18,55],
            ['>#rule_11',sms_len,50],
            ['<#rule_12',micro_loan_len,8],
            ['and#rule_40',
                ['>',endBillsLen,4],
                ['>',maxDueday,20],
                ['>',this_apply_dueday_predicted_score,20]
             ]
    ]
    return _pattern


if __name__ == '__main__':
    iterm = {'age': 30, 'sms_len': 70, 'micro_loan_len': 10, 'endBillsLen': 5, 'maxDueday': 20,
             'this_apply_dueday_predicted_score': 10}
    rule = rule_pattern(iterm)

    engine = RuleParser()
    out = engine.evaluate(_rule=rule)
    print(out)