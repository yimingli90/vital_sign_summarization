# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 16:03:54 2024

@author: YimingL
"""

import pandas as pd
import random
from datetime import timedelta

def summarize_temperature_vitals(patient_records, cut_in_time):
    # Convert cut-in time to a timestamp
    cut_in_time = pd.to_datetime(cut_in_time)

    for record in patient_records:
        patient_id = record["patientID"]
        admission_date = record["AdmissionDate"]
        discharge_date = record["DischargeDate"]
        temperatures = record["Temperatures"]
        febrile_intervals = record.get("FebrileIntervals", [])

        # Sort temperature records by PerformedDateTime
        temperatures = sorted(temperatures, key=lambda x: x["PerformedDateTime"])

        # Find the temperature record at the cut-in time
        last_fever_time = None
        last_fever_degree = None
        febrile_begin = None
        summary = ""
        
        highest_fever_degree = 0
        for temp in temperatures:
            temp_time = temp["PerformedDateTime"]
            temp_degree = temp["Degree"]

            if temp_time <= cut_in_time and temp_degree >= 37.8:  # Identify febrile state
                last_fever_time = temp_time
                last_fever_degree = temp_degree
                if not febrile_begin:
                    febrile_begin = temp_time
                if temp_degree > highest_fever_degree:
                    highest_fever_degree = temp_degree

        # Check if the cut-in time itself is febrile
        cut_in_temp = next((t for t in temperatures if t["PerformedDateTime"] == cut_in_time), None)
        is_febrile_at_cut_in = cut_in_temp and cut_in_temp["Degree"] >= 37.8
        is_febrile_at_cut_in = last_fever_degree >= 37.8

        if is_febrile_at_cut_in:
            # Case 1: Febrile at cut-in time
            summary = "Febrile now"
            for interval_start, interval_end in febrile_intervals:
                if interval_start <= cut_in_time <= interval_end:
                    febrile_duration = (cut_in_time - interval_start).total_seconds() / 3600
                    print(febrile_duration)
                    if febrile_duration > 48:
                        summary = (f"Consistently febrile for {(cut_in_time - interval_start).days} days, "
                                   f"last temperature {last_fever_degree}°C at {last_fever_time}")
                        break
                    elif 24 <= febrile_duration <= 48:
                        #Febrile, last temperature 39.2ºC 5 hours ago or Spiking fevers, last temperature 39.2ºC 5 hours ago
                        if random.randint(1, 2) == 1:
                            summary = (f"Febrile, last temperature {last_fever_degree}°C  {(cut_in_time - last_fever_time).total_seconds() / 3600} hours ago")
                        else:
                            
                            summary = (f"Consistently febrile for {febrile_duration} hours, "
                                   f"last temperature {last_fever_degree}°C at {last_fever_time}")                        
                    else:
                        summary = (f"New fever in the last {febrile_duration} hours, "
                                   f"up to {highest_fever_degree}°C")
        else:
            # Case 2: Afebrile at cut-in time
            if febrile_intervals:
                for interval_start, interval_end in febrile_intervals:
                    if interval_end < cut_in_time:
                        last_fever_time = interval_end
                        afebrile_duration = (cut_in_time - last_fever_time).total_seconds() / 3600
                        if afebrile_duration > 48:
                            summary = (f"Temperature settled,"
                                       f"now fever free for {(cut_in_time - last_fever_time).days} days")
                        else:
                            summary = (f"Afebrile for {afebrile_duration} hours since last fever")
                        break
            else:
                summary = "Afebrile since admission"

        print(f"Patient {patient_id}: {summary}")

# Example usage
patient_records = [
    {
        "patientID": "456",
        "AdmissionDate": pd.Timestamp("2023-07-10 09:00:00"),
        "DischargeDate": pd.Timestamp("2023-07-13 18:00:00"),
        "Temperatures": [
            {"PerformedDateTime": pd.Timestamp("2023-07-10 10:00:00"), "Type": "Temperature Tympanic", "Degree": 37.5, "Unit": "degrees C"},
            {"PerformedDateTime": pd.Timestamp("2023-07-11 12:00:00"), "Type": "Temperature Tympanic", "Degree": 38.7, "Unit": "degrees C"},
            {"PerformedDateTime": pd.Timestamp("2023-07-11 14:00:00"), "Type": "Temperature Tympanic", "Degree": 38.6, "Unit": "degrees C"},
            {"PerformedDateTime": pd.Timestamp("2023-07-12 10:00:00"), "Type": "Temperature Tympanic", "Degree": 38.9, "Unit": "degrees C"},
            {"PerformedDateTime": pd.Timestamp("2023-07-13 16:00:00"), "Type": "Temperature Tympanic", "Degree": 38.4, "Unit": "degrees C"}
        ],
        "FebrileIntervals": [
            (pd.Timestamp("2023-07-11 12:00:00"), pd.Timestamp("2023-07-13 16:00:00"))
        ]
    }
]

# Set a cut-in time
cut_in_time = "2023-07-12 14:00:00"
summarize_temperature_vitals(patient_records, cut_in_time)
    