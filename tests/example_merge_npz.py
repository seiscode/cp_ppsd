#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例脚本：使用ObsPy的PPSD.add_npz()方法合并单独的NPZ文件

这个脚本演示了如何将单文件模式生成的NPZ文件合并为完整的PPSD分析结果。
这是单文件处理模式的后续处理步骤。

使用方法：
    python example_merge_npz.py

作者: muly
日期: 2025-06-03
"""

import glob
import os
from pathlib import Path
from obspy.signal import PPSD


def merge_ppsd_files_by_station(npz_dir="./output/npz_single",
                                 output_dir="./output/merged_npz"):
    """
    按台站分组合并NPZ文件
    
    Args:
        npz_dir: 单文件NPZ文件目录
        output_dir: 合并后文件输出目录
    """
    
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 查找所有NPZ文件
    npz_files = glob.glob(os.path.join(npz_dir, "*.npz"))
    print(f"找到 {len(npz_files)} 个NPZ文件")
    
    # 按台站通道分组
    station_files = {}
    for npz_file in npz_files:
        filename = os.path.basename(npz_file)
        # 从文件名提取台站信息
        # 文件名格式: BJ.BBS.00.BHZ.20250324000000_PPSD_*_BJ-BBS-00-BHZ.npz
        parts = filename.split('_')
        if len(parts) >= 3:
            station_info = parts[-1].replace('.npz', '')  # BJ-BBS-00-BHZ
            station_id = station_info.replace('-', '.')   # BJ.BBS.00.BHZ
            
            if station_id not in station_files:
                station_files[station_id] = []
            station_files[station_id].append(npz_file)
    
    print(f"找到 {len(station_files)} 个台站通道")
    
    # 为每个台站合并文件
    for station_id, files in station_files.items():
        print(f"\n处理台站: {station_id} ({len(files)} 个文件)")
        
        if not files:
            print(f"  警告: 台站 {station_id} 没有找到文件")
            continue
        
        # 按时间排序文件
        files.sort()
        
        try:
            # 加载第一个文件作为基础
            print(f"  加载基础文件: {os.path.basename(files[0])}")
            merged_ppsd = PPSD.load_npz(files[0])
            
            # 逐个添加其他文件
            for npz_file in files[1:]:
                try:
                    print(f"  添加文件: {os.path.basename(npz_file)}")
                    merged_ppsd.add_npz(npz_file)
                except Exception as e:
                    print(f"    错误: 无法添加文件 {npz_file}: {e}")
                    continue
            
            # 保存合并后的文件
            merged_filename = f"MERGED_PPSD_{station_id.replace('.', '-')}.npz"
            merged_path = os.path.join(output_dir, merged_filename)
            merged_ppsd.save_npz(merged_path)
            
            # 显示统计信息
            times_processed = merged_ppsd.times_processed
            n_segments = len(times_processed) if times_processed else 0
            time_range = ""
            if times_processed:
                start_time = min(times_processed)
                end_time = max(times_processed)
                time_range = f"从 {start_time} 到 {end_time}"
            
            print(f"  ✓ 合并完成: {merged_filename}")
            print(f"    总时间段数: {n_segments}")
            print(f"    时间范围: {time_range}")
            
        except Exception as e:
            print(f"  ✗ 合并失败: {e}")
            continue


def merge_selective_files(file_pattern, output_file):
    """
    选择性合并特定模式的文件
    
    Args:
        file_pattern: 文件模式，如 "./output/npz_single/BJ.BBS.00.BHZ.*"
        output_file: 输出文件路径
    """
    
    files = glob.glob(file_pattern)
    files.sort()
    
    if not files:
        print(f"没有找到匹配的文件: {file_pattern}")
        return
    
    print(f"选择性合并 {len(files)} 个文件...")
    
    try:
        # 加载第一个文件
        merged_ppsd = PPSD.load_npz(files[0])
        print(f"基础文件: {os.path.basename(files[0])}")
        
        # 添加其他文件
        for npz_file in files[1:]:
            try:
                merged_ppsd.add_npz(npz_file)
                print(f"添加: {os.path.basename(npz_file)}")
            except Exception as e:
                print(f"跳过: {os.path.basename(npz_file)} - {e}")
                continue
        
        # 保存结果
        merged_ppsd.save_npz(output_file)
        
        # 显示统计信息
        times_processed = merged_ppsd.times_processed
        n_segments = len(times_processed) if times_processed else 0
        print(f"\n✓ 选择性合并完成: {output_file}")
        print(f"  总时间段数: {n_segments}")
        
    except Exception as e:
        print(f"✗ 选择性合并失败: {e}")


def main():
    """主函数"""
    print("PPSD NPZ文件合并示例")
    print("=" * 50)
    
    # 示例1: 按台站自动合并所有文件
    print("\n1. 按台站自动合并所有文件...")
    merge_ppsd_files_by_station()
    
    # 示例2: 选择性合并特定台站的文件
    print("\n2. 选择性合并示例...")
    
    # 合并BJ.BBS站所有时间段的数据
    merge_selective_files(
        "./output/npz_single/BJ.BBS.00.BHZ.*",
        "./output/merged_npz/SELECTIVE_BJ-BBS-00-BHZ_ALL.npz"
    )
    
    # 合并特定日期的所有台站数据（2025-03-24）
    merge_selective_files(
        "./output/npz_single/*20250324*",
        "./output/merged_npz/SELECTIVE_ALL_STATIONS_20250324.npz"
    )
    
    print("\n" + "=" * 50)
    print("合并完成！")
    print("\n使用建议:")
    print("1. 按台站合并适用于长期连续分析")
    print("2. 选择性合并适用于特定时间段或事件分析")
    print("3. 合并后的文件可以直接用于绘图和进一步分析")
    print("\n合并后可以使用以下代码进行分析:")
    print("```python")
    print("from obspy.signal import PPSD")
    print("ppsd = PPSD.load_npz('合并后的文件.npz')")
    print("ppsd.plot()  # 绘制标准PPSD图")
    print("ppsd.plot_temporal()  # 绘制时间演化图")
    print("ppsd.plot_spectrogram()  # 绘制频谱图")
    print("```")


if __name__ == "__main__":
    main() 