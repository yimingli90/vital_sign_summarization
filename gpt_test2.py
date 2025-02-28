# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 17:14:58 2025

@author: Yiming Li
"""
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from templates import TEMPLATE, TEMPLATE_SUMMARY_RULES

patient_data = """
Admission Date: 2019/8/7 20:19
Discharge Date: 2019/9/30 18:44

Temperature Records:
- 2019-09-14 06:41:16: 38.5°C
- 2019-09-14 08:49:27: 37.2°C
- 2019-09-14 11:12:43: 36.9°C
- 2019-09-14 11:39:35: 36.9°C
- 2019-09-14 13:47:16: 37.5°C
- 2019-09-14 18:32:44: 36.4°C
- 2019-09-14 22:53:34: 37.6°C
- 2019-09-15 06:50:40: 37.9°C
- 2019-09-15 10:38:21: 37.7°C
- 2019-09-15 13:47:23: 37.3°C
- 2019-09-15 19:29:48: 36.6°C
- 2019-09-15 23:09:34: 37.4°C
- 2019-09-16 06:50:13: 37.8°C
- 2019-09-16 10:30:28: 37.8°C
- 2019-09-16 15:18:01: 36.8°C
- 2019-09-16 18:01:49: 36.9°C
- 2019-09-16 18:57:36: 37.3°C
- 2019-09-16 22:47:15: 37.0°C
- 2019-09-17 06:38:50: 38.3°C
- 2019-09-17 10:52:23: 35.6°C
- 2019-09-17 10:53:16: 35.6°C
- 2019-09-17 14:06:07: 38.0°C
- 2019-09-17 16:05:02: 36.8°C
- 2019-09-17 17:20:17: 36.1°C
- 2019-09-17 22:31:40: 38.8°C
- 2019-09-18 02:00:37: 37.1°C
- 2019-09-18 06:09:42: 37.3°C
- 2019-09-18 08:10:49: 37.8°C
- 2019-09-18 10:32:19: 37.3°C
- 2019-09-18 14:20:37: 38.3°C
- 2019-09-18 18:23:05: 36.4°C
- 2019-09-18 21:43:36: 36.8°C
- 2019-09-19 02:10:20: 36.5°C
- 2019-09-19 05:09:33: 38.3°C

Cut-off Time: 2019/9/19 6:00
"""


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
    
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)
tmplt = PromptTemplate(
    input_variables=["patient_data"],
    template=TEMPLATE
    )

sum_mary = llm.predict(tmplt.format(patient_data=patient_data))