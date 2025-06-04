#!/usr/bin/env python3
"""
白色背景PPSD配色方案对比工具

此脚本专门展示白色背景的配色方案在PPSD图中的效果，适合科技报告和学术论文。
参考图片特征：白色背景，清晰的颜色渐变

使用方法:
    python tests/white_background_colormap_comparison.py
"""

import matplotlib.pyplot as plt
import numpy as np
import os


def create_white_background_colormap_comparison():
    """创建白色背景PPSD配色方案对比图"""
    
    # 白色背景配色方案 - 按照与参考图片的相似度和专业性排序
    white_bg_colormaps = {
        'YlOrRd': '黄-橙-红渐变，白色背景，最接近参考图片配色',
        'Reds': '白-红渐变，经典科技报告配色',
        'Blues': '白-蓝渐变，专业清爽配色',
        'Purples': '白-紫渐变，优雅专业配色',
        'Oranges': '白-橙渐变，温暖专业配色',
        'BuPu': '蓝-紫渐变，白色背景，现代配色',
        'GnBu': '绿-蓝渐变，白色背景，自然配色',
        'OrRd': '橙-红渐变，白色背景，高对比度'
    }
    
    # 创建示例数据（模拟PPSD概率密度）
    # 使用与参考图片类似的频率和功率谱密度范围
    periods = np.logspace(-2, 2, 100)  # 0.01 到 100 秒
    frequencies = 1.0 / periods
    power_db = np.linspace(-200, -50, 150)  # -200 到 -50 dB
    
    # 创建网格
    freq_mesh, db_mesh = np.meshgrid(frequencies, power_db)
    
    # 模拟PPSD概率密度分布 - 模仿参考图片的特征
    # 主要噪声峰在1-10秒周期（0.1-1 Hz）
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
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    fig.suptitle('白色背景PPSD配色方案对比 - 科技报告专用\n'
                 '目标：白色背景，清晰渐变，适合打印和学术发表', 
                 fontsize=16, fontweight='bold')
    
    axes = axes.flatten()
    
    for i, (cmap_name, description) in enumerate(white_bg_colormaps.items()):
        ax = axes[i]
        
        # 绘制PPSD概率密度图
        im = ax.pcolormesh(freq_mesh, db_mesh, Z, 
                          shading='auto', cmap=cmap_name, 
                          vmin=0, vmax=0.3)  # 匹配参考图片的概率范围
        
        # 设置坐标轴 - 匹配参考图片
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
        title_text = f'{cmap_name}\n{description}'
        ax.set_title(title_text, fontsize=11, fontweight='bold')
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Probability', fontsize=9)
        cbar.ax.tick_params(labelsize=8)
        
        # 设置颜色条范围匹配参考图片
        cbar.set_ticks([0.0, 0.1, 0.2, 0.3])
        
        # 设置白色背景
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    
    # 确保输出目录存在
    output_dir = './output/plots'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存对比图
    output_path = os.path.join(output_dir, 'white_background_colormap_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"白色背景PPSD配色方案对比图已保存: {output_path}")
    
    # 创建配色推荐报告
    create_white_background_recommendation()


def create_white_background_recommendation():
    """创建白色背景配色方案推荐报告"""
    
    print("\n" + "="*70)
    print("白色背景PPSD配色方案推荐报告")
    print("="*70)
    print("目标：白色背景，适合科技报告和学术论文")
    print()
    
    recommendations = [
        {
            "name": "YlOrRd",
            "match": "★★★★★",
            "description": "最佳匹配 - 黄-橙-红渐变，白色背景，最接近参考图片",
            "pros": ["白色背景", "颜色渐变接近参考图片", "高对比度", "打印友好"],
            "cons": ["在某些情况下可能过于鲜艳"],
            "use_case": "最推荐用于匹配参考图片配色"
        },
        {
            "name": "Reds",
            "match": "★★★★☆",
            "description": "经典选择 - 白色到红色渐变，科技报告标准配色",
            "pros": ["经典科技配色", "白色背景", "打印效果好", "广泛认知"],
            "cons": ["单色调，缺少颜色变化"],
            "use_case": "科技报告和学术论文的标准选择"
        },
        {
            "name": "Blues",
            "match": "★★★★☆",
            "description": "专业选择 - 白色到蓝色渐变，清爽专业",
            "pros": ["专业感强", "白色背景", "视觉舒适", "色盲友好"],
            "cons": ["缺少暖色调"],
            "use_case": "专业技术文档和演示"
        },
        {
            "name": "BuPu",
            "match": "★★★☆☆",
            "description": "现代选择 - 蓝色到紫色渐变，现代感强",
            "pros": ["现代设计", "白色背景", "颜色过渡自然"],
            "cons": ["可能不够传统"],
            "use_case": "现代科技报告和在线展示"
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['name'].upper()} {rec['match']}")
        print(f"   描述: {rec['description']}")
        print(f"   优点: {', '.join(rec['pros'])}")
        print(f"   缺点: {', '.join(rec['cons'])}")
        print(f"   适用场景: {rec['use_case']}")
        print()
    
    print("配置建议:")
    print("在 input/config_plot.toml 中设置:")
    print('  standard_cmap = "YlOrRd"    # 推荐：最接近参考图片，白色背景')
    print('  # 或者')
    print('  standard_cmap = "Reds"      # 备选：经典科技报告配色')
    print('  # 或者')
    print('  standard_cmap = "Blues"     # 备选：专业蓝色配色')
    print()
    
    print("特别说明:")
    print("- 所有推荐配色方案都具有白色背景")
    print("- 适合打印输出和学术发表")
    print("- 在黑白打印时仍能保持良好的对比度")
    print("- 符合科技报告的专业标准")


def main():
    """主函数"""
    print("正在生成白色背景PPSD配色方案对比图...")
    
    try:
        create_white_background_colormap_comparison()
        print("\n白色背景PPSD配色方案对比完成！")
        
    except Exception as e:
        print(f"生成对比图时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 