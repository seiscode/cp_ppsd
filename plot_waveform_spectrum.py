#!/usr/bin/env python3
"""
:Author: 
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
"""
BJ台网MinISEED数据波形+频谱+频谱图绘制工具

优化的版本，显著提高绘图速度：
- 优化图像尺寸和分辨率
- 数据采样以减少绘图点数
- 优化频谱图计算
- 高效渲染选项

功能特点：
- 自动检测指定目录下的miniseed文件
- 上面显示时域波形图（采样优化）
- 中间显示频域频谱图（FFT优化）
- 下面显示时频频谱图
- 保存优化尺寸PNG图像

使用方法：
    python plot_waveform_spectrum.py [data_directory]
    
参数：
    data_directory: miniseed文件所在目录（可选，默认为./data）

Date: 2025-01-30
"""

import os
import glob
import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import numpy as np
from obspy import read
import time
from mpl_toolkits.axes_grid1 import make_axes_locatable

# 设置非交互式后端
matplotlib.use('Agg')

# 配置字体和显示 - 优化设置
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 9  # 减小字体
plt.rcParams['figure.titlesize'] = 12  # 减小标题字体

# 性能优化配置
PERFORMANCE_MODE = {
    'fast': {
        'figsize': (10, 12),  # 减小图像尺寸
        'dpi': 150,          # 降低分辨率
        'max_points': 10000,  # 最大绘图点数
        'fft_max_points': 8192,  # FFT最大点数
        'specgram_nfft': 512,    # 频谱图窗口大小
        'rasterized': True       # 使用光栅化
    },
    'quality': {
        'figsize': (12, 14),
        'dpi': 200,
        'max_points': 50000,
        'fft_max_points': 16384,
        'specgram_nfft': 1024,
        'rasterized': False
    }
}


def find_miniseed_files(data_dir):
    """查找数据目录下的miniseed文件"""
    mseed_patterns = ['*.mseed', '*.miniseed', '*.ms']
    files = []
    
    for pattern in mseed_patterns:
        files.extend(glob.glob(os.path.join(data_dir, pattern)))
    
    return sorted(files)


def extract_station_info(filename):
    """从文件名提取台站信息"""
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


def downsample_for_plot(data, times, max_points):
    """数据采样以优化绘图性能"""
    if len(data) <= max_points:
        return data, times
    
    # 计算采样步长
    step = len(data) // max_points
    indices = np.arange(0, len(data), step)
    
    return data[indices], times[indices] if times is not None else None


def optimize_fft(data, max_points):
    """优化FFT计算"""
    if len(data) > max_points:
        # 采样数据用于FFT
        step = len(data) // max_points
        data = data[::step]
    
    return data


def detect_and_fill_gaps(st):
    """
    检测并填充数据间隙(gaps)
    
    Parameters:
    -----------
    st : obspy.Stream
        地震数据流
        
    Returns:
    --------
    st : obspy.Stream
        处理后的数据流
    gaps_info : list
        间隙信息列表
    """
    gaps_info = []
    
    # 首先检测gaps
    try:
        gaps = st.get_gaps()
        if gaps:
            print(f"  Detected {len(gaps)} gaps:")
            for gap in gaps:
                # 处理不同格式的gap信息
                if len(gap) == 7:
                    network, station, location, channel, start_time, end_time, duration = gap
                elif len(gap) >= 6:
                    network, station, location, channel, start_time, end_time = gap[:6]
                    duration = (end_time - start_time) if len(gap) < 7 else gap[6]
                else:
                    print(f"    Unexpected gap format: {gap}")
                    continue
                    
                gaps_info.append({
                    'id': f"{network}.{station}.{location}.{channel}",
                    'start': start_time,
                    'end': end_time,
                    'duration': duration
                })
                print(f"    {network}.{station}.{location}.{channel}: "
                      f"{start_time} to {end_time} "
                      f"(duration: {duration:.2f}s)")
        else:
            print("  No gaps detected")
            
    except Exception as e:
        print(f"  Warning: Could not detect gaps: {e}")
    
    # 使用ObsPy的merge方法进行补零操作
    try:
        original_traces = len(st)
        print(f"  Original traces: {original_traces}")
        
        # 补零合并 - 使用method=0和fill_value=0
        st.merge(method=0, fill_value=0)
        
        merged_traces = len(st)
        print(f"  After gap filling: {merged_traces} traces")
        
        if gaps_info:
            print(f"  ✓ Filled {len(gaps_info)} gaps with zeros")
        
        return st, gaps_info
        
    except Exception as e:
        print(f"  Error during gap filling: {e}")
        # 如果补零失败，使用快速合并作为备选
        st.merge(method=-1)
        return st, gaps_info


def plot_waveform_and_spectrum(st, station_info, output_dir, mode='fast', gaps_info=None):
    """
    绘制波形图（上）、频谱图（中）和频谱图（下）
    
    Parameters:
    -----------
    st : obspy.Stream
        地震数据流
    station_info : dict
        台站信息
    output_dir : str
        输出目录
    mode : str
        性能模式 ('fast' 或 'quality')
    gaps_info : list
        间隙信息列表
    """
    try:
        start_time = time.time()
        config = PERFORMANCE_MODE[mode]
        
        station_name = station_info['station']
        network = station_info['network']
        
        print(f"    Performance mode: {mode}")
        print(f"    Image size: {config['figsize']}, DPI: {config['dpi']}")
        
        # 为每个通道绘制组合图
        for tr in st:
            # 创建包含三个子图的图形 - 优化尺寸
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=config['figsize'])
            
            channel_id = f"{tr.stats.network}.{tr.stats.station}.{tr.stats.location}.{tr.stats.channel}"
            fig.suptitle(f'{channel_id} Waveform + Spectrum + Spectrogram', 
                         fontsize=12, fontweight='bold')
            
            # 数据预处理
            dt = tr.stats.delta
            npts = tr.stats.npts
            
            # 上图：时域波形 - 采样优化
            times = tr.times('matplotlib')
            data_plot, times_plot = downsample_for_plot(tr.data, times, config['max_points'])
            
            print(f"    Waveform points: {len(data_plot):,} (original: {npts:,})")
            
            ax1.plot(times_plot, data_plot, 'b-', linewidth=0.5, 
                    rasterized=config['rasterized'])
            ax1.set_title('Time Domain Waveform (Optimized)', fontsize=11)
            ax1.set_ylabel('Amplitude', fontsize=10)
            ax1.grid(True, alpha=0.3)
            
            # 简化时间轴格式
            if len(times_plot) > 0:
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            
            # 中图：频域谱 - FFT优化
            data_fft = optimize_fft(tr.data, config['fft_max_points'])
            freqs = np.fft.fftfreq(len(data_fft), dt)[:len(data_fft)//2]
            fft_data = np.abs(np.fft.fft(data_fft))[:len(data_fft)//2]
            
            print(f"    FFT points: {len(data_fft):,}")
            
            # 过滤零频率
            valid_indices = freqs > 1e-6
            freqs_valid = freqs[valid_indices]
            fft_valid = fft_data[valid_indices]
            
            # 频谱采样以减少绘图点数
            if len(freqs_valid) > 5000:
                step = len(freqs_valid) // 5000
                freqs_valid = freqs_valid[::step]
                fft_valid = fft_valid[::step]
            
            ax2.loglog(freqs_valid, fft_valid, 'r-', linewidth=0.8, 
                      rasterized=config['rasterized'])
            ax2.set_title('Frequency Spectrum (Optimized)', fontsize=11)
            ax2.set_xlabel('Frequency (Hz)', fontsize=10)
            ax2.set_ylabel('Amplitude', fontsize=10)
            ax2.grid(True, alpha=0.3, which='both')
            
            # 下图：频谱图
            print(f"    Spectrogram NFFT: {config['specgram_nfft']}")
            
            # 使用matplotlib的specgram（比ObsPy快）
            Pxx, freqs_spec, bins, im = ax3.specgram(
                tr.data, 
                Fs=tr.stats.sampling_rate,
                NFFT=config['specgram_nfft'], 
                noverlap=config['specgram_nfft']//2,
                cmap='viridis',
                rasterized=config['rasterized']
            )
            
            ax3.set_title('Spectrogram', fontsize=11)
            ax3.set_xlabel('Time (s)', fontsize=10)
            ax3.set_ylabel('Frequency (Hz)', fontsize=10)
            ax3.set_yscale('log')
            # 设置频率轴最大值为50Hz
            ax3.set_ylim(bottom=0.1, top=50)
            
            # 精确控制颜色条位置，使其右边缘与上面图对齐
            divider = make_axes_locatable(ax3)
            cax = divider.append_axes("right", size="2%", pad=0.05)
            cbar = plt.colorbar(im, cax=cax)
            cbar.set_label('Power', fontsize=9)
            
            # 简化信息框
            gaps_text = f" | Gaps: {len(gaps_info) if gaps_info else 0}"
            info_text = (f'Station: {tr.stats.station} | '
                        f'Channel: {tr.stats.channel} | '
                        f'SR: {tr.stats.sampling_rate}Hz\n'
                        f'Duration: {npts * dt:.1f}s | '
                        f'Points: {npts:,} | '
                        f'Mode: {mode}{gaps_text}')
            
            ax1.text(0.02, 0.98, info_text, transform=ax1.transAxes,
                    bbox=dict(boxstyle="round,pad=0.2", 
                             facecolor="white", alpha=0.8),
                    verticalalignment='top', fontsize=8)
            
            # 使用标准布局
            plt.tight_layout()
            
            # 保存优化图像
            start_time_str = tr.stats.starttime.strftime("%Y%m%d_%H%M%S")
            combined_file = os.path.join(output_dir, 
                                       f"{network}_{station_name}_{tr.stats.channel}_{start_time_str}.png")
            
            plt.savefig(combined_file, dpi=config['dpi'], bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            
            plt.close(fig)
            
            elapsed = time.time() - start_time
            print(f"    Plot completed in {elapsed:.2f}s: {os.path.basename(combined_file)}")
            
    except Exception as e:
        print(f"  Error plotting for {station_info['station']}: {e}")


def main():
    """主函数：波形频谱绘图工具"""
    parser = argparse.ArgumentParser(
        description='BJ台网MinISEED数据波形+频谱+频谱图绘制工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
    python plot_waveform_spectrum.py                    # 快速模式
    python plot_waveform_spectrum.py -q                 # 质量模式
    python plot_waveform_spectrum.py /path/to/mseed     # 指定数据目录
        """
    )
    
    parser.add_argument('data_directory', 
                       nargs='?', 
                       default='./data',
                       help='MinISEED文件所在目录 (默认: ./data)')
    
    parser.add_argument('-o', '--output', 
                       default='./output/waveforms',
                       help='输出图片目录 (默认: ./output/waveforms)')
    
    parser.add_argument('-q', '--quality', 
                       action='store_true',
                       help='使用质量模式（较慢但图像质量更好）')
    
    args = parser.parse_args()
    
    mode = 'quality' if args.quality else 'fast'
    
    print("=" * 70)
    print("BJ Network MinISEED Waveform + Spectrum + Spectrogram Tool")
    print("=" * 70)
    print(f"Performance mode: {mode.upper()}")
    
    data_dir = args.data_directory
    output_dir = args.output
    
    print(f"Data directory: {data_dir}")
    print(f"Output directory: {output_dir}")
    
    if not os.path.exists(data_dir):
        print(f"Error: Data directory {data_dir} not found")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    mseed_files = find_miniseed_files(data_dir)
    
    if not mseed_files:
        print(f"No miniseed files found in {data_dir}")
        return
    
    print(f"\nFound {len(mseed_files)} miniseed files:")
    for file in mseed_files:
        file_size = os.path.getsize(file) / (1024*1024)
        print(f"  {os.path.basename(file)} ({file_size:.1f} MB)")
    
    print(f"\n=== Processing with {mode.upper()} mode ===")
    total_start = time.time()
    successful_plots = 0
    
    for file_path in mseed_files:
        try:
            file_start = time.time()
            print(f"\nProcessing: {os.path.basename(file_path)}")
            
            st = read(file_path)
            print(f"  Read {len(st)} traces")
            
            # 检测gaps并补零填充
            st, gaps_info = detect_and_fill_gaps(st)
            
            station_info = extract_station_info(file_path)
            
            for tr in st:
                print(f"    {tr.id}: {tr.stats.npts} points, {tr.stats.sampling_rate} Hz")
            
            plot_waveform_and_spectrum(st, station_info, output_dir, mode, gaps_info)
            successful_plots += 1
            
            file_elapsed = time.time() - file_start
            print(f"  File processed in {file_elapsed:.2f}s")
            
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
            continue
    
    total_elapsed = time.time() - total_start
    
    print("\n=== Performance Summary ===")
    print(f"Total processing time: {total_elapsed:.2f}s")
    print(f"Average time per file: {total_elapsed/len(mseed_files):.2f}s")
    print(f"Successful plots: {successful_plots}/{len(mseed_files)}")
    print(f"Performance mode: {mode}")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main() 