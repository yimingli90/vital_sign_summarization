# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 15:06:30 2025

@author: Yiming Li
"""

import pickle
import time
import pandas as pd
import re
import os
from utilities import save_file
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from templates import TEMPLATE_MICRO

with open('./data/cases_ds.pkl', 'rb') as pk:
    cases = pickle.load(pk)
    
with open('./data/patients_with_long_febrile_period.pkl', 'rb') as pk:
    patients_with_long_febrile_period = pickle.load(pk)

load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

# Replace with your OpenAI API key
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

df = pd.read_csv('./data/micro.csv')
df["CollectionDateTime"] = pd.to_datetime(df["CollectionDateTime"], errors="coerce")
df = df[
    (~df['BatTestName'].str.contains('NOT TESTED', na=False)) &
    (~df['ResultFull'].str.contains('DO NOT REPORT', na=False)) &
    (~df["Result"].str.contains('DEL', na=False))
].copy() #DEL也不要
# 读取CSV数据


# ====================== 第一部分：处理DrugName和DrugResult非空记录 ======================
def process_part1(df):
    # 筛选有效记录
    part1_df = df[(df['DrugName'].notna()) & (df['DrugResult'].notna())].copy()
    part1_df['Date'] = part1_df['CollectionDateTime'].dt.strftime('%d/%m/%y')
    
    # 分组并生成 R/S 列表
    grouped = (
        part1_df.groupby(['Date', 'BatTestCode', 'BugCodeFull'], as_index=False)  # 确保分组列保留为普通列
        .apply(lambda x: pd.Series({
            'R': list(x[x['DrugResult'] == 'R']['DrugName']),
            'S': list(x[x['DrugResult'] == 'SS']['DrugName'])
        }))
        .reset_index(drop=True)  # 重置索引
    )
    
    # 生成新格式的输出
    output = []
    for _, row in grouped.iterrows():
        # 第一行：日期、样本类型和菌株
        line = f"{row['Date']} – {row['BatTestCode']} – {row['BugCodeFull']}\n"
        
        # 添加 R 抗生素
        if row['R']:
            for drug in row['R']:
                line += f"\t– R: {drug}\n"
        
        # 添加 S 抗生素
        if row['S']:
            for drug in row['S']:
                line += f"\t– S: {drug}\n"
        
        output.append(line.strip())  # 移除末尾的换行符
    
    return output

# ====================== 第二部分：处理DrugName和DrugResult为空记录 ======================
def process_part2(df):
    # 筛选有效记录
    reasoning = ""
    part2_df = df[
        (df['DrugName'].isna()) & 
        (df['DrugResult'].isna()) &
        (df['TestName'].notna() | df['BatTestName'].notna()) &
        # (df['BatTestName'].notna()) &
        (~df['ResultFull'].str.contains('DO NOT REPORT', na=False)) &
        (~df["Result"].str.contains('DEL', na=False))
    ].copy() #DEL也不要
    
    # 日期格式化
    part2_df['Date'] = part2_df['CollectionDateTime'].dt.strftime('%d/%m/%y')
    
    def determine_result(row):


        test_name = ""
        if "DET" == row["Result"]:
            return "Positive"
        if "NDET" == row["Result"] or "NEG" == row["Result"] or "NONE" == row["Result"] or "NONS" == row["Result"]:
            return "Negative"   
        if "positive" in row['ResultFull'].lower() and "negative" in row['ResultFull'].lower():
            return row["SpecimenFull"] + ' ' + row["ResultFull"]
        if row["TestName"] == "RESULT":
            if "GROWTH" in row['ResultFull']:
                return row["SpecimenFull"] + ' ' + row["ResultFull"]
            test_name = row["BatTestName"]
        else:
            test_name = row["TestName"]
        
        specimen_full = row["SpecimenFull"]
        result_full = row['ResultFull']
        try:
            response = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system",
                     "content": "You are a clinical data analyst specialized in interpreting patient temperature records."},
                    {"role": "user",
                     "content": TEMPLATE_MICRO.format(test_name=test_name, specimen_full = specimen_full, result_full=result_full)}
                ],
                temperature=0  # deterministic output
            )

            reasoning = response.choices[0].message.reasoning_content
            summary = response.choices[0].message.content
            print("Result:", result_full)
            print("Summary:", summary)

        except Exception as e:
            time.sleep(120)
            response = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system",
                     "content": "You are a clinical data analyst specialized in interpreting patient temperature records."},
                    {"role": "user",
                     "content": TEMPLATE_MICRO.format(test_name=test_name, specimen_full = specimen_full, result_full=result_full)}
                ],
                temperature=0  # deterministic output
            )

            reasoning = response.choices[0].message.reasoning_content
            summary = response.choices[0].message.content
            print("Result:", result_full)
            print("Summary:", summary)

        return summary
    
    summary  = determine_result
    part2_df['FinalResult'] = part2_df.apply(summary, axis=1)
    
    
    # 生成输出
    output = []
    for _, row in part2_df.iterrows():
        sample_type = row['BatTestName'] if row['TestName'] == 'RESULT' else row['TestName']
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
            (df["CollectionDateTime"] >= cut_in_time - pd.DateOffset(days=7)) &
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
i = 0
for case_ in cases:
    for example in case_:
        current_time = datetime.now().time()
        print(i)
        print(" Current time:", current_time)
        if "micro_records" not in example:
            continue  # 跳过没有 lab_records 的数据
        part1_results = process_part1(pd.DataFrame(example["micro_records"]))
        part2_results = process_part2(pd.DataFrame(example["micro_records"]))
       # final_output = merge_and_sort_results(part1_results, part2_results)
        example["micro_summary_part_1"] = part1_results
        example["micro_summary_part_2"] = part2_results
      # example["micro_summary_part_2_reasoning"] = reasoning
        i += 1
i = 0
for case_ in cases:
    for example in case_:

        current_time = datetime.now().time()
        print(i)
        print(" Current time:", current_time)
        if example["micro_records_1y"].empty:
            i += 1
            continue
        part2_results = process_part2(pd.DataFrame(example["micro_records_1y"]))
        part2_results_filter = [s for s in part2_results if "positive" in s.lower()]
       # final_output = merge_and_sort_results(part1_results, part2_results)
        example["micro_summary_1y"] = part2_results_filter

      # example["micro_summary_part_2_reasoning"] = reasoning
        i += 1



##post processing

i = 0
for case_ in cases:
    for example in case_:
        print(i)
        current_time = datetime.now().time()
        print(" Current time:", current_time)
        
        micro_records = example['micro_records']
        micro_records_1y = example['micro_records_1y']
        micro_df = pd.concat([micro_records, micro_records_1y], axis=0)
        
        bat_test_dict = {}
        test_dict = {}
        for _, row in micro_df.iterrows():
            bat_test_dict[row['BatTestCode']] = row['BatTestName']  # BatTestCode 作为 key
            test_dict[row['TestName']] = row['BatTestName'] 
            

        if len(example['micro_summary_part_1']) > 0:
            for j, sum_ in enumerate(example['micro_summary_part_1']):
                sum_ = sum_.replace('-', '–')
                sum_ = sum_.replace('BLOOD FOR CULTURE', '')
                str_list = sum_.split(' – ')
                
                if str_list[1] == "UC" or str_list[1] == "BLC":
                    example['micro_summary_part_1'][j] = sum_
                    continue
                
                if str_list[1] == "CT VALUE" or str_list[1] == "COMMENT":
                    if test_dict[str_list[1]] == "BLOOD CULTURE":
                        str_list[1] = "BLC"
                    elif test_dict[str_list[1]] == "URINE CULTURE":
                        str_list[1] = "UC"
                    else:
                        str_list[1] = test_dict[str_list[1]]
                elif str_list[1] in bat_test_dict.keys():
                    str_list[1] = bat_test_dict[str_list[1]]
                else:
                    example['micro_summary_part_1'][j] = sum_
                    continue
                
                example['micro_summary_part_1'][j] = ' – '.join(str_list)

        if len(example['micro_summary_part_2']) > 0:
            for j, sum_ in enumerate(example['micro_summary_part_2']):
                sum_ = sum_.replace('-', '–')
                sum_ = sum_.replace('BLOOD FOR CULTURE', '')
                str_list = sum_.split(' – ')
                
                if str_list[1] == "UC" or str_list[1] == "BLC":
                    example['micro_summary_part_2'][j] = sum_
                    continue
                
                if str_list[1] == "CT VALUE" or str_list[1] == "COMMENT":
                    if test_dict[str_list[1]] == "BLOOD CULTURE":
                        str_list[1] = "BLC"
                    elif test_dict[str_list[1]] == "URINE CULTURE":
                        str_list[1] = "UC"
                    else:
                        str_list[1] = test_dict[str_list[1]]
                elif str_list[1] in bat_test_dict.keys():
                    str_list[1] = bat_test_dict[str_list[1]]
                else:
                    example['micro_summary_part_2'][j] = sum_
                    continue
                
                example['micro_summary_part_2'][j] = ' – '.join(str_list)
        
        if 'micro_summary_1y' in example:
            for j, sum_ in enumerate(example['micro_summary_1y']):
                sum_ = sum_.replace('-', '–')
                sum_ = sum_.replace('BLOOD FOR CULTURE', '')
                str_list = sum_.split(' – ')
                
                if str_list[1] == "UC" or str_list[1] == "BLC":
                    example['micro_summary_1'][j] = sum_
                    continue
                
                if str_list[1] == "CT VALUE" or str_list[1] == "COMMENT":
                    if test_dict[str_list[1]] == "BLOOD CULTURE":
                        str_list[1] = "BLC"
                    elif test_dict[str_list[1]] == "URINE CULTURE":
                        str_list[1] = "UC"
                    else:
                        str_list[1] = test_dict[str_list[1]]
                elif str_list[1] in bat_test_dict.keys():
                    str_list[1] = bat_test_dict[str_list[1]]
                else:
                    example['micro_summary_1y'][j] = sum_
                    continue
                
                example['micro_summary_1y'][j] = ' – '.join(str_list)
        

        i += 1        


i = 0
for case_ in cases:
    for example in case_:
        
        if len(example['micro_summary_part_1']) > 0:
            part_1 = '\n'.join(example['micro_summary_part_2'])
        else:
            part_1 = ''
        if len(example['micro_summary_part_2']) > 0:
            data_lines = example['micro_summary_part_1'] + example['micro_summary_part_2']
            records_combined = []
            current_record = ""
            date_pattern = re.compile(r"^\d{2}/\d{2}")
            
            for line in data_lines:
                line = line.strip()
                if not line:
                    continue
                if date_pattern.match(line):
                    if current_record:
                        records_combined.append(current_record)
                    current_record = line
                else:
                    current_record += " " + line
            if current_record:
                records_combined.append(current_record)
            
            # 2. 解析记录：提取日期、sample_type、result和summary
            parsed_records = []
            for rec in records_combined:
                parts = rec.split(" – ")
                if len(parts) < 3:
                    continue
                date_str = parts[0].strip()
                sample_type = parts[1].strip()
                result_and_more = parts[2].strip()
                
                summary = ""
                summary_split = re.split(r"\*\*Summary:\*\*", result_and_more)
                result = summary_split[0].strip()
                if len(summary_split) > 1:
                    summary = summary_split[1].strip()
                if not summary and len(parts) > 3:
                    summary = " – ".join(parts[3:]).strip()
                
                parsed_records.append({
                    "date": date_str,
                    "sample_type": sample_type,
                    "result": result,
                    "summary": summary
                })
            
            # 3. 转换日期字符串为 datetime 对象（假设年份为2025）
            for rec in parsed_records:
                try:
                    year = str(example['cut_in_time'].year)
                    rec["date_obj"] = datetime.strptime(rec["date"] + "/"+year, "%d/%m/%Y")
                except Exception as e:
                    print(f"日期解析错误: {rec['date']}, 错误信息: {e}")
            
            # 4. 按日期降序排序（最新记录在前）
            records_sorted = sorted(parsed_records, key=lambda x: x["date_obj"], reverse=True)
            
            # 5. 添加时间过滤：例如4月20号之前7天的数据，即仅保留2025年4月13日至4月19日之间的记录
            cut_in_time = example['cut_in_time']
            start_date = cut_in_time - pd.DateOffset(days=7)
            # 保留 [start_date, reference_date) 之间的记录
            filtered_records = [rec for rec in records_sorted if start_date <= rec["date_obj"] <= cut_in_time]
            
            # 6. 分组：对相同 sample type 的记录进行分组
            grouped = {}
            for rec in filtered_records:
                stype = rec["sample_type"]
                grouped.setdefault(stype, []).append(rec)
            
            # 7. 筛选记录：若某一 sample type 的所有记录结果都包含 "Negative"（不区分大小写），只保留最新一条记录
            final_records = []
            for stype, rec_list in grouped.items():
                if all("NEGATIVE" in r["result"].upper() for r in rec_list):
                    final_records.append(rec_list[0])
                else:
                    final_records.extend(rec_list)
            
            # 8. 最终按日期降序整理记录，并生成一个完整的字符串（每条记录一行）
            final_records = sorted(final_records, key=lambda x: x["date_obj"], reverse=True)
            output_lines = []
            for rec in final_records:
                line = f'{rec["date"]} – {rec["sample_type"]} – {rec["result"]}'
                if rec["summary"]:
                    line += f'\n  Summary: {rec["summary"]}'
                output_lines.append(line)
            
            final_output = "\n".join(output_lines)
            
        if 'micro_summary_1y' in example:
            def parse_date(item):
                # 用正则匹配字符串开头的 "DD/MM"
                match = re.match(r"^(\d{2}/\d{2})", item)
                if match:
                    # 将匹配到的 "DD/MM" 转换成 "DD/MM/2025" 后解析为日期
                    date_str = match.group(1)
                    return datetime.strptime(date_str + "/2025", "%d/%m/%Y")
                else:
                    # 如果没有匹配到日期，返回一个最小值，保证它排在最末尾（或最前面）
                    return datetime.min

            # 按日期降序排序（reverse=True 表示最新在前）
            example['micro_summary_1y'] = sorted(example['micro_summary_1y'], key=parse_date, reverse=True)
            
            
            example['micro_final_results'] = final_output + '\n--------Previous result (1 year)--------\n' + '\n'.join(example['micro_summary_1y'])
        else:
            example['micro_final_results'] = final_output


save_file.save_variable_to_pickle(variable=cases, file_path='./data/cases_micro_ds.pkl')
with open('./data/cases_micro_ds.pkl', 'rb')as f:
    cases = pickle.load(f)

# filtered_df = df[(df['BatTestName'] == 'MRSA SCREEN') & (~df['ResultFull'].str.contains('NO METHICILLIN', na=False))]
# filtered_df = df[df['ResultFull'].str.contains("NEGATIVE", na=False)]
# # filtered_df = df[(df['ResultFull'].str.contains("ISOLATED", na=False)) & (df['ResultFull'].str.contains("NO ", na=False)) &]
# filtered_df = df[
#     df["ResultFull"].str.contains("NEGATIVE", case=False, na=False) &
#     df["BugCode"].isna()
# ]

# filtered_df = df[
#     df["ResultFull"].str.contains("ISOLATED", case=False, na=False) &
#     df["ResultFull"].str.contains("NEGATIVE", case=False, na=False) &
#     df["BugCode"].isna()
# ]

# filtered_df = df[
#     df["ResultFull"].str.contains("ISOLATED", case=False, na=False) &
#     df["ResultFull"].str.contains("NO", case=False, na=False) &
#     df["BugCode"].isna()
# ]

# filtered_df = df[
#     df["TestName"].str.contains("RESULT", case=False, na=False) &
#     df["DrugName"].isna() &
#     ~df["ResultFull"].str.contains("GROWTH", case=False, na=False) &
#     df["BugCode"].isna() &
#     (
#         df["ResultFull"].str.contains("no ", case=False, na=False) |
#         df["ResultFull"].str.contains("not ", case=False, na=False) |
#         df["ResultFull"].str.contains("negative", case=False, na=False)
#     )
# ]#Not No Negative in it. have both negative and negative then write spenc  判断为负且TestName is Result然后不是ndet等result结果  加上result里有N

# filtered_df = df[
#     df["TestName"].str.contains("RESULT", case=False, na=False) &
#     df["DrugName"].isna() &
#     ~df["Result"].str.contains("N", case=False, na=False) &
#     ~df["ResultFull"].str.contains("GROWTH", case=False, na=False) &
#     df["BugCode"].isna() &
#     (
#         df["ResultFull"].str.contains("no ", case=False, na=False) |
#         df["ResultFull"].str.contains("not ", case=False, na=False) |
#         df["ResultFull"].str.contains("negative", case=False, na=False)
#     )
# ]

# filtered_df = df[
#     ~df["TestName"].str.contains("RESULT", case=False, na=False) &
#     df["DrugName"].isna() &
#     df["BugCode"].notna()
# ]

# filtered_df = df[
#     df["ResultFull"].str.contains("positive", case=False, na=False) &
#     df["ResultFull"].str.contains("negative", case=False, na=False)
# ]#Not No Negative