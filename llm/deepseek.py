# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 11:44:01 2025

@author: Yiming Li
"""
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def call(content: str):
    
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system",
                 "content": "You are a clinical data analyst specialized in interpreting patient temperature records."},
                {"role": "user",
                 "content": content
                 }
            ],
            temperature=0  # deterministic output
        )
    
        reasoning = response.choices[0].message.reasoning_content
        summary = response.choices[0].message.content
    
    except Exception as e:
        print("Got deepseek api error: ", e)
        print("Possibly rate limit, sleep for 2 minutes.")
        time.sleep(120)
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system",
                 "content": "You are a clinical data analyst specialized in interpreting patient temperature records."},
                {"role": "user",
                 "content": content
                 }
            ],
            temperature=0  # deterministic output
        )
    
        reasoning = response.choices[0].message.reasoning_content
        summary = response.choices[0].message.content

    
    return reasoning, summary