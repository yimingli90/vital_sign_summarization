# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 10:52:17 2025

@author: Yiming Li
"""
import os
import time
import pickle
from openai import OpenAI
from dotenv import load_dotenv
from templates import TEMPLATE_TITE
from docx import Document
from docx.shared import Inches, RGBColor

load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

# Replace with your OpenAI API key
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

# Output Result
i = 0
with open('./data/cases_tmp.pkl', 'rb')as pk:
    cases = pickle.load(pk)
for case_ in cases:
    for example in case_:
        print(i)
        cut_in_time = example['cut_in_time']
        patient_data = example['vs_records']
        try:
            response = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system",
                     "content": "You are a clinical data analyst specialized in interpreting patient temperature records."},
                    {"role": "user",
                     "content": TEMPLATE_TITE.format(cut_in_time=cut_in_time, patient_data=patient_data)}
                ],
                temperature=0  # deterministic output
            )

            reasoning = response.choices[0].message.reasoning_content
            summary = response.choices[0].message.content
            example['ds_resoning'] = reasoning
            example['ds_summary_all'] = summary
            print("Summary:", summary)

        except Exception as e:
            time.sleep(120)
            response = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system",
                     "content": "You are a clinical data analyst specialized in interpreting patient temperature records."},
                    {"role": "user",
                     "content": TEMPLATE_TITE.format(cut_in_time=cut_in_time, patient_data=patient_data)}
                ],
                temperature=0  # deterministic output
            )

            reasoning = response.choices[0].message.reasoning_content
            summary = response.choices[0].message.content
            example['ds_resoning'] = reasoning
            example['ds_summary_all'] = summary
            print("Summary:", summary)
        i += 1

with open('./data/cases_ds.pkl', 'wb')as pk:
    pickle.dump(cases, pk)