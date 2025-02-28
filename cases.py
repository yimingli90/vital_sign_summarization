# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 11:22:41 2025

@author: Yiming Li
"""
import pandas as pd
from utilities import plot_records

cases = [[
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-08-19 09:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-09-22 10:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 156, 'cut_in_time': pd.Timestamp('2023-08-25 12:37:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 140, 'cut_in_time': pd.Timestamp('2023-06-14 09:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 89, 'cut_in_time': pd.Timestamp('2016-08-24 22:56:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 0, 'cut_in_time': pd.Timestamp('2023-12-11 04:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 31, 'cut_in_time': pd.Timestamp('2023-04-21 08:44:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 78, 'cut_in_time': pd.Timestamp('2020-04-22 22:00:00'), 'febrile': {}, 'heart_rate': {}},
    ],

        [
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-09-17 01:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-08-20 09:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 156, 'cut_in_time': pd.Timestamp('2023-08-26 19:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 140, 'cut_in_time': pd.Timestamp('2023-06-14 21:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 89, 'cut_in_time': pd.Timestamp('2016-08-18 08:56:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 186, 'cut_in_time': pd.Timestamp('2017-07-16 13:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 186, 'cut_in_time': pd.Timestamp('2017-08-16 20:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 28, 'cut_in_time': pd.Timestamp('2020-07-27 18:24:00'), 'febrile': {}, 'heart_rate': {}},
    ],

        [
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-08-28 03:40:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-09-19 06:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 156, 'cut_in_time': pd.Timestamp('2023-08-30 08:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 115, 'cut_in_time': pd.Timestamp('2017-05-12 05:39:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 130, 'cut_in_time': pd.Timestamp('2018-11-26 05:35:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 140, 'cut_in_time': pd.Timestamp('2023-06-21 21:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 89, 'cut_in_time': pd.Timestamp('2016-08-19 22:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 138, 'cut_in_time': pd.Timestamp('2024-08-01 12:00:00'), 'febrile': {}, 'heart_rate': {}},
    ],

        [
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-09-12 18:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-09-26 07:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 156, 'cut_in_time': pd.Timestamp('2023-09-04 08:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 130, 'cut_in_time': pd.Timestamp('2018-12-04 07:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 140, 'cut_in_time': pd.Timestamp('2023-06-25 22:40:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 89, 'cut_in_time': pd.Timestamp('2016-08-28 22:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 186, 'cut_in_time': pd.Timestamp('2017-08-17 21:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 57, 'cut_in_time': pd.Timestamp('2023-12-18 16:00:00'), 'febrile': {}, 'heart_rate': {}},
    ],

        [
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-08-08 12:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-08-18 12:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 8, 'cut_in_time': pd.Timestamp('2019-09-30 15:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 156, 'cut_in_time': pd.Timestamp('2023-11-28 08:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 140, 'cut_in_time': pd.Timestamp('2023-07-06 17:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 89, 'cut_in_time': pd.Timestamp('2016-09-01 11:00:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 186, 'cut_in_time': pd.Timestamp('2017-08-06 16:49:00'), 'febrile': {}, 'heart_rate': {}},
    {'index': 31, 'cut_in_time': pd.Timestamp('2023-04-20 06:00:00'), 'febrile': {}, 'heart_rate': {}},
    ]]


def get_cases():
    for case_ in cases:
        for record in case_:
            record['systolic_blood_pressure'] = {}
            record['cv_hmd_rule_sum'] = ''
            record['vs_records'] = ''
    return cases
