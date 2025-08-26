#!/usr/bin/env python3
"""
Author:
    muly (muly@cea-igp.ac.cn)
license:
    MIT License
    (https://opensource.org/licenses/MIT)

PPSD NPZ文件内容解析脚本
基于ObsPy官方文档：https://docs.obspy.org/master/packages/autogen/obspy.signal.spectral_estimation.PPSD.html

参考PPSD类的NPZ存储键值：
- NPZ_STORE_KEYS: 所有存储的键值
- NPZ_STORE_KEYS_SIMPLE_TYPES: 简单类型键值
- NPZ_STORE_KEYS_ARRAY_TYPES: 数组类型键值
- NPZ_STORE_KEYS_LIST_TYPES: 列表类型键值
"""

import numpy as np
import os
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非交互式后端


def analyze_npz_file(npz_filepath: str) -> dict:
    """
    解析单个NPZ文件内容
    
    Parameters:
    -----------
    npz_filepath : str
        NPZ文件路径
        
    Returns:
    --------
    dict : 解析结果字典
    """
    if not os.path.exists(npz_filepath):
        raise FileNotFoundError(f"NPZ文件不存在: {npz_filepath}")
    
    print(f"\n{'='*80}")
    print(f"解析NPZ文件: {os.path.basename(npz_filepath)}")
    print(f"{'='*80}")
    
    # 加载NPZ文件
    npz_data = np.load(npz_filepath, allow_pickle=True)
    
    analysis_result = {
        'filepath': npz_filepath,
        'file_size_mb': os.path.getsize(npz_filepath) / (1024*1024),
        'keys': list(npz_data.keys()),
        'metadata': {},
        'arrays': {},
        'statistics': {}
    }
    
    print(f"文件大小: {analysis_result['file_size_mb']:.2f} MB")
    print(f"包含键值数量: {len(analysis_result['keys'])}")
    print(f"所有键值: {analysis_result['keys']}")
    
    # 根据ObsPy PPSD文档分析各个键值
    for key in npz_data.keys():
        data = npz_data[key]
        print(f"\n--- 键值: {key} ---")
        print(f"数据类型: {type(data)}")
        
        if isinstance(data, np.ndarray):
            print(f"数组形状: {data.shape}")
            print(f"数组数据类型: {data.dtype}")
            if data.size > 0:
                if np.issubdtype(data.dtype, np.number):
                    print(f"数值范围: [{np.min(data):.6f}, {np.max(data):.6f}]")
                    print(f"均值: {np.mean(data):.6f}")
                    print(f"标准差: {np.std(data):.6f}")
                print(f"前5个元素: {data.flat[:5] if data.size >= 5 else data.flat[:]}")
            analysis_result['arrays'][key] = {
                'shape': data.shape,
                'dtype': str(data.dtype),
                'size': data.size
            }
        else:
            print(f"数据内容: {data}")
            analysis_result['metadata'][key] = data
    
    # 特定键值的详细分析（基于ObsPy PPSD文档）
    print(f"\n{'='*60}")
    print("PPSD核心数据分析")
    print(f"{'='*60}")
    
    # 台站信息
    if 'network' in npz_data and 'station' in npz_data:
        network = npz_data['network'].item() if hasattr(npz_data['network'], 'item') else npz_data['network']
        station = npz_data['station'].item() if hasattr(npz_data['station'], 'item') else npz_data['station']
        location = npz_data['location'].item() if 'location' in npz_data else ""
        channel = npz_data['channel'].item() if 'channel' in npz_data else ""
        print(f"台站标识: {network}.{station}.{location}.{channel}")
    
    # 频率/周期信息
    if 'period_bin_centers' in npz_data:
        periods = npz_data['period_bin_centers']
        print(f"周期范围: {np.min(periods):.4f} - {np.max(periods):.4f} 秒")
        print(f"周期分箱数量: {len(periods)}")
        
    if 'psd_frequencies' in npz_data:
        frequencies = npz_data['psd_frequencies']
        print(f"频率范围: {np.min(frequencies):.6f} - {np.max(frequencies):.6f} Hz")
    
    # dB分箱信息
    if 'db_bin_edges' in npz_data:
        db_edges = npz_data['db_bin_edges']
        print(f"dB分箱范围: {np.min(db_edges):.1f} - {np.max(db_edges):.1f} dB")
        print(f"dB分箱数量: {len(db_edges)-1}")
        
    if 'db_bin_centers' in npz_data:
        db_centers = npz_data['db_bin_centers']
        print(f"dB中心值范围: {np.min(db_centers):.1f} - {np.max(db_centers):.1f} dB")
    
    # 直方图数据
    if 'current_histogram' in npz_data:
        histogram = npz_data['current_histogram']
        print(f"PPSD直方图形状: {histogram.shape}")
        print(f"直方图数据范围: {np.min(histogram):.6f} - {np.max(histogram):.6f}")
        print(f"非零元素数量: {np.count_nonzero(histogram)}")
        total_probability = np.sum(histogram)
        print(f"总概率: {total_probability:.6f}")
        
        analysis_result['statistics']['histogram_shape'] = histogram.shape
        analysis_result['statistics']['total_probability'] = total_probability
        analysis_result['statistics']['non_zero_bins'] = int(np.count_nonzero(histogram))
    
    # 时间信息
    if 'times_processed' in npz_data:
        times = npz_data['times_processed']
        print(f"处理的时间段数量: {len(times)}")
        if len(times) > 0:
            # 转换时间戳
            start_time = datetime.fromtimestamp(times[0])
            end_time = datetime.fromtimestamp(times[-1])
            print(f"时间范围: {start_time} - {end_time}")
            duration_hours = (times[-1] - times[0]) / 3600
            print(f"数据持续时间: {duration_hours:.2f} 小时")
            
            analysis_result['statistics']['time_segments'] = len(times)
            analysis_result['statistics']['duration_hours'] = duration_hours
    
    # 数据覆盖度
    if 'times_data' in npz_data and 'times_gaps' in npz_data:
        data_times = npz_data['times_data']
        gap_times = npz_data['times_gaps']
        print(f"数据时间段: {len(data_times)}")
        print(f"间隙时间段: {len(gap_times)}")
    
    npz_data.close()
    return analysis_result


def create_summary_visualization(analysis_results: list):
    """
    创建NPZ文件分析结果的汇总可视化
    
    Parameters:
    -----------
    analysis_results : list
        多个NPZ文件的分析结果列表
    """
    if not analysis_results:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('PPSD NPZ文件内容分析汇总', fontsize=16, fontweight='bold')
    
    # 提取数据
    stations = []
    file_sizes = []
    time_segments = []
    duration_hours = []
    total_probabilities = []
    
    for result in analysis_results:
        # 从文件名提取台站信息
        filename = os.path.basename(result['filepath'])
        station_part = filename.split('_')[-1].replace('.npz', '')
        stations.append(station_part)
        
        file_sizes.append(result['file_size_mb'])
        
        if 'time_segments' in result['statistics']:
            time_segments.append(result['statistics']['time_segments'])
        else:
            time_segments.append(0)
            
        if 'duration_hours' in result['statistics']:
            duration_hours.append(result['statistics']['duration_hours'])
        else:
            duration_hours.append(0)
            
        if 'total_probability' in result['statistics']:
            total_probabilities.append(result['statistics']['total_probability'])
        else:
            total_probabilities.append(0)
    
    # 子图1: 文件大小对比
    axes[0, 0].bar(range(len(stations)), file_sizes, color='skyblue', alpha=0.7)
    axes[0, 0].set_title('NPZ文件大小对比')
    axes[0, 0].set_ylabel('文件大小 (MB)')
    axes[0, 0].set_xticks(range(len(stations)))
    axes[0, 0].set_xticklabels(stations, rotation=45, ha='right')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 子图2: 时间段数量对比
    axes[0, 1].bar(range(len(stations)), time_segments, color='lightgreen', alpha=0.7)
    axes[0, 1].set_title('处理时间段数量对比')
    axes[0, 1].set_ylabel('时间段数量')
    axes[0, 1].set_xticks(range(len(stations)))
    axes[0, 1].set_xticklabels(stations, rotation=45, ha='right')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 子图3: 数据持续时间对比
    axes[1, 0].bar(range(len(stations)), duration_hours, color='orange', alpha=0.7)
    axes[1, 0].set_title('数据持续时间对比')
    axes[1, 0].set_ylabel('持续时间 (小时)')
    axes[1, 0].set_xticks(range(len(stations)))
    axes[1, 0].set_xticklabels(stations, rotation=45, ha='right')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 子图4: 总概率对比
    axes[1, 1].bar(range(len(stations)), total_probabilities, color='pink', alpha=0.7)
    axes[1, 1].set_title('PPSD直方图总概率对比')
    axes[1, 1].set_ylabel('总概率')
    axes[1, 1].set_xticks(range(len(stations)))
    axes[1, 1].set_xticklabels(stations, rotation=45, ha='right')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = 'npz_analysis_summary.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n汇总可视化图已保存: {output_path}")

def main():
    """主函数"""
    npz_dir = "./output/npz/"
    
    if not os.path.exists(npz_dir):
        print(f"错误: NPZ目录不存在: {npz_dir}")
        return
    
    # 查找所有NPZ文件
    npz_files = list(Path(npz_dir).glob("*.npz"))
    
    if not npz_files:
        print(f"错误: 在 {npz_dir} 中未找到NPZ文件")
        return
    
    print(f"找到 {len(npz_files)} 个NPZ文件")
    
    # 分析每个NPZ文件
    analysis_results = []
    for npz_file in sorted(npz_files):
        try:
            result = analyze_npz_file(str(npz_file))
            analysis_results.append(result)
        except Exception as e:
            print(f"分析文件 {npz_file} 时出错: {e}")
    
    # 创建汇总可视化
    if analysis_results:
        create_summary_visualization(analysis_results)
    
    # 输出总结
    print(f"\n{'='*80}")
    print("NPZ文件分析总结")
    print(f"{'='*80}")
    print(f"成功分析的文件数量: {len(analysis_results)}")
    
    if analysis_results:
        total_size = sum(r['file_size_mb'] for r in analysis_results)
        print(f"总文件大小: {total_size:.2f} MB")
        
        total_segments = sum(r['statistics'].get('time_segments', 0) for r in analysis_results)
        print(f"总时间段数量: {total_segments}")
        
        avg_duration = np.mean([r['statistics'].get('duration_hours', 0) for r in analysis_results])
        print(f"平均数据持续时间: {avg_duration:.2f} 小时")
    
    print("\n基于ObsPy PPSD文档的NPZ文件结构:")
    print("- network, station, location, channel: 台站标识信息")
    print("- period_bin_centers, period_bin_left_edges, period_bin_right_edges: 周期分箱")
    print("- db_bin_centers, db_bin_edges: dB分箱")
    print("- current_histogram: PPSD概率密度直方图矩阵")
    print("- times_processed: 处理的时间段时间戳")
    print("- times_data, times_gaps: 数据和间隙时间信息")
    print("- psd_frequencies, psd_periods: 功率谱密度频率和周期")

if __name__ == "__main__":
    main() 
