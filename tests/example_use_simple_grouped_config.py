#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: 
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)

使用简单分组配置的示例

演示如何在实际PPSD绘图代码中使用按绘图类型分组的配置
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cp_ppsd.simple_config_adapter import SimpleConfigAdapter


def load_grouped_config(config_path: str):
    """
    加载分组配置并转换为兼容格式
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        适配后的配置字典
    """
    adapter = SimpleConfigAdapter(config_path)
    return adapter.get_config()


def simulate_ppsd_plotting(config):
    """
    模拟PPSD绘图过程，展示如何使用分组配置
    
    Args:
        config: 配置字典
    """
    print("=== 模拟PPSD绘图过程 ===\n")
    
    # 获取要绘制的图形类型
    plot_types = config.get('plot_types', ['standard'])
    print(f"准备绘制图形类型: {plot_types}")
    
    for plot_type in plot_types:
        print(f"\n--- 绘制 {plot_type} 图 ---")
        
        if plot_type == 'standard':
            print("标准PPSD图配置:")
            print(f"  显示直方图: {config.get('show_histogram', True)}")
            print(f"  周期范围: {config.get('period_lim', [0.01, 1000.0])}")
            print(f"  配色方案: {config.get('standard_cmap', 'viridis')}")
            
            # 百分位数线
            if config.get('show_percentiles', False):
                print("  百分位数线:")
                print(f"    百分位数: {config.get('percentiles', [])}")
                print(f"    颜色: {config.get('percentile_color', 'gray')}")
                print(f"    线宽: {config.get('percentile_linewidth', 1.0)}")
                print(f"    样式: {config.get('percentile_linestyle', '--')}")
            
            # 皮特森噪声模型
            if config.get('show_noise_models', False):
                print("  皮特森噪声模型:")
                print(f"    NLNM颜色: {config.get('peterson_nlnm_color', 'blue')}")
                print(f"    NHNM颜色: {config.get('peterson_nhnm_color', 'red')}")
                print(f"    线宽: {config.get('peterson_linewidth', 1.0)}")
            
            # 统计线
            if config.get('show_mode', False):
                print("  众数线:")
                print(f"    颜色: {config.get('mode_color', 'orange')}")
                print(f"    线宽: {config.get('mode_linewidth', 1.0)}")
            
            if config.get('show_mean', False):
                print("  均值线:")
                print(f"    颜色: {config.get('mean_color', 'green')}")
                print(f"    线宽: {config.get('mean_linewidth', 1.0)}")
        
        elif plot_type == 'temporal':
            print("时间演化图配置:")
            periods = config.get('temporal_plot_periods', [1.0, 8.0, 20.0])
            print(f"  绘制周期: {periods}")
            time_format = config.get('time_format_x_temporal', '%H:%M')
            print(f"  时间格式: {time_format}")
            cmap = config.get('temporal_cmap', 'Blues')
            print(f"  配色方案: {cmap}")
        
        elif plot_type == 'spectrogram':
            print("频谱图配置:")
            clim = config.get('spectrogram_clim', [-180, -100])
            print(f"  颜色范围: {clim}")
            time_format = config.get('time_format_x_spectrogram', '%Y-%m-%d')
            print(f"  时间格式: {time_format}")
            cmap = config.get('spectrogram_cmap', 'viridis')
            print(f"  配色方案: {cmap}")


def compare_configurations():
    """比较原始配置与分组配置的优势"""
    print("\n=== 配置组织对比 ===\n")
    
    print("1. 传统配置 (config_plot.toml):")
    print("   [X] 所有参数混合在[args]中")
    print("   [X] 百分位数参数分散")
    print("   [X] 不同绘图类型参数混杂")
    print("   [X] 参数关联性不明确")
    
    print("\n2. 简单分组配置 (config_plot_simple_grouped.toml):")
    print("   [√] 按绘图类型清晰分组")
    print("   [√] 相关参数集中管理")
    print("   [√] standard分组包含所有标准图参数")
    print("   [√] temporal和spectrogram参数独立")
    print("   [√] 百分位数、皮特森曲线参数关联明确")
    
    print("\n3. 分组结构优势:")
    print("   [DIR] [standard] - 标准PPSD图的所有配置")
    print("     ├── 基础显示参数")
    print("     ├── 百分位数线配置组")
    print("     ├── 皮特森曲线配置组")
    print("     ├── 众数线配置组")
    print("     └── 均值线配置组")
    print("   [DIR] [temporal] - 时间演化图专用配置")
    print("   [DIR] [spectrogram] - 频谱图专用配置")


def main():
    """主函数：演示简单分组配置的使用"""
    
    # 加载分组配置
    config_path = "input/config_plot_simple_grouped.toml"
    config = load_grouped_config(config_path)
    
    # 模拟绘图过程
    simulate_ppsd_plotting(config)
    
    # 配置对比
    compare_configurations()
    
    print("\n=== 使用建议 ===")
    print("1. 现有代码无需修改 - 适配器自动转换")
    print("2. 配置文件结构清晰 - 按功能分组")
    print("3. 参数关联明确 - 相关参数集中")
    print("4. 维护简单 - 添加新参数时位置明确")
    print("5. 向后兼容 - 支持现有参数名")


if __name__ == "__main__":
    main() 