# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 11:24:32 2024

@author: YimingL
"""
import pandas as pd

# Fever threshold
FEVER_THRESHOLD = 37.8



# Find records with continuous febrile periods > 48 hours
patients_with_long_febrile_period = []
check = []

for record in sign_records:
    patient_id = record["patientID"]
    admission_date = record["AdmissionDate"]
    discharge_date = record["DischargeDate"]
    temperatures = record["Temperature Tympanic"]

    # Sort temperature readings by time
    temperatures = sorted(temperatures, key=lambda x: x["PerformedDateTime"])

    # Initialize variables
    febrile_intervals = []
    current_start = None
    current_end = None

    for temp in temperatures:
        performed_time = temp["PerformedDateTime"]
        try:
            degree = float(temp["Degree"])
        except ValueError:
            continue

        if degree >= FEVER_THRESHOLD:  # If febrile
            if current_start is None:  # Start a new febrile period
                current_start = performed_time
            current_end = performed_time  # Extend the current febrile period
        else:  # If afebrile
            if current_start is not None:  # Close the current febrile period
                febrile_intervals.append((current_start, current_end))
                current_start = None
                current_end = None

    # Add the last interval if it was open
    if current_start is not None:
        febrile_intervals.append((current_start, current_end))

    # Check if any febrile period lasts more than 48 hours
    long_febrile_period = any(
        (end - start).total_seconds() > 48 * 3600 for start, end in febrile_intervals
    )


    if long_febrile_period:
        check.append(record)
        patients_with_long_febrile_period.append({
            "patientID": patient_id,
            "AdmissionDate": admission_date,
            "DischargeDate": discharge_date,
            "FebrileIntervals": febrile_intervals, 
            "Temperature Tympanic": temperatures# Optional: List of febrile intervals
        })

# Output the result
print(patients_with_long_febrile_period)
