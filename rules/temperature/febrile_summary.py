# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 11:45:57 2025

@author: YimingL
"""

from datetime import timedelta
from . import load_decision_tree_config, THRESHOLD_TEMPERATURE


def process_decision_tree():
    """加载决策树/Load decision tree"""
    decision_tree_config = load_decision_tree_config()
    print("Decision Tree Configuration Loaded:", decision_tree_config)
    
    return decision_tree_config
    
        
def evaluate_condition(condition, context):
    """评估条件/Evaluate condition"""
    return eval(condition, {}, context)

def traverse_rules(rules, context):
    """递归遍历规则/Recursive rules traversal"""
    condition = rules.get("condition")
    if condition is None or evaluate_condition(condition, context):
        
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


def parse_temperature_data(data: list, cutoff_time):
    """解析体温数据并生成总结/Generate summarization"""
    
    # 提取体温记录并排序/Sort the records by the performed date and time (this is a double check here)
    records = sorted(data["Temperature Tympanic"], key=lambda x: x["PerformedDateTime"])
    tmp_records = []
    for record in records:
        try:
            record["Degree"] = float(record["Degree"])
            tmp_records.append(record)
        except ValueError:
            continue
    records = tmp_records
    del tmp_records
    
    # Key Time Point
    start_24h = cutoff_time - timedelta(hours=24)
    start_5d = cutoff_time - timedelta(days=5)
    admission_time = data["AdmissionDate"]
    
    # Key fever records
    fever_records = [r for r in records if r["Degree"] >= THRESHOLD_TEMPERATURE and r["PerformedDateTime"] >= start_24h and r["PerformedDateTime"] <= cutoff_time]
    last_fever_time = fever_records[-1]["PerformedDateTime"] if fever_records else None
    initial_fever_time = last_fever_time
    highest_fever_degree = 0
    
    if fever_records:
        
        # 查找初始发烧时间/Find the initial fever time
        for record in reversed(records):
            if record["PerformedDateTime"] > cutoff_time:
                continue
            if record["PerformedDateTime"] < initial_fever_time - timedelta(hours=24):
                break
            if record["Degree"] >= THRESHOLD_TEMPERATURE:
                initial_fever_time = record["PerformedDateTime"]
                if record["Degree"] >= highest_fever_degree:
                    highest_fever_degree = record["Degree"]
        
        fever_duration = (last_fever_time - initial_fever_time).total_seconds() / 3600
        
        fever_duration_hours = int(fever_duration)
        days_fever = int(fever_duration // 24)
        hours_ago = int((cutoff_time - last_fever_time).total_seconds() / 3600)
        extra_description = ""
        days_ago = 999 # Appears if ther is a bug
        if (initial_fever_time - records[0]["PerformedDateTime"]).total_seconds() / 3600 <= 24:
            extra_description = "since admission"
            
    elif any([r['Degree'] >= THRESHOLD_TEMPERATURE for r in records if r['PerformedDateTime'] >= start_5d and r['PerformedDateTime'] <= cutoff_time]):
        print("CASE 4")
        last_fever_time = admission_time # initialize
        for r in records:
            if r['PerformedDateTime'] >= start_5d  and r['PerformedDateTime'] <= cutoff_time and r['Degree'] >= THRESHOLD_TEMPERATURE:
                if r['PerformedDateTime'] >= last_fever_time:
                    last_fever_time = r['PerformedDateTime']        
        days_ago = (cutoff_time - last_fever_time).days
        fever_duration = 0
        fever_duration_hours = 0
        days_fever = 0
        hours_ago = 0
        extra_description = ""
        
        
    else:
        if start_5d <= admission_time:
            extra_description = "since admission."
        else:
            extra_description = ""
        fever_duration = 0
        fever_duration_hours = 0
        days_fever = 0
        hours_ago = 0
        days_ago = 0
        print("CASE 5")
        

    # 上下文变量/Context variables
    context = {
        "records": records,
        "start_24h": start_24h,
        "start_5d": start_5d,
        "cutoff_time": cutoff_time,
        "fever_duration": fever_duration,
        "fever_duration_hours": fever_duration_hours,
        "last_fever_degree": fever_records[-1]["Degree"] if fever_records else None,
        "highest_fever_degree": highest_fever_degree,
        "days_fever": days_fever,
        "hours_ago": hours_ago,
        "days_ago": days_ago,
        "extra_description": extra_description
    }

    # 加载决策树/Load decision tree
    rules = process_decision_tree()
    
    # 生成结果并返回/Generate results and return
    summary = traverse_rules(rules['check_fever'], context)
    if " 0 hours ago." in summary:
        summary = summary.replace("0 hours ago.", "right now.")
    return summary

