# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 10:09:48 2024

@author: YimingL
"""

import pickle
import random
import pandas as pd
from rules import temp_rules
from rules.temperature import febrile_summary
from utilities.utilities import random_cut_in_time
from utilities import plot_records


if __name__ == '__main__':
    sign  = 'Temperature Tympanic'
    print("Vital sign is " + sign + '.')
    with open ('./data/' + sign + ' records.pkl', 'rb') as f:
        sign_records = pickle.load(f)
        
    #Get patient records with more than 2 days febrile
    if sign == 'Temperature Tympanic':
        print("Getting patients records with long_febrile_period. ")
        patients_with_long_febrile_period = temp_rules.get_long_febrile_records(sign_records=sign_records)
    
    # Example usage
    # Case 1: Febrile at admission, then settled
    case_1 = patients_with_long_febrile_period[88]
    case_1_example_cut_in = pd.Timestamp('2024-03-24 01:50:53.786380805')
    
    # Case 2: long in_patient record,long afebrile interval
    case_2 = patients_with_long_febrile_period[0]
    case_2_example_cut_in = pd.Timestamp('2023-12-16 09:00:00')

    case_ = random.choice(sign_records)
    cut_in_time = random_cut_in_time(case_)
    
    case_ = case_2
    cut_in_time = pd.Timestamp('2023-12-11 04:00:00')
    #cut_in_time = case_2_example_cut_in
    summary = febrile_summary.parse_temperature_data(data=case_, cutoff_time=cut_in_time)
    #summary = temp_rules.summarize_temperature_vitals(case, cut_in_time)
    print(f"Patient {case_['patientID']}: {summary}")
    plot_records.plot_temperature_records(data=case_, cutoff_time=cut_in_time)
    # tomorrow work: rewrite the febrile duration function in plot
    