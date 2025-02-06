# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 10:51:12 2025

@author: YimingL
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from datetime import timedelta
from . import THRESHOLD_TEMPERATURE

#THRESHOLD_TEMPERATURE = 37.8
    
def plot_temperature_records(data: dict, cutoff_time): 
    """绘制体温记录/Plot patient temperature record"""
    # 转换体温数据为 DataFrame/Transform the records to DataFrame
    temp_records = pd.DataFrame(data["Temperature Tympanic"])
    
    # 尝试将 "Degree" 列转换为数字，无法转换的会被设为 NaN/Transform "Degree" to numeric, or NaN
    temp_records["Degree"] = pd.to_numeric(temp_records["Degree"], errors='coerce')
    
    # 删除 "Degree" 列中为 NaN 的行/Del the NaN records
    temp_records.dropna(subset=["Degree"], inplace=True)
    
    # 将 "Degree" 列转换为 float 类型/Transform "Degree" to float
    temp_records["Degree"] = temp_records["Degree"].astype(float)

    # 筛选出 `cut-in time` 之前的数据/Filter the data before cut-in time
    cut_in_data = temp_records[temp_records["PerformedDateTime"] <= cutoff_time]

    # 选择起始时间/Choose the start date
    start_time = max(data["AdmissionDate"], cutoff_time - pd.Timedelta(days=5))
    plot_data = cut_in_data[cut_in_data["PerformedDateTime"] >= start_time]
    
    # 如果离 `cut-in time` 最近五天内没有数据，则选取最近的两个数据点/Choose the last two data point if there is no data in last 5 days of cut-in time
    if len(plot_data) == 0:
        plot_data = cut_in_data.tail(2)

    # 发热状态判断/Check if febrile at cut-in
    fever_records = [r for _, r in temp_records.iterrows() if r["Degree"] >= THRESHOLD_TEMPERATURE  and r["PerformedDateTime"] <= cutoff_time and r["PerformedDateTime"] >= min(plot_data['PerformedDateTime'])]
    
    # 多段发热区间识别/Recognise multiple fever intervals
    fever_intervals = []
    current_start = None
    last_time = None
    
    for record in fever_records:
        if current_start is None:
            current_start = record["PerformedDateTime"]
        elif (record["PerformedDateTime"] - last_time) > timedelta(hours=24):  # 间隔超过24小时，视为新发热段/See it as new febrile if time gap is more than 24 hours
            fever_intervals.append((current_start, last_time))
            current_start = record["PerformedDateTime"]
        last_time = record["PerformedDateTime"]
    
    if current_start is not None:
        fever_intervals.append((current_start, last_time))
    
    # 绘图/Plot
    plt.figure(figsize=(12, 6))

    
    # 红色的：发热/Red point: febrile
    high_temp_data = plot_data[plot_data["Degree"] >= THRESHOLD_TEMPERATURE]
    plt.scatter(high_temp_data["PerformedDateTime"], high_temp_data["Degree"], color="red", label="High Temperature (≥37.8°C)")
    
    # 蓝色点：非发热/Blue point: afebrile
    low_temp_data = plot_data[plot_data["Degree"] < THRESHOLD_TEMPERATURE]
    plt.scatter(low_temp_data["PerformedDateTime"], low_temp_data["Degree"], color="blue", label="Normal Temperature (<37.8°C)")
    plt.plot(plot_data["PerformedDateTime"], plot_data["Degree"], color="gray", linestyle="-", alpha=0.5)

    # 绘制cut-in时间以及入院时间/Plot cut-in time and admission date
    plt.axvline(cutoff_time, color="red", linestyle="--", label="Cut-in Time")
    if start_time == data["AdmissionDate"]:
        plt.axvline(start_time, color="blue", linestyle="--", label="Addmission Date")
        formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M")
        plt.text(start_time, plot_data["Degree"].max() + 0.3, f"Admission Date\n{formatted_start_time}",
                 color="blue", fontsize=10, ha="center", va="bottom")
        
    # 在cut-in时间上方标注具体时间/Mark the cut-in time
    formatted_cutoff_time = cutoff_time.strftime("%Y-%m-%d %H:%M")
    plt.text(cutoff_time, plot_data["Degree"].max() + 0.3, f"Cut-in Time\n{formatted_cutoff_time}",
             color="red", fontsize=10, ha="center", va="bottom")
    
    # 如果检测到发热区间，绘制多段发热区间/Plot multiple fever invtervals if exist
    if fever_intervals:
        
        # 普通发热区间/Plot fever intervals
        for i, (start, end) in enumerate(fever_intervals[:-1]):  # 不包含最后一个区间/The last interval is not included
            if start == end:
                plt.axvline(x=start, color='orange', linestyle='-',
                            label="Fever Interval" if i == 0 else None)
            else:
                plt.axvspan(start, end, color="orange", alpha=0.3,
                            label="Fever Interval" if i == 0 else None)
        
        # 最后一个发热区间用红色标注/Use the red mark for the last fever interval
        last_start, last_end = fever_intervals[-1]
        if last_start == last_end:
            plt.axvline(x=last_start, color="red", linestyle="-", label="Last Fever Interval")
        else:
            plt.axvspan(last_start, last_end, color="red", alpha=0.3, label="Last Fever Interval")
    else:
        
        # 如果没有发热区间，绘制最后一个发热记录的红色竖线/Plot a red vertical line for the last fever record if there is no fever interval
        if fever_records:
            last_fever_time = fever_records[-1]["PerformedDateTime"]
            plt.axvline(x=last_fever_time, color="red", linestyle="--", label="Last Fever Record")
    
    # 图表设置/Plot settings
    # Fix x-axis range and add regular ticks
    if start_time == data["AdmissionDate"]:
        plt.xlim(start_time - pd.Timedelta(hours=1), cutoff_time)
    else:
        plt.xlim(start_time, cutoff_time)
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=12))  # Major ticks every 12 hours
    #plt.gca().xaxis.set_minor_locator(plt.matplotlib.dates.HourLocator(interval=6))   # Minor ticks every 6 hours
    plt.gcf().autofmt_xdate()  # Rotate date labels for better readability

    plt.title("Patient Temperature Timeline", fontsize=15)
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # 显示图标/Show plot
    plt.show()
    
    # 返回发热区间/Return fever intervals, this is not needed
    return fever_intervals



def plot_temperature_records_for_reader(data: dict, cutoff_time): 
    """绘制体温记录/Plot patient temperature record"""
    # 转换体温数据为 DataFrame/Transform the records to DataFrame
    temp_records = pd.DataFrame(data["Temperature Tympanic"])
    temp_records["Degree"] = pd.to_numeric(temp_records["Degree"], errors='coerce')
    temp_records.dropna(subset=["Degree"], inplace=True)
    temp_records["Degree"] = temp_records["Degree"].astype(float)
    cut_in_data = temp_records[temp_records["PerformedDateTime"] <= cutoff_time]
    start_time = max(data["AdmissionDate"], cutoff_time - pd.Timedelta(hours=120))
    plot_data = cut_in_data[cut_in_data["PerformedDateTime"] >= start_time]
    if len(plot_data) == 0:
        plot_data = cut_in_data.tail(2)
    
    plt.figure(figsize=(12, 6))

    # Plot temperature data as grey dots and lines for neutrality
    plt.scatter(plot_data["PerformedDateTime"], plot_data["Degree"], color="blue", label="Temperature")
    plt.plot(plot_data["PerformedDateTime"], plot_data["Degree"], color="grey", linestyle="-", alpha=0.5)
    
    # Draw vertical lines for cut-in time and admission date
    plt.axvline(cutoff_time, color="red", linestyle="--", label="Cut-in Time")

    if start_time == data["AdmissionDate"]:
        plt.axvline(start_time, color="blue", linestyle="--", label="Admission Date")
        formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M")
        plt.text(start_time, 42 + 0.2, f"Admission Date\n{formatted_start_time}",
                 color="blue", fontsize=10, ha="center", va="bottom")
    
    # Add cut-in time annotation
    formatted_cutoff_time = cutoff_time.strftime("%Y-%m-%d %H:%M")
    plt.text(cutoff_time, 42 + 0.2, f"Cut-in Time\n{formatted_cutoff_time}",
             color="red", fontsize=10, ha="center", va="bottom")
    
    # Fix y-axis range and add minor grid lines
    plt.ylim(35, 42)  # Adjust as needed for your data range
    plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    plt.grid(which='minor', linestyle=':', linewidth=0.5)

    # Fix x-axis range and add regular ticks
    if start_time == data["AdmissionDate"]:
        plt.xlim(start_time - pd.Timedelta(hours=1), cutoff_time)
    else:
        plt.xlim(start_time, cutoff_time)
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=12))  # Major ticks every 12 hours
    #plt.gca().xaxis.set_minor_locator(plt.matplotlib.dates.HourLocator(interval=6))   # Minor ticks every 6 hours
    plt.gcf().autofmt_xdate()  # Rotate date labels for better readability

    # Chart settings
    plt.title("Patient Temperature Timeline", fontsize=15)
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True, which='major', linestyle='-', linewidth=0.8)
    plt.tight_layout()
    
    # Show plot
    plt.show()
    return plt, plot_data


def plot_temperature_records_for_reader_fig(data: dict, cutoff_time):
    """绘制体温记录/Plot patient temperature record"""
    # 转换体温数据为 DataFrame
    temp_records = pd.DataFrame(data["Temperature Tympanic"])
    temp_records["Degree"] = pd.to_numeric(temp_records["Degree"], errors='coerce')
    temp_records.dropna(subset=["Degree"], inplace=True)
    temp_records["Degree"] = temp_records["Degree"].astype(float)
    cut_in_data = temp_records[temp_records["PerformedDateTime"] <= cutoff_time]
    start_time = max(data["AdmissionDate"], cutoff_time - pd.Timedelta(hours=120))
    plot_data = cut_in_data[cut_in_data["PerformedDateTime"] >= start_time]
    if len(plot_data) == 0:
        plot_data = cut_in_data.tail(2)

    # 创建 Figure 和 Axes
    fig, ax = plt.subplots(figsize=(12, 6))

    # 绘制温度数据点和线
    ax.scatter(plot_data["PerformedDateTime"], plot_data["Degree"], color="blue", label="Temperature")
    ax.plot(plot_data["PerformedDateTime"], plot_data["Degree"], color="grey", linestyle="-", alpha=0.5)
    
    # 画 cut-in 时间和入院时间的竖线
    ax.axvline(cutoff_time, color="red", linestyle="--", label="Cut-in Time")
    
    if start_time == data["AdmissionDate"]:
        ax.axvline(start_time, color="blue", linestyle="--", label="Admission Date")
        formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M")
        ax.text(start_time, 42 + 0.2, f"Admission Date\n{formatted_start_time}",
                color="blue", fontsize=10, ha="center", va="bottom")

    # 添加 cut-in 时间标注
    formatted_cutoff_time = cutoff_time.strftime("%Y-%m-%d %H:%M")
    ax.text(cutoff_time, 42 + 0.2, f"Cut-in Time\n{formatted_cutoff_time}",
            color="red", fontsize=10, ha="center", va="bottom")

    # 设置 y 轴范围和次级刻度
    ax.set_ylim(35, 42)
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    ax.grid(which='minor', linestyle=':', linewidth=0.5)

    # 设置 x 轴范围和主刻度
    if start_time == data["AdmissionDate"]:
        ax.set_xlim(start_time - pd.Timedelta(hours=1), cutoff_time)
    else:
        ax.set_xlim(start_time, cutoff_time)
    
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=12))  # 主要刻度间隔 12 小时
    fig.autofmt_xdate()  # 旋转日期标签

    # 图表标题和标签
    ax.set_title("Patient Temperature Timeline", fontsize=15)
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    ax.grid(True, which='major', linestyle='-', linewidth=0.8)
    fig.tight_layout()

    # 返回 Figure 而不是 plt
    return fig, plot_data
