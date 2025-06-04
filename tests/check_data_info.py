#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据文件基本信息
"""

import obspy
from pathlib import Path

def check_data_info():
    """检查数据文件信息"""
    print("=== 数据文件信息检查 ===")
    
    # 读取数据文件
    data_dir = Path('./data/')
    mseed_files = list(data_dir.rglob('*.mseed'))
    
    if not mseed_files:
        print("未找到mseed文件")
        return
    
    print(f"找到 {len(mseed_files)} 个mseed文件")
    
    # 检查每个文件的基本信息
    sampling_rates = set()
    channels = set()
    
    for i, file_path in enumerate(mseed_files[:3]):  # 只检查前3个文件
        print(f"\n文件 {i+1}: {file_path.name}")
        try:
            st = obspy.read(str(file_path))
            for tr in st:
                print(f"  台站: {tr.stats.network}.{tr.stats.station}.{tr.stats.location}.{tr.stats.channel}")
                print(f"  采样率: {tr.stats.sampling_rate} Hz")
                print(f"  奈奎斯特周期: {2.0/tr.stats.sampling_rate:.3f} 秒")
                print(f"  数据长度: {tr.stats.npts} 点 ({tr.stats.npts/tr.stats.sampling_rate:.1f} 秒)")
                print(f"  时间范围: {tr.stats.starttime} - {tr.stats.endtime}")
                
                sampling_rates.add(tr.stats.sampling_rate)
                channels.add(f"{tr.stats.network}.{tr.stats.station}.{tr.stats.location}.{tr.stats.channel}")
        except Exception as e:
            print(f"  读取失败: {e}")
    
    print(f"\n=== 数据概要 ===")
    print(f"采样率: {sorted(sampling_rates)} Hz")
    print(f"通道数: {len(channels)}")
    print(f"最小奈奎斯特周期: {2.0/max(sampling_rates):.3f} 秒")
    print(f"最大奈奎斯特周期: {2.0/min(sampling_rates):.3f} 秒")
    
    # 检查配置文件中的周期范围
    import toml
    try:
        with open('input/config.toml', 'r', encoding='utf-8') as f:
            config = toml.load(f)
        
        period_limits = config.get('args', {}).get('period_limits', [0.01, 1000.0])
        min_period, max_period = period_limits
        
        print(f"\n=== 配置兼容性检查 ===")
        print(f"配置的周期范围: {min_period} - {max_period} 秒")
        
        min_nyquist = 2.0/max(sampling_rates)
        if min_period >= min_nyquist:
            print(f"✓ 最小周期 {min_period}s >= 最小奈奎斯特周期 {min_nyquist:.3f}s")
        else:
            print(f"⚠ 最小周期 {min_period}s < 最小奈奎斯特周期 {min_nyquist:.3f}s")
            print(f"  建议将最小周期调整为 {min_nyquist:.3f}s 或更大")
            
    except Exception as e:
        print(f"读取配置文件失败: {e}")

if __name__ == '__main__':
    check_data_info() 