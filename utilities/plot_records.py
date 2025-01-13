# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 10:51:12 2025

@author: YimingL
"""
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta

from datetime import timedelta
import pandas as pd
import matplotlib.pyplot as plt

def plot_temperature_records(data: dict, cutoff_time): 
    # 转换体温数据为 DataFrame
    temp_records = pd.DataFrame(data["Temperature Tympanic"])
    
    # 尝试将 "Degree" 列转换为数字，无法转换的会被设为 NaN
    temp_records["Degree"] = pd.to_numeric(temp_records["Degree"], errors='coerce')
    
    # 删除 "Degree" 列中为 NaN 的行
    temp_records.dropna(subset=["Degree"], inplace=True)
    
    # 将 "Degree" 列转换为 float 类型
    temp_records["Degree"] = temp_records["Degree"].astype(float)

    # 筛选出距离 `cut-in time` 最近的 15 个数据点
    cut_in_data = temp_records[temp_records["PerformedDateTime"] <= cutoff_time]
    
    if len(cut_in_data) > 20:
        plot_data = cut_in_data.tail(20)
    else:
        # 若不足 15 点，则取 `cut-in time` 前最近 5 天的数据
        start_time = max(data["AdmissionDate"], cutoff_time - pd.Timedelta(days=5))
        plot_data = cut_in_data[cut_in_data["PerformedDateTime"] >= start_time]
    
    # 发热状态判断
    THRESHOLD_TEMPERATURE = 37.8
    fever_records = [r for _, r in temp_records.iterrows() if r["Degree"] >= THRESHOLD_TEMPERATURE  and r["PerformedDateTime"] <= cutoff_time and r["PerformedDateTime"] >= min(plot_data['PerformedDateTime'])]
    
    # 多段发热区间识别
    fever_intervals = []
    current_start = None
    last_time = None
    
    for record in fever_records:
        if current_start is None:
            current_start = record["PerformedDateTime"]
        elif (record["PerformedDateTime"] - last_time) > timedelta(hours=24):  # 间隔超过1小时，视为新发热段
            fever_intervals.append((current_start, last_time))
            current_start = record["PerformedDateTime"]
        last_time = record["PerformedDateTime"]
    
    if current_start is not None:
        fever_intervals.append((current_start, last_time))
    
    # 绘图
    plt.figure(figsize=(12, 6))
    
    # 按照体温阈值标注点的颜色
    colors = ["red" if temp >= THRESHOLD_TEMPERATURE else "blue" for temp in plot_data["Degree"]]
    
    # 绘制体温曲线，标注颜色
    plt.scatter(plot_data["PerformedDateTime"], plot_data["Degree"], c=colors, label="Temperature Tympanic")
    plt.plot(plot_data["PerformedDateTime"], plot_data["Degree"], color="gray", linestyle="-", alpha=0.5)
    
    # 绘制cut-in时间
    plt.axvline(cutoff_time, color="red", linestyle="--", label="Cut-in Time")
    
    # 如果检测到发热区间，绘制多段发热区间
    if fever_intervals:
        # 普通发热区间
        for i, (start, end) in enumerate(fever_intervals[:-1]):  # 不包含最后一个区间
            if start == end:
                plt.axvline(x=start, color='orange', linestyle='-', label="Fever Interval" if i == 0 else None)
            else:
                plt.axvspan(start, end, color="orange", alpha=0.3, label="Fever Interval" if i == 0 else None)
        
        # 最后一个发热区间用红色标注
        last_start, last_end = fever_intervals[-1]
        if last_start == last_end:
            plt.axvline(x=last_start, color="red", linestyle="-", label="Last Fever Interval")
        else:
            plt.axvspan(last_start, last_end, color="red", alpha=0.3, label="Last Fever Interval")
    else:
        # 如果没有发热区间，绘制最后一个发热记录的红色竖线
        if fever_records:
            last_fever_time = fever_records[-1]["PerformedDateTime"]
            plt.axvline(x=last_fever_time, color="red", linestyle="--", label="Last Fever Record")
    
    # 图表设置
    plt.title("Patient Temperature Timeline with Highlighted Last Fever")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # 显示图表
    plt.show()
    
    # 返回发热区间
    return fever_intervals


