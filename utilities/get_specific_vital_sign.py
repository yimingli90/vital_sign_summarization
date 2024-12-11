# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 15:10:23 2024

@author: YimingL
"""
from save_file import save_dataframe_to_csv

def get_specific_vital_sign(specific_sign: str, vital_sign_df):
    
    vital_sign_df = vital_sign_df
    filtered_data = vital_sign_df[vital_sign_df['EventName'] == specific_sign]
    save_dataframe_to_csv(df=filtered_data, file_path='./data/' + specific_sign + '.csv')

    return filtered_data
