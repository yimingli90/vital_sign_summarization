# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 16:03:50 2025

@author: YimingL
"""

TEMPLATE_TEST = """
## Task:
You are a doctor. Summarize the patient's vital signs, including febrile records, heart rate, and blood pressure, based on the provided data and rules.

## Instructions:
1. Use only the provided information and timestamps. Do not make up any information not present in the records.
2. Summarize the vital signs in 2 concise sentences.
3. Follow the rules for febrile duration, heart rate, blood pressure, and cardiovascular status.
4. The cut-off time is the timestamp when you see the patient [2019-08-20 09:00:00].

##Rules for Febrile Record:
1. Determine if the patient is febrile at the cut-off time:
    • Check if there is any temperature reading above 37.7°C within the 24 hours before the cut-off time.
    • If such a reading exists, the patient is considered febrile at the cut-off time.
    • Otherwise, the patient is considered afebrile.

2. If the patient is febrile, summarize based on fever duration:
    • Fever duration ≤ 24 hours:
      → "New fever in the last 24 hours, up to [last_fever_degree]ºC"
    • Fever duration between 24 and 48 hours, round fever duration to the nearest hour:
      → "Febrile for [fever_duration] hours, last fever [last_fever_degree]ºC, [hours_ago] hours ago"
    • Fever duration > 48 hours, convert fever duration to days:
      → "Consistently febrile for [days_fever] days, last temperature [last_fever_degree]ºC [hours_ago] hours ago [extra_description]"
      • If the fever started right at admission, append "Consistently febrile since admission".

3. If the patient is afebrile:
    • Check if there were any fevers in the 5 days prior to the cut-off time:
        • If no fevers in the past 5 days:
        → "Consistently afebrile"
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
    • Output: "Unstable concerning heart rate, [latest_heart_rate] bpm."
2. Tachycardia
    • If the latest recorded heart rate is between 110 bpm and 130 bpm (inclusive), the patient is classified as having tachycardia.
    • Output: "Heart rate tachycardia, [latest_heart_rate] bpm."
3. Raised Heart Rate
    • If the latest recorded heart rate is between 90 bpm and 110 bpm (inclusive), the heart rate is raised but not considered tachycardia.
    • Output: "Heart rate raised, [latest_heart_rate] bpm."
4. Normal Heart Rate
    • If the latest recorded heart rate is between 50 bpm and 90 bpm (inclusive), the heart rate is considered normal.
    • Output: "Heart rate normal, [latest_heart_rate] bpm."
5. Low Heart Rate
    • If the latest recorded heart rate is below 50 bpm (inclusive), the heart rate is low, which may indicate bradycardia.
    • Output: "Heart rate low, [latest_heart_rate] bpm."

##Rules for Heart Rate Record:
1. Unstable Heart Rate:
    • If the latest recorded heart rate is greater than 130 bpm, the patient is considered to have an unstable concerning heart rate.
    • Output: "Unstable concerning heart rate, [latest_heart_rate] bpm."
2. Tachycardia
    • If the latest recorded heart rate is between 110 bpm and 130 bpm (inclusive), the patient is classified as having tachycardia.
    • Output: "Heart rate tachycardia, [latest_heart_rate] bpm."
3. Raised Heart Rate
    • If the latest recorded heart rate is between 90 bpm and 110 bpm (inclusive), the heart rate is raised but not considered tachycardia.
    • Output: "Heart rate raised, [latest_heart_rate] bpm."
4. Normal Heart Rate
    • If the latest recorded heart rate is between 50 bpm and 90 bpm (inclusive), the heart rate is considered normal.
    • Output: "Heart rate normal, [latest_heart_rate] bpm."
5. Low Heart Rate
    • If the latest recorded heart rate is below 50 bpm (inclusive), the heart rate is low, which may indicate bradycardia.
    • Output: "Heart rate low, [latest_heart_rate] bpm."

##Rules for Blood Pressure Record:
1. Unstable Heart Rate:
    • If the latest recorded heart rate is greater than 130 bpm, the patient is considered to have an unstable concerning heart rate.
    • Output: "Unstable concerning heart rate, [latest_heart_rate] bpm."
2. Tachycardia:
    • If the latest recorded heart rate is between 110 bpm and 130 bpm (inclusive), the patient is classified as having tachycardia.
    • Output: "Heart rate tachycardia, [latest_heart_rate] bpm."
3. Raised Heart Rate:
    • If the latest recorded heart rate is between 90 bpm and 110 bpm (inclusive), the heart rate is raised but not considered tachycardia.
    • Output: "Heart rate raised, [latest_heart_rate] bpm."
4. Normal Heart Rate:
    • If the latest recorded heart rate is between 50 bpm and 90 bpm (inclusive), the heart rate is considered normal.
    • Output: "Heart rate normal, [latest_heart_rate] bpm."
5. Low Heart Rate:
    • If the latest recorded heart rate is below 50 bpm (inclusive), the heart rate is low, which may indicate bradycardia.
    • Output: "Heart rate low, [latest_heart_rate] bpm."
6. No Heart Rate Record:
    • Output: No Heart Rate Record.

##Rules for Blood Pressure Record:
1. Hypotension Shock:
    • If the latest systolic blood pressure is 90 mmHg or lower, the patient is considered to be in a hypotensive shock state.
    • Output: "Systolic blood pressure hypotension shocked, {latest_blood_pressure} mmHg."
2. Low Blood Pressure:
    • If the latest systolic blood pressure is between 91 mmHg and 100 mmHg (inclusive), the patient has low blood pressure.
    • Output: "Systolic blood pressure low, {latest_blood_pressure} mmHg."
3. Slightly Low Blood Pressure:
    • If the latest systolic blood pressure is between 101 mmHg and 110 mmHg (inclusive), the patient has slightly low blood pressure.
    • Output: "Systolic blood pressure slightly low, {latest_blood_pressure} mmHg."
4. Normal Blood Pressure:
    • If the latest systolic blood pressure is between 111 mmHg and 219 mmHg (inclusive), the patient has a normal blood pressure.
    • Output: "Systolic blood pressure normal, {latest_blood_pressure} mmHg."
5. Hypertensive Crisis:
    • If the latest systolic blood pressure is 220 mmHg or higher, the patient is experiencing a hypertensive crisis, which may require immediate medical attention.
    • Output: "Systolic blood pressure hypertensive crisis, {latest_blood_pressure} mmHg."
5. No Blood Pressure Record:
    • Output: No Blood Pressure Record.
    
##Rules for Cardiovascular Status Check:
1. Cardiovascular stable:
    • If both heart rate and blood pressure are normal
    • Output: "Cardiovascular stable, heart rate [latest_heart_rate] bpm and blood pressure {latest_blood_pressure} mmHg."
2. Otherwise:
    Out put is the combinition of the heart rate output and blood pressure output.
    
##Patient Data:
    
Admission Date: 2019-08-07 20:19:00
Cut-off time: 2019-08-20 09:00:00

Temperature Records:
- 2019-08-15 11:03:50: 36.7°C
- 2019-08-15 15:36:00: 37.1°C
- 2019-08-15 19:16:15: 37.4°C
- 2019-08-15 22:31:56: 36.8°C
- 2019-08-16 07:11:27: 36.1°C
- 2019-08-16 11:35:39: 36.8°C
- 2019-08-16 16:07:21: 36.7°C
- 2019-08-17 06:32:47: 36.0°C
- 2019-08-17 10:48:01: 36.0°C
- 2019-08-17 15:58:14: 36.9°C
- 2019-08-17 19:26:37: 37.1°C
- 2019-08-17 20:58:48: 37.1°C
- 2019-08-18 06:10:41: 37.4°C
- 2019-08-18 13:54:06: 37.6°C
- 2019-08-18 15:00:00: 37.4°C
- 2019-08-18 18:08:00: 37.9°C
- 2019-08-18 21:27:56: 38.7°C
- 2019-08-19 06:02:15: 38.2°C
- 2019-08-19 09:12:13: 37.2°C
- 2019-08-19 10:22:09: 37.9°C
- 2019-08-19 11:19:03: 37.9°C
- 2019-08-19 12:23:56: 38.0°C
- 2019-08-19 15:50:18: 39.8°C
- 2019-08-19 16:37:49: 39.1°C
- 2019-08-19 17:20:42: 38.1°C
- 2019-08-19 18:59:30: 38.2°C
- 2019-08-19 21:55:44: 39.7°C
- 2019-08-20 00:07:43: 38.1°C
- 2019-08-20 01:43:00: 38.4°C
- 2019-08-20 03:42:17: 39.3°C
- 2019-08-20 04:49:26: 38.5°C
- 2019-08-20 06:13:56: 37.8°C
- 2019-08-20 07:24:36: 36.6°C
- 2019-08-20 08:39:21: 37.5°C
- 2019-08-20 08:40:43: 37.5°C

Heart Rate Records:
- 2019-08-20 08:40:43: 116 bpm

Systolic Blood Pressure:
- 2019-08-20 08:40:43: 125 mmHg

##Expected Output:
1. Febrile Summary:
    • Calculate febrile and afebrile duration based on the rules.
2. Cardiovascular Status:
    • Summarize heart rate and blood pressure, combining them into a cardiovascular status.

3. Final Summary:
    • Provide a 3-sentence summary of the patient's vital signs.

##Example Output:
1. Febrile Summary:
    • "Consistently febrile for 5 days, last temperature 38.3°C 1 hour ago."
2. Cardiovascular Status:
    • "Heart rate raised, 102 bpm. Systolic blood pressure normal, 112 mmHg."
3. Final Summary:
    • "The patient has been consistently febrile for 5 days, with the last fever of 38.3°C recorded 1 hour ago. The heart rate is raised at 102 bpm, and blood pressure is normal at 112 mmHg. Overall, the patient is febrile with a raised heart rate but stable blood pressure."
"""

TEMPLATE_SUMMARY_RULES = """
Task:
For a patient, we have 3 kinds of vital signs for him/her: Temperature Tympanic, Heart Rate, Systolic Blood Pressure. For each vital sign, we use rule based method to geneeate a summarization. We need you to write a human like summarization combine the rules based vital sign summarizations, please write the summarization concisely and clearly.


## Note:
Use only the provided information. Don't make up any information that's not from the summarizations.

Rule Based Summarization:
{temperature_tympanic}
{cardiovascular_status}

"""

TEMPLATE_ALL = """
## Task:
You are a doctor. Summarize the patient's vital signs, including febrile records, heart rate, and blood pressure, based on the provided data and rules.

## Instructions:
1. Use only the provided information and timestamps. Do not make up any information not present in the records.
2. Summarize the vital signs in 2 concise sentences.
3. Follow the rules for febrile duration, heart rate, blood pressure, and cardiovascular status.
4. The cut-off time is the timestamp when you see the patient [{cut_in_time}].

##Rules for Febrile Record:
1. Determine if the patient is febrile at the cut-off time:
    • Check if there is any temperature reading above 37.7°C within the 24 hours before the cut-off time.
    • If such a reading exists, the patient is considered febrile at the cut-off time.
    • Otherwise, the patient is considered afebrile.

2. If the patient is febrile, summarize based on fever duration:
    • Fever duration ≤ 24 hours:
      → "New fever in the last 24 hours, up to [last_fever_degree]ºC"
    • Fever duration between 24 and 48 hours, round fever duration to the nearest hour:
      → "Febrile for [fever_duration] hours, last fever [last_fever_degree]ºC, [hours_ago] hours ago"
    • Fever duration > 48 hours, convert fever duration to days:
      → "Consistently febrile for [days_fever] days, last temperature [last_fever_degree]ºC [hours_ago] hours ago [extra_description]"
      • If the fever started right at admission, append "Consistently febrile since admission".

3. If the patient is afebrile:
    • Check if there were any fevers in the 5 days prior to the cut-off time:
        • If no fevers in the past 5 days:
        → "Consistently afebrile"
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
    • Output: "Unstable concerning heart rate, [latest_heart_rate] bpm."
2. Tachycardia
    • If the latest recorded heart rate is between 110 bpm and 130 bpm (inclusive), the patient is classified as having tachycardia.
    • Output: "Heart rate tachycardia, [latest_heart_rate] bpm."
3. Raised Heart Rate
    • If the latest recorded heart rate is between 90 bpm and 110 bpm (inclusive), the heart rate is raised but not considered tachycardia.
    • Output: "Heart rate raised, [latest_heart_rate] bpm."
4. Normal Heart Rate
    • If the latest recorded heart rate is between 50 bpm and 90 bpm (inclusive), the heart rate is considered normal.
    • Output: "Heart rate normal, [latest_heart_rate] bpm."
5. Low Heart Rate
    • If the latest recorded heart rate is below 50 bpm (inclusive), the heart rate is low, which may indicate bradycardia.
    • Output: "Heart rate low, [latest_heart_rate] bpm."
6. No Heart Rate Record:
    • Output: No Heart Rate Record.

##Rules for Blood Pressure Record:
1. Hypotension Shock:
    • If the latest systolic blood pressure is 90 mmHg or lower, the patient is considered to be in a hypotensive shock state.
    • Output: "Systolic blood pressure hypotension shocked, [latest_blood_pressure] mmHg."
2. Low Blood Pressure:
    • If the latest systolic blood pressure is between 91 mmHg and 100 mmHg (inclusive), the patient has low blood pressure.
    • Output: "Systolic blood pressure low, [latest_blood_pressure] mmHg."
3. Slightly Low Blood Pressure:
    • If the latest systolic blood pressure is between 101 mmHg and 110 mmHg (inclusive), the patient has slightly low blood pressure.
    • Output: "Systolic blood pressure slightly low, [latest_blood_pressure] mmHg."
4. Normal Blood Pressure:
    • If the latest systolic blood pressure is between 111 mmHg and 219 mmHg (inclusive), the patient has a normal blood pressure.
    • Output: "Systolic blood pressure normal, [latest_blood_pressure] mmHg."
5. Hypertensive Crisis:
    • If the latest systolic blood pressure is 220 mmHg or higher, the patient is experiencing a hypertensive crisis, which may require immediate medical attention.
    • Output: "Systolic blood pressure hypertensive crisis, [latest_blood_pressure] mmHg."
6. No Blood Pressure Record:
    • Output: No Blood Pressure Record.
    
##Rules for Cardiovascular Status Check:
1. Cardiovascular stable:
    • If both heart rate and blood pressure are normal
    • Output: "Cardiovascular stable, heart rate [latest_heart_rate] bpm and blood pressure [latest_blood_pressure] mmHg."
2. Otherwise:
    Out put is the combinition of the heart rate output and blood pressure output.
    
##Patient Data:
    
{patient_data}

##Expected Output:
1. Febrile Summary:
    • Calculate febrile and afebrile duration based on the rules.
2. Cardiovascular Status:
    • Summarize heart rate and blood pressure, combining them into a cardiovascular status.

3. Final Summary:
    • Provide a 3-sentence summary of the patient's vital signs.

##Example Output:
1. Febrile Summary:
    • "Consistently febrile for 5 days, last temperature 38.3°C 1 hour ago."
2. Cardiovascular Status:
    • "Heart rate raised, 102 bpm. Systolic blood pressure normal, 112 mmHg."
3. Final Summary:
    • "The patient has been consistently febrile for 5 days, with the last fever of 38.3°C recorded 1 hour ago. The heart rate is raised at 102 bpm, and blood pressure is normal at 112 mmHg. Overall, the patient is febrile with a raised heart rate but stable blood pressure."
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
    • Fever duration between 24 and 48 hours:
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
    "Febrile for 5 days, last spike 38.3°C. 
     HR raised, 102 bpm. SBP, 112 mmHg. 
     SBP stable, 112 mmHg"
2. Example two:
    "Febrile for 36 hours, last spike 38.3°C, 3 hours ago. 
     Cardiovascular stable."
3. Example three:
    "Afebrile. 
     HR low, 45 bpm.
     No Blood Pressure Record."
4. Example four:
    "New fever in the last 24 hours, 39ºC. 
     Tachycardia, 125 bpm.
     SBP normal."
"""