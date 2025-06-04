#!/usr/bin/env python3
"""
BJ台网指定台站仪器响应图绘制工具 (最终版)

专门绘制BBS、DAX、DSQ、FHY、JIZ台站的仪器响应图，解决中文字体显示问题。

参考文档：
https://docs.obspy.org/master/packages/autogen/obspy.core.inventory.inventory.Inventory.plot_response.html
"""

import os
import matplotlib.pyplot as plt
from obspy import read_inventory
import matplotlib
import matplotlib.font_manager as fm

# 设置非交互式后端
matplotlib.use('Agg')

def setup_chinese_fonts():
    """
    设置中文字体支持
    """
    # 尝试多种中文字体设置方法
    chinese_fonts = [
        'DejaVu Sans',  # 系统默认字体（支持部分中文）
        'SimHei',       # 黑体
        'Microsoft YaHei',  # 微软雅黑
        'WenQuanYi Micro Hei',  # 文泉驿微米黑
        'Noto Sans CJK SC',     # Google Noto字体
        'Source Han Sans CN'     # 思源黑体
    ]
    
    # 设置字体
    plt.rcParams['font.sans-serif'] = chinese_fonts
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    
    # 设置字体大小
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['figure.titlesize'] = 16
    
    print("已配置中文字体支持")

def plot_station_response_with_chinese(inventory, station, output_dir):
    """
    绘制单个台站的响应图（支持中文标题）
    """
    try:
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
        
        # 使用中文标题
        fig.suptitle(f'BJ.{station} 台站仪器响应特性', 
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
        
        # 设置中文轴标签和标题
        axes[0].set_title(f'幅度响应 - {station}台站')
        axes[1].set_title(f'相位响应 - {station}台站')
        axes[0].set_ylabel('幅度 (dB)')
        axes[1].set_ylabel('相位 (度)')
        axes[1].set_xlabel('频率 (Hz)')
        
        # 添加网格
        axes[0].grid(True, alpha=0.3)
        axes[1].grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图像
        output_file = os.path.join(output_dir, f"BJ_{station}_response.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"  响应图已保存: {output_file}")
        
        plt.close(fig)
        return True
        
    except Exception as e:
        print(f"  错误: 绘制台站 {station} 响应图时出错: {e}")
        return False

def plot_comparison_response_chinese(inventory, stations, output_dir):
    """
    绘制多台站对比响应图（中文版本）
    """
    try:
        # 创建对比图
        fig, axes = plt.subplots(2, 1, figsize=(16, 12))
        
        # 使用中文标题
        station_names = ', '.join(stations)
        fig.suptitle(f'BJ台网多台站仪器响应对比 ({station_names})', 
                     fontsize=16, fontweight='bold')
        
        valid_stations = []
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        
        for i, station in enumerate(stations):
            try:
                station_inv = inventory.select(station=station)
                if len(station_inv.networks) > 0:
                    # 绘制垂直分量响应
                    inventory.plot_response(
                        min_freq=0.001,
                        output='VEL',
                        network='BJ',
                        station=station,
                        location='*',
                        channel='*Z',  # 只绘制垂直分量
                        axes=axes,
                        show=False,
                        label_epoch_dates=False
                    )
                    valid_stations.append(station)
                    print(f"  已添加台站 {station} 到对比图")
                    
            except Exception as e:
                print(f"  警告: 台站 {station} 无法添加到对比图: {e}")
                continue
        
        # 设置中文标题和标签
        axes[0].set_title('幅度响应对比 (垂直分量)', fontsize=14)
        axes[1].set_title('相位响应对比 (垂直分量)', fontsize=14)
        axes[0].set_ylabel('幅度 (dB)')
        axes[1].set_ylabel('相位 (度)')
        axes[1].set_xlabel('频率 (Hz)')
        
        # 添加网格
        axes[0].grid(True, alpha=0.3)
        axes[1].grid(True, alpha=0.3)
        
        # 调整图例
        if valid_stations:
            # 手动创建图例，避免中文显示问题
            legend_labels = [f'{station}台站' for station in valid_stations]
            axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        # 保存对比图
        comparison_file = os.path.join(output_dir, 
                                     "BJ_stations_response_comparison_chinese.png")
        plt.savefig(comparison_file, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print(f"  中文对比图已保存: {comparison_file}")
        
        plt.close(fig)
        
        return len(valid_stations)
        
    except Exception as e:
        print(f"  错误: 绘制中文对比图时出错: {e}")
        return 0

def main():
    """
    主函数 - 专门绘制指定台站响应图
    """
    print("=" * 70)
    print("BJ台网指定台站仪器响应图绘制工具")
    print("目标台站: BBS, DAX, DSQ, FHY, JIZ")
    print("=" * 70)
    
    # 设置中文字体
    setup_chinese_fonts()
    
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
        if plot_station_response_with_chinese(inventory, station, output_dir):
            successful_plots += 1
    
    print(f"\n成功绘制 {successful_plots} 个台站的个别响应图")
    
    # 绘制对比图
    if available_stations:
        print(f"\n=== 绘制多台站对比图 ===")
        valid_count = plot_comparison_response_chinese(inventory, 
                                                     available_stations, 
                                                     output_dir)
        print(f"对比图包含 {valid_count} 个台站的响应")
    
    # 生成总结报告
    print(f"\n=== 绘制完成 ===")
    print(f"请求的台站: {', '.join(target_stations)}")
    print(f"成功处理的台站: {', '.join(available_stations)}")
    if missing_stations:
        print(f"未找到的台站: {', '.join(missing_stations)}")
    print(f"生成的图像数量: {successful_plots + (1 if available_stations else 0)}")
    print(f"所有图像保存在: {output_dir}")
    
    # 列出生成的文件
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) 
                if f.endswith('.png') and 'chinese' in f or 
                   any(station in f for station in available_stations)]
        if files:
            print(f"\n本次生成的新文件:")
            for file in sorted(files):
                if any(station in file for station in available_stations) or 'chinese' in file:
                    file_path = os.path.join(output_dir, file)
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    print(f"  {file} ({file_size:.1f} KB)")

if __name__ == "__main__":
    main() 