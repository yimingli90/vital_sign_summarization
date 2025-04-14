# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:15:26 2025

@author: Yiming Li
"""
from typing import Dict, List


class AntibioticResult:
    def __init__(self, raw_fields: Dict[str, str]):
        self.drug_name = raw_fields.get('drug_name', '').strip()
        self.drug_result = raw_fields.get('drug_result', '').strip()
        self.raw_fields = raw_fields  # 保存所有原始字段

class Result:
    def __init__(self, accession_number: str):
        self.accession_number = accession_number
        self.collection_datetime = None
        self.specimen = None
        self.bug_name = None
        self.bug_result = None
        self.test_name = None
        self.antibiotics: Dict[str, AntibioticResult] = {}
        self.raw_fields_list: List[Dict[str, str]] = []

    def add_micro_result(self, row: Dict[str, str]):
        if not self.collection_datetime:
            self.collection_datetime = row.get('collection_datetime')
        if not self.specimen:
            self.specimen = row.get('specimen')
        if not self.bug_name:
            self.bug_name = row.get('bug_name')
        if not self.bug_result:
            self.bug_result = row.get('bug_result')
        if not self.test_name:
            self.test_name = row.get('test_name')
        self.raw_fields_list.append(row)

    def add_antibiotic_result(self, row: Dict[str, str]):
        drug_name = row.get('drug_name', '').strip()
        if drug_name:
            self.antibiotics[drug_name] = AntibioticResult(row)
        self.raw_fields_list.append(row)

    @property
    def has_antibiotics(self) -> bool:
        return len(self.antibiotics) > 0

    def print_antibiotics(self):
        if not self.antibiotics:
            print(f"No antibiotic results for accession {self.accession_number}.")
            return
        
        print(f"Antibiotic results for accession {self.accession_number}:")
        for drug_name, antibiotic_result in self.antibiotics.items():
            print(f"  {drug_name}: {antibiotic_result.drug_result}")


