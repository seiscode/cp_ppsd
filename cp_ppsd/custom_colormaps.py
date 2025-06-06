#!/usr/bin/env python3
"""
:Author:
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
"""
自定义配色方案模块

此模块定义了用于PPSD可视化的自定义配色方案，包括基于现有配色方案的修改版本。
这些配色方案针对地球物理数据可视化进行了优化。

使用方法:
    from cp_ppsd.custom_colormaps import get_custom_colormap

    # 获取自定义配色方案
    cmap = get_custom_colormap('viridis_custom')
"""

from typing import Optional, Dict, Any
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm
import numpy as np
import matplotlib.pyplot as plt


def create_custom_colormaps() -> Dict[str, Any]:
    """
    创建所有自定义配色方案

    Returns:
        Dict[str, Any]: 自定义配色方案字典
    """
    custom_cmaps = {}

    # 1. Viridis自定义版本 (截取0.0-0.8部分，增强对比度，突出PDF曲线)
    viridis_scm = cm.get_cmap('viridis')
    viridis_colors = viridis_scm(np.linspace(0.0, 0.8, 256))
    custom_cmaps['viridis_custom'] = LinearSegmentedColormap.from_list(
        'viridis_custom', viridis_colors, N=256
    )

    # 2. Ocean水色配色方案 (截取0.2-0.9部分，突出中高值，增强PDF对比度)
    ocean_scm = cm.get_cmap('ocean')
    ocean_colors = ocean_scm(np.linspace(0.2, 0.9, 256))
    custom_cmaps['ocean_custom'] = LinearSegmentedColormap.from_list(
        'ocean_custom', ocean_colors, N=256
    )

    # 3. Ocean反向配色方案 (截取0.0-0.6部分，浅色背景，强化PDF曲线对比度)
    ocean_r_scm = cm.get_cmap('ocean_r')
    ocean_r_colors = ocean_r_scm(np.linspace(0.0, 0.6, 256))
    custom_cmaps['ocean_r_custom'] = LinearSegmentedColormap.from_list(
        'ocean_r_custom', ocean_r_colors, N=256
    )

    # 4. Hot反向配色方案 (截取0.0-0.6部分，浅色背景，冷色调强化PDF可视化)
    hot_r_scm = cm.get_cmap('hot_r')
    hot_r_colors = hot_r_scm(np.linspace(0.0, 0.6, 256))
    custom_cmaps['hot_r_custom'] = LinearSegmentedColormap.from_list(
        'hot_r_custom', hot_r_colors, N=256
    )

    # 5. Plasma配色方案 (截取0.1-0.85部分，高对比度，突出PDF峰值)
    plasma_scm = cm.get_cmap('plasma')
    plasma_colors = plasma_scm(np.linspace(0.1, 0.85, 256))
    custom_cmaps['plasma_custom'] = LinearSegmentedColormap.from_list(
        'plasma_custom', plasma_colors, N=256
    )

    # 6. CMRmap反向配色方案 (截取0.0-0.8部分，科学标准，优化PDF显示)
    cmrmap_r_scm = cm.get_cmap('CMRmap_r')
    cmrmap_r_colors = cmrmap_r_scm(np.linspace(0.0, 0.8, 256))
    custom_cmaps['CMRmap_r_custom'] = LinearSegmentedColormap.from_list(
        'CMRmap_r_custom', cmrmap_r_colors, N=256
    )

    return custom_cmaps


def get_custom_colormap(name: str) -> Optional[Any]:
    """
    获取指定的自定义配色方案

    Args:
        name (str): 配色方案名称

    Returns:
        Optional[Any]: 配色方案对象，如果不存在则返回None
    """
    custom_cmaps = create_custom_colormaps()
    return custom_cmaps.get(name)


def list_custom_colormaps() -> Dict[str, str]:
    """
    列出所有可用的自定义配色方案及其描述

    Returns:
        Dict[str, str]: 配色方案名称和描述的字典
    """
    descriptions = {
        'viridis_custom': 'Viridis配色（0-80%范围）- 增强对比度，突出PDF曲线',
        'ocean_custom': 'Ocean水色配色（20-90%范围）- 突出中高值，增强PDF对比度',
        'ocean_r_custom': 'Ocean反向配色（0-60%范围）- 浅色背景，强化PDF曲线对比度',
        'hot_r_custom': 'Hot反向配色（0-60%范围）- 浅色背景，冷色调强化PDF可视化',
        'plasma_custom': 'Plasma配色（10-85%范围）- 高对比度，突出PDF峰值',
        'CMRmap_r_custom': 'CMRmap反向配色（0-80%范围）- 科学标准，优化PDF显示'
    }
    return descriptions


def register_custom_colormaps():
    """
    将自定义配色方案注册到matplotlib中，使其可以通过名称直接使用
    """
    custom_cmaps = create_custom_colormaps()

    for name, cmap in custom_cmaps.items():
        # 注册到matplotlib的配色方案注册表中
        cm.register_cmap(name=name, cmap=cmap)

    print(f"已注册 {len(custom_cmaps)} 个自定义配色方案:")
    for name, desc in list_custom_colormaps().items():
        print(f"  - {name}: {desc}")


def create_colormap_preview():
    """
    创建自定义配色方案预览图
    """
    # 设置中文字体支持
    try:
        import matplotlib.font_manager as fm

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
            plt.rcParams['font.sans-serif'] = [chinese_font,
                                               'DejaVu Sans', 'Arial']
            print(f"设置中文字体: {chinese_font}")
        else:
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial',
                                               'Liberation Sans']
            print("未找到中文字体，使用默认字体")

        # 解决负号显示问题
        plt.rcParams['axes.unicode_minus'] = False

    except Exception as e:
        print(f"设置中文字体失败: {e}")

    custom_cmaps = create_custom_colormaps()

    # 创建预览数据
    gradient = np.linspace(0, 1, 256).reshape(1, -1)

    # 创建预览图
    fig, axes = plt.subplots(len(custom_cmaps), 1, figsize=(10, 8))
    fig.suptitle('自定义配色方案预览', fontsize=16, fontweight='bold')

    descriptions = list_custom_colormaps()

    for i, (name, cmap) in enumerate(custom_cmaps.items()):
        ax = axes[i] if len(custom_cmaps) > 1 else axes

        # 显示配色方案
        ax.imshow(gradient, aspect='auto', cmap=cmap)
        ax.set_xlim(0, 256)
        ax.set_yticks([])
        ax.set_title(f'{name}: {descriptions[name]}', fontsize=12)

        # 添加数值标签
        ax.set_xticks([0, 64, 128, 192, 256])
        ax.set_xticklabels(['0.0', '0.25', '0.5', '0.75', '1.0'])

    plt.tight_layout()

    # 保存预览图
    import os
    output_dir = './output/plots'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'custom_colormaps_preview.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    print(f"自定义配色方案预览图已保存: {output_path}")


def main():
    """主函数 - 演示自定义配色方案"""
    print("自定义配色方案模块")
    print("=" * 50)

    # 注册自定义配色方案
    register_custom_colormaps()
    print()

    # 创建预览图
    create_colormap_preview()
    print()

    # 显示使用说明
    print("使用方法:")
    print("1. 在配置文件中使用自定义配色方案:")
    print("   standard_cmap = \"viridis_custom\"")
    print("   standard_cmap = \"ocean_custom\"")
    print("   standard_cmap = \"plasma_custom\"")
    print()
    print("2. 在Python代码中使用:")
    print("   from cp_ppsd.custom_colormaps import get_custom_colormap")
    print("   cmap = get_custom_colormap('viridis_custom')")
    print()
    print("3. 直接使用matplotlib:")
    print("   import matplotlib.pyplot as plt")
    print("   plt.imshow(data, cmap='viridis_custom')")


if __name__ == '__main__':
    main()
