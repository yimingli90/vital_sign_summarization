# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 15:06:30 2025

@author: Yiming Li
"""

import pickle
import pandas as pd
import re
from utilities import save_file
from datetime import datetime

with open('./data/cases_rules.pkl', 'rb') as pk:
    cases = pickle.load(pk)
    
with open('./data/patients_with_long_febrile_period.pkl', 'rb') as pk:
    patients_with_long_febrile_period = pickle.load(pk)

df = pd.read_csv('./data/micro.csv')
df["CollectionDateTime"] = pd.to_datetime(df["CollectionDateTime"], errors="coerce")
filtered_df = df[(df['BatTestName'] == 'MRSA SCREEN') & (~df['ResultFull'].str.contains('NO METHICILLIN', na=False))]
filtered_df = df[df['ResultFull'].str.contains("NEGATIVE", na=False)]
# filtered_df = df[(df['ResultFull'].str.contains("ISOLATED", na=False)) & (df['ResultFull'].str.contains("NO ", na=False)) &]
filtered_df = df[
    df["ResultFull"].str.contains("NEGATIVE", case=False, na=False) &
    df["BugCode"].isna()
]

filtered_df = df[
    df["ResultFull"].str.contains("ISOLATED", case=False, na=False) &
    df["ResultFull"].str.contains("NEGATIVE", case=False, na=False) &
    df["BugCode"].isna()
]

filtered_df = df[
    df["ResultFull"].str.contains("ISOLATED", case=False, na=False) &
    df["ResultFull"].str.contains("NO", case=False, na=False) &
    df["BugCode"].isna()
]

filtered_df = df[
    df["TestName"].str.contains("RESULT", case=False, na=False) &
    df["DrugName"].isna() &
    ~df["ResultFull"].str.contains("GROWTH", case=False, na=False) &
    df["BugCode"].isna()
]#Not No Negative in it. have both negative and negative then write spenc

filtered_df = df[
    df["ResultFull"].str.contains("positive", case=False, na=False) &
    df["ResultFull"].str.contains("negative", case=False, na=False)
]#Not No Negative
import pandas as pd
import re
from io import StringIO

# 读取CSV数据


# ====================== 第一部分：处理DrugName和DrugResult非空记录 ======================
def process_part1(df):
    # 筛选有效记录
    part1_df = df[(df['DrugName'].notna()) & (df['DrugResult'].notna())].copy()
    part1_df['Date'] = part1_df['CollectionDateTime'].dt.strftime('%d/%m')
    
    # 分组并生成 R/S 列表
    grouped = (
        part1_df.groupby(['Date', 'BatTestCode', 'BugCodeFull'], as_index=False)  # 确保分组列保留为普通列
        .apply(lambda x: pd.Series({
            'R': list(x[x['DrugResult'] == 'R']['DrugCode']),
            'S': list(x[x['DrugResult'] == 'SS']['DrugCode'])
        }))
        .reset_index(drop=True)  # 重置索引
    )
    
    # 生成输出
    output = []
    for _, row in grouped.iterrows():
        line = f"{row['Date']} – {row['BatTestCode']} – {row['BugCodeFull']}"
        if row['R']:
            line += f" – R {', '.join(row['R'])}"
        if row['S']:
            line += f"; S {', '.join(row['S'])}" if row['R'] else f" – S {', '.join(row['S'])}"
        output.append(line)
    
    return output

# ====================== 第二部分：处理DrugName和DrugResult为空记录 ======================
def process_part2(df):
    # 筛选有效记录
    part2_df = df[
        (df['DrugName'].isna()) & 
        (df['DrugResult'].isna()) &
        (df['TestName'].notna()) &
        (df['BatTestName'].notna()) &
        (df["BugCode"].isna()) &
        (~df['ResultFull'].str.contains('DO NOT REPORT', na=False))
    ].copy()
    
    # 日期格式化
    part2_df['Date'] = part2_df['CollectionDateTime'].dt.strftime('%d/%m')
    
    # 判断结果状态
    neg_keywords = re.compile(r'\b(No ISOLATED|NEGATIVE|NO|no|NOT|not|none|NONE|None|Not|Negative|negtive)\b', re.IGNORECASE)
    pos_keywords = re.compile(r'\b(Positive|POSITIVE|positive)\b')
    
    def determine_result(row):
        if "DET" == row["Result"]:
            return "Positive"
        if "NDET" == row["Result"] or "NEG" == row["Result"] or "NONE" == row["Result"] or "NONS" == row["Result"]:
            return "Negative"   
        if "GROWTH" in row['ResultFull']:
            return row["Result"]
        if "NOT detected" in row['ResultFull'] or "not seen" in row['ResultFull']:
            return "Negative"
        if  pos_keywords.search(row['ResultFull']) and ("Negative" in row['ResultFull'] or "NEGATIVE" in row['ResultFull']):
            return row["Result"]
        if "No" in row['ResultFull'] or "NO " in row['ResultFull'] or "NOT " in row['ResultFull'] or "Not " in row['ResultFull']:
            if "isolated" in row['ResultFull'] or "ISOLATED" in row['ResultFull'] or "SEEN" in row['ResultFull'] or "seen" in row['ResultFull']:
                return "Negative"
        if pd.notna(row['ResultFull']):
            if "negative" in row['ResultFull'].lower() and "positive" in row['ResultFull'].lower():
                return row['Result']
            elif pos_keywords.search(row['ResultFull']):
                return 'positive'
        
        if row['TestName'] == 'RESULT' and not str(row['Result']).startswith('NG'):
            return 'Negative'
        
        return row['Result']
    
    part2_df['FinalResult'] = part2_df.apply(determine_result, axis=1)
    
    # 生成输出
    output = []
    for _, row in part2_df.iterrows():
        sample_type = row['BatTestCode'] if row['TestName'] == 'RESULT' else row['TestName']
        output.append(f"{row['Date']} – {sample_type} – {row['FinalResult']}")
    
    return output
    
# ====================== 合并并排序结果 ======================
def merge_and_sort_results(part1_results, part2_results):
    # 合并结果
    combined_results = part1_results + part2_results
    
    # 按日期排序
    combined_results.sort(key=lambda x: pd.to_datetime(x.split(' – ')[0], format='%d/%m'))
    
    # 转换为字符串
    return '\n'.join(combined_results)

for case_ in cases:
    for example in case_:
        data = patients_with_long_febrile_period[example['index']]
        example['patientID'] = data['patientID']
        admission_date = example['AdmissionDate']
        cut_in_time = example['cut_in_time']
        patient_id = example['patientID']
    
        # 筛选符合条件的 DataFrame
        matched_df = df[
            (df["ClusterID"] == patient_id) &
            (df["CollectionDateTime"] >= admission_date) &
            (df["CollectionDateTime"] <= cut_in_time)
        ]
        
        matched_df_1y = df[
            (df["ClusterID"] == patient_id) &
            (df["CollectionDateTime"] >= admission_date - pd.DateOffset(years=1)) &
            (df["CollectionDateTime"] < admission_date)
        ]
        # 转换 DataFrame 为 list，每行变成一个字典
        example["micro_records"] = matched_df
        example["micro_records_1y"] = matched_df_1y
# 遍历 data_list
for case_ in cases:
    for example in case_:
        if "micro_records" not in example:
            continue  # 跳过没有 lab_records 的数据
        part1_results = process_part1(pd.DataFrame(example["micro_records"]))
        part2_results = process_part2(pd.DataFrame(example["micro_records"]))
        final_output = merge_and_sort_results(part1_results, part2_results)
        example["micro_summary"] = final_output


save_file.save_variable_to_pickle(variable=cases, file_path='./data/cases_micro.pkl')


