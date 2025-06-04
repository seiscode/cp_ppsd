#!/usr/bin/env python3
"""
BJ台网台站仪器响应图绘制工具 (改进版)

使用ObsPy的Inventory.plot_response方法绘制台站的仪器响应特性。

功能特点：
- 支持中文字体显示
- 生成个别台站响应图
- 生成多台站对比图
- 自动检测可用台站
- 保存高质量PNG图像

参考文档：
https://docs.obspy.org/master/packages/autogen/obspy.core.inventory.inventory.Inventory.plot_response.html
"""

import os
import matplotlib.pyplot as plt
from obspy import read_inventory
import matplotlib
import numpy as np

# 设置非交互式后端
matplotlib.use('Agg')

# 配置中文字体支持
try:
    # 尝试使用中文字体
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
except:
    # 如果中文字体不可用，使用英文
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    print("注意：中文字体不可用，将使用英文标题")


def plot_individual_station_response(inventory, station, output_dir):
    """
    绘制单个台站的响应图
    
    Parameters:
    -----------
    inventory : obspy.Inventory
        仪器响应inventory对象
    station : str
        台站代码
    output_dir : str
        输出目录
        
    Returns:
    --------
    bool : 成功返回True，失败返回False
    """
    try:
        # 检查台站是否存在
        station_inv = inventory.select(station=station)
        if len(station_inv.networks) == 0:
            print(f"  警告: 在inventory中未找到台站 {station}")
            return False
            
        # 显示台站通道信息
        print(f"  台站 {station} 的通道:")
        for network in station_inv.networks:
            for sta in network.stations:
                for chan in sta.channels:
                    print(f"    {network.code}.{sta.code}."
                          f"{chan.location_code}.{chan.code}")
        
        # 创建图形
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # 使用英文标题避免字体问题
        fig.suptitle(f'BJ.{station} Station Instrument Response', 
                     fontsize=16, fontweight='bold')
        
        # 绘制响应图
        inventory.plot_response(
            min_freq=0.001,  # 0.001 Hz (1000s period)
            output='VEL',    # Velocity response
            network='BJ',
            station=station,
            location='*',
            channel='*',
            axes=axes,
            show=False,
            label_epoch_dates=True
        )
        
        # 设置轴标签和标题
        axes[0].set_title(f'Amplitude Response - Station {station}')
        axes[1].set_title(f'Phase Response - Station {station}')
        axes[0].grid(True, alpha=0.3)
        axes[1].grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图像
        output_file = os.path.join(output_dir, f"BJ_{station}_response.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  响应图已保存: {output_file}")
        
        plt.close(fig)
        return True
        
    except Exception as e:
        print(f"  错误: 绘制台站 {station} 响应图时出错: {e}")
        return False


def plot_comparison_response(inventory, stations, output_dir):
    """
    绘制多台站对比响应图
    
    Parameters:
    -----------
    inventory : obspy.Inventory
        仪器响应inventory对象
    stations : list
        台站代码列表
    output_dir : str
        输出目录
    """
    try:
        # 创建对比图
        fig, axes = plt.subplots(2, 1, figsize=(16, 12))
        fig.suptitle('BJ Network Multi-Station Response Comparison', 
                     fontsize=16, fontweight='bold')
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink']
        
        valid_stations = []
        for i, station in enumerate(stations):
            try:
                station_inv = inventory.select(station=station)
                if len(station_inv.networks) > 0:
                    # 为不同台站使用不同颜色
                    color = colors[i % len(colors)]
                    
                    # 绘制垂直分量响应
                    inventory.plot_response(
                        min_freq=0.001,
                        output='VEL',
                        network='BJ',
                        station=station,
                        location='*',
                        channel='*Z',  # Only vertical component
                        axes=axes,
                        show=False,
                        label_epoch_dates=False
                    )
                    valid_stations.append(station)
                    
            except Exception as e:
                print(f"  警告: 台站 {station} 无法添加到对比图: {e}")
                continue
        
        # 设置标题和网格
        axes[0].set_title('Amplitude Response Comparison (Vertical Components)')
        axes[1].set_title('Phase Response Comparison (Vertical Components)')
        axes[0].grid(True, alpha=0.3)
        axes[1].grid(True, alpha=0.3)
        
        # 调整图例位置
        if valid_stations:
            axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        # 保存对比图
        comparison_file = os.path.join(
            output_dir, 
            "BJ_multi_station_response_comparison.png"
        )
        plt.savefig(comparison_file, dpi=300, bbox_inches='tight')
        print(f"  对比图已保存: {comparison_file}")
        
        plt.close(fig)
        
        return len(valid_stations)
        
    except Exception as e:
        print(f"  错误: 绘制对比图时出错: {e}")
        return 0


def analyze_inventory_contents(inventory):
    """
    分析inventory内容并返回可用的台站信息
    
    Parameters:
    -----------
    inventory : obspy.Inventory
        仪器响应inventory对象
        
    Returns:
    --------
    dict : 包含台站信息的字典
    """
    analysis = {
        'total_networks': len(inventory.networks),
        'stations': [],
        'channels_by_station': {},
        'instrument_types': set()
    }
    
    for network in inventory.networks:
        for station in network.stations:
            station_code = station.code
            analysis['stations'].append(station_code)
            analysis['channels_by_station'][station_code] = []
            
            for channel in station.channels:
                channel_id = f"{channel.location_code}.{channel.code}"
                analysis['channels_by_station'][station_code].append(channel_id)
                
                # 识别仪器类型
                if channel.code.startswith('BH'):
                    analysis['instrument_types'].add('Broadband')
                elif channel.code.startswith('SH'):
                    analysis['instrument_types'].add('Short-period')
                elif channel.code.startswith('HH'):
                    analysis['instrument_types'].add('High-frequency')
    
    return analysis


def main():
    """
    主函数
    """
    print("=" * 70)
    print("BJ Network Station Response Plotting Tool (Improved Version)")
    print("=" * 70)
    
    # 输入文件路径
    inventory_file = "../input/BJ.XML"
    
    # 检查文件存在性
    if not os.path.exists(inventory_file):
        print(f"错误: 找不到仪器响应文件 {inventory_file}")
        return
    
    # 读取inventory
    print(f"正在读取仪器响应文件: {inventory_file}")
    try:
        inventory = read_inventory(inventory_file)
        print(f"成功读取 inventory，包含 {len(inventory.networks)} 个台网")
    except Exception as e:
        print(f"读取inventory文件时出错: {e}")
        return
    
    # 指定要绘制的台站
    target_stations = ['BBS', 'DAX', 'DSQ', 'FHY', 'JIZ']
    
    # 检查哪些台站可用
    all_stations = []
    for network in inventory.networks:
        for station in network.stations:
            all_stations.append(station.code)
    
    available_stations = [s for s in target_stations if s in all_stations]
    missing_stations = [s for s in target_stations if s not in all_stations]
    
    print(f"\n=== 台站状态检查 ===")
    print(f"BJ.XML中的所有台站: {', '.join(sorted(all_stations))}")
    print(f"目标台站: {', '.join(target_stations)}")
    print(f"可用台站: {', '.join(available_stations)}")
    if missing_stations:
        print(f"缺失台站: {', '.join(missing_stations)}")
    
    # 创建输出目录
    output_dir = "../output/response_plots"
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n输出目录: {output_dir}")
    
    # 绘制个别台站响应图
    print(f"\n=== 绘制个别台站响应图 ===")
    successful_plots = 0
    for station in available_stations:
        print(f"\n正在处理台站: {station}")
        if plot_individual_station_response(inventory, station, output_dir):
            successful_plots += 1
    
    print(f"\n成功绘制 {successful_plots} 个台站的响应图")
    
    # 绘制对比图
    if available_stations:
        print(f"\n=== 绘制多台站对比图 ===")
        valid_count = plot_comparison_response(inventory, available_stations, 
                                             output_dir)
        print(f"对比图包含 {valid_count} 个台站的响应")
    
    # 生成总结报告
    print(f"\n=== 处理完成 ===")
    print(f"已处理台站: {len(available_stations)}")
    print(f"成功生成图像: {successful_plots + (1 if available_stations else 0)}")
    print(f"输出目录: {output_dir}")
    
    # 列出生成的文件
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
        print(f"\n生成的文件:")
        for file in sorted(files):
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"  {file} ({file_size:.1f} KB)")


if __name__ == "__main__":
    main() 