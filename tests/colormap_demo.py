#!/usr/bin/env python3
"""
PPSD配色方案演示脚本

此脚本展示不同配色方案在PPSD图中的效果，帮助用户选择最适合的清爽配色。

使用方法:
    python tests/colormap_demo.py
"""

import matplotlib.pyplot as plt
import numpy as np
import os


def create_colormap_demo():
    """创建配色方案演示图"""
    
    # 清爽配色方案列表
    fresh_colormaps = {
        'Blues': '蓝色系 - 经典清爽，适合科学报告',
        'BuGn': '蓝绿色系 - 自然清新，视觉舒适',
        'GnBu': '绿蓝色系 - 海洋风格，层次丰富',
        'Purples': '紫色系 - 优雅高贵，对比柔和',
        'viridis_r': '反向viridis - 现代感强，色彩平衡',
        'plasma_r': '反向plasma - 温暖清新，渐变自然',
        'cividis': '色盲友好 - 无障碍设计，科学标准',
        'YlGnBu': '黄绿蓝 - 三色渐变，层次清晰'
    }
    
    # 创建示例数据（模拟PPSD概率密度）
    x = np.linspace(0.01, 100, 100)  # 周期
    y = np.linspace(-200, -50, 150)  # dB
    X, Y = np.meshgrid(x, y)
    
    # 模拟PPSD概率密度分布
    Z = np.exp(-((np.log10(X) - 0.5)**2 / 0.5 + (Y + 120)**2 / 1000))
    Z += 0.3 * np.exp(-((np.log10(X) - 1.5)**2 / 0.3 + (Y + 100)**2 / 800))
    Z += 0.2 * np.exp(-((np.log10(X) + 0.5)**2 / 0.8 + (Y + 140)**2 / 1200))
    
    # 创建演示图
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    fig.suptitle('PPSD清爽配色方案演示', fontsize=16, fontweight='bold')
    
    for i, (cmap_name, description) in enumerate(fresh_colormaps.items()):
        row = i // 4
        col = i % 4
        ax = axes[row, col]
        
        # 绘制PPSD概率密度图
        im = ax.contourf(X, Y, Z, levels=20, cmap=cmap_name, alpha=0.8)
        
        # 添加等高线
        ax.contour(X, Y, Z, levels=10, colors='white', 
                   alpha=0.3, linewidths=0.5)
        
        # 设置坐标轴
        ax.set_xscale('log')
        ax.set_xlabel('周期 (s)', fontsize=10)
        ax.set_ylabel('功率谱密度 (dB)', fontsize=10)
        title_text = f'{cmap_name}\n{description}'
        ax.set_title(title_text, fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('概率密度', fontsize=9)
        cbar.ax.tick_params(labelsize=8)
    
    plt.tight_layout()
    
    # 保存演示图
    output_dir = './output/plots/'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'colormap_demo.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"配色方案演示图已保存: {output_path}")
    
    return output_path


def print_colormap_recommendations():
    """打印配色方案推荐"""
    print("\n" + "="*60)
    print("PPSD清爽配色方案推荐")
    print("="*60)
    
    recommendations = {
        "科学报告推荐": {
            "Blues": "经典蓝色系，专业感强，适合学术论文",
            "cividis": "色盲友好，符合科学可视化标准"
        },
        "视觉舒适推荐": {
            "BuGn": "蓝绿渐变，自然清新，长时间观看不疲劳",
            "GnBu": "绿蓝渐变，海洋风格，层次丰富"
        },
        "现代风格推荐": {
            "viridis_r": "反向viridis，现代感强，色彩平衡",
            "YlGnBu": "三色渐变，层次清晰，对比度好"
        },
        "优雅风格推荐": {
            "Purples": "紫色系，优雅高贵，对比柔和",
            "plasma_r": "反向plasma，温暖清新"
        }
    }
    
    for category, cmaps in recommendations.items():
        print(f"\n{category}:")
        for cmap, desc in cmaps.items():
            print(f"  • {cmap:12} - {desc}")
    
    print("\n配置方法:")
    print("在 input/config_plot.toml 中修改:")
    print('  standard_cmap = "Blues"      # 标准PPSD图')
    print('  spectrogram_cmap = "BuGn"    # 频谱图')
    print('  temporal_cmap = "GnBu"       # 时间演化图')


def main():
    """主函数"""
    print("开始生成PPSD配色方案演示...")
    
    try:
        # 创建配色方案演示
        demo_path = create_colormap_demo()
        
        # 打印推荐信息
        print_colormap_recommendations()
        
        print("\n演示完成！")
        print(f"请查看生成的演示图: {demo_path}")
        print("根据演示效果选择您喜欢的配色方案。")
        
    except Exception as e:
        print(f"生成演示时发生错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main()) 