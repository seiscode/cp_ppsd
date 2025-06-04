#!/usr/bin/env python3
"""
PPSD配色方案对比工具

此脚本展示多种配色方案在PPSD图中的效果，帮助用户选择最接近参考图片的配色方案。
参考图片特征：紫色-蓝色-绿色-黄色-红色渐变

使用方法:
    python tests/ppsd_colormap_comparison.py
"""

import matplotlib.pyplot as plt
import numpy as np
import os


def create_ppsd_colormap_comparison():
    """创建PPSD配色方案对比图"""
    
    # 候选配色方案 - 按照与参考图片的相似度排序
    candidate_colormaps = {
        'plasma': '紫-蓝-绿-黄-红渐变，最接近参考图片',
        'jet': '经典科学配色，蓝-绿-黄-红渐变',
        'turbo': '现代版jet，更平滑的蓝-绿-黄-红渐变',
        'viridis': '紫-蓝-绿-黄渐变，科学标准配色',
        'inferno': '黑-紫-红-黄渐变，高对比度',
        'magma': '黑-紫-红-白渐变，优雅风格',
        'rainbow': '彩虹配色，全光谱渐变',
        'gist_rainbow': '另一种彩虹配色，更鲜艳'
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
    fig.suptitle('PPSD配色方案对比 - 参考图片配色匹配\n'
                 '目标：紫色-蓝色-绿色-黄色-红色渐变', 
                 fontsize=16, fontweight='bold')
    
    axes = axes.flatten()
    
    for i, (cmap_name, description) in enumerate(candidate_colormaps.items()):
        ax = axes[i]
        
        # 绘制PPSD概率密度图
        im = ax.pcolormesh(freq_mesh, db_mesh, Z, 
                          shading='auto', cmap=cmap_name, 
                          vmin=0, vmax=0.3)  # 匹配参考图片的概率范围
        
        # 设置坐标轴 - 匹配参考图片
        ax.set_xscale('log')
        ax.set_xlim(0.01, 10)  # 频率范围
        ax.set_ylim(-200, -50)  # 功率谱密度范围
        ax.set_xlabel('频率 (Hz)', fontsize=10)
        ax.set_ylabel('功率谱密度 (dB)', fontsize=10)
        
        # 添加周期轴（顶部）
        ax2 = ax.twiny()
        ax2.set_xscale('log')
        ax2.set_xlim(100, 0.1)  # 周期范围（与频率相反）
        ax2.set_xlabel('周期 (秒)', fontsize=10)
        
        # 设置标题
        title_text = f'{cmap_name}\n{description}'
        ax.set_title(title_text, fontsize=11, fontweight='bold')
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('概率密度', fontsize=9)
        cbar.ax.tick_params(labelsize=8)
        
        # 设置颜色条范围匹配参考图片
        cbar.set_ticks([0.0, 0.1, 0.2, 0.3])
    
    plt.tight_layout()
    
    # 确保输出目录存在
    output_dir = './output/plots'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存对比图
    output_path = os.path.join(output_dir, 'ppsd_colormap_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"PPSD配色方案对比图已保存: {output_path}")
    
    # 创建配色推荐报告
    create_colormap_recommendation()


def create_colormap_recommendation():
    """创建配色方案推荐报告"""
    
    print("\n" + "="*70)
    print("PPSD配色方案推荐报告")
    print("="*70)
    print("参考图片特征：紫色-蓝色-绿色-黄色-红色渐变")
    print()
    
    recommendations = [
        {
            "name": "plasma",
            "match": "★★★★★",
            "description": "最佳匹配 - 紫-蓝-绿-黄-红渐变，与参考图片最相似",
            "pros": ["颜色渐变完全匹配", "科学可视化标准", "高对比度"],
            "cons": ["在某些显示器上可能过于鲜艳"]
        },
        {
            "name": "jet",
            "match": "★★★★☆",
            "description": "经典选择 - 蓝-绿-黄-红渐变，缺少紫色部分",
            "pros": ["经典科学配色", "广泛认知", "高对比度"],
            "cons": ["缺少低值紫色", "在某些情况下可能失真"]
        },
        {
            "name": "turbo",
            "match": "★★★★☆",
            "description": "现代版jet - 更平滑的蓝-绿-黄-红渐变",
            "pros": ["比jet更平滑", "感知均匀性更好", "现代设计"],
            "cons": ["缺少紫色部分", "相对较新的配色"]
        },
        {
            "name": "viridis",
            "match": "★★★☆☆",
            "description": "科学标准 - 紫-蓝-绿-黄渐变，缺少红色",
            "pros": ["感知均匀", "色盲友好", "科学标准"],
            "cons": ["缺少红色高值部分", "整体偏暗"]
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['name'].upper()} {rec['match']}")
        print(f"   描述: {rec['description']}")
        print(f"   优点: {', '.join(rec['pros'])}")
        print(f"   缺点: {', '.join(rec['cons'])}")
        print()
    
    print("配置建议:")
    print("在 input/config_plot.toml 中设置:")
    print('  standard_cmap = "plasma"    # 推荐：最接近参考图片')
    print('  # 或者')
    print('  standard_cmap = "jet"       # 备选：经典科学配色')
    print()
    print("当前配置已设置为: plasma")


def main():
    """主函数"""
    print("正在生成PPSD配色方案对比图...")
    
    try:
        create_ppsd_colormap_comparison()
        print("\nPPSD配色方案对比完成！")
        
    except Exception as e:
        print(f"生成对比图时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 