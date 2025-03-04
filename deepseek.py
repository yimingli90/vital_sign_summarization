# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 10:52:17 2025

@author: Yiming Li
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
from templates import TEMPLATE_TITE
from docx import Document
from docx.shared import Inches, RGBColor
load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

# Replace with your OpenAI API key
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")




# Output Result
i = 0
for example in cases[1]:
    print(i)
    i += 1
    example = cases[1][2]
    cut_in_time = example['cut_in_time']
    patient_data = example['vs_records']
    
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "You are a clinical data analyst specialized in interpreting patient temperature records."},
            {"role": "user", "content": TEMPLATE_TITE.format(cut_in_time=cut_in_time, patient_data=patient_data)}
        ],
        temperature=0  # deterministic output
    )

    resoning  = response.choices[0].message.reasoning_content
    summary = response.choices[0].message.content
    example['ds_resoning'] = resoning
    example['ds_summary_all'] = summary
print("Summary:", summary)

for j, item in enumerate(case[1]):  # 遍历每组 8 个记录

    openai_summary_rules = item["rule_summarization"]
    ds_summary = item["ds_summary_all"]

    # 添加记录标题
    doc.add_heading(f"Record {j+1}", level=2)

    # 创建一个新段落
    p = doc.add_paragraph()

    # 插入 "Rule Summarization:" 并设置蓝色
    run_rule = p.add_run("GPT-4o-mini Summarization (Summarize Rules): ")
    run_rule.font.color.rgb = RGBColor(0, 0, 255)  # 蓝色

    # 插入规则总结文本（默认颜色）
    p.add_run(openai_summary_rules + "\n")

    # 插入 "GPT-4 Summarization:" 并设置蓝色
    run_gpt = p.add_run("DeepSeek Summarization (Summarize Data): ")
    run_gpt.font.color.rgb = RGBColor(0, 0, 255)  # 蓝色

    # 插入 GPT-4 总结文本（默认颜色）
    p.add_run(ds_summary + "\n")



# **保存 Word 文档**
output_folder='./data/summarization/Three Signs'
output_path = os.path.join(output_folder, f"Group_{i+1}.docx")
doc.save(output_path)
print(f"✅ Saved: {output_path}")