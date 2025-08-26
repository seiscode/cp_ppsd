#!/usr/bin/env python3
"""
Author:
    muly (muly@cea-igp.ac.cn)
license:
    MIT License
    (https://opensource.org/licenses/MIT)
"""
"""
自定义配色方案PPSD对比工具

此脚本展示自定义配色方案在PPSD图中的效果，包括基于现有配色方案的修改版本。
这些配色方案针对地球物理数据可视化进行了优化。

使用方法:
    python tests/custom_colormap_comparison.py
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cp_ppsd.custom_colormaps import create_custom_colormaps, list_custom_colormaps


def create_custom_colormap_comparison():
    """创建自定义配色方案PPSD对比图"""
    
    # 获取自定义配色方案
    custom_cmaps = create_custom_colormaps()
    descriptions = list_custom_colormaps()
    
    # 创建示例数据（模拟PPSD概率密度）
    periods = np.logspace(-2, 2, 100)  # 0.01 到 100 秒
    frequencies = 1.0 / periods
    power_db = np.linspace(-200, -50, 150)  # -200 到 -50 dB
    
    # 创建网格
    freq_mesh, db_mesh = np.meshgrid(frequencies, power_db)
    
    # 模拟PPSD概率密度分布
    Z = np.zeros_like(freq_mesh)
    
    # 低频噪声峰 (长周期，低频)
    Z += 0.25 * np.exp(-((np.log10(freq_mesh) - np.log10(0.2))**2 / 0.3 + 
                         (db_mesh + 130)**2 / 400))
    
    # 中频噪声峰
    Z += 0.30 * np.exp(-((np.log10(freq_mesh) - np.log10(2.0))**2 / 0.2 + 
                         (db_mesh + 140)**2 / 300))
    
    # 高频噪声
    Z += 0.15 * np.exp(-((np.log10(freq_mesh) - np.log10(10.0))**2 / 0.4 + 
                         (db_mesh + 120)**2 / 500))
    
    # 背景噪声
    Z += 0.05 * np.exp(-((db_mesh + 160)**2 / 1000))
    
    # 创建对比图
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('自定义配色方案PPSD对比 - Custom Colormaps\n'
                 '基于现有配色方案的优化版本，针对地球物理数据可视化', 
                 fontsize=16, fontweight='bold')
    
    axes = axes.flatten()
    
    for i, (cmap_name, cmap) in enumerate(custom_cmaps.items()):
        ax = axes[i]
        
        # 绘制PPSD概率密度图
        im = ax.pcolormesh(freq_mesh, db_mesh, Z, 
                          shading='auto', cmap=cmap, 
                          vmin=0, vmax=0.3)
        
        # 设置坐标轴
        ax.set_xscale('log')
        ax.set_xlim(0.01, 10)  # 频率范围
        ax.set_ylim(-200, -50)  # 功率谱密度范围
        ax.set_xlabel('Frequency (Hz)', fontsize=10)
        ax.set_ylabel('Power (dB)', fontsize=10)
        
        # 添加周期轴（顶部）
        ax2 = ax.twiny()
        ax2.set_xscale('log')
        ax2.set_xlim(100, 0.1)  # 周期范围（与频率相反）
        ax2.set_xlabel('Period (sec)', fontsize=10)
        
        # 设置标题
        title_text = f'{cmap_name}\n{descriptions[cmap_name]}'
        ax.set_title(title_text, fontsize=11, fontweight='bold')
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Probability', fontsize=9)
        cbar.ax.tick_params(labelsize=8)
        
        # 设置颜色条范围
        cbar.set_ticks([0.0, 0.1, 0.2, 0.3])
        
        # 设置白色背景
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    
    # 确保输出目录存在
    output_dir = './output/plots'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存对比图
    output_path = os.path.join(output_dir, 'custom_colormap_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"自定义配色方案对比图已保存: {output_path}")
    
    # 创建配色推荐报告
    create_custom_recommendation()


def create_custom_recommendation():
    """创建自定义配色方案推荐报告"""
    
    print("\n" + "="*70)
    print("自定义配色方案推荐报告")
    print("="*70)
    print("基于现有配色方案的优化版本，针对地球物理数据可视化")
    print()
    
    recommendations = [
        {
            "name": "viridis_custom",
            "match": "★★★★★",
            "description": "Viridis自定义版本 - 去除深色部分，突出中高值",
            "base": "viridis",
            "range": "0.3-1.0",
            "pros": ["去除深色部分", "突出中高值", "连续渐变", "科学标准"],
            "cons": ["可能丢失低值信息"],
            "use_case": "标准PPSD可视化，突出高概率区域",
            "colors": "连续"
        },
        {
            "name": "ocean_custom",
            "match": "★★★★☆",
            "description": "Ocean水色配色 - 蓝绿色调，适合海洋数据",
            "base": "ocean",
            "range": "0.5-1.0",
            "pros": ["蓝绿色调", "海洋主题", "视觉舒适", "专业感强"],
            "cons": ["色彩范围有限", "可能不够鲜明"],
            "use_case": "海洋地震学、水下噪声分析",
            "colors": "连续"
        },
        {
            "name": "ocean_r_custom",
            "match": "★★★★☆",
            "description": "Ocean反向配色 - 浅色到深色，优雅渐变",
            "base": "ocean_r",
            "range": "0.0-0.6",
            "pros": ["浅色背景", "优雅渐变", "打印友好", "对比度好"],
            "cons": ["深色可能过暗"],
            "use_case": "学术论文、正式报告",
            "colors": "连续"
        },
        {
            "name": "hot_r_custom",
            "match": "★★★☆☆",
            "description": "Hot反向配色 - 去除过亮部分，温暖色调",
            "base": "hot_r",
            "range": "0.0-0.8",
            "pros": ["温暖色调", "去除过亮部分", "视觉吸引", "对比度高"],
            "cons": ["可能过于鲜艳", "不够科学"],
            "use_case": "演示展示、教学用途",
            "colors": "连续"
        },
        {
            "name": "plasma_custom",
            "match": "★★★★☆",
            "description": "Plasma完整配色 - 紫-蓝-绿-黄-红渐变",
            "base": "plasma",
            "range": "0.0-1.0",
            "pros": ["完整色彩范围", "现代感强", "高对比度", "感知均匀"],
            "cons": ["可能过于鲜艳"],
            "use_case": "现代科学可视化、高对比度需求",
            "colors": "连续"
        },
        {
            "name": "CMRmap_r_custom",
            "match": "★★★☆☆",
            "description": "CMRmap反向配色 - 优化对比度，科学可视化",
            "base": "CMRmap_r",
            "range": "0.0-0.6",
            "pros": ["科学标准", "优化对比度", "传统配色", "专业认知"],
            "cons": ["色彩单调", "缺少变化"],
            "use_case": "传统科学可视化、保守需求",
            "colors": "连续"
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['name'].upper()} {rec['match']}")
        print(f"   描述: {rec['description']}")
        print(f"   基础配色: {rec['base']} (范围: {rec['range']})")
        print(f"   颜色类型: {rec['colors']}")
        print(f"   优点: {', '.join(rec['pros'])}")
        print(f"   缺点: {', '.join(rec['cons'])}")
        print(f"   适用场景: {rec['use_case']}")
        print()
    
    print("配置建议:")
    print("在 input/config_plot.toml 中设置:")
    print('  standard_cmap = "viridis_custom"    # 推荐：去除深色，突出中高值')
    print('  # 或者')
    print('  standard_cmap = "ocean_custom"      # 备选：蓝绿色调，海洋主题')
    print('  # 或者')
    print('  standard_cmap = "plasma_custom"     # 备选：现代感强，高对比度')
    print()
    
    print("技术说明:")
    print("自定义配色方案的优势:")
    print("- 基于成熟配色方案，保证质量")
    print("- 针对PPSD数据特点进行优化")
    print("- 去除不适合的颜色范围")
    print("- 提高数据可读性和美观度")
    print()
    print("实现原理:")
    print("- 使用ListedColormap截取原配色方案的特定范围")
    print("- 通过np.linspace控制颜色采样点")
    print("- 保持原配色方案的色彩特性和渐变质量")
    print()
    print("应用建议:")
    print("- viridis_custom: 通用PPSD可视化首选")
    print("- ocean_custom: 海洋地震学专用")
    print("- plasma_custom: 现代科学可视化")


def create_comparison_with_original():
    """创建自定义配色方案与原始配色方案的对比"""
    
    print("\n" + "="*70)
    print("自定义 vs 原始配色方案效果对比")
    print("="*70)
    
    # 创建示例数据
    periods = np.logspace(-2, 2, 50)
    frequencies = 1.0 / periods
    power_db = np.linspace(-200, -50, 75)
    freq_mesh, db_mesh = np.meshgrid(frequencies, power_db)
    
    # 简化的PPSD数据
    Z = 0.3 * np.exp(-((np.log10(freq_mesh) - np.log10(1.0))**2 / 0.5 + 
                       (db_mesh + 140)**2 / 500))
    
    # 对比配色方案
    comparison_maps = {
        'viridis (原始)': 'viridis',
        'viridis_custom': 'viridis_custom',
        'ocean (原始)': 'ocean', 
        'ocean_custom': 'ocean_custom'
    }
    
    # 注册自定义配色方案
    from cp_ppsd.custom_colormaps import register_custom_colormaps
    register_custom_colormaps()
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('自定义 vs 原始配色方案效果对比', fontsize=14, fontweight='bold')
    
    axes = axes.flatten()
    
    for i, (title, cmap) in enumerate(comparison_maps.items()):
        ax = axes[i]
        
        im = ax.pcolormesh(freq_mesh, db_mesh, Z, 
                          shading='auto', cmap=cmap, vmin=0, vmax=0.3)
        
        ax.set_xscale('log')
        ax.set_xlim(0.1, 10)
        ax.set_ylim(-180, -100)
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Power (dB)')
        ax.set_title(title, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Probability')
    
    plt.tight_layout()
    
    # 保存对比图
    output_path = './output/plots/custom_vs_original_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"自定义vs原始配色对比图已保存: {output_path}")


def main():
    """主函数"""
    print("正在生成自定义配色方案PPSD对比图...")
    
    try:
        create_custom_colormap_comparison()
        create_comparison_with_original()
        print("\n自定义配色方案对比完成！")
        
    except Exception as e:
        print(f"生成对比图时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 
