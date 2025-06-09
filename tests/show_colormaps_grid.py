#!/usr/bin/env python3
"""
配色方案网格展示脚本

按照一行两列的布局展示所有自定义配色方案，
方便用户比较和选择合适的配色方案。

作者: muly
日期: 2025年6月7日
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from cp_ppsd.custom_colormaps import create_custom_colormaps, list_custom_colormaps


def setup_chinese_fonts():
    """设置中文字体支持"""
    try:
        # 尝试多种中文字体配置方案
        font_options = [
            'WenQuanYi Micro Hei',
            'WenQuanYi Zen Hei', 
            'Noto Sans CJK SC',
            'Source Han Sans CN',
            'DejaVu Sans',
            'SimHei',
            'Microsoft YaHei',
            'SimSun',
            'PingFang SC',
            'Heiti SC',
            'STHeiti',
            'Arial Unicode MS',
            'Liberation Sans'
        ]

        # 获取系统可用字体列表
        available_fonts = [f.name for f in fm.fontManager.ttflist]

        # 寻找可用的中文字体
        chinese_font = None
        for font in font_options:
            if font and font in available_fonts:
                chinese_font = font
                break

        # 设置字体
        if chinese_font:
            plt.rcParams['font.sans-serif'] = [chinese_font, 'DejaVu Sans', 
                                               'Arial']
            print(f"✓ 设置中文字体: {chinese_font}")
        else:
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 
                                               'Liberation Sans']
            print("⚠ 未找到中文字体，使用默认字体")

        # 解决负号显示问题
        plt.rcParams['axes.unicode_minus'] = False

    except Exception as e:
        print(f"❌ 设置中文字体失败: {e}")


def create_gradient_data():
    """创建用于展示配色方案的渐变数据"""
    # 创建一个256x40的渐变条
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack([gradient] * 40)  # 重复40行，增加高度
    return gradient


def create_colormap_grid():
    """创建一行两列布局的配色方案展示图"""
    # 设置中文字体
    setup_chinese_fonts()
    
    # 获取配色方案
    custom_cmaps = create_custom_colormaps()
    descriptions = list_custom_colormaps()
    
    # 创建渐变数据
    gradient = create_gradient_data()
    
    # 配色方案名称列表（移除最后一个science_custom）
    cmap_names = list(custom_cmaps.keys())[:-1]
    n_cmaps = len(cmap_names)
    
    # 计算网格布局：一行两列
    n_cols = 2
    n_rows = (n_cmaps + n_cols - 1) // n_cols  # 向上取整
    
    # 创建图形（增加高度和间距避免文字重叠）
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, n_rows * 2.2))
    fig.suptitle('配色方案展示 - 一行两列布局', fontsize=18, fontweight='bold', y=0.96)
    
    # 确保axes是二维数组
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    elif n_cols == 1:
        axes = axes.reshape(-1, 1)
    
    # 展示每个配色方案
    for i, cmap_name in enumerate(cmap_names):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row, col]
        
        # 获取配色方案
        cmap = custom_cmaps[cmap_name]
        
        # 显示渐变条
        im = ax.imshow(gradient, aspect='auto', cmap=cmap, vmin=0, vmax=1)
        
        # 设置标题
        # 提取配色方案的简短描述
        desc = descriptions.get(cmap_name, '')
        short_desc = desc.split('-')[0].strip() if '-' in desc else desc[:35]
        
        title = f"{cmap_name}\n{short_desc}"
        ax.set_title(title, fontsize=9, fontweight='bold', pad=8)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('数值范围', fontsize=9)
        cbar.ax.tick_params(labelsize=8)
        
        # 设置坐标轴
        ax.set_xlim(0, 255)
        ax.set_ylim(0, 39)
        
        # 设置X轴标签
        x_ticks = [0, 64, 128, 192, 255]
        x_labels = ['0.0', '0.25', '0.5', '0.75', '1.0']
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels, fontsize=9)
        ax.set_xlabel('归一化数值', fontsize=9)
        
        # 隐藏Y轴
        ax.set_yticks([])
        ax.set_ylabel('')
    
    # 隐藏多余的子图
    for i in range(n_cmaps, n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        axes[row, col].set_visible(False)
    
    # 调整布局（增加间距避免文字重叠）
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, hspace=0.6, wspace=0.35)
    
    return fig


def create_comparison_grid():
    """创建配色方案比较网格（更紧凑的版本）"""
    # 设置中文字体
    setup_chinese_fonts()
    
    # 获取配色方案
    custom_cmaps = create_custom_colormaps()
    descriptions = list_custom_colormaps()
    
    # 创建渐变数据（更窄的条带）
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack([gradient] * 20)  # 减少高度到20行
    
    # 配色方案名称列表（移除最后一个science_custom）
    cmap_names = list(custom_cmaps.keys())[:-1]
    n_cmaps = len(cmap_names)
    
    # 计算网格布局：一行两列
    n_cols = 2
    n_rows = (n_cmaps + n_cols - 1) // n_cols
    
    # 创建图形（更大的图像，增加间距）
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(22, n_rows * 1.8))
    fig.suptitle('PPSD配色方案对比图 - 按一行两列布局', 
                 fontsize=20, fontweight='bold', y=0.96)
    
    # 确保axes是二维数组
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    elif n_cols == 1:
        axes = axes.reshape(-1, 1)
    
    # 展示每个配色方案
    for i, cmap_name in enumerate(cmap_names):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row, col]
        
        # 获取配色方案
        cmap = custom_cmaps[cmap_name]
        
        # 显示渐变条
        ax.imshow(gradient, aspect='auto', cmap=cmap, vmin=0, vmax=1, 
                  interpolation='bilinear')
        
        # 设置标题（更简洁）
        desc = descriptions.get(cmap_name, '')
        if '(' in desc:
            short_desc = desc.split('(')[1].split(')')[0]
        else:
            short_desc = desc.split('-')[0].strip() if '-' in desc else ''
        
        title = f"{cmap_name}\n{short_desc}"
        ax.set_title(title, fontsize=10, fontweight='bold', pad=12)
        
        # 设置坐标轴（更简洁）
        ax.set_xlim(0, 255)
        ax.set_ylim(0, 19)
        
        # 设置X轴标签
        x_ticks = [0, 51, 102, 153, 204, 255]
        x_labels = ['0.0', '0.2', '0.4', '0.6', '0.8', '1.0']
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels, fontsize=10)
        ax.set_xlabel('PPSD值 (归一化)', fontsize=10, fontweight='bold')
        
        # 隐藏Y轴
        ax.set_yticks([])
        ax.set_ylabel('')
        
        # 添加边框
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
            spine.set_color('black')
    
    # 隐藏多余的子图
    for i in range(n_cmaps, n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        axes[row, col].set_visible(False)
    
    # 调整布局（增加间距避免文字重叠）
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, hspace=0.5, wspace=0.3)
    
    return fig


def save_colormap_previews():
    """保存配色方案预览图"""
    print("🎨 开始生成配色方案展示图...")
    
    # 创建标准网格展示
    print("📊 生成标准网格展示图...")
    fig1 = create_colormap_grid()
    output_file1 = 'colormap_grid_standard.png'
    fig1.savefig(output_file1, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 保存标准展示图: {output_file1}")
    
    # 创建比较网格展示
    print("📈 生成比较网格展示图...")
    fig2 = create_comparison_grid()
    output_file2 = 'colormap_grid_comparison.png'
    fig2.savefig(output_file2, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 保存比较展示图: {output_file2}")
    
    plt.show()
    
    # 统计信息
    custom_cmaps = create_custom_colormaps()
    print("\n📋 配色方案统计:")
    print(f"   总计: {len(custom_cmaps) - 1} 个配色方案 (已排除science_custom)")
    print("   布局: 一行两列网格")
    print("   分辨率: 300 DPI")
    print("   格式: PNG")


def main():
    """主函数"""
    print("🚀 配色方案网格展示生成器")
    print("=" * 50)
    
    try:
        save_colormap_previews()
        print("\n🎉 配色方案展示图生成完成！")
        
    except Exception as e:
        print(f"\n❌ 生成过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 