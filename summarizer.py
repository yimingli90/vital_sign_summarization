# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 10:09:48 2024

@author: YimingL
"""

import pickle
import random
import pandas as pd
from rules import temp_rules
from utilities.utilities import random_cut_in_time, plot_records


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

    case = random.choice(sign_records)
    cut_in_time = random_cut_in_time(case)
    #cut_in_time = case_1_example_cut_in
    summary = temp_rules.summarize_temperature_vitals(case, cut_in_time)
    print(f"Patient {case['patientID']}: {summary}")
    plot_records(data=case, cut_in_time=cut_in_time)
    # Set a cut-in time


    # # Example usage
    # patient_records = [
    #     {
    #         "patientID": 456,
    #         "AdmissionDate": pd.Timestamp("2023-07-10 09:00:00"),
    #         "DischargeDate": pd.Timestamp("2023-07-17 18:00:00"),
    #         "Temperature Tympanic": [
    #             {"PerformedDateTime": pd.Timestamp("2023-07-10 10:00:00"), "Type": "Temperature Tympanic", "Degree": 36.5, "Unit": "degrees C"},
    #             {"PerformedDateTime": pd.Timestamp("2023-07-11 12:00:00"), "Type": "Temperature Tympanic", "Degree": 38.7, "Unit": "degrees C"},
    #             {"PerformedDateTime": pd.Timestamp("2023-07-12 14:00:00"), "Type": "Temperature Tympanic", "Degree": 36.6, "Unit": "degrees C"},
    #             {"PerformedDateTime": pd.Timestamp("2023-07-13 10:00:00"), "Type": "Temperature Tympanic", "Degree": 38.9, "Unit": "degrees C"},
    #             {"PerformedDateTime": pd.Timestamp("2023-07-14 16:00:00"), "Type": "Temperature Tympanic", "Degree": 38.4, "Unit": "degrees C"},
    #             {"PerformedDateTime": pd.Timestamp("2023-07-15 10:00:00"), "Type": "Temperature Tympanic", "Degree": 38.9, "Unit": "degrees C"},
    #             {"PerformedDateTime": pd.Timestamp("2023-07-16 16:00:00"), "Type": "Temperature Tympanic", "Degree": 38.5, "Unit": "degrees C"},
    #         ],
    #     }
    # ]

    # cut_in_time = "2023-07-14 18:40:00"
    # cut_in_time = pd.Timestamp(cut_in_time)
    # summary = temp_rules.summarize_temperature_vitals(patient_records[0], cut_in_time)
    # print(f"Patient {patient_records[0]['patientID']}: {summary}")
        
    