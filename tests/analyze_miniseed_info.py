#!/usr/bin/env python3
"""
MinISEED文件信息分析工具

分析data目录下的miniseed文件的基本信息，不依赖ObsPy。

功能特点：
- 分析文件大小和基本信息
- 从文件名提取台站信息
- 生成数据概览报告

Date: 2025-01-30
"""

import os
import glob
from datetime import datetime


def find_miniseed_files(data_dir):
    """
    查找数据目录下的miniseed文件
    
    Parameters:
    -----------
    data_dir : str
        数据目录路径
        
    Returns:
    --------
    list : miniseed文件路径列表
    """
    mseed_patterns = ['*.mseed', '*.miniseed', '*.ms']
    files = []
    
    for pattern in mseed_patterns:
        files.extend(glob.glob(os.path.join(data_dir, pattern)))
    
    return sorted(files)


def extract_station_info(filename):
    """
    从文件名提取台站信息
    
    Parameters:
    -----------
    filename : str
        文件名
        
    Returns:
    --------
    dict : 包含台站信息的字典
    """
    basename = os.path.basename(filename)
    parts = basename.split('.')
    
    info = {
        'network': parts[0] if len(parts) > 0 else 'Unknown',
        'station': parts[1] if len(parts) > 1 else 'Unknown',
        'location': parts[2] if len(parts) > 2 else '00',
        'channel': parts[3] if len(parts) > 3 else 'Unknown',
        'datetime_str': parts[4] if len(parts) > 4 else 'Unknown',
        'filename': basename
    }
    
    # 尝试解析时间戳
    if info['datetime_str'] and info['datetime_str'] != 'Unknown':
        try:
            # 格式例如: 20250326000000
            if len(info['datetime_str']) >= 14:
                year = int(info['datetime_str'][:4])
                month = int(info['datetime_str'][4:6])
                day = int(info['datetime_str'][6:8])
                hour = int(info['datetime_str'][8:10])
                minute = int(info['datetime_str'][10:12])
                second = int(info['datetime_str'][12:14])
                
                info['start_time'] = datetime(year, month, day, hour, minute, second)
                info['date_str'] = f"{year}-{month:02d}-{day:02d}"
                info['time_str'] = f"{hour:02d}:{minute:02d}:{second:02d}"
            else:
                info['start_time'] = None
                info['date_str'] = 'Unknown'
                info['time_str'] = 'Unknown'
        except (ValueError, IndexError):
            info['start_time'] = None
            info['date_str'] = 'Unknown'
            info['time_str'] = 'Unknown'
    else:
        info['start_time'] = None
        info['date_str'] = 'Unknown'
        info['time_str'] = 'Unknown'
    
    return info


def analyze_file_info(file_path):
    """
    分析单个文件的基本信息
    
    Parameters:
    -----------
    file_path : str
        文件路径
        
    Returns:
    --------
    dict : 文件信息字典
    """
    try:
        stat = os.stat(file_path)
        
        info = {
            'path': file_path,
            'size_bytes': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'created_time': datetime.fromtimestamp(stat.st_ctime)
        }
        
        # 提取台站信息
        station_info = extract_station_info(file_path)
        info.update(station_info)
        
        return info
        
    except Exception as e:
        print(f"Error analyzing file {file_path}: {e}")
        return None


def generate_summary_report(files_info):
    """
    生成数据汇总报告
    
    Parameters:
    -----------
    files_info : list
        文件信息列表
    """
    print("\n" + "=" * 70)
    print("BJ Network MinISEED Data Summary Report")
    print("=" * 70)
    
    if not files_info:
        print("No valid files found.")
        return
    
    # 基本统计
    total_files = len(files_info)
    total_size = sum(f['size_bytes'] for f in files_info)
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"\n=== Basic Statistics ===")
    print(f"Total files: {total_files}")
    print(f"Total size: {total_size_mb:.1f} MB ({total_size:,} bytes)")
    print(f"Average file size: {total_size_mb/total_files:.1f} MB")
    
    # 台站统计
    networks = set(f['network'] for f in files_info)
    stations = set(f['station'] for f in files_info)
    channels = set(f['channel'] for f in files_info)
    
    print(f"\n=== Network Information ===")
    print(f"Networks: {', '.join(sorted(networks))}")
    print(f"Stations: {', '.join(sorted(stations))}")
    print(f"Channels: {', '.join(sorted(channels))}")
    
    # 按台站分组
    print(f"\n=== Station Details ===")
    station_groups = {}
    for f in files_info:
        station = f['station']
        if station not in station_groups:
            station_groups[station] = []
        station_groups[station].append(f)
    
    for station in sorted(station_groups.keys()):
        files = station_groups[station]
        total_mb = sum(f['size_mb'] for f in files)
        channels = sorted(set(f['channel'] for f in files))
        dates = sorted(set(f['date_str'] for f in files if f['date_str'] != 'Unknown'))
        
        print(f"\n  Station {station}:")
        print(f"    Files: {len(files)}")
        print(f"    Size: {total_mb:.1f} MB")
        print(f"    Channels: {', '.join(channels)}")
        if dates:
            print(f"    Date(s): {', '.join(dates)}")
    
    # 详细文件列表
    print(f"\n=== Detailed File List ===")
    print(f"{'No.':<3} {'Station':<7} {'Channel':<7} {'Date':<12} {'Time':<10} {'Size(MB)':<9} {'Filename'}")
    print("-" * 70)
    
    for i, f in enumerate(sorted(files_info, key=lambda x: (x['station'], x['channel'])), 1):
        print(f"{i:<3} {f['station']:<7} {f['channel']:<7} {f['date_str']:<12} "
              f"{f['time_str']:<10} {f['size_mb']:<9.1f} {f['filename']}")


def main():
    """
    主函数：分析miniseed文件信息
    """
    print("=" * 70)
    print("BJ Network MinISEED File Information Analyzer")
    print("=" * 70)
    
    # 数据目录
    data_dir = "../data"
    
    # 检查数据目录
    if not os.path.exists(data_dir):
        print(f"Error: Data directory {data_dir} not found")
        return
    
    print(f"Scanning directory: {data_dir}")
    
    # 查找miniseed文件
    mseed_files = find_miniseed_files(data_dir)
    
    if not mseed_files:
        print(f"No miniseed files found in {data_dir}")
        return
    
    print(f"\nFound {len(mseed_files)} miniseed files:")
    
    # 分析每个文件
    files_info = []
    for file_path in mseed_files:
        print(f"Analyzing: {os.path.basename(file_path)}")
        
        file_info = analyze_file_info(file_path)
        if file_info:
            files_info.append(file_info)
            print(f"  Size: {file_info['size_mb']:.1f} MB")
            print(f"  Station: {file_info['network']}.{file_info['station']}")
            print(f"  Channel: {file_info['channel']}")
            if file_info['start_time']:
                print(f"  Time: {file_info['date_str']} {file_info['time_str']}")
    
    # 生成汇总报告
    generate_summary_report(files_info)
    
    # 建议
    print(f"\n=== Recommendations ===")
    print("To visualize these waveforms, you need ObsPy installed.")
    print("Install command: pip install obspy")
    print("\nOnce ObsPy is available, use:")
    print("  python3 plot_miniseed_waveforms.py")
    
    print(f"\nAnalysis complete!")


if __name__ == "__main__":
    main() 