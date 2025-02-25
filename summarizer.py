# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 10:09:48 2024

@author: YimingL
"""

import pickle
import random
import os
import pandas as pd

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from rules import old_rules
from rules.temperature import febrile_summary
from rules.heart_rate import hr_summary
from rules.systolic_blood_pressure import sbp_summary
from utilities.utilities import random_cut_in_time
from utilities import plot_records, save_file
from cases import get_cases
from templates import TEMPLATE


def example_usage():
    
    # Example usage
    # Case 1: Febrile at admission, then settled
    case_1 = patients_with_long_febrile_period[88]
    case_1_example_cut_in = pd.Timestamp('2024-03-24 01:50:53.786380805') # pd.Timestamp('2024-03-24 01:50:53.786380805')
    
    # Case 2: long in_patient record,long afebrile interval
    case_2 = patients_with_long_febrile_period[0]
    case_2_example_cut_in = pd.Timestamp('2023-12-06 15:00:00')  # pd.Timestamp('2023-12-11 04:00:00') 
    
    case_3 = patients_with_long_febrile_period[8]
    case_3_example_cut_in = pd.Timestamp('2019-09-30 15:00:00')  # pd.Timestamp('2023-12-11 04:00:00') 
    
    case_ = random.choice(patients_with_long_febrile_period)
    cut_in_time = random_cut_in_time(case_)
    print(patients_with_long_febrile_period.index(case_))
    
    case_ = case_3
    cut_in_time = case_3_example_cut_in
    
    summary = febrile_summary.parse_temperature_data(data=case_, cutoff_time=cut_in_time)
    #summary = temp_rules.summarize_temperature_vitals(case, cut_in_time)
    print(f"Patient {case_['patientID']}: {summary}")
    plot_records.plot_temperature_records(data=case_, cutoff_time=cut_in_time)
    # tomorrow work: rewrite the febrile duration function in plot
    plot_records.plot_temperature_records_for_reader(data=case_, cutoff_time=cut_in_time)


def open_ai():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    summarize_template = TEMPLATE
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)
    template = PromptTemplate(
        input_variables=["temperature_records"],
        template=summarize_template
    )
    
    return llm, template

def rule_summarization(cases: list):
    count = 0
    for case_ in cases:
        for example in case_:
            print(count)
            count += 1
            data = patients_with_long_febrile_period[example['index']]
            cut_in_time = example['cut_in_time']
            human_reader_plt, df = plot_records.plot_temperature_records_for_reader_fig(data=data, cutoff_time=cut_in_time)
        
            result_string = "\n".join(df["PerformedDateTime"].dt.strftime("%Y-%m-%d %H:%M:%S") + ": " + df["Degree"].astype(str)  + "°C" )
            string_list = (df["PerformedDateTime"].dt.strftime("%Y-%m-%d %H:%M:%S") + " - " + df["Degree"].astype(str) + "°C").tolist()
                        
            # Febrile records
            example['febrile']['febrile_rule_summarization'] = febrile_summary.parse_temperature_data(data=data, cutoff_time=cut_in_time)
            example['febrile']['human_reader_plt'] = human_reader_plt
            example['AdmissionDate'] = data['AdmissionDate']
            example['DischargeDate'] = data['DischargeDate']
            #result_string = "Admission Date: " + example['AdmissionDate'].strftime("%Y-%m-%d %H:%M:%S") + '\n\n' + result_string
            #result_string += '\n\n' + "Cut-off time: " + example['cut_in_time'].strftime("%Y-%m-%d %H:%M:%S")
            example['febrile']['febrile_records'] = result_string
            
            # Heart rates records
            example['heart_rate']['hr_rule_summary'], hr_records = hr_summary.parse_hr_data(data=data, cutoff_time=cut_in_time)
            hr_string = ""
            for r in hr_records:
                hr_string += r["PerformedDateTime"].strftime("%Y-%m-%d %H:%M:%S") + ": " + r["Value"] + " " + r["Unit"] + "\n"
            example['heart_rate']['hr_records'] = hr_string
            human_reader_plt_hr, _ = plot_records.plot_hr_records_for_reader_fig(data=data, cutoff_time=cut_in_time)
            example['heart_rate']['human_reader_plt'] = human_reader_plt_hr
            
            # Systolic blood pressure records
            example['systolic_blood_pressure']['sbp_rule_summary'], sbp_records = sbp_summary.parse_sbp_data(data=data, cutoff_time=cut_in_time)
            sbp_string = ""
            for r in sbp_records:
                sbp_string += r["PerformedDateTime"].strftime("%Y-%m-%d %H:%M:%S") + ": " + r["Value"] + " " + r["Unit"] + "\n"
            example['systolic_blood_pressure']['sbp_records'] = sbp_string
            human_reader_plt_sbp, _ = plot_records.plot_sbp_records_for_reader_fig(data=data, cutoff_time=cut_in_time)
            example['systolic_blood_pressure']['human_reader_plt'] = human_reader_plt_sbp
            
            if 'normal' in example['systolic_blood_pressure']['sbp_rule_summary'] and 'normal' in example['heart_rate']['hr_rule_summary']:
                example['cv_hmd_rule_sum'] = "Cardiovascular stable, " + example['heart_rate']['hr_rule_summary'] + " " + example['systolic_blood_pressure']['sbp_rule_summary']
            else:
                example['cv_hmd_rule_sum'] = example['heart_rate']['hr_rule_summary'] + "\n" + example['systolic_blood_pressure']['sbp_rule_summary']
            
            
if __name__ == '__main__':
    sign = 'Temperature Tympanic'
    sign = 'Temperature Tympanic&Heart Rate&Systolic Blood Pressure'
    print("Vital sign is " + sign + '.')
    with open ('./data/' + sign + ' records.pkl', 'rb') as f:
        sign_records = pickle.load(f)
        
    #Get patient records with more than 2 days febrile
    if sign == 'Temperature Tympanic':
        print("Getting patients records with long_febrile_period. ")
        patients_with_long_febrile_period = old_rules.get_long_febrile_records(sign_records=sign_records)
        save_file.save_variable_to_pickle(variable=patients_with_long_febrile_period, file_path='./data/patients_with_long_febrile_period.pkl')
    
    with open('./data/patients_with_long_febrile_period.pkl', 'rb') as pk:
        patients_with_long_febrile_period = pickle.load(pk)
        
    cases = get_cases()
    rule_summarization(cases=cases)

    
    llm_openai, template = open_ai()
    
    for case_ in cases:
        for example in case_:
               
            temp_data = example['records']
            admission_date = example['AdmissionDate']
            cut_off_time = example['cut_in_time']
            
            summary = llm_openai.predict(template.format(temperature_records=temp_data, admission_date=admission_date, cut_off_time=cut_off_time))
            example['open_ai_summarization'] = summary
    
    for case_ in cases:
        for example in case_:
            print(example['open_ai_summarization'])
            print(example['rule_summarization'])
            print('\n')

    # 调用函数，生成 Word 文档
    save_file.save_plots_summarization_to_word(data_list=cases, output_folder='./data/summarization/GPT')
    
    #save_file.save_variable_to_pickle(cases, './data/summarization/cases_structured_prompt')
