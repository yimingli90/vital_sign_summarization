# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 11:20:08 2025

@author: Yiming Li
"""
from micro.data_handler import DataHandler, CSVDataHandler
from micro.micro_result import Result
from typing import Dict, List


handler = CSVDataHandler("example_csv.csv")
all_rows = handler.get_all_rows()

def create_results(handler: DataHandler) -> Dict[str, Result]:
    results = {}
    for row in handler.get_all_rows():
        accession_number = row.get('accession_number', '').strip()
        if not accession_number:
            continue

        if accession_number not in results:
            results[accession_number] = Result(accession_number)

        if row.get('drug_name', '').strip():
            results[accession_number].add_antibiotic_result(row)
        else:
            results[accession_number].add_micro_result(row)
    return results

for row in all_rows:
    accession = handler.get_field(row, "accession_number")
    bug_name = handler.get_field(row, "bug_name")
    print(f"{accession}: {bug_name}")

results = create_results(handler)