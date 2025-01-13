# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 12:08:33 2025

@author: YimingL
"""

import os
import configparser

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

# 加载 config.ini 配置
CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# 提供 JSON 配置文件路径（相对于项目根目录）
DECISION_TREE_CONFIG_PATH = os.path.join(ROOT_DIR, config['Paths']['decision_tree_config'])


# 提供阈值温度/Threshold temperature
THRESHOLD_TEMPERATURE = float(config['Vital Signs']['febrile_threshold'])