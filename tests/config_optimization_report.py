#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置参数优化建议报告

基于实际数据特性分析，提供具体的配置参数优化建议。
"""

import os
import sys
import toml
import obspy
import numpy as np
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def analyze_data_characteristics():
    """分析数据特性"""
    print("=== 数据特性分析 ===")
    
    data_dir = Path('./data/')
    mseed_files = list(data_dir.rglob('*.mseed'))
    
    if not mseed_files:
        print("未找到mseed文件")
        return {}
    
    sampling_rates = []
    channels = set()
    total_duration = 0
    data_gaps = []
    
    print(f"分析 {len(mseed_files)} 个数据文件...")
    
    for file_path in mseed_files:
        try:
            st = obspy.read(str(file_path))
            for tr in st:
                sampling_rates.append(tr.stats.sampling_rate)
                channels.add(f"{tr.stats.network}.{tr.stats.station}.{tr.stats.location}.{tr.stats.channel}")
                duration = tr.stats.npts / tr.stats.sampling_rate
                total_duration += duration
                
                # 检查数据间断
                if hasattr(tr.stats, 'gaps'):
                    data_gaps.extend(tr.stats.gaps)
                    
        except Exception as e:
            print(f"  读取文件失败 {file_path.name}: {e}")
    
    # 统计结果
    unique_sampling_rates = list(set(sampling_rates))
    min_nyquist_period = 2.0 / max(unique_sampling_rates)
    max_nyquist_period = 2.0 / min(unique_sampling_rates)
    
    characteristics = {
        'sampling_rates': unique_sampling_rates,
        'channels': list(channels),
        'total_duration_hours': total_duration / 3600,
        'min_nyquist_period': min_nyquist_period,
        'max_nyquist_period': max_nyquist_period,
        'has_gaps': len(data_gaps) > 0,
        'num_gaps': len(data_gaps)
    }
    
    print(f"✓ 采样率: {unique_sampling_rates} Hz")
    print(f"✓ 通道数: {len(channels)}")
    print(f"✓ 总数据时长: {total_duration/3600:.1f} 小时")
    print(f"✓ 奈奎斯特周期范围: {min_nyquist_period:.3f} - {max_nyquist_period:.3f} 秒")
    print(f"✓ 数据间断: {'有' if characteristics['has_gaps'] else '无'} ({characteristics['num_gaps']}个)")
    
    return characteristics


def load_current_config():
    """加载当前配置"""
    config_path = "input/config.toml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = toml.load(f)
        print(f"✓ 成功加载配置文件: {config_path}")
        return config
    except Exception as e:
        print(f"✗ 加载配置文件失败: {e}")
        return {}


def generate_optimization_recommendations(data_chars, current_config):
    """生成优化建议"""
    print("\n=== 配置优化建议 ===")
    
    args = current_config.get('args', {})
    recommendations = []
    
    # 1. 周期范围优化
    current_period_limits = args.get('period_limits', [0.01, 1000.0])
    min_period, max_period = current_period_limits
    
    print("\n1. 周期范围优化:")
    if min_period < data_chars['min_nyquist_period']:
        recommended_min = data_chars['min_nyquist_period'] * 1.1  # 留10%余量
        print(f"  ⚠ 当前最小周期 {min_period}s 小于奈奎斯特周期 {data_chars['min_nyquist_period']:.3f}s")
        print(f"  建议: 将最小周期调整为 {recommended_min:.3f}s")
        recommendations.append({
            'parameter': 'period_limits[0]',
            'current': min_period,
            'recommended': round(recommended_min, 3),
            'reason': '避免混叠，确保频率分析有效性'
        })
    else:
        print(f"  ✓ 最小周期 {min_period}s 设置合理")
    
    # 检查最大周期是否过大
    if max_period > 1000:
        print(f"  ⚠ 最大周期 {max_period}s 可能过大，建议根据研究目标调整")
        recommendations.append({
            'parameter': 'period_limits[1]',
            'current': max_period,
            'recommended': 100.0,
            'reason': '减少计算量，聚焦于地震学关注的频段'
        })
    
    # 2. 时间窗口优化
    ppsd_length = args.get('ppsd_length', 3600)
    overlap = args.get('overlap', 0.5)
    
    print(f"\n2. 时间窗口优化:")
    print(f"  当前设置: 窗口长度 {ppsd_length}s, 重叠 {overlap*100:.0f}%")
    
    # 根据数据总时长建议窗口长度
    total_hours = data_chars['total_duration_hours']
    if total_hours < 24:
        if ppsd_length > 1800:
            recommendations.append({
                'parameter': 'ppsd_length',
                'current': ppsd_length,
                'recommended': 1800,
                'reason': f'数据总时长仅{total_hours:.1f}小时，建议使用较短窗口'
            })
    elif total_hours > 168:  # 一周以上
        if ppsd_length < 3600:
            recommendations.append({
                'parameter': 'ppsd_length',
                'current': ppsd_length,
                'recommended': 3600,
                'reason': f'数据总时长{total_hours:.1f}小时，可使用标准1小时窗口'
            })
    
    # 3. dB分箱优化
    db_bins = args.get('db_bins', [-200.0, -50.0, 0.25])
    if len(db_bins) == 3:
        min_db, max_db, step_db = db_bins
        num_bins = int((max_db - min_db) / step_db)
        
        print(f"\n3. dB分箱优化:")
        print(f"  当前设置: {min_db} 到 {max_db}dB, 步长 {step_db}dB ({num_bins}个分箱)")
        
        if num_bins > 800:
            new_step = 0.5
            recommendations.append({
                'parameter': 'db_bins[2]',
                'current': step_db,
                'recommended': new_step,
                'reason': f'当前分箱数{num_bins}过多，建议增大步长以提高计算效率'
            })
        elif num_bins < 100:
            new_step = 0.125
            recommendations.append({
                'parameter': 'db_bins[2]',
                'current': step_db,
                'recommended': new_step,
                'reason': f'当前分箱数{num_bins}过少，建议减小步长以提高精度'
            })
    
    # 4. 数据质量控制优化
    skip_on_gaps = args.get('skip_on_gaps', False)
    
    print(f"\n4. 数据质量控制优化:")
    if data_chars['has_gaps']:
        print(f"  检测到 {data_chars['num_gaps']} 个数据间断")
        if not skip_on_gaps:
            print(f"  当前设置: skip_on_gaps = {skip_on_gaps} (补零处理)")
            print(f"  建议: 考虑设置为 true 以跳过有间断的数据段")
            recommendations.append({
                'parameter': 'skip_on_gaps',
                'current': skip_on_gaps,
                'recommended': True,
                'reason': '数据存在间断，跳过可避免补零产生的伪影'
            })
    else:
        print(f"  ✓ 数据连续性良好，当前设置 skip_on_gaps = {skip_on_gaps} 合适")
    
    # 5. 性能优化建议
    print(f"\n5. 性能优化建议:")
    effective_step = ppsd_length * (1 - overlap)
    windows_per_hour = 3600 / effective_step
    total_windows = total_hours * windows_per_hour
    
    print(f"  预计处理窗口数: {total_windows:.0f}个")
    if total_windows > 10000:
        print(f"  ⚠ 窗口数量较多，建议:")
        print(f"    - 增大时间窗口长度")
        print(f"    - 减小重叠比例")
        print(f"    - 限制处理时间范围")
    
    return recommendations


def generate_optimized_config(current_config, recommendations):
    """生成优化后的配置"""
    print(f"\n=== 生成优化配置 ===")
    
    if not recommendations:
        print("无需优化，当前配置已经很好")
        return
    
    # 复制当前配置
    optimized_config = current_config.copy()
    
    # 应用建议
    for rec in recommendations:
        param = rec['parameter']
        new_value = rec['recommended']
        
        if param == 'period_limits[0]':
            optimized_config['args']['period_limits'][0] = new_value
        elif param == 'period_limits[1]':
            optimized_config['args']['period_limits'][1] = new_value
        elif param == 'ppsd_length':
            optimized_config['args']['ppsd_length'] = new_value
        elif param == 'db_bins[2]':
            optimized_config['args']['db_bins'][2] = new_value
        elif param == 'skip_on_gaps':
            optimized_config['args']['skip_on_gaps'] = new_value
    
    # 保存优化配置
    output_path = "input/config_optimized.toml"
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # 添加注释
            f.write("# 优化后的PPSD计算配置文件\n")
            f.write("# 基于数据特性分析自动生成\n")
            f.write("# 使用方法：python run_cp_ppsd.py input/config_optimized.toml\n\n")
            toml.dump(optimized_config, f)
        
        print(f"✓ 优化配置已保存到: {output_path}")
        
        # 显示主要变化
        print(f"\n主要优化项:")
        for rec in recommendations:
            print(f"  - {rec['parameter']}: {rec['current']} → {rec['recommended']}")
            print(f"    原因: {rec['reason']}")
            
    except Exception as e:
        print(f"✗ 保存优化配置失败: {e}")


def performance_estimation(config):
    """性能估算"""
    print(f"\n=== 性能估算 ===")
    
    args = config.get('args', {})
    ppsd_length = args.get('ppsd_length', 3600)
    overlap = args.get('overlap', 0.5)
    period_limits = args.get('period_limits', [0.01, 1000.0])
    period_step = args.get('period_step_octaves', 0.125)
    db_bins = args.get('db_bins', [-200.0, -50.0, 0.25])
    
    # 计算矩阵大小
    min_freq = 1.0 / period_limits[1]
    max_freq = 1.0 / period_limits[0]
    freq_bins = int(np.log2(max_freq / min_freq) / period_step) + 1
    
    if len(db_bins) == 3:
        db_bin_count = int((db_bins[1] - db_bins[0]) / db_bins[2])
    else:
        db_bin_count = 600
    
    matrix_size = freq_bins * db_bin_count
    memory_mb = matrix_size * 8 / 1024 / 1024  # 假设float64
    
    # 计算处理效率
    effective_step = ppsd_length * (1 - overlap)
    
    print(f"PPSD矩阵:")
    print(f"  - 频率分箱: {freq_bins}个")
    print(f"  - dB分箱: {db_bin_count}个")
    print(f"  - 矩阵大小: {freq_bins} × {db_bin_count}")
    print(f"  - 内存估算: {memory_mb:.1f} MB/台站")
    
    print(f"\n处理效率:")
    print(f"  - 时间窗口: {ppsd_length}s")
    print(f"  - 有效步长: {effective_step}s")
    print(f"  - 每小时窗口数: {3600/effective_step:.1f}个")
    
    # 给出性能建议
    if memory_mb > 100:
        print(f"  ⚠ 内存使用较高，建议减少分箱数量")
    if 3600/effective_step > 10:
        print(f"  ⚠ 窗口密度较高，建议增大时间步长")


def main():
    """主函数"""
    print("PPSD配置参数优化建议报告")
    print("=" * 50)
    
    # 分析数据特性
    data_characteristics = analyze_data_characteristics()
    if not data_characteristics:
        return
    
    # 加载当前配置
    current_config = load_current_config()
    if not current_config:
        return
    
    # 生成优化建议
    recommendations = generate_optimization_recommendations(
        data_characteristics, current_config)
    
    # 性能估算
    performance_estimation(current_config)
    
    # 生成优化配置
    if recommendations:
        generate_optimized_config(current_config, recommendations)
    
    print("\n" + "=" * 50)
    print("配置优化分析完成！")
    
    if recommendations:
        print(f"\n发现 {len(recommendations)} 项优化建议")
        print("请查看生成的 input/config_optimized.toml 文件")
        print("测试命令: python run_cp_ppsd.py input/config_optimized.toml")
    else:
        print("\n当前配置已经很好，无需优化")


if __name__ == '__main__':
    main() 