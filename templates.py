# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 16:03:50 2025

@author: YimingL
"""

TEMPLATE = """
Task:
You are a doctor, please summarize the following patient temperature record concisely and clearly, focusing only on fever and afebrile status and time duration. 


Note:
Use only the provided temeprature information and time information. Don't make up any information that's not from the records. Please read the time data carefully.
You need to calcluate the febrile duration and afebrile duration information by yourself, do not use a specific date and time in summarization, use terms like hours or days. Please calculate the time duration carefully. Cut-off time is the time stamp that you come to see the patient.

Example Summarization Styles:
'Febrile for 27 hours, last fever 37.8°C, 14 hours ago.'
'Consistently febrile  for 9 days, last fever 38.0°C 3 hours ago.'
'Afebrile, last fever 2 days ago.'
'Consistently afebrile since admission.'


Admission Date:
{admission_date}
Patient Temperature Record:
{temperature_records}
Cut-off Time:
{cut_off_time}
"""

TEMPLATE_SUMMARY_RULES = """
Task:
For a patient, we have 3 kinds of vital signs: Temperature Tympanic, Heart Rate, Systolic Blood Pressure. For each vital sign, we use rule based method to geneeate a summarization. We need you to write a human like summarization combine the rules based vital sign summarizations, please write the summarization concisely and clearly. These 3 vital signs belong to one patient.


Note:
Use only the provided information. Don't make up any information that's not from the summarizations.

Rule Based Summarization:
{temperature_tympanic}
{cardiovascular_status}

"""
