# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 13:46:22 2025

@author: YimingL
"""

import pickle
import time
import pandas as pd
import re
import os
import ast
from llm import deepseek
from utilities import save_file
from datetime import datetime
from templates import TEMPLATE_MICRO

PATIENTS_INFO = './data/patients_with_long_febrile_period.pkl'
CASES_DS = './data/cases_ds.pkl'
MICRO_CSV = './data/micro.csv'

def _get_micro_df():
    """Pre-precessing of the micro results."""
    
    df = pd.read_csv(MICRO_CSV)
    df["CollectionDateTime"] = pd.to_datetime(df["CollectionDateTime"], errors="coerce")
    
    # Remove non-sense results
    df_filtered = df[
        ~df['TestName'].str.contains('NOT TESTED', na=False) &
        ~df['ResultFull'].str.contains('DO NOT REPORT', na=False) &
        ~df["Result"].str.contains('DEL', na=False)
        # ~df["TestName"].str.fullmatch("COMMENT", na=False)
    ].copy()
    
    return df_filtered


def _add_micro_df(df):
    
    """Add micro results to each example."""
    
    with open(CASES_DS, 'rb') as pk:
        cases = pickle.load(pk)
    with open(PATIENTS_INFO, 'rb') as pk:
        patients_with_long_febrile_period = pickle.load(pk)
    
    print("Adding micro data")
    count = 0
    for case_ in cases:
        for example in case_:
            print(count)
            count += 1
            
            example["micro_info"] = {}
            data = patients_with_long_febrile_period[example['index']]
            example['patientID'] = data['patientID']
            admission_date = example['AdmissionDate']
            cut_in_time = example['cut_in_time']
            patient_id = example['patientID']
        
            # Only keep the data 7 days before the admission
            matched_df = df[
                (df["ClusterID"] == patient_id) &
                (df["CollectionDateTime"] >= cut_in_time - pd.DateOffset(days=7)) &
                (df["CollectionDateTime"] <= cut_in_time)
            ]
            
            # Get the records one year before the admission
            matched_df_1y = df[
                (df["ClusterID"] == patient_id) &
                (df["CollectionDateTime"] >= admission_date - pd.DateOffset(years=1)) &
                (df["CollectionDateTime"] < admission_date)
            ]
            
            example["micro_info"]["micro_records"] = matched_df.sort_values(by='CollectionDateTime', ascending=False)
            example["micro_info"]["micro_records_1y"] = matched_df_1y.sort_values(by='CollectionDateTime', ascending=False)
    return cases

def _determine_result(row):
    
    """"Return the determined result, with other results confirmed by the LLM"""
    
    reasoning = ""
    if "DET" == row["Result"]:
        return reasoning + "!!@@##" + "Positive"
    if "NDET" == row["Result"] or "NEG" == row["Result"] or "NONE" == row["Result"] or "NONS" == row["Result"]:
        return reasoning + "!!@@##" + "**Negative**"   
    if "positive" in row['ResultFull'].lower() and "negative" in row['ResultFull'].lower():
        return reasoning + "!!@@##" + row["SpecimenFull"] + ' ' + row["ResultFull"]
    if row["TestName"] == "RESULT":
        test_name = row["BatTestName"]
    else:
        test_name = row["TestName"]
    
    specimen_full = row["SpecimenFull"]
    test_name = ""
    result_full = row['ResultFull']
    
    content = TEMPLATE_MICRO.format(test_name=test_name, specimen_full = specimen_full, result_full=result_full)
    reasoning, summary = deepseek.call(content=content)
    
    return reasoning + "!!@@##" + summary

def _process_abx_info(df):
    
    """Processing antibiotic sensitive and resistant info"""
    
    abx_df = df[(df['DrugName'].notna()) & (df['DrugResult'].notna())].copy()
    abx_df['Date'] = abx_df['CollectionDateTime'].dt.strftime('%d/%m/%y')
    
    # Group results by accessionn and gene
    grouped = (
        abx_df.groupby(['Date', 'AccessionNumber', 'BatTestName', 'BugCodeFull'], as_index=False)
        .apply(lambda x: pd.Series({
            'R': list(x[x['DrugResult'] == 'R']['DrugName']),
            'SS': list(x[x['DrugResult'] == 'SS']['DrugName'])
        }))
        .reset_index(drop=True)  
    )
    
    # Generate output
    output_all = [] # Records all the abx results both SS and R for the further LLM usage
    output_results = [] # Rsults shown in the infeciton review
    all_negative = True
    for _, row in grouped.iterrows():
        # First line
        line = f"{row['Date']} – {row['BatTestName']} – {row['BugCodeFull']}\n"
        
        # Add resistant abx
        if row['R']:
            all_negative = False
            for drug in row['R']:
                line += f"\t– R: {drug}\n"
                
            # If not all results are SS, reports all sentiment
            output_results.append(line.strip())
        
        # Add sensitive abx
        if row['SS']:
            for drug in row['SS']:
                line += f"\t– S: {drug}\n"
        
        if all_negative:
            tmp_line = f"{row['Date']} – {row['BatTestName']} – {row['BugCodeFull']}\n" + "\t– All sensitive\n"
            output_results.append(tmp_line.strip())

        output_all.append(line.strip())
        
    return output_all, output_results    

def _process_other_info(df):
    
    """Processing other micro results info"""
    
    other_df = df[
        df['DrugName'].isna() & 
        df['DrugResult'].isna() &
        (df['TestName'].notna() | df['BatTestName'].notna()) &
        ~df["ResultFull"].str.contains("GROWTH", case=False, na=False)
    ].copy() 
    other_df['Date'] = other_df['CollectionDateTime'].dt.strftime('%d/%m/%y')


    
    def merge_records(df):
        """Merge the the sample type results and sort by date"""
        
        df['Date'] = pd.to_datetime(df['Date'])
        

        def standardize_test_entry(test_names, final_results):
            # Pair TestName and FinalResult
            paired = sorted(zip(test_names, final_results), key=lambda x: x[0])
            sorted_names = [x[0] for x in paired]
            sorted_results = [x[1] for x in paired]
            
            # Standardize result representation (extract content between ** or use original)
            standardized_results = []
            for result in sorted_results:
                if '**' in result:
                    parts = [p.strip() for p in result.split('**') if p.strip()]
                    standardized_results.append(parts[0] if parts else result)
                else:
                    standardized_results.append(result)
            
            return '|'.join(sorted_names), '|'.join(standardized_results)
        
        # Create standardized composite key
        df['TestKey'] = df.apply(
            lambda row: (
                str(row['BatTestName']) + '||' + 
                standardize_test_entry(row['TestName'], row['FinalResult'])[0]
            ), 
            axis=1
        )
        
        # Sort by date descending, then keep only the first record of each (TestKey+ResultKey) pair
        df['ResultKey'] = df.apply(
            lambda row: standardize_test_entry(row['TestName'], row['FinalResult'])[1],
            axis=1
        )
        
        # Sort by date descending, then keep only the first record of each (TestKey+ResultKey) pair
        df = df.sort_values('Date', ascending=False)
        df = df.drop_duplicates(subset=['TestKey', 'ResultKey'], keep='first')
        df = df.sort_values('Date', ascending=False)
        
        # Generate output
        results = []
        for _, row in df.iterrows():
            date = row['Date'].strftime('%d/%m/%y')
            bat_test_name = row['BatTestName']
            test_names = row['TestName']
            final_results = row['FinalResult']
            
            # Case 1: BatTestName is empty
            if pd.isna(bat_test_name) or bat_test_name == '':
                for test, result in zip(test_names, final_results):
                    neg_pos = result.split('**')[1] if '**' in result else result
                    results.append(f"{date} - {test} - {neg_pos.strip()}")
            
            # Case 2: All results are Negative
            elif all('Negative' in result for result in final_results):
                results.append(f"{date} - {bat_test_name} - Negative")
            
            # Case 3: Contains Positive results
            else:
                output_lines = [f"{date} - {bat_test_name}"]
                for test, result in zip(test_names, final_results):
                    if 'Negative' in result:
                        output_lines.append(f"   - {test} Negative")
                results.append('\n'.join(output_lines))
        
        return results
    
    if not other_df.empty:
        result = _determine_result
        other_df['FinalResult'] = other_df.apply(result, axis=1)
        split_df = other_df['FinalResult'].str.split("!!@@##", expand=True)
        other_df['ResultReasoning'] = split_df[0]
        other_df['FinalResult'] = split_df[1]
        other_df = other_df.fillna('')
        other_df_filtered = other_df[~other_df["FinalResult"].str.contains("No clear Result", case=False, na=False)]
       
        # Group the the results with the same AccessionNumber and BatTestName
        grouped_other_df = other_df_filtered.groupby(["Date", "AccessionNumber", "BatTestName"]).agg({
            "TestName": lambda x: list(x),
            "FinalResult": lambda x: list(x)
            }).reset_index()
        
        if not grouped_other_df.empty:
            processed_results = merge_records(grouped_other_df) 
            other_sum_merged = '\n'.join(processed_results)
            output = []
            for _, row in other_df_filtered.iterrows():
                sample_type = row['BatTestName'] if row['TestName'] == 'RESULT' else row['TestName']
                output.append(f"{row['Date']} – {sample_type} – {row['FinalResult']}")
            other_sum_all = '\n'.join(output)

        else:
            other_sum_merged, other_sum_all = '', ''
    else:
        other_df['FinalResult'] = ''
        other_df['ResultReasoning'] = ''
        other_sum_merged, other_sum_all = '', ''
        
    # Result with "GROWTH" in it will be processed separately
    growth_df = df[
        df['DrugName'].isna() & 
        df['DrugResult'].isna() &
        (df['TestName'].notna() | df['BatTestName'].notna()) &
        df["ResultFull"].str.contains("GROWTH", case=False, na=False)
    ].copy()
    growth_df['Date'] = growth_df['CollectionDateTime'].dt.strftime('%d/%m/%y')
    growth_df["CollectionDate"] = pd.to_datetime(growth_df["CollectionDateTime"]).dt.date
    grouped = growth_df.groupby(["CollectionDate", "BatTestName"]).agg({
    "SpecimenFull": lambda x: list(x),  
    "ResultFull": lambda x: list(x)     
}).reset_index()
    
    def clean_result(result):
        match_ = re.search(r"NO GROWTH AFTER (\d+) (DAYS|WEEKS)", result)
        if match_:
            time_value = int(match_.group(1))
            time_unit = match_.group(2)
            
            # >= 5 DAYS
            if (time_unit == "DAYS" and time_value >= 5) or (time_unit == "WEEKS" and time_value >= 1):
                # return "NO GROWTH"
                return result.replace(match_.group(0), "NO GROWTH.") # Only change the "NO GROWTH AFTER X DAYS/WEEKS" part
        return result
    
    def summarize_row(row):
        date = pd.to_datetime(row["CollectionDate"]).strftime('%d/%m/%y')  # 格式化日期
        test_name = row["BatTestName"]
        specimens = row["SpecimenFull"]
        results = [clean_result(result) for result in row["ResultFull"]]  # 处理结果文本
        
        # 组合 SpecimenFull 和 ResultFull
        summary_parts = [f"– {specimen} – {result}" for specimen, result in zip(specimens, results)]
        summary = f"{date} –  {test_name} " + " \n" + " \n".join(summary_parts)
        summary = summary.replace("– BLOOD FOR CULTURE", "– ")
    
        return summary
    
    if not grouped.empty:
        grouped["Summary"] = grouped.apply(summarize_row, axis=1)
    else:
        grouped["Summary"] = ''
    
    growth_sum = "\n".join(grouped["Summary"].tolist())
    sum_mereged = growth_sum + '\n' + other_sum_merged
    sum_all = growth_sum + '\n' + other_sum_all
    
    return sum_mereged, sum_all, other_df, growth_df

def _process_1y_info(df):
    
    """Process patient mico data 1 year before the admission"""
    
    df_1y = df[
        df["BatTestName"].str.contains("MRSA", case=False, na=False) |
        df["BatTestName"].str.contains("ESBL", case=False, na=False) |
        df["BatTestName"].str.contains("VRE", case=False, na=False) |
        df["BatTestName"].str.contains("CPE", case=False, na=False) |
        df["BatTestName"].str.contains("CANDIDA AURIS", case=False, na=False)
    ].copy() 
    df_1y['Date'] = df_1y['CollectionDateTime'].dt.strftime('%d/%m/%y')
    
    if df_1y.empty:
        print("1y empty, skip")
        df_1y['FinalResult'] = ''
        df_1y['ResultReasoning'] = ''
        df_1y_sum = ''
        
    else:
        print("Found 1y records as follow:")
        print(df_1y)
        print("Determining result")
        result = _determine_result
        df_1y['FinalResult'] = df_1y.apply(result, axis=1)
        split_df = df_1y['FinalResult'].str.split("!!@@##", expand=True)
        df_1y['ResultReasoning'] = split_df[0]
        df_1y['FinalResult'] = split_df[1]
        df_1y = df_1y.fillna('')
        df_1y_positive = df_1y[df_1y["FinalResult"].str.contains("Positive", case=False, na=False)]
        
        output = []
        for _, row in df_1y_positive.iterrows():
            sample_type = row['BatTestName'] if row['TestName'] == 'RESULT' else row['TestName']
            output.append(f"{row['Date']} – {sample_type} – {row['FinalResult']}")
        df_1y_sum = '\n'.join(output)
            
    return df_1y_sum, df_1y

def _add_micro_results(flag:str, cases):
    """Add micro results to the eaxmples"""
    
    count = 0
    for case_ in cases:
        for example in case_:
            print(count)
            current_time = datetime.now().time()
            print(" Current time:", current_time)
            
            if "micro_records" not in example["micro_info"]:
                count += 1
                continue
            if flag == "abx":
                abx_all, abx_results = _process_abx_info(df=example["micro_info"]["micro_records"])
                example["micro_info"]["abx_results"] = abx_results
                example["micro_info"]["abx_all"] = abx_all
            elif flag == 'other':
                other_results_merged, other_results_all, other_df, growth_df = _process_other_info(df=example["micro_info"]["micro_records"])
                example["micro_info"]["other_results_merged"] = other_results_merged
                example["micro_info"]["other_results_all"] = other_results_all
                example["micro_info"]["other_df"] = other_df
                example["micro_info"]["growth_df"] = growth_df
            else:
                result_1y, df_1y = _process_1y_info(df=example["micro_info"]["micro_records_1y"])
                example["micro_info"]["micro_records_1y_filtered"] = df_1y
                example["micro_info"]["1y_results"] = result_1y
                if result_1y:
                    print("Have positive 1y results")
                    print(count)
                    print(df_1y)

            count += 1
    
    
def _gen_final_results(cases):
    """"Generate final micro summarization"""

    for case_ in cases:
        for example in case_:
            results_1y = example["micro_info"]['1y_results']
            abx_results = '\n'.join(example["micro_info"]['abx_results'])
            other_results = example["micro_info"]['other_results_merged']
            
            micro_sum = abx_results + '\n' + other_results
            if results_1y:
                micro_sum += '\n-------------------Precious records (one year)-------------------\n'
                micro_sum += results_1y 
            example["micro_info"]['micro_sum'] = micro_sum.replace('FAECES MOLECULAR ASSAY', 'FAECES MOLECULAR ASSAY PCR')
            
    
    
if __name__ == '__main__':
    micro_df = _get_micro_df()
    cases = _add_micro_df(micro_df)
    
    print("Adding abx info")
    _add_micro_results(flag="abx", cases=cases)
    
    print("Adding other info")
    _add_micro_results(flag="other", cases=cases)
    
    print("Adding 1y info")
    _add_micro_results(flag="1y", cases=cases)
    
    print("Generating final micro summarization")
    _gen_final_results(cases=cases)
    
    save_file.save_variable_to_pickle(variable=cases, file_path='./data/cases_micro_ds_v2.pkl')
    
    # with open('./data/cases_micro_ds.pkl', 'rb')as f:
    #     cases = pickle.load(f)
    # 下一步内容： 对于abxresult 需要用list保存所有数据，输出数据只有positive或者all negative
    
# filtered_df = micro_df[
#     #~micro_df["TestName"].str.contains("RESULT", case=False, na=False) &
#     # micro_df["ResultFull"].str.contains("GROWTH", case=False, na=False) &
#     micro_df["BatTestName"].str.contains("ENTERIC PARASITE PCR", case=False, na=False)
#   #  micro_df["BatTestName"].str.contains("COMMENT", case=False, na=False)
# ]
#                 (df["BatTestName"].str.contains("MRSA", case=False, na=False) |
#                  df["BatTestName"].str.contains("ESBL", case=False, na=False) |
#                  df["BatTestName"].str.contains("VRE", case=False, na=False) |
#                  df["BatTestName"].str.contains("CPE", case=False, na=False) |
#                  df["BatTestName"].str.contains("CANDIDA AURIS", case=False, na=False)
#                  )