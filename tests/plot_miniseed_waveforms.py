#!/usr/bin/env python3
"""
BJ台网MinISEED数据波形图绘制工具

使用ObsPy读取和绘制data目录下的miniseed文件数据波形。

功能特点：
- 自动检测data目录下的miniseed文件
- 生成单个台站波形图
- 生成多台站对比波形图
- 支持时间域和频谱分析
- 保存高质量PNG图像

Author: AI Assistant
Date: 2025-01-30
"""

import os
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from obspy import read, UTCDateTime
import matplotlib
import numpy as np
from datetime import datetime

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


def plot_single_waveform(st, station_info, output_dir):
    """
    绘制单个台站的波形图
    
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
        # 创建图形
        fig, axes = plt.subplots(len(st), 1, figsize=(15, 3*len(st)))
        if len(st) == 1:
            axes = [axes]
        
        station_name = station_info['station']
        network = station_info['network']
        
        fig.suptitle(f'{network}.{station_name} Waveform Data', 
                     fontsize=16, fontweight='bold')
        
        for i, tr in enumerate(st):
            # 绘制波形
            times = tr.times('matplotlib')
            axes[i].plot(times, tr.data, 'b-', linewidth=0.8)
            
            # 设置标题和标签
            channel_id = f"{tr.stats.network}.{tr.stats.station}.{tr.stats.location}.{tr.stats.channel}"
            axes[i].set_title(f'Channel: {channel_id}')
            axes[i].set_ylabel('Amplitude (counts)')
            
            # 格式化时间轴
            axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            axes[i].xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
            
            # 添加网格
            axes[i].grid(True, alpha=0.3)
            
            # 显示采样率和数据点数
            sampling_rate = tr.stats.sampling_rate
            npts = tr.stats.npts
            duration = npts / sampling_rate
            
            info_text = (f'Sampling Rate: {sampling_rate} Hz, '
                        f'Points: {npts}, Duration: {duration:.1f}s')
            axes[i].text(0.02, 0.95, info_text, transform=axes[i].transAxes,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                        verticalalignment='top', fontsize=9)
        
        # 设置最后一个子图的x轴标签
        axes[-1].set_xlabel('Time (UTC)')
        
        # 旋转x轴标签
        for ax in axes:
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # 保存图像
        output_file = os.path.join(output_dir, f"{network}_{station_name}_waveform.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"  Waveform plot saved: {output_file}")
        
        plt.close(fig)
        return True
        
    except Exception as e:
        print(f"  Error plotting waveform for {station_info['station']}: {e}")
        return False


def plot_multi_station_comparison(streams_dict, output_dir):
    """
    绘制多台站波形对比图
    
    Parameters:
    -----------
    streams_dict : dict
        包含多个台站数据流的字典
    output_dir : str
        输出目录
    """
    try:
        # 计算需要的子图数量
        total_traces = sum(len(st) for st in streams_dict.values())
        
        # 创建图形
        fig, axes = plt.subplots(total_traces, 1, figsize=(18, 2.5*total_traces))
        if total_traces == 1:
            axes = [axes]
        
        fig.suptitle('BJ Network Multi-Station Waveform Comparison', 
                     fontsize=16, fontweight='bold')
        
        ax_idx = 0
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink']
        
        for i, (station, st) in enumerate(sorted(streams_dict.items())):
            color = colors[i % len(colors)]
            
            for tr in st:
                # 绘制波形
                times = tr.times('matplotlib')
                axes[ax_idx].plot(times, tr.data, color=color, linewidth=0.8)
                
                # 设置标题
                channel_id = f"{tr.stats.network}.{tr.stats.station}.{tr.stats.location}.{tr.stats.channel}"
                axes[ax_idx].set_title(f'{channel_id}', fontsize=12)
                axes[ax_idx].set_ylabel('Amplitude', fontsize=10)
                
                # 格式化时间轴
                axes[ax_idx].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                axes[ax_idx].xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
                
                # 添加网格
                axes[ax_idx].grid(True, alpha=0.3)
                
                # 添加台站信息
                info_text = f"Station: {tr.stats.station}, SR: {tr.stats.sampling_rate} Hz"
                axes[ax_idx].text(0.02, 0.95, info_text, transform=axes[ax_idx].transAxes,
                                 bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
                                 verticalalignment='top', fontsize=8)
                
                ax_idx += 1
        
        # 设置最后一个子图的x轴标签
        axes[-1].set_xlabel('Time (UTC)', fontsize=12)
        
        # 旋转x轴标签
        for ax in axes:
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # 保存对比图
        comparison_file = os.path.join(output_dir, "BJ_multi_station_waveform_comparison.png")
        plt.savefig(comparison_file, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print(f"  Multi-station comparison plot saved: {comparison_file}")
        
        plt.close(fig)
        return True
        
    except Exception as e:
        print(f"  Error plotting multi-station comparison: {e}")
        return False


def plot_frequency_spectrum(st, station_info, output_dir):
    """
    绘制频谱图
    
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
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            channel_id = f"{tr.stats.network}.{tr.stats.station}.{tr.stats.location}.{tr.stats.channel}"
            fig.suptitle(f'{channel_id} Waveform and Frequency Spectrum', 
                         fontsize=14, fontweight='bold')
            
            # 上图：时域波形
            times = tr.times('matplotlib')
            ax1.plot(times, tr.data, 'b-', linewidth=0.8)
            ax1.set_title('Waveform (Time Domain)')
            ax1.set_ylabel('Amplitude (counts)')
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            
            # 下图：频域谱
            # 计算FFT
            dt = tr.stats.delta
            npts = tr.stats.npts
            freqs = np.fft.fftfreq(npts, dt)[:npts//2]
            fft_data = np.abs(np.fft.fft(tr.data))[:npts//2]
            
            ax2.loglog(freqs[1:], fft_data[1:], 'r-', linewidth=1)
            ax2.set_title('Frequency Spectrum')
            ax2.set_xlabel('Frequency (Hz)')
            ax2.set_ylabel('Amplitude')
            ax2.grid(True, alpha=0.3)
            
            # 添加信息
            info_text = (f'Sampling Rate: {tr.stats.sampling_rate} Hz\n'
                        f'Duration: {npts * dt:.1f}s\n'
                        f'Start Time: {tr.stats.starttime}')
            ax1.text(0.02, 0.98, info_text, transform=ax1.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                    verticalalignment='top', fontsize=9)
            
            plt.tight_layout()
            
            # 保存频谱图
            spectrum_file = os.path.join(output_dir, 
                                       f"{network}_{station_name}_{tr.stats.channel}_spectrum.png")
            plt.savefig(spectrum_file, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"  Spectrum plot saved: {spectrum_file}")
            
            plt.close(fig)
            
    except Exception as e:
        print(f"  Error plotting spectrum for {station_info['station']}: {e}")


def main():
    """
    主函数：绘制miniseed数据波形图
    """
    print("=" * 70)
    print("BJ Network MinISEED Waveform Plotting Tool")
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
    
    # 读取数据并绘制波形
    print(f"\n=== Processing Individual Station Waveforms ===")
    streams_dict = {}
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
            
            # 存储数据流用于对比图
            streams_dict[station_name] = st
            
            # 绘制单个台站波形图
            if plot_single_waveform(st, station_info, output_dir):
                successful_plots += 1
            
            # 绘制频谱图（可选）
            plot_frequency_spectrum(st, station_info, output_dir)
            
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
            continue
    
    print(f"\nSuccessfully processed {successful_plots} stations")
    
    # 绘制多台站对比图
    if streams_dict:
        print(f"\n=== Creating Multi-Station Comparison ===")
        plot_multi_station_comparison(streams_dict, output_dir)
    
    # 生成报告
    print(f"\n=== Processing Complete ===")
    print(f"Total files processed: {len(mseed_files)}")
    print(f"Successful waveform plots: {successful_plots}")
    print(f"Stations in comparison: {len(streams_dict)}")
    print(f"All plots saved in: {output_dir}")
    
    # 列出生成的文件
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
        if files:
            print(f"\nGenerated files:")
            for file in sorted(files):
                file_path = os.path.join(output_dir, file)
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"  {file} ({file_size:.1f} KB)")


if __name__ == "__main__":
    main() 