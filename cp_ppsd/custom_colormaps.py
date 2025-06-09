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

    # 6. 白到红色配色方案 (简化中间色，快速反应数据变化，优化PDF显示)
    white_to_red_colors = [
        '#FFFFFF',  # 白色 (起点，极少占比)
        '#FFD700',  # 金色 (快速过渡)
        '#FFA500',  # 标准橘色 (中等值)
        '#FF4500',  # 橘红色 (高值)
        '#FF0000',  # 纯红色 (很高值)
        '#CC0000'   # 深红色 (终点，最高值)
    ]
    custom_cmaps['yellow_r_custom'] = LinearSegmentedColormap.from_list(
        'yellow_r_custom', white_to_red_colors, N=256
    )

    # 7. 蓝色反向配色方案 (简化为5色，从白色快速变深，适合海洋数据可视化)
    blue_r_colors = [
        '#FFFFFF',  # 白色 (起点，极少占比)
        '#42A5F5',  # 材料蓝 (快速过渡)
        '#1976D2',  # 深蓝 (中等值)
        '#0D47A1',  # 深蓝色 (高值)
        '#001540'   # 深夜蓝 (终点，最高值)
    ]
    custom_cmaps['blue_r_custom'] = LinearSegmentedColormap.from_list(
        'blue_r_custom', blue_r_colors, N=256
    )

    # 8. PQLX配色方案 (参考ObsPy官方PQLX配色，从白色到彩虹色谱，紫蓝过渡)
    pqlx_colors = [
        (0.00, '#ffffff'),  # 白色 (0%, 起点，最浅色)
        (0.08, '#87ceeb'),  # 天空海蓝 (8%, 白色到蓝色的平滑过渡)
        (0.15, '#4682b4'),  # 钢蓝色 (15%, 低值)
        (0.30, '#00FFFF'),  # 青色 (30%, 中低值)
        (0.50, '#00FF00'),  # 绿色 (50%, 中等值)
        (0.80, '#FFFF00'),  # 黄色 (80%, 高值)
        (1.00, '#FF0000')   # 红色 (100%, 终点，最高值)
    ]
    custom_cmaps['pqlx_custom'] = LinearSegmentedColormap.from_list(
        'pqlx_custom', pqlx_colors, N=256
    )

    # 9. 山峦日落反向配色方案 (白色起点，删除蓝色，纯暖色调过渡)
    mountain_sunset_r_colors = [
        '#ffffff',  # 白色 (0%, 起点)
        '#ff9800',  # 橙色 (33%, 暖色调开始)
        '#ff5722',  # 橙红色 (67%, 中高值)
        '#c62828'   # 深红色 (100%, 终点)
    ]
    custom_cmaps['mountain_sunset_r_custom'] = LinearSegmentedColormap.from_list(
        'mountain_sunset_r_custom', mountain_sunset_r_colors, N=256
    )

    # 10. Loyel 2024配色方案 (灵感来自高级感配色设计，白色到深蓝黑的渐变)
    loyel_2024_colors = [
        '#ffffff',  # 白色 (0%, 起点，最浅色)
        '#e9a621',  # 金黄色 (20%, Color 05)
        '#ca7508',  # 橙色 (40%, Color 04)
        '#763262',  # 紫红色 (60%, Color 03)
        '#00225d',  # 深蓝色 (80%, Color 02)
        '#171635'   # 深蓝黑色 (100%, Color 01)
    ]
    custom_cmaps['loyel_2024_custom'] = LinearSegmentedColormap.from_list(
        'loyel_2024_custom', loyel_2024_colors, N=256
    )

    # 11. 胖熊猫配色方案 (灵感来自胖熊猫设计室，白色到深蓝的绿蓝渐变)
    fatpanda_colors = [
        '#ffffff',  # 白色 (0%, 起点，最浅色)
        '#aec60c',  # 黄绿色 (20%, 最亮的绿色)
        '#8cb24a',  # 中绿色 (40%, 中等绿色)
        '#6d9d39',  # 深绿色 (60%, 较深绿色)
        '#4984ac',  # 中蓝色 (80%, 中等蓝色)
        '#08739d'   # 深蓝绿色 (100%, 最深的蓝色)
    ]
    custom_cmaps['fatpanda_custom'] = LinearSegmentedColormap.from_list(
        'fatpanda_custom', fatpanda_colors, N=256
    )

    # 13. 高级反差配色方案 (红黄蓝绿经典配色的高级版本)
    premium_contrast_colors = [
        '#ffffff',  # 白色 (0%, 起点，最浅色)
        '#d4af37',  # 金黄色 (20%, 高级金色调)
        '#2e8b57',  # 海绿色 (40%, 深绿色调)
        '#1e3a8a',  # 皇家蓝 (60%, 深蓝色调)
        '#8b0000',  # 深红色 (80%, 酒红色调)
        '#2c1810'   # 深棕色 (100%, 最深色)
    ]
    custom_cmaps['premium_contrast_custom'] = LinearSegmentedColormap.from_list(
        'premium_contrast_custom', premium_contrast_colors, N=256
    )

    # 14. 秋天配色方案 (黄色、绿色、蓝色的秋季色彩组合)
    autumn_colors = [
        (0.00, '#ffffff'),  # 白色 (0%, 起点，最浅色)
        (0.10, '#ffff00'),  # 黄色 (10%, 明亮黄色调)
        (0.33, '#b8860b'),  # 暗金黄色 (33%, 深黄色调)
        (0.50, '#228b22'),  # 森林绿 (50%, 高级绿色调)
        (0.67, '#4682b4'),  # 钢蓝色 (67%, 中等蓝色调)
        (0.83, '#191970'),  # 午夜蓝 (83%, 深蓝色调)
        (1.00, '#0f1419')   # 深蓝黑色 (100%, 最深色)
    ]
    custom_cmaps['autumn_custom'] = LinearSegmentedColormap.from_list(
        'autumn_custom', autumn_colors, N=256
    )

    # 15. 北极光高级配色方案 (8色版本)
    aurora_premium_colors = [
        (0.00, '#ffffff'),  # 纯白色 (0%, 最低概率密度，透明背景)
        (0.10, '#87ceeb'),  # 天蓝色 (5%, 低概率，中浅蓝冷色)
        (0.20, '#0066cc'),  # 深蓝色 (15%, 中低概率，深冷色)
        (0.35, '#00cc99'),  # 青绿色 (35%, 中等概率，过渡色)
        (0.50, '#00cc33'),  # 绿色 (50%, 中高概率，中性色)
        (0.65, '#99cc00'),  # 黄绿色 (65%, 高概率，暖色开始)
        (0.80, '#ff9900'),  # 橙色 (80%, 很高概率，强烈暖色)
        (1.00, '#cc0000')   # 深红色 (100%, 最高概率，告警色)
    ]
    custom_cmaps['aurora_premium_custom'] = LinearSegmentedColormap.from_list(
        'aurora_premium_custom', aurora_premium_colors, N=256
    )

    # 16. 海洋深度配色方案 (显示海洋色彩)
    ocean_depth_colors = [
        (0.00, '#ffffff'),  # 海面泡沫 (0%, 白色浪花，很小占比)
        (0.05, '#87ceeb'),  # 天空海蓝 (5%, 直接跳到明显海洋色)
        (0.15, '#4682b4'),  # 钢铁海蓝 (15%, 开阔海域的深蓝)
        (0.35, '#008b8b'),  # 深海青绿 (35%, 珊瑚礁的神秘色彩)
        (0.50, '#2e8b57'),  # 海洋绿松 (50%, 海藻丰富的中层海域)
        (0.65, '#006666'),  # 海底青蓝 (65%, 深海底层的幽深)
        (0.80, '#003366'),  # 深渊蓝黑 (80%, 海洋深渊的神秘)
        (1.00, '#001122')   # 海底深渊 (100%, 最深海底，近乎黑暗)
    ]
    custom_cmaps['ocean_depth_custom'] = LinearSegmentedColormap.from_list(
        'ocean_depth_custom', ocean_depth_colors, N=256
    )
    
    # 17. 森林四季配色方案 (8色版本：春晨薄雾→夏日翠绿→秋日金黄→深秋火红)
    forest_seasons_colors = [
        (0.00, '#ffffff'),  # 春晨薄雾 (0%, 纯白晨雾，极小占比)
        (0.05, '#e8f5e8'),  # 春意初绿 (5%, 初春生机，浅色冷色)
        (0.15, '#90ee90'),  # 春叶嫩绿 (15%, 春天活力，浅绿色)
        (0.35, '#228b22'),  # 夏日深绿 (35%, 夏季茂盛，深绿冷色)
        (0.50, '#ffd700'),  # 秋日金黄 (50%, 秋天金叶，暖色开始)
        (0.65, '#ff8c00'),  # 秋叶橙黄 (65%, 深秋渐变，暖色)
        (0.80, '#dc143c'),  # 深秋火红 (80%, 秋叶绚烂，强烈暖色)
        (1.00, '#8b0000')   # 冬日深红 (100%, 深秋尾声，深暖色)
    ]
    custom_cmaps['forest_seasons_custom'] = LinearSegmentedColormap.from_list(
        'forest_seasons_custom', forest_seasons_colors, N=256
    )
    
    # 18. 沙漠日月配色方案 (8色版本：黎明薄雾→晨光蓝紫→金沙烈日→夕阳火红，低值颜色增强可见度)
    desert_day_colors = [
        (0.00, '#ffffff'),  # 黎明薄雾 (0%, 纯白晨雾，极小占比)
        (0.05, '#f0e68c'),  # 晨光卡其 (5%, 晨光初现，明显浅暖色)
        (0.15, '#cd853f'),  # 正午秘鲁 (15%, 正午沙丘，暖色)
        (0.35, '#b8860b'),  # 午后暗金 (35%, 午后烈日，深金色)
        (0.50, '#87ceeb'),  # 晨曦天蓝 (50%, 沙漠晨空，明显浅蓝冷色)
        (0.65, '#20b2aa'),  # 仙人掌绿 (65%, 沙漠植物，明显青绿冷色)
        (0.80, '#ff4500'),  # 夕阳橙红 (80%, 夕阳西下，强烈暖色)
        (1.00, '#8b0000')   # 夜幕深红 (100%, 沙漠夜晚，深暖色)
    ]
    custom_cmaps['desert_day_custom'] = LinearSegmentedColormap.from_list(
        'desert_day_custom', desert_day_colors, N=256
    )
    
    # 19. 和谐强对比配色方案 (8色版本：强对比度+自然过渡+色彩和谐)
    strong_contrast_colors = [
        (0.00, '#ffffff'),  # 纯白色 (0%, 极小占比)
        (0.05, '#87ceeb'),  # 天空蓝 (5%, 浅冷色，自然过渡)
        (0.15, '#4169e1'),  # 皇家蓝 (15%, 深冷色，强对比)
        (0.35, '#32cd32'),  # 酸橙绿 (35%, 鲜亮中性色，对比蓝色)
        (0.50, '#ffd700'),  # 金色 (50%, 温暖明亮，对比绿色)
        (0.65, '#ff8c00'),  # 深橙色 (65%, 暖色过渡，对比金色)
        (0.80, '#dc143c'),  # 深红色 (80%, 强烈暖色，对比橙色)
        (1.00, '#800080')   # 紫色 (100%, 深色收尾，和谐过渡)
    ]
    custom_cmaps['strong_contrast_custom'] = LinearSegmentedColormap.from_list(
        'strong_contrast_custom', strong_contrast_colors, N=256
    )
    
    # 20. 科学配色方案 (8色版本：白色背景，专业高级，期刊级视觉效果)
    science_colors = [
        (0.00, '#ffffff'),  # 春晨薄雾 (0%, 纯白晨雾，极小占比)
        (0.05, '#87ceeb'),  # 天空海蓝 (5%, 直接跳到明显海洋色)
        (0.15, '#4169e1'),  # 钢铁海蓝 (15%, 开阔海域的深蓝)
        (0.35, '#008b8b'),  # 深海青绿 (35%, 珊瑚礁的神秘色彩)
        (0.50, '#ffd700'),  # 秋日金黄 (50%, 秋天金叶，暖色开始)
        (0.65, '#ff8c00'),  # 秋叶橙黄 (65%, 深秋渐变，暖色)
        (0.80, '#dc143c'),  # 深秋火红 (80%, 秋叶绚烂，强烈暖色)
        (1.00, '#8b0000')   # 冬日深红 (100%, 深秋尾声，深暖色)
    ]
    custom_cmaps['science_custom'] = LinearSegmentedColormap.from_list(
        'science_custom', science_colors, N=256
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
        'yellow_r_custom': '白到红色配色（简化中间色，快速反应数据变化）- 暖色调，优化PDF显示',
        'blue_r_custom': '蓝色反向配色（简化为5色，从白色快速变深）- 冷色调，适合海洋数据',
        'pqlx_custom': 'PQLX配色（紫蓝过渡）- 白色到彩虹色谱，紫蓝平滑过渡，适合地震学PPSD标准显示',
        'mountain_sunset_r_custom': '山峦日落暖色配色（4色）- 白色到深红的纯暖色调过渡，删除蓝色元素',
        'loyel_2024_custom': 'Loyel 2024高级感配色（6色）- 白色到深蓝黑的专业渐变，包含金黄、橙色、紫红的丰富层次',
                'fatpanda_custom': '胖熊猫配色（6色）- 白色到深蓝的绿蓝渐变，包含黄绿、中绿、深绿的丰富绿色层次',
        'premium_contrast_custom': '高级反差配色（6色）- 红黄蓝绿经典配色的高级版本，金黄、海绿、皇家蓝、深红的强烈对比',
        'autumn_custom': '秋天配色（7色）- 黄绿蓝秋季色彩组合，纯黄、森林绿、钢蓝的丰富层次',
        'aurora_premium_custom': '北极光高级配色（8色）- 白色最低值，删除浅蓝色，'
                                 '直接过渡到深色，强对比度突出数据',
        'ocean_depth_custom': '海洋深度配色（8色）- 白色占比极小，快速过渡到海洋色彩，'
                              '突出数据显示，从海面到深海的自然层次',
        'forest_seasons_custom': '森林四季配色（8色）- 春晨薄雾→夏日翠绿→秋日金黄→深秋火红，'
                                 '包含金黄色，白色占比极小（0-5%）',
        'desert_day_custom': '沙漠日月配色（8色）- 黎明薄雾→晨曦天蓝→金沙烈日→夕阳火红，'
                             '低值颜色增强可见度，白色占比极小（0-4%）',
        'strong_contrast_custom': '和谐强对比配色（8色）- 天空蓝→皇家蓝→酸橙绿→金色→深橙→深红→紫色，'
                                  '强对比度与自然过渡并存，白色占比极小（0-5%）',
        'science_custom': '专业科学配色（8色）- 白色→浅冰蓝→天蓝→专业蓝→深蓝→棕褐→橙棕→深红，'
                          '白色背景，简洁专业，期刊级科学可视化标准'
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
