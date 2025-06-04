#!/usr/bin/env python3
"""
定性配色方案PPSD对比工具

此脚本展示定性配色方案(Qualitative colormaps)在PPSD图中的效果。
定性配色方案通常用于分类数据，在PPSD连续数据中会产生独特的视觉效果。

使用方法:
    python tests/qualitative_colormap_comparison.py
"""

import matplotlib.pyplot as plt
import numpy as np
import os


def create_qualitative_colormap_comparison():
    """创建定性配色方案PPSD对比图"""
    
    # 定性配色方案 - 按照视觉效果和实用性排序
    qualitative_colormaps = {
        'Set1': '经典定性配色，鲜明对比，8种颜色',
        'Set2': '柔和定性配色，视觉舒适，8种颜色',
        'Set3': '淡雅定性配色，层次丰富，12种颜色',
        'Paired': '成对配色，相近色彩成对，12种颜色',
        'Accent': '强调色配色，高对比度，8种颜色',
        'Dark2': '深色定性配色，沉稳专业，8种颜色',
        'Pastel1': '柔和粉彩配色，温和淡雅，9种颜色',
        'tab10': 'Tableau风格，现代感强，10种颜色'
    }
    
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
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    fig.suptitle('定性配色方案PPSD对比 - Qualitative Colormaps\n'
                 '注意：定性配色用于连续数据会产生分段效果', 
                 fontsize=16, fontweight='bold')
    
    axes = axes.flatten()
    
    for i, (cmap_name, description) in enumerate(qualitative_colormaps.items()):
        ax = axes[i]
        
        # 绘制PPSD概率密度图
        im = ax.pcolormesh(freq_mesh, db_mesh, Z, 
                          shading='auto', cmap=cmap_name, 
                          vmin=0, vmax=0.3)  # 匹配参考图片的概率范围
        
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
        title_text = f'{cmap_name}\n{description}'
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
    output_path = os.path.join(output_dir, 'qualitative_colormap_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"定性配色方案对比图已保存: {output_path}")
    
    # 创建配色推荐报告
    create_qualitative_recommendation()


def create_qualitative_recommendation():
    """创建定性配色方案推荐报告"""
    
    print("\n" + "="*70)
    print("定性配色方案推荐报告")
    print("="*70)
    print("注意：定性配色方案用于连续PPSD数据会产生分段效果")
    print()
    
    recommendations = [
        {
            "name": "Set1",
            "match": "★★★★☆",
            "description": "经典定性配色 - 鲜明对比，8种颜色",
            "pros": ["颜色鲜明", "对比度高", "经典配色", "易于区分"],
            "cons": ["分段效果明显", "可能过于鲜艳", "不够平滑"],
            "use_case": "需要强调不同概率区间的场合",
            "colors": 8
        },
        {
            "name": "Set2",
            "match": "★★★★☆",
            "description": "柔和定性配色 - 视觉舒适，8种颜色",
            "pros": ["颜色柔和", "视觉舒适", "专业感强", "适合长时间观看"],
            "cons": ["分段效果存在", "对比度中等"],
            "use_case": "专业报告和演示",
            "colors": 8
        },
        {
            "name": "Paired",
            "match": "★★★☆☆",
            "description": "成对配色 - 相近色彩成对，12种颜色",
            "pros": ["颜色层次丰富", "成对关系清晰", "12种颜色"],
            "cons": ["复杂度高", "可能混乱", "不适合连续数据"],
            "use_case": "需要展示复杂分类关系",
            "colors": 12
        },
        {
            "name": "tab10",
            "match": "★★★☆☆",
            "description": "Tableau风格 - 现代感强，10种颜色",
            "pros": ["现代设计", "颜色平衡", "商业感强"],
            "cons": ["分段明显", "不够科学", "商业化"],
            "use_case": "商业报告和现代演示",
            "colors": 10
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['name'].upper()} {rec['match']}")
        print(f"   描述: {rec['description']}")
        print(f"   颜色数量: {rec['colors']}种")
        print(f"   优点: {', '.join(rec['pros'])}")
        print(f"   缺点: {', '.join(rec['cons'])}")
        print(f"   适用场景: {rec['use_case']}")
        print()
    
    print("配置建议:")
    print("在 input/config_plot.toml 中设置:")
    print('  standard_cmap = "Set1"      # 推荐：经典定性配色，鲜明对比')
    print('  # 或者')
    print('  standard_cmap = "Set2"      # 备选：柔和定性配色，视觉舒适')
    print('  # 或者')
    print('  standard_cmap = "Paired"    # 备选：成对配色，层次丰富')
    print()
    
    print("重要说明:")
    print("⚠️  定性配色方案的特点和限制:")
    print("- 定性配色方案设计用于分类数据，不是连续数据")
    print("- 在PPSD连续概率数据中会产生明显的分段效果")
    print("- 颜色之间没有自然的渐变过渡")
    print("- 可能会误导数据的连续性解释")
    print()
    print("✅ 如果您确实需要定性配色效果:")
    print("- 可以用于强调不同的概率区间")
    print("- 适合需要明确区分数据范围的场合")
    print("- 建议配合详细的图例说明")
    print()
    print("🔄 替代建议:")
    print("- 如需连续渐变：推荐使用YlOrRd, Reds, Blues等连续配色")
    print("- 如需分段效果：可以考虑使用定性配色方案")


def create_mixed_comparison():
    """创建定性vs连续配色方案对比"""
    
    print("\n" + "="*70)
    print("定性 vs 连续配色方案效果对比")
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
        'Set1 (定性)': 'Set1',
        'YlOrRd (连续)': 'YlOrRd',
        'Set2 (定性)': 'Set2', 
        'Reds (连续)': 'Reds'
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('定性 vs 连续配色方案效果对比', fontsize=14, fontweight='bold')
    
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
    output_path = './output/plots/qualitative_vs_continuous_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"定性vs连续配色对比图已保存: {output_path}")


def main():
    """主函数"""
    print("正在生成定性配色方案PPSD对比图...")
    
    try:
        create_qualitative_colormap_comparison()
        create_mixed_comparison()
        print("\n定性配色方案对比完成！")
        
    except Exception as e:
        print(f"生成对比图时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 