# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 14:54:24 2025

@author: YimingL
"""

TEMPLATE_TITE = """
## Task:
You are a doctor. Summarize the patient's vital signs, including febrile records, heart rate, and blood pressure, based on the provided data and rules.

## Instructions:
1. Use only the provided information and timestamps. Do not make up any information not present in the records.
2. Summarize the vital signs in a few words.
3. Follow the rules for febrile duration, heart rate, blood pressure, and cardiovascular status.
4. The cut-off time is the timestamp when you see the patient [{cut_in_time}].

##Rules for Febrile Record:
1. Determine if the patient is febrile at the cut-off time:
    • Check if there is any temperature reading above 37.7°C within the 24 hours before the cut-off time.
    • If such a reading exists, the patient is considered febrile at the cut-off time.
    • Otherwise, the patient is considered afebrile.

2. If the patient is febrile, summarize based on fever duration:
    • If the fever started right at admission:
      → "Febrile since admission, last spike [last_fever_degree]ºC.". 
    • Fever duration ≤ 24 hours:
      → "New fever in the last 24 hours, [last_fever_degree]ºC"
    • Fever duration between 24 and 48 hours, round fever duration to the nearest hour:
      → "Febrile,  last fever [last_fever_degree]ºC, [hours_ago] hours ago."
    • Fever duration > 48 hours, convert fever duration to days:
      → "Febrile for [days_fever] days, last spike [last_fever_degree]ºC."


3. If the patient is afebrile:
    • Check if there were any fevers in the 5 days prior to the cut-off time:
        • If no fevers in the past 5 days:
        → "Afebrile"
    • If a fever occurred within the past 5 days, convert afebrile duration to days:
        → "Afebrile, last fever [days_ago] days ago"
4. Fever duration calculation:
    • Starting from the last recorded fever before the cut-off time, trace backwards:
        • If another fever record [>37.7°C] is found within the 24 hours prior [include 24 hours], extend the fever start time backwards to this record.
        • Continue until either:
            • A 24-hour gap without fever is encountered, or
            • The admission time is reached.


##Rules for Heart Rate Record:
1. Unstable Heart Rate:
    • If the latest recorded heart rate is greater than 130 bpm, the patient is considered to have an unstable concerning heart rate.
    • Output: "Unstable concerning HR, [latest_heart_rate] bpm."
2. Tachycardia
    • If the latest recorded heart rate is between 110 bpm and 130 bpm (inclusive), the patient is classified as having tachycardia.
    • Output: "Tachycardia, [latest_heart_rate] bpm."
3. Raised Heart Rate
    • If the latest recorded heart rate is between 90 bpm and 110 bpm (inclusive), the heart rate is raised but not considered tachycardia.
    • Output: "HR raised, [latest_heart_rate] bpm."
4. Normal Heart Rate
    • If the latest recorded heart rate is between 50 bpm and 90 bpm (inclusive), the heart rate is considered normal.
    • Output: "HR stable."
5. Low Heart Rate
    • If the latest recorded heart rate is below 50 bpm (inclusive), the heart rate is low, which may indicate bradycardia.
    • Output: "HR low, [latest_heart_rate] bpm."
6. No Heart Rate Record:
    • Output: "No Heart Rate Record."


##Rules for Blood Pressure Record:
1. Hypotension Shock:
    • If the latest systolic blood pressure is 90 mmHg or lower:
    • Output: "Hypotension shocked, [latest_blood_pressure] mmHg."
2. Low Blood Pressure:
    • If the latest systolic blood pressure is between 91 mmHg and 100 mmHg (inclusive):.
    • Output: "SBP low, [latest_blood_pressure] mmHg."
3. Slightly Low Blood Pressure:
    • If the latest systolic blood pressure is between 101 mmHg and 110 mmHg (inclusive):.
    • Output: "SBP slightly low, [latest_blood_pressure] mmHg."
4. Normal Blood Pressure:
    • If the latest systolic blood pressure is between 111 mmHg and 219 mmHg (inclusive):.
    • Output: "SBP normal."
5. Hypertensive Crisis:
    • If the latest systolic blood pressure is 220 mmHg or higher:
    • Output: "Hypertensive crisis, [latest_blood_pressure] mmHg."
6. No Blood Pressure Record:
    • Output: "No Blood Pressure Record."
    
##Rules for Cardiovascular Status Check:
1. Cardiovascular stable:
    • If both heart rate and blood pressure are normal:
    • Output: "Cardiovascular stable."
2. Otherwise:
    Out put is the combinition of the heart rate output and blood pressure output with few words.
    
    
##Patient Data:
    
{patient_data}


##Expected Output:
    • Provide a few words summary of the patient's vital signs in 2 or lines.


##Example Output:
1. Example one:
    • "Febrile for 5 days, last spike 38.3°C. 
       HR raised, 102 bpm. SVP, 112 mmHg. 
       SVP stable, 112 mmHg"
2. Example two:
    • "Febrile for 36 hours, last spike 38.3°C, 3 hours ago. 
       Cardiovascular stable."
3. Example three:
    • "Afebrile. 
       HR low, 45 bpm.
       No Blood Pressure Record."
4. Example four:
    • "New fever in the last 24 hours, 39ºC. 
       Tachycardia, 125 bpm.
       SBP normal."
"""