#!/usr/bin/env python3
"""
:Author: 
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
"""
从PPSD NPZ文件中提取所有PSD值并在频率-dB坐标系中绘制
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import os
from datetime import datetime
from obspy.signal.spectral_estimation import PPSD
from obspy import read_inventory
from typing import Optional, Dict

# 设置非交互式后端
matplotlib.use('Agg')


def setup_chinese_fonts():
    """
    设置中文字体支持
    """
    # 尝试多种中文字体配置方案
    font_options = [
        # Linux系统常见中文字体
        'WenQuanYi Micro Hei',
        'WenQuanYi Zen Hei', 
        'Noto Sans CJK SC',
        'Source Han Sans CN',
        'DejaVu Sans',
        # Windows系统中文字体
        'SimHei',
        'Microsoft YaHei',
        'SimSun',
        # macOS系统中文字体
        'PingFang SC',
        'Heiti SC',
        'STHeiti',
        # 通用备选字体
        'Arial Unicode MS',
        'Liberation Sans'
    ]
    
    # 获取系统可用字体列表
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    print("正在检测中文字体支持...")
    
    # 寻找可用的中文字体
    chinese_font = None
    for font in font_options:
        if font in available_fonts:
            chinese_font = font
            print(f"找到中文字体: {font}")
            break
    
    if not chinese_font:
        print("未找到专用中文字体，使用系统默认字体")
        # 尝试查找包含中文关键词的字体
        for font_name in available_fonts:
            if any(keyword in font_name.lower() for keyword in 
                   ['noto', 'wenquanyi', 'simhei', 'simsun', 'microsoft']):
                chinese_font = font_name
                print(f"找到候选中文字体: {font_name}")
                break
    
    # 设置字体
    if chinese_font:
        plt.rcParams['font.sans-serif'] = [chinese_font, 'DejaVu Sans',
                                           'Arial']
    else:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial',
                                           'Liberation Sans']
    
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False
    
    print(f"当前字体设置: {plt.rcParams['font.sans-serif']}")
    
    return chinese_font


# 在导入后立即设置字体
setup_chinese_fonts()


def extract_and_plot_psd_values(npz_filepath: str, 
                                output_dir: str = "./output/plots/"):
    """
    从NPZ文件中提取所有PSD值并绘制在频率-dB坐标系中
    使用ObsPy标准方法重新加载PPSD对象以确保频率轴一致性
    
    Parameters:
    -----------
    npz_filepath : str
        NPZ文件路径
    output_dir : str
        输出图像目录
    """
    if not os.path.exists(npz_filepath):
        raise FileNotFoundError(f"NPZ文件不存在: {npz_filepath}")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"正在处理NPZ文件: {os.path.basename(npz_filepath)}")
    
    try:
        # 方法1: 尝试使用ObsPy直接加载PPSD对象
        print("尝试使用ObsPy直接加载PPSD对象...")
        
        # 自动搜索inventory文件
        inventory_paths = [
            "./input/BJ.dataless",     # 默认路径
            "./BJ.dataless",           # 当前目录
            "input/BJ.dataless",       # 相对路径
            "../input/BJ.dataless",    # 上级目录
        ]
        
        inventory = None
        
        for path in inventory_paths:
            if os.path.exists(path):
                try:
                    inventory = read_inventory(path)
                    print(f"✓ 找到inventory文件: {path}")
                    break
                except Exception as e:
                    print(f"警告: 无法读取inventory文件 {path}: {e}")
                    continue
        
        if inventory is not None:
            # 使用ObsPy的load_npz方法
            ppsd = PPSD.load_npz(npz_filepath, metadata=inventory)
            
            # 从PPSD对象获取标准的频率和周期网格
            periods = ppsd.period_bin_centers
            frequencies = 1.0 / periods
            db_bin_centers = ppsd.db_bin_centers
            
            # 获取概率密度直方图
            histogram = ppsd.current_histogram
            
            # 获取原始PSD数据
            binned_psds = np.array(ppsd._binned_psds)
            times_processed = ppsd._times_processed
            
            print("✓ 成功使用ObsPy标准方法加载PPSD对象")
            
        else:
            print("警告: 未找到inventory文件，回退到手动解析NPZ文件...")
            raise FileNotFoundError("需要inventory文件进行完整分析")
            
    except Exception as e:
        print(f"ObsPy加载失败: {e}")
        print("回退到手动解析NPZ文件...")
        
        # 方法2: 手动解析NPZ文件（备用方法）
        npz_data = np.load(npz_filepath, allow_pickle=True)
        
        # 从NPZ文件中提取数据
        binned_psds = npz_data['_binned_psds']
        times_processed = npz_data['_times_processed']
        db_bin_edges = npz_data['_db_bin_edges']
        period_binning = npz_data['_period_binning']
        psd_periods = npz_data['_psd_periods']
        
        # 计算dB分箱中心
        db_bin_centers = (db_bin_edges[:-1] + db_bin_edges[1:]) / 2
        
        # 从period_binning中提取周期信息
        period_bin_center_indices = period_binning[2].astype(int)
        periods = psd_periods[period_bin_center_indices]
        frequencies = 1.0 / periods
        
        # 重建直方图矩阵
        histogram = np.zeros((len(periods), len(db_bin_centers)))
        
        npz_data.close()
    
    # 提取台站信息
    filename = os.path.basename(npz_filepath)
    parts = filename.replace('.npz', '').split('_')
    if len(parts) >= 3:
        station_info = parts[-1]  # 例如: "BJ-DAX-00-BHZ"
        station_parts = station_info.split('-')
        if len(station_parts) == 4:
            network, station, location, channel = station_parts
        else:
            network = station = location = channel = "Unknown"
    else:
        network = station = location = channel = "Unknown"
    
    # 时间信息
    if len(times_processed) > 0:
        # 确保times_processed是numpy数组
        times_processed = np.array(times_processed)
        
        # 时间戳可能是纳秒级别，需要转换为秒
        if times_processed[0] > 1e12:  # 纳秒时间戳
            times_processed_sec = times_processed / 1e9
        else:  # 秒时间戳
            times_processed_sec = times_processed
        
        start_time = datetime.fromtimestamp(times_processed_sec[0])
        end_time = datetime.fromtimestamp(times_processed_sec[-1])
        time_str = (f"{start_time.strftime('%Y-%m-%d %H:%M')} - "
                    f"{end_time.strftime('%Y-%m-%d %H:%M')}")
    else:
        time_str = "未知时间"
        times_processed_sec = np.array(times_processed)
    
    # 检查数据有效性
    if binned_psds.size == 0 or len(periods) == 0:
        print("警告: NPZ文件中没有有效的PSD数据")
        return
    
    print("数据信息:")
    print(f"  台站: {network}.{station}.{location}.{channel}")
    print(f"  时间范围: {time_str}")
    print(f"  频率范围: {np.min(frequencies):.6f} - {np.max(frequencies):.6f} Hz")
    print(f"  周期范围: {np.min(periods):.6f} - {np.max(periods):.6f} 秒")
    print(f"  dB范围: {np.min(db_bin_centers):.1f} - "
          f"{np.max(db_bin_centers):.1f} dB")
    print(f"  处理的时间段数: {len(times_processed)}")
    
    # 创建四子图布局
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'PPSD分析 - {network}.{station}.{location}.{channel}\n'
                 f'时间: {time_str}', fontsize=14, fontweight='bold')
    
    # 配色方案设置
    light_colormap = 'Blues'      # 清淡风格配色（用于PPSD概率密度分布）
    curve_colormap = 'viridis'    # 保持viridis（用于各时间段PSD曲线）
    
    # 子图1: 标准PPSD热力图（概率密度）
    ax1 = axes[0, 0]
    
    if histogram.size > 0 and np.any(histogram > 0):
        # 创建网格
        freq_mesh, db_mesh = np.meshgrid(frequencies, db_bin_centers)
        
        # 绘制热力图 - 使用清淡的Blues配色
        im = ax1.pcolormesh(freq_mesh, db_mesh, histogram.T,
                            shading='auto', cmap=light_colormap)
        ax1.set_xscale('log')  # 设置X轴为对数坐标
        ax1.set_xlabel('频率 (Hz)')
        ax1.set_ylabel('功率谱密度 (dB)')
        ax1.set_title('PPSD概率密度分布')
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax1)
        cbar.set_label('概率密度')
    else:
        ax1.text(0.5, 0.5, '无有效PPSD数据', ha='center', va='center',
                 transform=ax1.transAxes)
        ax1.set_title('PPSD概率密度分布（无数据）')
    
    # 子图2: PSD值散点图
    ax2 = axes[0, 1]
    
    # 从直方图中提取非零概率的点
    freq_points = []
    db_points = []
    prob_weights = []
    
    for i, freq in enumerate(frequencies):
        for j, db in enumerate(db_bin_centers):
            prob = histogram[i, j]
            if prob > 0:
                freq_points.append(freq)
                db_points.append(db)
                prob_weights.append(prob)
    
    if len(freq_points) > 0:
        freq_points = np.array(freq_points)
        db_points = np.array(db_points)
        prob_weights = np.array(prob_weights)
        
        # 使用清淡的散点图配色 - 使用淡蓝色系
        scatter = ax2.scatter(freq_points, db_points, c=prob_weights,
                              cmap='Blues', alpha=0.7, s=25, 
                              edgecolors='lightgray', linewidth=0.5)
        ax2.set_xscale('log')  # 设置X轴为对数坐标
        ax2.set_xlabel('频率 (Hz)')
        ax2.set_ylabel('功率谱密度 (dB)')
        ax2.set_title('PSD值散点图')
        
        # 添加颜色条
        cbar2 = plt.colorbar(scatter, ax=ax2)
        cbar2.set_label('概率密度')
    else:
        ax2.text(0.5, 0.5, '无有效散点数据', ha='center', va='center',
                 transform=ax2.transAxes)
        ax2.set_title('PSD值散点图（无数据）')
    
    # 子图3: 每个时间段的PSD值（频率-功率谱密度图）
    ax3 = axes[1, 0]
    
    # 绘制每个时间段的PSD曲线
    n_time_segments = binned_psds.shape[0]
    
    # 为了避免图像过于拥挤，选择性显示时间段
    if n_time_segments <= 10:
        # 如果时间段较少，显示所有
        time_indices = range(n_time_segments)
        alpha = 0.7
    elif n_time_segments <= 50:
        # 中等数量，显示一半
        time_indices = range(0, n_time_segments, 2)
        alpha = 0.5
    else:
        # 时间段很多，只显示代表性的几条
        time_indices = range(0, n_time_segments, 
                             max(1, n_time_segments // 20))
        alpha = 0.4
    
    # 使用viridis颜色映射来区分不同时间段（保持原有配色）
    colors = matplotlib.colormaps[curve_colormap](
        np.linspace(0, 1, len(time_indices)))
    
    for i, (time_idx, color) in enumerate(zip(time_indices, colors)):
        psd_values = binned_psds[time_idx, :]
        
        # 过滤掉无效值
        valid_mask = ~np.isnan(psd_values) & ~np.isinf(psd_values)
        valid_freqs = frequencies[valid_mask]
        valid_psds = psd_values[valid_mask]
        
        if len(valid_freqs) > 0:
            # 转换时间戳为可读格式
            if i < len(times_processed_sec):
                time_label = datetime.fromtimestamp(
                    times_processed_sec[time_idx]).strftime('%m-%d %H:%M')
            else:
                time_label = f'时段 {time_idx+1}'
            
            ax3.plot(valid_freqs, valid_psds, color=color, alpha=alpha,
                     linewidth=1, 
                     label=time_label if i < 5 else "")  # 只显示前5个标签
    
    ax3.set_xscale('log')  # 设置X轴为对数坐标
    ax3.set_xlabel('频率 (Hz)')
    ax3.set_ylabel('功率谱密度 (dB)')
    ax3.set_title(f'各时间段PSD曲线 (显示 {len(time_indices)}/{n_time_segments} 个时段)')
    ax3.grid(True, alpha=0.3)
    
    # 添加图例（仅显示前几个）
    if len(time_indices) <= 10:
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    # 子图4: 时间序列PSD分析图
    ax4 = axes[1, 1]
    
    if len(times_processed_sec) > 0 and binned_psds.size > 0:
        # 计算每个时间段的PSD统计值
        # 选择几个有代表性的频率点进行时间序列分析
        target_freqs = [0.1, 1.0, 10.0]  # Hz
        freq_indices = []
        freq_labels = []
        
        for target_freq in target_freqs:
            # 找到最接近目标频率的索引
            freq_diff = np.abs(frequencies - target_freq)
            closest_idx = np.argmin(freq_diff)
            # 确保误差不太大
            if freq_diff[closest_idx] < target_freq * 0.5:  
                freq_indices.append(closest_idx)
                freq_labels.append(f'{frequencies[closest_idx]:.2f} Hz')
        
        # 转换时间戳为datetime对象
        datetime_objects = [datetime.fromtimestamp(t) 
                            for t in times_processed_sec]
        
        # 绘制不同频率的时间序列
        colors_ts = ['blue', 'red', 'green', 'orange', 'purple']
        
        for i, (freq_idx, freq_label) in enumerate(
                zip(freq_indices, freq_labels)):
            psd_time_series = binned_psds[:, freq_idx]
            
            # 过滤无效值
            valid_mask = (~np.isnan(psd_time_series) & 
                          ~np.isinf(psd_time_series))
            valid_times = [datetime_objects[j] for j in 
                           range(len(datetime_objects)) if valid_mask[j]]
            valid_psds = psd_time_series[valid_mask]
            
            if len(valid_times) > 0:
                color = colors_ts[i % len(colors_ts)]
                ax4.plot(valid_times, valid_psds, color=color, 
                         marker='o', markersize=3, linewidth=1.5, 
                         alpha=0.8, label=freq_label)
        
        ax4.set_xlabel('时间')
        ax4.set_ylabel('功率谱密度 (dB)')
        ax4.set_title('PSD时间序列分析')
        ax4.grid(True, alpha=0.3)
        ax4.legend(fontsize=8)
        
        # 格式化x轴时间显示
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d\n%H:%M'))
        ax4.xaxis.set_major_locator(
            mdates.HourLocator(interval=max(1, len(datetime_objects)//10)))
        
        # 旋转x轴标签以避免重叠
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
    else:
        ax4.text(0.5, 0.5, '时间序列数据不足', 
                 ha='center', va='center', transform=ax4.transAxes, 
                 fontsize=12, style='italic', color='gray')
        ax4.set_title('PSD时间序列分析')
        ax4.set_xticks([])
        ax4.set_yticks([])
    
    # 调整布局
    plt.tight_layout()

    # 保存图像
    # 从时间戳提取开始时间用于文件名
    if len(times_processed_sec) > 0:
        start_time = datetime.fromtimestamp(times_processed_sec[0])
        datetime_str = start_time.strftime('%Y%m%d%H%M')
        output_filename = (f"psd_analysis_{datetime_str}_"
                           f"{network}-{station}-{location}-{channel}.png")
    else:
        # 如果没有时间信息，使用当前时间
        datetime_str = datetime.now().strftime('%Y%m%d%H%M')
        output_filename = (f"psd_analysis_{datetime_str}_"
                           f"{network}-{station}-{location}-{channel}.png")
    
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ PSD分析图已保存: {output_path}")


def main():
    """
    主函数 - 支持命令行参数
    
    使用方法:
        python run_plot_psd.py                    # 使用默认NPZ文件
        python run_plot_psd.py path/to/file.npz   # 指定NPZ文件
        python run_plot_psd.py file.npz out_dir/  # 指定NPZ文件和输出目录
    """
    import sys
    
    # 解析命令行参数
    if len(sys.argv) == 1:
        # 使用默认NPZ文件
        npz_file = "./output/npz/PPSD_202503251600_BJ-DAX-00-BHZ.npz"
        output_dir = "./output/plots/"
    elif len(sys.argv) == 2:
        # 指定NPZ文件，使用默认输出目录
        npz_file = sys.argv[1]
        output_dir = "./output/plots/"
    elif len(sys.argv) == 3:
        # 指定NPZ文件和输出目录
        npz_file = sys.argv[1]
        output_dir = sys.argv[2]
    else:
        print("使用方法:")
        print("  python run_plot_psd.py                    "
              "# 使用默认NPZ文件")
        print("  python run_plot_psd.py path/to/file.npz   "
              "# 指定NPZ文件")
        print("  python run_plot_psd.py file.npz out_dir/  "
              "# 指定NPZ文件和输出目录")
        return
    
    # 检查NPZ文件是否存在
    if not os.path.exists(npz_file):
        print(f"错误: 找不到NPZ文件 {npz_file}")
        print("请先运行PPSD计算生成NPZ文件")
        
        # 尝试查找可用的NPZ文件
        npz_dir = "./output/npz/"
        if os.path.exists(npz_dir):
            npz_files = [f for f in os.listdir(npz_dir) if f.endswith('.npz')]
            if npz_files:
                print(f"\n可用的NPZ文件 (在 {npz_dir}):")
                for f in sorted(npz_files):
                    print(f"  {f}")
        return
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"分析NPZ文件: {npz_file}")
    print(f"输出目录: {output_dir}")
    
    # 执行分析
    extract_and_plot_psd_values(npz_file, output_dir)
    
    print("\n✓ PSD值分析完成！")


if __name__ == "__main__":
    main() 