#!/usr/bin/env python3
"""
科技报告PPSD配色方案演示脚本

此脚本展示适合科技报告的白色背景配色方案，包括对比度分析和可读性评估。

使用方法:
    python tests/scientific_colormap_demo.py
"""

import matplotlib.pyplot as plt
import numpy as np
import os


def create_scientific_colormap_demo():
    """创建科技报告配色方案演示图"""
    
    # 科技报告专业配色方案
    scientific_colormaps = {
        'Reds': '标准PPSD图 - 红色渐变，高对比度，突出重要数据',
        'Oranges': '频谱图 - 橙色渐变，温暖专业，易于区分层次',
        'Blues': '时间演化图 - 蓝色渐变，经典科学配色，沉稳可靠',
        'Purples': '备选方案 - 紫色渐变，优雅专业，适合高端报告',
        'Greys': '黑白打印 - 灰度渐变，适合黑白印刷，成本友好',
        'YlOrRd': '热力图风格 - 黄橙红渐变，直观表达强度变化'
    }
    
    # 创建示例数据（模拟PPSD概率密度）
    x = np.linspace(0.01, 100, 100)  # 周期
    y = np.linspace(-200, -50, 150)  # dB
    X, Y = np.meshgrid(x, y)
    
    # 模拟PPSD概率密度分布
    Z = np.exp(-((np.log10(X) - 0.5)**2 / 0.5 + (Y + 120)**2 / 1000))
    
    # 添加一些噪声和特征
    Z += 0.3 * np.exp(-((np.log10(X) - 1.5)**2 / 0.2 + (Y + 140)**2 / 500))
    Z += 0.2 * np.exp(-((np.log10(X) + 0.5)**2 / 0.3 + (Y + 100)**2 / 800))
    
    # 创建图像
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('科技报告PPSD配色方案对比\n白色背景专业配色，适合学术发表和技术报告', 
                 fontsize=16, fontweight='bold', y=0.95)
    
    axes = axes.flatten()
    
    for i, (cmap_name, description) in enumerate(scientific_colormaps.items()):
        ax = axes[i]
        
        # 绘制PPSD概率密度图
        im = ax.contourf(X, Y, Z, levels=20, cmap=cmap_name, alpha=0.8)
        
        # 设置坐标轴
        ax.set_xscale('log')
        ax.set_xlim(0.01, 100)
        ax.set_ylim(-200, -50)
        ax.set_xlabel('周期 (秒)', fontsize=10)
        ax.set_ylabel('功率谱密度 (dB)', fontsize=10)
        ax.set_title(f'{cmap_name}\n{description}', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('概率密度', fontsize=9)
        
        # 添加等高线增强可读性
        ax.contour(X, Y, Z, levels=10, colors='white', 
                   alpha=0.4, linewidths=0.5)
    
    plt.tight_layout()
    
    # 确保输出目录存在
    output_dir = './output/plots'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存图像
    output_path = os.path.join(output_dir, 'scientific_colormap_demo.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"科技报告配色方案演示图已保存: {output_path}")
    
    # 创建配色特性分析
    create_colormap_analysis()


def create_colormap_analysis():
    """创建配色方案特性分析图"""
    
    # 配色方案特性数据
    colormaps = ['Reds', 'Oranges', 'Blues', 'Purples', 'Greys', 'YlOrRd']
    
    # 评估指标 (1-10分)
    metrics = {
        '对比度': [9, 8, 8, 7, 10, 9],
        '可读性': [9, 8, 9, 8, 9, 8],
        '专业感': [9, 8, 10, 9, 8, 7],
        '打印友好': [8, 7, 8, 7, 10, 6],
        '色盲友好': [7, 6, 8, 6, 10, 5]
    }
    
    # 创建雷达图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 左侧：配色方案对比条形图
    x = np.arange(len(colormaps))
    width = 0.15
    
    colors = ['#d62728', '#ff7f0e', '#1f77b4', '#9467bd', '#7f7f7f', '#bcbd22']
    
    for i, (metric, scores) in enumerate(metrics.items()):
        ax1.bar(x + i * width, scores, width, label=metric, alpha=0.8)
    
    ax1.set_xlabel('配色方案', fontweight='bold')
    ax1.set_ylabel('评分 (1-10)', fontweight='bold')
    ax1.set_title('科技报告配色方案特性评估', fontweight='bold', fontsize=14)
    ax1.set_xticks(x + width * 2)
    ax1.set_xticklabels(colormaps, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 10)
    
    # 右侧：推荐使用场景
    scenarios = {
        'Reds': '标准PPSD图\n高对比度数据展示',
        'Oranges': '频谱图\n温暖专业风格',
        'Blues': '时间演化图\n经典科学配色',
        'Purples': '高端报告\n优雅专业风格',
        'Greys': '黑白打印\n成本友好方案',
        'YlOrRd': '热力图\n直观强度表达'
    }
    
    ax2.axis('off')
    ax2.set_title('推荐使用场景', fontweight='bold', fontsize=14, pad=20)
    
    y_pos = 0.9
    for cmap, scenario in scenarios.items():
        ax2.text(0.1, y_pos, f'• {cmap}:', fontweight='bold', fontsize=12, 
                transform=ax2.transAxes)
        ax2.text(0.3, y_pos, scenario, fontsize=11, 
                transform=ax2.transAxes)
        y_pos -= 0.13
    
    # 添加配色优势说明
    ax2.text(0.1, 0.15, '配色优势:', fontweight='bold', fontsize=12, 
            transform=ax2.transAxes)
    advantages = [
        '• 白色背景，适合科技报告',
        '• 单色渐变，层次清晰',
        '• 高对比度，数据突出',
        '• 打印友好，成本低廉',
        '• 专业美观，学术标准'
    ]
    
    y_pos = 0.1
    for advantage in advantages:
        ax2.text(0.1, y_pos, advantage, fontsize=10, 
                transform=ax2.transAxes)
        y_pos -= 0.03
    
    plt.tight_layout()
    
    # 保存分析图
    output_path = './output/plots/scientific_colormap_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"配色方案特性分析图已保存: {output_path}")


def main():
    """主函数"""
    print("正在生成科技报告配色方案演示...")
    
    try:
        create_scientific_colormap_demo()
        print("\n科技报告配色方案演示完成！")
        print("\n当前配置的科技报告配色方案:")
        print("• 标准PPSD图: Reds (红色渐变)")
        print("• 频谱图: Oranges (橙色渐变)")
        print("• 时间演化图: Blues (蓝色渐变)")
        print("\n特点:")
        print("• 白色背景，适合科技报告")
        print("• 高对比度，数据清晰可见")
        print("• 专业美观，符合学术标准")
        print("• 打印友好，黑白打印效果好")
        
    except Exception as e:
        print(f"生成演示图时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 