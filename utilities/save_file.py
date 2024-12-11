# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 12:07:19 2024

@author: YimingL
"""

import json
import pickle

def save_dict_to_json(dict_list: dict, file_path: str):
    with open(file_path, 'w') as json_file:
        json.dump(dict_list, json_file, indent=4)
    print(f"Data has been saved to {file_path}")

def save_variable_to_pickle(variable, file_path: str):
    with open(file_path, 'wb') as file:
        pickle.dump(variable, file)
    print(f"Data has been saved as {file_path}")

def save_dataframe_to_csv(df, file_path):
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Data has been saved to {file_path}")
    

