#!/usr/bin/env python3
"""
绘制BJ台网指定台站的仪器幅频响应图

使用ObsPy的Inventory.plot_response方法绘制BBS、DAX、DSQ、FY、JIZ台站的
仪器响应特性，并保存为图像文件。

参考文档：
https://docs.obspy.org/master/packages/autogen/obspy.core.inventory.inventory.Inventory.plot_response.html
"""

import os
import matplotlib.pyplot as plt
from obspy import read_inventory
import matplotlib

# 设置非交互式后端，适合服务器环境
matplotlib.use('Agg')


def plot_station_responses():
    """
    绘制指定台站的幅频响应图
    """
    # 输入文件路径
    inventory_file = "../input/BJ.XML"
    
    # 检查文件是否存在
    if not os.path.exists(inventory_file):
        print(f"错误: 找不到仪器响应文件 {inventory_file}")
        return
    
    # 读取仪器响应文件
    print(f"正在读取仪器响应文件: {inventory_file}")
    try:
        inventory = read_inventory(inventory_file)
        print(f"成功读取 inventory，包含 {len(inventory.networks)} 个台网")
        
        # 显示inventory内容概览
        print("\nInventory 内容概览:")
        print(inventory.get_contents())
        
    except Exception as e:
        print(f"读取inventory文件时出错: {e}")
        return
    
    # 要绘制的台站列表
    stations = ['BBS', 'DAX', 'DSQ', 'FY', 'JIZ']
    
    # 创建输出目录
    output_dir = "../output/response_plots"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n开始绘制台站响应图...")
    print(f"输出目录: {output_dir}")
    
    # 设置绘图参数
    min_freq = 0.001  # 最低频率 0.001 Hz (1000秒周期)
    
    # 为每个台站单独绘制响应图
    for station in stations:
        print(f"\n正在处理台站: {station}")
        
        try:
            # 检查台站是否存在于inventory中
            station_inv = inventory.select(station=station)
            if len(station_inv.networks) == 0:
                print(f"  警告: 在inventory中未找到台站 {station}")
                continue
                
            # 显示该台站的通道信息
            print(f"  台站 {station} 的通道:")
            for network in station_inv.networks:
                for sta in network.stations:
                    for chan in sta.channels:
                        channel_id = (f"    {network.code}.{sta.code}."
                                     f"{chan.location_code}.{chan.code}")
                        print(channel_id)
            
            # 创建图形
            fig, axes = plt.subplots(2, 1, figsize=(12, 10))
            title = f'BJ.{station} 台站仪器响应特性'
            fig.suptitle(title, fontsize=16, fontweight='bold')
            
            # 绘制响应图
            inventory.plot_response(
                min_freq=min_freq,
                output='VEL',  # 速度响应
                network='BJ',
                station=station,
                location='*',  # 所有位置代码
                channel='*',   # 所有通道
                axes=axes,
                show=False,
                label_epoch_dates=True  # 在图例中显示epoch日期
            )
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图像
            output_file = os.path.join(output_dir, f"BJ_{station}_response.png")
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"  响应图已保存: {output_file}")
            
            # 关闭图形释放内存
            plt.close(fig)
            
        except Exception as e:
            print(f"  错误: 绘制台站 {station} 响应图时出错: {e}")
            continue
    
    # 绘制所有台站的综合对比图
    print("\n正在绘制所有台站的综合对比图...")
    
    try:
        # 创建大图形用于对比
        fig, axes = plt.subplots(2, 1, figsize=(15, 12))
        comp_title = 'BJ台网多台站仪器响应对比 (BBS, DAX, DSQ, FY, JIZ)'
        fig.suptitle(comp_title, fontsize=16, fontweight='bold')
        
        # 绘制所有指定台站的响应
        for station in stations:
            try:
                station_inv = inventory.select(station=station)
                if len(station_inv.networks) > 0:
                    inventory.plot_response(
                        min_freq=min_freq,
                        output='VEL',
                        network='BJ',
                        station=station,
                        location='*',
                        channel='*Z',  # 只绘制垂直分量
                        axes=axes,
                        show=False,
                        label_epoch_dates=False
                    )
            except Exception as e:
                print(f"  警告: 台站 {station} 无法添加到综合图: {e}")
                continue
        
        # 调整布局和标签
        axes[0].set_title('幅度响应 (所有台站对比)')
        axes[1].set_title('相位响应 (所有台站对比)')
        axes[0].grid(True, alpha=0.3)
        axes[1].grid(True, alpha=0.3)
        axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        # 保存综合对比图
        comparison_file = os.path.join(
            output_dir,
            "BJ_all_stations_response_comparison.png"
        )
        plt.savefig(comparison_file, dpi=300, bbox_inches='tight')
        print(f"  综合对比图已保存: {comparison_file}")
        
        plt.close(fig)
        
    except Exception as e:
        print(f"  错误: 绘制综合对比图时出错: {e}")
    
    print("\n响应图绘制完成!")
    print(f"所有图像已保存在: {output_dir}")


def main():
    """主函数：绘制台站响应图"""
    
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
    
    plot_station_responses()


if __name__ == "__main__":
    main() 