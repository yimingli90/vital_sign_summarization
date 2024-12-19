# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 15:10:23 2024

@author: YimingL
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utilities.save_file import save_dataframe_to_csv

def get_specific_vital_sign(specific_sign: str, vital_sign_df):
    
    vital_sign_df = vital_sign_df
    filtered_data = vital_sign_df[vital_sign_df['EventName'] == specific_sign]
    save_dataframe_to_csv(df=filtered_data, file_path='./data/' + specific_sign + '.csv')

    return filtered_data

def random_cut_in_time(case):
    start_time = case['AdmissionDate']
    end_time = case['DischargeDate']

    # 将时间戳转换为整数（表示为时间戳的纳秒数）
    start_ns = start_time.value
    end_ns = end_time.value

    # 在范围内随机生成一个整数
    random_ns = np.random.randint(start_ns, end_ns, dtype=np.int64)# we should assume cut-in time after the first 

    # 将随机生成的整数转换回时间戳
    cut_in_time = pd.Timestamp(random_ns)
    
    return cut_in_time

def plot_records(data: dict, cut_in_time):
    # 转换体温数据为DataFrame
    temp_records = pd.DataFrame(data["Temperature Tympanic"])
    
    # 尝试将 "Degree" 列转换为数字，无法转换的会被设为 NaN
    temp_records["Degree"] = pd.to_numeric(temp_records["Degree"], errors='coerce')
    
    # 删除 "Degree" 列中为 NaN 的行
    temp_records.dropna(subset=["Degree"], inplace=True)
    
    # 将 "Degree" 列转换为 float 类型
    temp_records["Degree"] = temp_records["Degree"].astype(float)
    

    # 筛选cut-in前的15个数据点
    cut_in_data = temp_records[temp_records["PerformedDateTime"] <= cut_in_time]
    if len(cut_in_data) > 15:
        plot_data = cut_in_data.tail(15)
    else:
        # 若不足15点，则取cut-in前5天内的数据
        start_time = max(data["AdmissionDate"], cut_in_time - pd.Timedelta(days=5))
        plot_data = cut_in_data[cut_in_data["PerformedDateTime"] >= start_time]
    
    # 自动识别发热区间
    fever_threshold = 37.5
    fever_intervals = []
    in_fever = False
    fever_start = None
    previous_time = None
    
    for _, row in plot_data.iterrows():
        if row["Degree"] >= fever_threshold:
            if not in_fever:
                fever_start = row["PerformedDateTime"]
                in_fever = True
            previous_time = row["PerformedDateTime"]
        else:
            if in_fever:
                fever_intervals.append((fever_start, previous_time))  # 使用上一个时间点
                in_fever = False
    
    if in_fever:
        fever_intervals.append((fever_start, plot_data["PerformedDateTime"].iloc[-1]))
    
    # 绘图
    plt.figure(figsize=(12, 6))
    
    # 按照体温阈值标注点的颜色
    colors = ["red" if temp > fever_threshold else "blue" for temp in plot_data["Degree"]]
    
    # 绘制体温曲线，标注颜色
    plt.scatter(plot_data["PerformedDateTime"], plot_data["Degree"], c=colors, label="Temperature Tympanic")
    plt.plot(plot_data["PerformedDateTime"], plot_data["Degree"], color="gray", linestyle="-", alpha=0.5)
    
    # 绘制cut-in时间
    plt.axvline(cut_in_time, color="red", linestyle="--", label="Cut-in Time")
    
    # 标注自动识别的发热区间
    for i, (start, end) in enumerate(fever_intervals):
        if i == 0:
            if start == end:
                plt.axvline(x=start, color='orange', linestyle='-', label="Fever Interval")
            else:
                plt.axvspan(start, end, color="orange", alpha=0.3, label="Fever Interval")
        else:
            if start == end:
                plt.axvline(x=start, color='orange', linestyle='-')
            else:
                plt.axvspan(start, end, color="orange", alpha=0.3)  # 不重复添加label
    
    # 图表设置
    plt.title("Patient Temperature Timeline Before Cut-in Time with Fever Intervals")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # 显示图表
    plt.show()
    pass