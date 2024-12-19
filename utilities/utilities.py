# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 15:10:23 2024

@author: YimingL
"""
import numpy as np
import pandas as pd
from utilities.save_file import save_dataframe_to_csv

def get_specific_vital_sign(specific_sign: str, vital_sign_df):
    
    vital_sign_df = vital_sign_df
    filtered_data = vital_sign_df[vital_sign_df['EventName'] == specific_sign]
    save_dataframe_to_csv(df=filtered_data, file_path='./data/' + specific_sign + '.csv')

    return filtered_data

def random_cut_in_time(case):
    start_time = case['AdmissionDate']
    end_time = case['DischargeDate']

    # 将时间戳转换为整数（表示为时间戳的纳秒数）
    start_ns = start_time.value
    end_ns = end_time.value

    # 在范围内随机生成一个整数
    random_ns = np.random.randint(start_ns, end_ns, dtype=np.int64)# we should assume cut-in time after the first 

    # 将随机生成的整数转换回时间戳
    cut_in_time = pd.Timestamp(random_ns)
    
    return cut_in_time