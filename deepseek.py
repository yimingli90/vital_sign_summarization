# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 10:52:17 2025

@author: Yiming Li
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
from templates import TEMPLATE

load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

# Replace with your OpenAI API key
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

# Patient Data
patient_data = """
Admission Date: 2019/8/7 20:19
Discharge Date: 2019/9/30 18:44

Temperature Records:
- 2019-09-14 06:41:16: 38.5°C
- 2019-09-14 08:49:27: 37.2°C
- 2019-09-14 11:12:43: 36.9°C
- 2019-09-14 11:39:35: 36.9°C
- 2019-09-14 13:47:16: 37.5°C
- 2019-09-14 18:32:44: 36.4°C
- 2019-09-14 22:53:34: 37.6°C
- 2019-09-15 06:50:40: 37.9°C
- 2019-09-15 10:38:21: 37.7°C
- 2019-09-15 13:47:23: 37.3°C
- 2019-09-15 19:29:48: 36.6°C
- 2019-09-15 23:09:34: 37.4°C
- 2019-09-16 06:50:13: 37.8°C
- 2019-09-16 10:30:28: 37.8°C
- 2019-09-16 15:18:01: 36.8°C
- 2019-09-16 18:01:49: 36.9°C
- 2019-09-16 18:57:36: 37.3°C
- 2019-09-16 22:47:15: 37.0°C
- 2019-09-17 06:38:50: 38.3°C
- 2019-09-17 10:52:23: 35.6°C
- 2019-09-17 10:53:16: 35.6°C
- 2019-09-17 14:06:07: 38.0°C
- 2019-09-17 16:05:02: 36.8°C
- 2019-09-17 17:20:17: 36.1°C
- 2019-09-17 22:31:40: 38.8°C
- 2019-09-18 02:00:37: 37.1°C
- 2019-09-18 06:09:42: 37.3°C
- 2019-09-18 08:10:49: 37.8°C
- 2019-09-18 10:32:19: 37.3°C
- 2019-09-18 14:20:37: 38.3°C
- 2019-09-18 18:23:05: 36.4°C
- 2019-09-18 21:43:36: 36.8°C
- 2019-09-19 02:10:20: 36.5°C
- 2019-09-19 05:09:33: 38.3°C

Cut-off Time: 2019/9/19 6:00
"""

# Fever Identification Rules
fever_rules = """
1. Determine if the patient is febrile at the cut-off time:
    • Check if there is any temperature reading above 37.7°C within the 24 hours before the cut-off time.
    • If such a reading exists, the patient is considered febrile at the cut-off time.
    • Otherwise, the patient is considered afebrile.

2. If the patient is febrile, summarize based on fever duration:
    • Fever duration ≤ 24 hours:
      → "New fever in the last 24 hours, up to {last_fever_degree}ºC"
    • Fever duration between 24 and 48 hours:
      → "Febrile for {fever_duration} hours, last fever {last_fever_degree}ºC, {hours_ago} hours ago"
    • Fever duration > 48 hours:
      → "Consistently febrile for {days_fever} days, last temperature {last_fever_degree}ºC {hours_ago} hours ago {extra_description}"
      • If the fever started right at admission, append "Consistently febrile since admission".

3. If the patient is afebrile:
    • Check if there were any fevers in the 5 days prior to the cut-off time:
        • If no fevers in the past 5 days:
        → "Consistently afebrile"
    • If a fever occurred within the past 5 days:
        → "Afebrile, last fever {days_ago} days ago"
4. Fever duration calculation:
    • Starting from the last recorded fever before the cut-off time, trace backwards:
        • If another fever record (>37.7°C) is found within the 24 hours prior (include 24 hours), extend the fever start time backwards to this record.
        • Continue until either:
            • A 24-hour gap without fever is encountered, or
            • The admission time is reached.
"""

# OpenAI API Call using new client structure
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role": "system", "content": "You are a clinical data analyst specialized in interpreting patient temperature records."},
        {"role": "user", "content": TEMPLATE.format(patient_data=patient_data)}
    ],
    temperature=0  # deterministic output
)

# Output Result

fever_summary = response.choices[0].message.content
print("Fever Summary:", fever_summary)