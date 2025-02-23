# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 14:38:48 2025

@author: YimingL
"""

import sys

from ..call_rules import traverse_rules
from datetime import timedelta
from . import load_decision_tree_config


def process_decision_tree():
    """加载决策树/Load decision tree"""
    
    decision_tree_config = load_decision_tree_config()
    
    return decision_tree_config
    

def parse_hr_data(data: list, cutoff_time):
    """解析数据并生成总结/Generate summarization"""
    
    records = data['Heart Rate']

    # Key time point
    start_12h = cutoff_time - timedelta(hours=12)
    records_12h = [r for r in records if r['PerformedDateTime'] >= start_12h and r['PerformedDateTime'] <= cutoff_time]
    if len(records_12h) == 0:
        return "No heart rate record", records_12h
    latest_heart_rate = int(records_12h[-1]['Value'])
    
    # 上下文变量/Context variables
    context = {
        "latest_heart_rate": latest_heart_rate
    }
    # 加载决策树/Load decision tree
    rules = process_decision_tree()
    
    # 生成结果并返回/Generate results and return
    summary = traverse_rules(rules['check_heart_rate'], context)
    return summary, records_12h
