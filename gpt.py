# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 15:27:11 2025

@author: Yiming Li
"""

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Replace with your OpenAI API key
client = openai.OpenAI(api_key=openai_api_key)

# Patient Data
patient_data = """
Admission Date: 2023-07-04 07:08:00
Discharge Date: 2023-07-06 16:30:00

Temperature Records:
- 2023-07-04 07:42:47 → 38.5°C
- 2023-07-04 15:01:37 → 39.0°C
- 2023-07-05 06:46:48 → 38.6°C

Cut-off Time: 2023-07-06 04:00:00
"""

# Fever Identification Rules
fever_rules = """
1. Determine if the patient is febrile at the cut-off time:
   - Check if any temperature exceeds 37.8°C within the 24 hours before the cut-off.
   - If yes, the patient is febrile. Otherwise, afebrile.

2. If febrile, summarize based on fever duration:
   - ≤ 24 hours → "New fever in the last 24 hours, up to {last_fever_degree}ºC"
   - 24–48 hours → "Febrile for {fever_duration} hours, last fever {last_fever_degree}ºC, {hours_ago} hours ago"
   - > 48 hours → "Consistently febrile for {days_fever} days, last temperature {last_fever_degree}ºC {hours_ago} hours ago"
   - If the fever started at admission, append "Consistently febrile since admission".

3. If afebrile:
   - If no fevers in the last 5 days → "Consistently afebrile"
   - If a fever occurred within the past 5 days → "Afebrile, last fever {days_ago} days ago"

4. Fever duration calculation:
   - Start from the last fever and trace back.
   - Continue if there’s another fever within 24 hours.
   - Stop if a 24-hour gap is found or the admission time is reached.
"""

# OpenAI API Call using new client structure
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a clinical data analyst specialized in interpreting patient temperature records."},
        {"role": "user", "content": f"Given the following patient data:\n\n{patient_data}"},
        {"role": "user", "content": f"Apply these fever identification rules:\n\n{fever_rules}"},
        {"role": "user", "content": "Generate the appropriate fever summary based on the rules."}
    ],
    temperature=0  # deterministic output
)

# Output Result
fever_summary = response.choices[0].message.content
print("Fever Summary:", fever_summary)
