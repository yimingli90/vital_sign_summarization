# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 11:19:15 2025

@author: Yiming Li
"""

import csv
from abc import ABC, abstractmethod
from typing import List, Dict

class DataHandler(ABC):
    """Abstract base class for data handlers"""
    @abstractmethod
    def get_field(self, row: Dict[str, str], field_name: str) -> str:
        """Get a field value from a single row"""
        pass

    @abstractmethod
    def get_all_rows(self) -> List[Dict[str, str]]:
        """Get all rows as a list of dictionaries"""
        pass


class CSVDataHandler(DataHandler):
    """Handler for CSV format microbiology data"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.field_names = [
            'index', 'cluster_id', 'collection_datetime', 'accession_number',
            'bat_test_code', 'bat_test_name', 'test_code', 'test_name',
            'specimen', 'result', 'result_full', 'result_further_info',
            'bug_code', 'bug_code_full', 'bug_name', 'bug_result',
            'susceptability_batch', 'susceptability_method',
            'drug_code', 'drug_name', 'drug_result', 'mic'
        ]
        self.rows = self._load_csv()

    def _load_csv(self) -> List[Dict[str, str]]:
        with open(self.file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            return [dict(zip(self.field_names, row)) for row in reader]

    def get_all_rows(self) -> List[Dict[str, str]]:
        return self.rows

    def get_field(self, row: Dict[str, str], field_name: str) -> str:
        return row.get(field_name, '')  # 安全返回，找不到就返回空字符串
