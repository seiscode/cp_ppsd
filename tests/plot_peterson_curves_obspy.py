#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Peterson曲线绘图工具 - 使用ObsPy官方数据
使用ObsPy库的get_nlnm()和get_nhnm()函数绘制Peterson (1993) 噪声模型
用于地震台站噪声水平评估的标准参考曲线

作者: muly
创建时间: 2025-01-30
参考: https://docs.obspy.org/master/packages/autogen/obspy.signal.spectral_estimation.get_nlnm.html
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path

try:
    from obspy.signal.spectral_estimation import get_nlnm, get_nhnm
    OBSPY_AVAILABLE = True
except ImportError:
    OBSPY_AVAILABLE = False
    print("警告: ObsPy库未安装，将使用备用数据")

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

def get_peterson_data_obspy():
    """
    使用ObsPy官方函数获取Peterson噪声模型数据
    
    Returns:
        tuple: (nlnm_periods, nlnm_power, nhnm_periods, nhnm_power)
    """
    if not OBSPY_AVAILABLE:
        raise ImportError("需要安装ObsPy库: pip install obspy")
    
    # 获取NLNM数据 (New Low Noise Model)
    nlnm_periods, nlnm_power = get_nlnm()
    
    # 获取NHNM数据 (New High Noise Model)  
    nhnm_periods, nhnm_power = get_nhnm()
    
    return nlnm_periods, nlnm_power, nhnm_periods, nhnm_power

def get_peterson_data_fallback():
    """
    备用Peterson数据（当ObsPy不可用时）
    基于Peterson (1993)的原始数据点
    """
    # NLNM数据点
    nlnm_periods = np.array([
        0.10, 0.17, 0.40, 0.80, 1.24, 2.40, 4.30, 5.00, 6.00, 10.00,
        12.00, 15.60, 21.90, 31.60, 45.00, 70.00, 101.00, 154.00, 
        328.00, 600.00, 10000.00
    ])
    nlnm_power = np.array([
        -162.36, -166.7, -170.0, -166.4, -168.6, -159.98, -141.1, -71.36, 
        -97.26, -132.18, -205.27, -37.65, -114.37, -160.58, -187.50, 
        -216.47, -185.00, -168.34, -217.43, -258.28, -346.88
    ])
    
    # NHNM数据点
    nhnm_periods = np.array([
        0.10, 0.22, 0.32, 0.80, 3.80, 4.60, 6.30, 7.90, 15.40, 20.00,
        354.80, 10000.00
    ])
    nhnm_power = np.array([
        -108.73, -150.34, -122.31, -116.85, -108.48, -74.66, -93.95,
        -73.54, -81.78, -187.50, -216.85, -346.88
    ])
    
    return nlnm_periods, nlnm_power, nhnm_periods, nhnm_power

def plot_peterson_curves_official(save_path=None, show_plot=True, use_chinese=True):
    """
    绘制Peterson噪声模型曲线
    
    Parameters:
        save_path (str): 图像保存路径
        show_plot (bool): 是否显示图像
        use_chinese (bool): 是否使用中文标签
    """
    
    # 获取数据
    try:
        nlnm_periods, nlnm_power, nhnm_periods, nhnm_power = get_peterson_data_obspy()
        data_source = "ObsPy官方数据"
    except (ImportError, Exception):
        nlnm_periods, nlnm_power, nhnm_periods, nhnm_power = get_peterson_data_fallback()
        data_source = "备用数据"
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 设置标签
    if use_chinese:
        main_title = f'Peterson (1993) 地震台站噪声模型\n数据源: {data_source}'
        period_label = '周期 (秒)'
        freq_label = '频率 (Hz)'
        power_label = '功率谱密度 (dB re 1(m/s²)²/Hz)'
        nlnm_label = 'NLNM (新低噪声模型)'
        nhnm_label = 'NHNM (新高噪声模型)'
        title1 = '周期 vs 功率谱密度'
        title2 = '频率 vs 功率谱密度'
        ref_text = '参考文献: Peterson, J. (1993). Observations and modeling of seismic background noise.'
    else:
        main_title = f'Peterson (1993) Seismic Station Noise Models\nData Source: {data_source}'
        period_label = 'Period (s)'
        freq_label = 'Frequency (Hz)'
        power_label = 'Power Spectral Density (dB re 1(m/s²)²/Hz)'
        nlnm_label = 'NLNM (New Low Noise Model)'
        nhnm_label = 'NHNM (New High Noise Model)'
        title1 = 'Period vs Power Spectral Density'
        title2 = 'Frequency vs Power Spectral Density'
        ref_text = 'Reference: Peterson, J. (1993). Observations and modeling of seismic background noise.'
    
    # 第一个子图：周期 vs 功率谱密度
    ax1.semilogx(nlnm_periods, nlnm_power, 'b-', linewidth=2, label=nlnm_label, marker='o', markersize=4)
    ax1.semilogx(nhnm_periods, nhnm_power, 'r-', linewidth=2, label=nhnm_label, marker='s', markersize=4)
    
    ax1.set_xlabel(period_label, fontsize=12)
    ax1.set_ylabel(power_label, fontsize=12)
    ax1.set_title(title1, fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=11)
    ax1.set_xlim(0.01, 10000)
    ax1.set_ylim(-400, -50)
    
    # 添加重要周期标记
    important_periods = [0.1, 1, 10, 100, 1000]
    for period in important_periods:
        ax1.axvline(x=period, color='gray', linestyle='--', alpha=0.5)
        if period >= ax1.get_xlim()[0] and period <= ax1.get_xlim()[1]:
            ax1.text(period, -380, f'{period}s', rotation=90, 
                    verticalalignment='bottom', fontsize=9, alpha=0.7)
    
    # 第二个子图：频率 vs 功率谱密度
    nlnm_frequencies = 1.0 / nlnm_periods
    nhnm_frequencies = 1.0 / nhnm_periods
    
    ax2.loglog(nlnm_frequencies, nlnm_power, 'b-', linewidth=2, label=nlnm_label, marker='o', markersize=4)
    ax2.loglog(nhnm_frequencies, nhnm_power, 'r-', linewidth=2, label=nhnm_label, marker='s', markersize=4)
    
    ax2.set_xlabel(freq_label, fontsize=12)
    ax2.set_ylabel(power_label, fontsize=12)
    ax2.set_title(title2, fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=11)
    ax2.set_xlim(0.0001, 10)
    ax2.set_ylim(-400, -50)
    
    # 添加重要频率标记
    important_freqs = [0.001, 0.01, 0.1, 1, 10]
    for freq in important_freqs:
        ax2.axvline(x=freq, color='gray', linestyle='--', alpha=0.5)
        if freq >= ax2.get_xlim()[0] and freq <= ax2.get_xlim()[1]:
            ax2.text(freq, -380, f'{freq}Hz', rotation=90, 
                    verticalalignment='bottom', fontsize=9, alpha=0.7)
    
    # 设置主标题
    fig.suptitle(main_title, fontsize=16, fontweight='bold', y=0.95)
    
    # 添加参考文献信息
    fig.text(0.5, 0.02, ref_text, ha='center', fontsize=10, style='italic')
    
    # 调整布局
    plt.tight_layout()
    plt.subplots_adjust(top=0.90, bottom=0.08)
    
    # 保存图像
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Peterson曲线图已保存到: {save_path}")
    
    # 显示图像
    if show_plot:
        plt.show()
    
    return fig, (ax1, ax2)

def plot_single_peterson_curve(save_path=None, show_plot=True, use_chinese=True):
    """
    绘制单一Peterson曲线图（仅频率 vs 功率谱密度）
    """
    # 获取数据
    try:
        nlnm_periods, nlnm_power, nhnm_periods, nhnm_power = get_peterson_data_obspy()
        data_source = "ObsPy官方数据"
    except (ImportError, Exception):
        nlnm_periods, nlnm_power, nhnm_periods, nhnm_power = get_peterson_data_fallback()
        data_source = "备用数据"
    
    # 转换为频率
    nlnm_frequencies = 1.0 / nlnm_periods
    nhnm_frequencies = 1.0 / nhnm_periods
    
    # 创建图形
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 设置标签
    if use_chinese:
        title = f'Peterson (1993) 地震台站噪声模型 ({data_source})'
        freq_label = '频率 (Hz)'
        power_label = '功率谱密度 (dB re 1(m/s²)²/Hz)'
        nlnm_label = 'NLNM (新低噪声模型)'
        nhnm_label = 'NHNM (新高噪声模型)'
        ref_text = '参考文献: Peterson, J. (1993). Observations and modeling of seismic background noise.'
    else:
        title = f'Peterson (1993) Seismic Station Noise Models ({data_source})'
        freq_label = 'Frequency (Hz)'
        power_label = 'Power Spectral Density (dB re 1(m/s²)²/Hz)'
        nlnm_label = 'NLNM (New Low Noise Model)'
        nhnm_label = 'NHNM (New High Noise Model)'
        ref_text = 'Reference: Peterson, J. (1993). Observations and modeling of seismic background noise.'
    
    # 绘制曲线
    ax.semilogx(nlnm_frequencies, nlnm_power, 'b-', linewidth=3, 
                label=nlnm_label, marker='o', markersize=6, markerfacecolor='lightblue')
    ax.semilogx(nhnm_frequencies, nhnm_power, 'r-', linewidth=3, 
                label=nhnm_label, marker='s', markersize=6, markerfacecolor='lightcoral')
    
    # 填充NLNM和NHNM之间的区域
    ax.fill_between(nlnm_frequencies, nlnm_power, nhnm_power, 
                    where=(nlnm_frequencies <= nhnm_frequencies.max()), 
                    alpha=0.2, color='green', label='正常噪声范围' if use_chinese else 'Normal Noise Range')
    
    ax.set_xlabel(freq_label, fontsize=14)
    ax.set_ylabel(power_label, fontsize=14)
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12, loc='upper right')
    ax.set_xlim(0.001, 100)
    ax.set_ylim(-400, -50)
    
    # 添加重要频率标记和标签
    microseism_freqs = [0.05, 0.14]  # 一次和二次微震频率
    microseism_labels = ['一次微震' if use_chinese else 'Primary Microseism',
                        '二次微震' if use_chinese else 'Secondary Microseism']
    
    for freq, label in zip(microseism_freqs, microseism_labels):
        ax.axvline(x=freq, color='purple', linestyle=':', alpha=0.7, linewidth=2)
        ax.text(freq, -100, label, rotation=90, verticalalignment='bottom', 
                fontsize=10, color='purple', fontweight='bold')
    
    # 添加参考文献信息
    ax.text(0.02, 0.02, ref_text, transform=ax.transAxes, fontsize=10, 
            style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # 保存图像
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Peterson曲线图已保存到: {save_path}")
    
    # 显示图像
    if show_plot:
        plt.show()
    
    return fig, ax

def main():
    """主函数"""
    # 确保输出目录存在
    output_dir = Path("Docs/pics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("正在生成Peterson噪声模型曲线图...")
    
    # 检查ObsPy是否可用
    if OBSPY_AVAILABLE:
        print("✓ 使用ObsPy官方数据")
    else:
        print("⚠ 使用备用数据 (建议安装ObsPy: pip install obspy)")
    
    # 生成双子图版本
    plot_peterson_curves_official(
        save_path=output_dir / "peterson_curves_obspy_双图.png",
        show_plot=False,
        use_chinese=True
    )
    
    # 生成单图版本
    plot_single_peterson_curve(
        save_path=output_dir / "peterson_curves_obspy_标准.png", 
        show_plot=False,
        use_chinese=True
    )
    
    # 生成英文版本
    plot_single_peterson_curve(
        save_path=output_dir / "peterson_curves_obspy_english.png",
        show_plot=False,
        use_chinese=False
    )
    
    print("Peterson曲线图生成完成！")
    print(f"输出目录: {output_dir}")
    
    # 测试数据获取
    try:
        nlnm_periods, nlnm_power, nhnm_periods, nhnm_power = get_peterson_data_obspy()
        print(f"\n数据统计:")
        print(f"NLNM数据点数: {len(nlnm_periods)}")
        print(f"NHNM数据点数: {len(nhnm_periods)}")
        print(f"周期范围: {nlnm_periods.min():.3f} - {nlnm_periods.max():.1f} 秒")
        print(f"功率范围: {nlnm_power.min():.1f} - {nlnm_power.max():.1f} dB")
    except Exception as e:
        print(f"数据获取测试失败: {e}")

if __name__ == "__main__":
    main() 