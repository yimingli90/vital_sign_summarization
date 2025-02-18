# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 14:43:32 2025

@author: YimingL
"""

def _evaluate_condition(condition, context):
    """评估条件/Evaluate condition"""
    return eval(condition, {}, context)


def traverse_rules(rules, context):
    """递归遍历规则/Recursive rules traversal"""
    condition = rules.get("condition")
    if condition is None or _evaluate_condition(condition, context):
        
        # 如果满足条件，检查是否有下一级规则/If the condition is true, check whether a child rule is available
        if "true" in rules:
            true_branch = rules["true"]
            if isinstance(true_branch, dict):
                return traverse_rules(true_branch, context)
            else:
                return true_branch.format(**context)
    else:
        
        # 如果条件不满足，检查false分支/If the condition is false, check false branch
        if "false" in rules:
            false_branch = rules["false"]
            if isinstance(false_branch, dict):
                return traverse_rules(false_branch, context)
            else:
                return false_branch.format(**context)