# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 11:15:13 2025

@author: Yiming Li
"""

from datetime import timedelta

from datetime import timedelta

def classify_and_collect_cases(patient_records, case_limit=10):
    """
    根据患者数据，在每个患者记录中找到满足五个case条件的cut-in time，且每个case最多保存10个示例。
    Find cut-in times in patient records that satisfy the five cases, with each case limited to 10 examples.

    参数 (Parameters):
        patient_records (list): 包含患者数据的列表，格式为dict。
                               List of patient records in dict format.
        case_limit (int): 每个case的示例数量限制。
                         Maximum number of examples per case.

    返回 (Returns):
        cases (dict): 每个case对应的示例列表。
                     A dictionary containing examples for each case.
    """
    cases = {1: [], 2: [], 3: [], 4: [], 5: []}  # 用于存储每个case的示例 (Stores examples for each case)
    
    # 遍历所有患者记录 (Iterate through all patient records)
    for patient_data in patient_records:
        # 如果所有case都已经达到限制数量，则停止 (Stop if all cases are full)
        if all(len(cases[case]) >= case_limit for case in cases):
            break
        
        # 按时间排序体温记录 (Sort temperature records by time)
        temperature_records = sorted(patient_data['Temperature Tympanic'], key=lambda x: x['PerformedDateTime'])
        
        # 遍历所有可能的cut-in time (Iterate through all potential cut-in times)
        for record in temperature_records:
            cutoff_time = record['PerformedDateTime']  # 当前cut-in time (Current cut-in time)
            
            # 获取最近五天的时间范围 (Get the past 5 days' time range)
            past_5_days = cutoff_time - timedelta(days=5)
            
            # 提取发热区间 (Extract febrile intervals)
            febrile_intervals = patient_data['FebrileIntervals']
            
            # 提取最近五天的体温记录 (Extract temperature records in the past 5 days)
            temperature_past_5_days = [
                temp for temp in temperature_records 
                if past_5_days <= temp['PerformedDateTime'] <= cutoff_time
            ]
            
            # 判断当前时间点是否发热 (Determine if febrile at the current time)
            try:
                is_febrile = float(record['Degree']) >= 37.8
            except:
                continue
            
            # 计算发热持续时间 (Calculate febrile duration)
            febrile_duration = 0
            for start, end in febrile_intervals:
                if start <= cutoff_time <= end:  # 截断时间点在发热区间内 (Cutoff time falls within febrile interval)
                    febrile_duration = (end - start).total_seconds() / 3600  # 转换为小时 (Convert to hours)
                    break
            
            # 判断过去五天内是否有发热记录 (Check if there were febrile records in the past 5 days)
            had_febrile_in_past_5_days = any(
                (start <= past_5_days <= end or past_5_days <= start <= cutoff_time)
                for start, end in febrile_intervals
            )
            
            # 根据逻辑分类到case (Classify into cases based on logic)
            if is_febrile:
                if febrile_duration < 24:
                    case = 1
                elif 24 <= febrile_duration <= 48:
                    case = 2
                else:
                    case = 3
            else:
                if had_febrile_in_past_5_days:
                    case = 4
                else:
                    case = 5
            
            # 检查当前case是否已达到限制 (Check if the case has reached the limit)
            if len(cases[case]) < case_limit:
                # 保存符合条件的示例 (Save the example)
                cases[case].append({
                    'patientID': patient_data['patientID'],  # 患者ID (Patient ID)
                    'cutoff_time': cutoff_time              # 截断时间 (Cutoff time)
                })
            break  # 每个患者只记录一个例子 (Only record one example per patient)
    
    return cases

# 示例患者数据 (Example patient records)
patient_records = patients_with_long_febrile_period

# 查找每个case的示例 (Find examples for each case)
cases_examples = classify_and_collect_cases(patient_records)

# 输出结果 (Output the results)
for case, examples in cases_examples.items():
    print(f"Case {case}: Found {len(examples)} examples")
    for example in examples:
        print(f"  PatientID: {example['patientID']}, Cutoff Time: {example['cutoff_time']}")
