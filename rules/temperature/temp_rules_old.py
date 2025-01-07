# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 16:03:54 2024

@author: YimingL
"""

import pickle
import pandas as pd
import numpy as np

import random
from datetime import timedelta

FEVER_THRESHOLD = 37.8
def get_long_febrile_records(sign_records: list):
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
            (end - start).total_seconds() >= 48 * 3600 for start, end in febrile_intervals
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
    
    # Return the result
    return patients_with_long_febrile_period


def _check_if_continuously_febrile(temperatures: list, cut_in_time):
    # Filter records before cut-in time
    pre_cut_in_temps = []
    for temp in temperatures:
        try:
            if temp["PerformedDateTime"] <= cut_in_time:
                temp["Degree"] = float(temp["Degree"])
                pre_cut_in_temps.append(temp)
        except ValueError:
            continue

    pre_cut_in_temps = [
        temp for temp in temperatures if temp["PerformedDateTime"] <= cut_in_time
    ]
    
    if len(pre_cut_in_temps) < 2:
        print("Temperature reocrds number error, pleas check your code.")
        return False  # Check if records are less than 2
    
    # Get the latest two records before cut-in
    last_temp = pre_cut_in_temps[-1]
    second_last_temp = pre_cut_in_temps[-2]

    if (
        last_temp["Degree"] > FEVER_THRESHOLD
        and second_last_temp["Degree"] > FEVER_THRESHOLD
    ):
        # 如果最近两条记录都是发烧，查找连续发烧的起始时间
        continuously_febrile_start = None
        for temp in reversed(pre_cut_in_temps):
            if temp["Degree"] < FEVER_THRESHOLD:
                break
            continuously_febrile_start = temp["PerformedDateTime"]
        return True, continuously_febrile_start

    elif (
        last_temp["Degree"] > FEVER_THRESHOLD
        and second_last_temp["Degree"] <= FEVER_THRESHOLD
    ):
        # 如果最近一条发烧，再前一条不发烧
        return False, None
    
    return False, "Check code."    

def _is_febrile_at_cut_in(temperatures: list, cut_in_time):
    # Find the temperature record at the cut-in time
    last_fever_time = None
    last_fever_degree = None
    febrile_begin = None
    highest_fever_degree = 0
    is_febrile_at_cut_in = False
    flag_same_time = False
    
    for temp in temperatures:
        try:
            temp_degree = float(temp["Degree"])
        except ValueError:
            continue
        temp_time = temp["PerformedDateTime"]
        temp_degree = float(temp["Degree"])
        
        if temp_time == cut_in_time:
            if temp_degree >= FEVER_THRESHOLD:
                flag_same_time = True
                is_febrile_at_cut_in = True
                break
            else:
                flag_same_time = True
                is_febrile_at_cut_in = False
                break
        if temp_time <= cut_in_time :
            last_temp_time = temp_time #last time to measure temperatuere
            last_fever_degree = temp_degree #last time temperature degree
            
            if temp_degree >= FEVER_THRESHOLD:  # Identify febrile state
                last_fever_time = temp_time # last time time febrile
                last_fever_degree = temp_degree # last time febrile degree
                if not febrile_begin:
                    febrile_begin = temp_time
                if temp_degree > highest_fever_degree:
                    highest_fever_degree = temp_degree

    if not flag_same_time:
        is_febrile_at_cut_in = last_temp_time == last_fever_time
        
    return is_febrile_at_cut_in, last_fever_time, last_fever_degree, highest_fever_degree

def summarize_temperature_vitals(record, cut_in_time):
    # Convert cut-in time to a timestamp
    cut_in_time = pd.to_datetime(cut_in_time)

    
    patient_id = record["patientID"]
    temperatures = record["Temperature Tympanic"]


    # Sort temperature records by PerformedDateTime, if cut-in time before the first temperature record time, then return no record.
    temperatures = sorted(temperatures, key=lambda x: x["PerformedDateTime"])
    first_temp_time = temperatures[0]["PerformedDateTime"]
    if cut_in_time < first_temp_time:
        return "No temperature record."
    
    febrile_at_cut_in, last_fever_time, last_fever_degree, highest_fever_degree =  _is_febrile_at_cut_in(temperatures, cut_in_time)
    
    # If temperature at cut-in time or the last temperature before cut-in time, then is is febrile. 
    print("febrile_at_cut_in:")
    print(febrile_at_cut_in)
    if febrile_at_cut_in:
        summary = "Febrile now"
        # Case 1: Febrile at admission, cut-in time betweent first temp record and second temp record.
        if last_fever_time == first_temp_time:
            summary = (f"Febrile at admission, temperature {last_fever_degree}°C at {last_fever_time}")
            return summary
            
        # Case 2: Febrile at admission, continusously febrile (more than two continuously high temop previous records)
        continuously_febrile, interval_start = _check_if_continuously_febrile(temperatures=temperatures, cut_in_time=cut_in_time)
        print(continuously_febrile)
        if continuously_febrile:
            febrile_duration = (cut_in_time - interval_start).total_seconds() / 3600
            if febrile_duration > 48: # More than two days
                summary = (f"Consistently febrile for {(cut_in_time - interval_start).days} days, "
                           f"last temperature {last_fever_degree}°C at {last_fever_time}")
                return summary
            elif 24 <= febrile_duration <= 48:
                summary = (f"Consistently febrile for {febrile_duration} hours, "
                       f"last temperature {last_fever_degree}°C at {last_fever_time}")
                return summary
            else:
                if febrile_duration >= 1: # More than 1h use h otherwise use minutes
                    summary = (f"Febrile, last temperature {last_fever_degree}°C  {(cut_in_time - last_fever_time).total_seconds() / 3600} hours ago at {last_fever_time}")
                    return summary
                else:
                    summary = (f"Febrile, last temperature {last_fever_degree}°C  {(cut_in_time - last_fever_time).total_seconds() / 60} minutes ago at {last_fever_time}")
                    return summary
        else: # Cut in timeonly last is febrile and last last afebrile will be sonsiderd 
            summary = (f"New fever in the last {(cut_in_time - last_fever_time).total_seconds() / 3600} hours, "
                       f"up to {highest_fever_degree}°C at {last_fever_time}")
            return summary
    else:
        if last_fever_time:
            
            afebrile_duration = (cut_in_time - last_fever_time).total_seconds() / 3600
            
            if afebrile_duration > 48:
                print("check")
                if (cut_in_time - first_temp_time).days > 7:
                    summary = (f"Temperature settled,"
                                    f"now fever free for {(cut_in_time - last_fever_time).days} days")
                    return summary
                else:
                    if float(temperatures[0]['Degree']) >= FEVER_THRESHOLD:
                        summary = (f"Temperature settled,  febrile at admission"
                                        f"now fever free for {(cut_in_time - last_fever_time).days} days")
                        return summary
                    else:
                        summary = (f"Temperature settled, "
                                        f"now fever free for {(cut_in_time - last_fever_time).days} days")
                        return summary
                        
            else:
                if float(temperatures[0]['Degree']) >= FEVER_THRESHOLD:
                    summary = (f"Febrile at admission, now afebrile for {afebrile_duration} hours since last fever")
                    return summary
                
                summary = (f"Afebrile for {afebrile_duration} hours since last fever")
                return summary

        else:
            summary = "Afebrile since admission"
            return summary
        


 

