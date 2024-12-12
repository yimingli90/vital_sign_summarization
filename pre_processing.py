# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 11:23:28 2024

@author: YimingL
"""

import os
import json
import pickle
import pandas as pd
from collections import defaultdict
from utilities.save_file import save_dict_to_json, save_variable_to_pickle
from utilities.get_specific_vital_sign import get_specific_vital_sign

inpt_recs_path = './data/inpt_episodes.csv'
vital_sign_path = './data/vitals.csv'
#linked_data_path = './data/linked_data.json'
linked_data_path = './data/linked_data.pkl'
linked_data_raw_path = './data/linked_data_raw.pkl'
#linked_data_finished_path = './data/linked_data.pkl'

def get_inpt_recs(admissions_df, save_file_path: str):
    linked_data = defaultdict(list)

    admissions_df = admissions_df 
    admissions_df['AdmissionDate'] = pd.to_datetime(admissions_df['AdmissionDate'])
    admissions_df['DischargeDate'] = pd.to_datetime(admissions_df['DischargeDate'])
    
    for _, row in admissions_df.iterrows():
        cluster_id = row['ClusterID']
        
        exists = any(
            admission['AdmissionDate'] == row['AdmissionDate'] and
            admission['DischargeDate'] == row['DischargeDate']
            for admission in linked_data[cluster_id]
            )
        if not exists:
            linked_data[cluster_id].append({
                "AdmissionDate": row['AdmissionDate'],
                "DischargeDate": row['DischargeDate'],
            })
    linked_data = dict(linked_data)
    save_variable_to_pickle(variable=linked_data, file_path=save_file_path)

def add_vital_sign(admissions_df, vital_sign_df, linked_data_raw_path: str, vital_sign: str):
    admissions_df = admissions_df

    vital_sign_df = vital_sign_df
    if os.path.exists('./data/' + vital_sign + '.csv'):
       specific_sign_df = pd.read_csv('./data/' + vital_sign + '.csv')
    else:
       specific_sign_df = get_specific_vital_sign(specific_sign=vital_sign, vital_sign_df=vital_sign_df)
    specific_sign_df['PerformedDateTime'] = pd.to_datetime(specific_sign_df['PerformedDateTime'])
    
    # with open(linked_data_path, 'rb') as json_file:
    #     linked_data = json.load(json_file)
    with open(linked_data_raw_path, 'rb') as pkl_file:
        linked_data = pickle.load(pkl_file)     
        
    for key in linked_data.keys():
        for _dict in linked_data[key]:
            _dict[vital_sign] = []
    linked_data = dict(linked_data)
    
    idx = 0
    for _, temp_row in specific_sign_df.iterrows():
        if idx % 10000 == 0:
            print(idx)
        cluster_id = temp_row['ClusterID']
        if cluster_id in linked_data:
            temp_record = {
                "PerformedDateTime": temp_row['PerformedDateTime'],
                "Type": temp_row['EventName'],
                "Degree": temp_row['EventResult'],
                "Unit": temp_row['ResultUnits']
            }
            # Check each admission record for the corresponding ClusterID
            for admission_record in linked_data[cluster_id]:
                if pd.to_datetime(admission_record["AdmissionDate"]) <= temp_record["PerformedDateTime"] <= pd.to_datetime(admission_record["DischargeDate"]):
                    admission_record[vital_sign].append(temp_record)
                    break  # Stop checking further records for this temperature
        idx += 1
    return linked_data

if __name__ == '__main__':
    #admissions_df = pd.read_csv(file, dtype=str)
    admissions_df = pd.read_csv(inpt_recs_path) 
    print("Finished reading amission info")
    vital_sign_df = pd.read_csv(vital_sign_path)
    print("Finished reading all vital signs")
    
    if os.path.exists(linked_data_raw_path):
        print("The file exists.")
    else:
        print("Start linking cluster id")
        get_inpt_recs(admissions_df=admissions_df, save_file_path=linked_data_raw_path)
        print("Finished linking cluster id")
    
    sign = 'Temperature Tympanic'
    print("Start adding adding " + sign)
    linked_data = add_vital_sign(admissions_df=admissions_df, vital_sign_df=vital_sign_df, linked_data_raw_path=linked_data_raw_path, vital_sign=sign)
    print("Finised adding adding " + sign)
    save_variable_to_pickle(variable=linked_data, file_path=linked_data_path)
    #save_dict_to_json(dict_list=linked_data, file_path='./data/linked_data.json')


