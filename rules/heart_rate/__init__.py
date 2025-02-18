# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 12:12:10 2025

@author: YimingL
"""

import os
import json
from rules import DECISION_TREE_CONFIG_PATH

# 加载决策树配置文件
def load_decision_tree_config():
    """加载决策树配置文件"""
    try:
        with open(DECISION_TREE_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Decision tree configuration file not found: {DECISION_TREE_CONFIG_PATH}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {DECISION_TREE_CONFIG_PATH}")

      