# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 17:18:51 2024

@author: Yiming Li
"""

check_adm = []
for _, row in admissions_df.iterrows():
    if row['ClusterID'] == 1375222:
        check_adm.append(row)

check_sign = []
for _, row in specific_sign_df.iterrows():
    if row['ClusterID'] == 1375222:
        check_sign.append(row)