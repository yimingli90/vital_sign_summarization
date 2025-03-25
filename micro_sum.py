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
from utilities import save_file
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from templates import TEMPLATE_MICRO

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

PATIENTS_INFO = './data/patients_with_long_febrile_period.pkl'
CASES_DS = './data/cases_ds.pkl'
MICRO_CSV = './data/micro.csv'

def _get_micro_df():
    """Pre-precessing of the micro results."""
    
    df = pd.read_csv(MICRO_CSV)
    df["CollectionDateTime"] = pd.to_datetime(df["CollectionDateTime"], errors="coerce")
    
    # Remove non-sense results
    df_filtered = df[
        ~df['BatTestName'].str.contains('NOT TESTED', na=False) &
        ~df['ResultFull'].str.contains('DO NOT REPORT', na=False) &
        ~df["Result"].str.contains('DEL', na=False) &
        ~df["Result"].str.fullmatch("NONE", na=False) &
        ~df["TestName"].str.fullmatch("COMMENT", na=False)
    ].copy()
    
    return df_filtered


def _add_micro_df(df):
    """Add micro results to each example."""
    
    with open(CASES_DS, 'rb') as pk:
        cases = pickle.load(pk)
    with open(PATIENTS_INFO, 'rb') as pk:
        patients_with_long_febrile_period = pickle.load(pk)
        
    for case_ in cases:
        for example in case_:
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
    
    ds_reasoning = ""
    
    other_df = df[
        df['DrugName'].isna() & 
        df['DrugResult'].isna() &
        (df['TestName'].notna() | df['BatTestName'].notna())
    ].copy() 

    other_df['Date'] = other_df['CollectionDateTime'].dt.strftime('%d/%m/%y')
    
    


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
            else:
                other_results = _process_other_info(df=example["micro_records"])
                example["micro_info"]["other_results"] = other_results

            count += 1
    
    
if __name__ == '__main__':
    micro_df = _get_micro_df()
    cases = _add_micro_df(micro_df)
    _add_micro_results(flag="abx", cases=cases)
    _add_micro_results(flag="other", cases=cases)
    # 下一步内容： 对于abxresult 需要用list保存所有数据，输出数据只有positive或者all negative
    
