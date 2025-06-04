#!/usr/bin/env python3
"""
BJ台网MinISEED数据频谱图绘制工具

仅绘制频谱分析图，不生成波形图。
频谱图横轴使用对数坐标显示。

功能特点：
- 自动检测data目录下的miniseed文件
- 只生成频谱分析图（不生成波形图）
- 频谱图横轴使用对数坐标
- 保存高质量PNG图像

Author: AI Assistant  
Date: 2025-01-30
"""

import os
import glob
import matplotlib.pyplot as plt
from obspy import read
import matplotlib
import numpy as np

# 设置非交互式后端
matplotlib.use('Agg')

# 配置字体和显示
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10
plt.rcParams['figure.titlesize'] = 14


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
        'filename': basename
    }
    
    return info


def plot_frequency_spectrum_only(st, station_info, output_dir):
    """
    仅绘制频谱图，横轴使用对数坐标
    
    Parameters:
    -----------
    st : obspy.Stream
        地震数据流
    station_info : dict
        台站信息
    output_dir : str
        输出目录
    """
    try:
        station_name = station_info['station']
        network = station_info['network']
        
        # 为每个通道绘制频谱
        for tr in st:
            # 只创建一个子图用于频谱
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            
            channel_id = f"{tr.stats.network}.{tr.stats.station}.{tr.stats.location}.{tr.stats.channel}"
            fig.suptitle(f'{channel_id} Frequency Spectrum (Log Scale)', 
                         fontsize=14, fontweight='bold')
            
            # 计算FFT
            dt = tr.stats.delta
            npts = tr.stats.npts
            freqs = np.fft.fftfreq(npts, dt)[:npts//2]
            fft_data = np.abs(np.fft.fft(tr.data))[:npts//2]
            
            # 过滤零频率分量和极低频率
            valid_indices = freqs > 1e-6  # 避免log(0)
            freqs_valid = freqs[valid_indices]
            fft_valid = fft_data[valid_indices]
            
            # 绘制频谱图，横轴和纵轴都使用对数坐标
            ax.loglog(freqs_valid, fft_valid, 'r-', linewidth=1.2, alpha=0.8)
            
            ax.set_title(f'Frequency Spectrum - {channel_id}', fontsize=12)
            ax.set_xlabel('Frequency (Hz)', fontsize=11)
            ax.set_ylabel('Amplitude (counts)', fontsize=11)
            ax.grid(True, alpha=0.3, which='both')
            
            # 设置坐标轴范围
            ax.set_xlim([max(freqs_valid.min(), 1e-3), freqs_valid.max()])
            
            # 添加台站详细信息
            info_text = (f'Station: {tr.stats.station}\n'
                        f'Channel: {tr.stats.channel}\n'
                        f'Sampling Rate: {tr.stats.sampling_rate} Hz\n'
                        f'Duration: {npts * dt:.1f}s\n'
                        f'Data Points: {npts:,}\n'
                        f'Start Time: {tr.stats.starttime.strftime("%Y-%m-%d %H:%M:%S")}')
            
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9),
                    verticalalignment='top', fontsize=9, 
                    fontfamily='monospace')
            
            # 添加频率标记线
            # 标记一些重要频率
            important_freqs = [0.01, 0.1, 1, 10]  # Hz
            for freq in important_freqs:
                if freq >= freqs_valid.min() and freq <= freqs_valid.max():
                    ax.axvline(x=freq, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
                    ax.text(freq, ax.get_ylim()[1]*0.8, f'{freq} Hz', 
                           rotation=90, fontsize=8, alpha=0.7, 
                           verticalalignment='top', horizontalalignment='right')
            
            plt.tight_layout()
            
            # 保存频谱图
            spectrum_file = os.path.join(output_dir, 
                                       f"{network}_{station_name}_{tr.stats.channel}_spectrum_log.png")
            plt.savefig(spectrum_file, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"  Spectrum plot saved: {spectrum_file}")
            
            plt.close(fig)
            
    except Exception as e:
        print(f"  Error plotting spectrum for {station_info['station']}: {e}")


def main():
    """
    主函数：只绘制miniseed数据频谱图
    """
    print("=" * 70)
    print("BJ Network MinISEED Frequency Spectrum Tool (Log Scale)")
    print("=" * 70)
    
    # 数据目录
    data_dir = "../data"
    output_dir = "../output/plots"
    
    # 检查数据目录
    if not os.path.exists(data_dir):
        print(f"Error: Data directory {data_dir} not found")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # 查找miniseed文件
    mseed_files = find_miniseed_files(data_dir)
    
    if not mseed_files:
        print(f"No miniseed files found in {data_dir}")
        return
    
    print(f"\nFound {len(mseed_files)} miniseed files:")
    for file in mseed_files:
        file_size = os.path.getsize(file) / (1024*1024)  # MB
        print(f"  {os.path.basename(file)} ({file_size:.1f} MB)")
    
    # 读取数据并绘制频谱图
    print(f"\n=== Processing Frequency Spectrum Analysis ===")
    successful_plots = 0
    
    for file_path in mseed_files:
        try:
            print(f"\nProcessing: {os.path.basename(file_path)}")
            
            # 读取数据
            st = read(file_path)
            print(f"  Read {len(st)} traces")
            
            # 提取台站信息
            station_info = extract_station_info(file_path)
            station_name = station_info['station']
            
            # 显示数据信息
            for tr in st:
                print(f"    {tr.id}: {tr.stats.starttime} - {tr.stats.endtime}, "
                      f"{tr.stats.sampling_rate} Hz, {tr.stats.npts} points")
            
            # 绘制频谱图
            plot_frequency_spectrum_only(st, station_info, output_dir)
            successful_plots += 1
            
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
            continue
    
    # 生成报告
    print(f"\n=== Processing Complete ===")
    print(f"Total files processed: {len(mseed_files)}")
    print(f"Successful spectrum plots: {successful_plots}")
    print(f"All plots saved in: {output_dir}")
    
    # 列出生成的频谱图文件
    if os.path.exists(output_dir):
        spectrum_files = [f for f in os.listdir(output_dir) if f.endswith('_spectrum_log.png')]
        if spectrum_files:
            print(f"\nGenerated spectrum files:")
            for file in sorted(spectrum_files):
                file_path = os.path.join(output_dir, file)
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"  {file} ({file_size:.1f} KB)")


if __name__ == "__main__":
    main() 