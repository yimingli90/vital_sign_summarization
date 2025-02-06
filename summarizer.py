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
from rules import temp_rules
from rules.temperature import febrile_summary
from utilities.utilities import random_cut_in_time
from utilities import plot_records
from cases import get_cases



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

if __name__ == '__main__':
    sign  = 'Temperature Tympanic'
    print("Vital sign is " + sign + '.')
    with open ('./data/' + sign + ' records.pkl', 'rb') as f:
        sign_records = pickle.load(f)
        
    #Get patient records with more than 2 days febrile
    if sign == 'Temperature Tympanic':
        print("Getting patients records with long_febrile_period. ")
        patients_with_long_febrile_period = temp_rules.get_long_febrile_records(sign_records=sign_records)
   
    cases = get_cases()
    for case_ in cases:
        for example in case_:
            data = patients_with_long_febrile_period[example['index']]
            cut_in_time = example['cut_in_time']
            human_reader_plt, df = plot_records.plot_temperature_records_for_reader_fig(data=data, cutoff_time=cut_in_time)
        
            result_string = "\n".join(df["PerformedDateTime"].dt.strftime("%Y-%m-%d %H:%M:%S") + ": " + df["Degree"].astype(str))
            string_list = (df["PerformedDateTime"].dt.strftime("%Y-%m-%d %H:%M:%S") + " - " + df["Degree"].astype(str) + "°C").tolist()
                        
            
            example['rule_summarization'] = febrile_summary.parse_temperature_data(data=data, cutoff_time=cut_in_time)
            example['human_reader_plt'] = human_reader_plt
            example['AdmissionDate'] = data['AdmissionDate']
            example['DischargeDate'] = data['DischargeDate']
            result_string = "Admission Date: " + example['AdmissionDate'].strftime("%Y-%m-%d %H:%M:%S") + '\n\n' + result_string
            result_string += '\n\n' + "Cut-off time: " + example['cut_in_time'].strftime("%Y-%m-%d %H:%M:%S")
            example['records'] = result_string
            
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    summarize_template = """
    "Summarize the following patient temperature record concisely and clearly, focusing only on fever status and recent trends. Use a brief style like: 'New fever in the last 24 hours, up to 38.8°C.'. Here, 24 hours is just an example—you may need to determine the time information yourself, whether in hours or days. Cut-off time is the time stamp that a doctor comes to see the patient temperature record.

Patient Temperature Record:
{temperature_records}
    """
    
    llm = ChatOpenAI(model="gpt-4", temperature=0.2, openai_api_key=openai_api_key)
    template = PromptTemplate(
        input_variables=["temperature_records"],
        template=summarize_template
    )
    
    for case_ in cases:
        for example in case_:
               
            temp_data = example['records']
            rule_sum = febrile_summary.parse_temperature_data(data=data, cutoff_time=cut_in_time)
            
            summary = llm.predict(template.format(temperature_records=temp_data))
            example['open_ai_summarization'] = summary
    
    for case_ in cases:
        for example in case_:
            print(example['open_ai_summarization'])
            print(example['rule_summarization'])
            print('\n')

    