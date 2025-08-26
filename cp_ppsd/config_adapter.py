#!/usr/bin/env python3
"""
Author:
    muly (muly@cea-igp.ac.cn)
license:
    MIT License
    (https://opensource.org/licenses/MIT)
"""

import toml
from typing import Dict, Any


class ConfigAdapter:
    """
    配置适配器类

    负责将细致分组的配置转换为现有代码期望的格式
    """

    def __init__(self, config_path: str):
        """
        初始化适配器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.raw_config = self._load_config()
        self.adapted_config = self._adapt_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载原始配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}

    def _adapt_config(self) -> Dict[str, Any]:
        """
        将细致分组配置适配为兼容格式

        Returns:
            适配后的配置字典
        """
        adapted = {}

        # 1. 处理基础路径和全局设置
        if 'paths' in self.raw_config:
            adapted.update(self.raw_config['paths'])

        if 'global' in self.raw_config:
            adapted['log_level'] = self.raw_config['global'].get('log_level', 'INFO')

        # 2. 处理显示设置
        if 'display' in self.raw_config:
            # dpi 和 figure_size 已硬编码，不再从配置读取
            pass

        # 3. 处理标准图基础设置
        if 'standard' in self.raw_config and 'basic' in self.raw_config['standard']:
            basic_config = self.raw_config['standard']['basic']
            adapted.update({
                'plot_types': basic_config.get('plot_types', ["standard"]),
                'npz_merge_strategy': basic_config.get('npz_merge_strategy', True),
                'show_histogram': basic_config.get('show_histogram', True),
                'show_percentiles': basic_config.get('show_percentiles', False),
                'show_noise_models': basic_config.get('show_noise_models', True),
                'show_mode': basic_config.get('show_mode', True),
                'show_mean': basic_config.get('show_mean', False),
                'coverage_alpha': basic_config.get('coverage_alpha', 0.5),
                'period_lim': basic_config.get('period_lim', [0.01, 1000.0]),
                'xaxis_frequency': basic_config.get('xaxis_frequency', False),
                'cumulative_plot': basic_config.get('cumulative_plot', False),
                'cumulative_number_of_colors': basic_config.get('cumulative_number_of_colors', 25),

                'standard_cmap': basic_config.get('standard_cmap', 'viridis'),
                'grid': basic_config.get('standard_grid', True)
            })

        # 4. 处理百分位数配置 [percentiles] -> show_percentiles + percentiles + 样式
        if 'percentiles' in self.raw_config:
            percentiles_config = self.raw_config['percentiles']
            adapted.update({
                'show_percentiles': percentiles_config.get('enabled', True),
                'percentiles': percentiles_config.get('values', [10, 50, 90]),
                'percentile_color': percentiles_config.get('color', 'lightgray'),
                'percentile_linewidth': percentiles_config.get('linewidth', 1.0),
                'percentile_linestyle': percentiles_config.get('linestyle', '--'),
                'percentile_alpha': percentiles_config.get('alpha', 0.8)
            })

        # 5. 处理皮特森曲线配置 [peterson_curves] -> show_noise_models + 样式
        if 'peterson_curves' in self.raw_config:
            peterson_config = self.raw_config['peterson_curves']
            adapted.update({
                'show_noise_models': peterson_config.get('enabled', True),
                'peterson_nlnm_color': peterson_config.get('nlnm_color', 'blue'),
                'peterson_nhnm_color': peterson_config.get('nhnm_color', 'red'),
                'peterson_linewidth': peterson_config.get('nlnm_linewidth', 1.0),
                'peterson_linestyle': peterson_config.get('nlnm_linestyle', '--'),
                'peterson_alpha': peterson_config.get('nlnm_alpha', 0.8)
            })

        # 6. 处理众数线配置 [mode_line] -> show_mode + 样式
        if 'mode_line' in self.raw_config:
            mode_config = self.raw_config['mode_line']
            adapted.update({
                'show_mode': mode_config.get('enabled', False),
                'mode_color': mode_config.get('color', 'orange'),
                'mode_linewidth': mode_config.get('linewidth', 2.0),
                'mode_linestyle': mode_config.get('linestyle', '-'),
                'mode_alpha': mode_config.get('alpha', 0.9)
            })

        # 7. 处理均值线配置 [mean_line] -> show_mean + 样式
        if 'mean_line' in self.raw_config:
            mean_config = self.raw_config['mean_line']
            adapted.update({
                'show_mean': mean_config.get('enabled', False),
                'mean_color': mean_config.get('color', 'green'),
                'mean_linewidth': mean_config.get('linewidth', 2.0),
                'mean_linestyle': mean_config.get('linestyle', '-'),
                'mean_alpha': mean_config.get('alpha', 0.9)
            })

        # 8. 处理时间演化图配置
        if 'temporal' in self.raw_config:
            temporal_config = self.raw_config['temporal']
            adapted.update({
                'plot_periods': temporal_config.get('plot_periods', [1.0, 8.0, 20.0]),
                'time_format_x': temporal_config.get('time_format_x', '%H:%M')
            })

        # 9. 处理频谱图配置
        if 'spectrogram' in self.raw_config:
            spectrogram_config = self.raw_config['spectrogram']
            adapted.update({
                'clim': spectrogram_config.get('clim', [-180, -100]),
                'spectrogram_time_format_x': spectrogram_config.get('time_format_x', '%Y-%m-%d')
            })

        # 10. 处理配色方案
        if 'colormaps' in self.raw_config:
            cmap_config = self.raw_config['colormaps']
            adapted['available_cmaps'] = cmap_config.get('available', [])

        return adapted

    def get_config(self) -> Dict[str, Any]:
        """获取适配后的配置"""
        return self.adapted_config

    def get_section(self, section: str) -> Dict[str, Any]:
        """获取特定分组的配置"""
        return self.raw_config.get(section, {})

    def print_mapping(self):
        """打印配置映射关系"""
        print("=== 配置映射关系 ===\n")

        print("细致分组 -> 兼容格式:")
        print("├── [percentiles]")
        print("│   ├── enabled -> show_percentiles")
        print("│   ├── values -> percentiles")
        print("│   ├── color -> percentile_color")
        print("│   ├── linewidth -> percentile_linewidth")
        print("│   ├── linestyle -> percentile_linestyle")
        print("│   └── alpha -> percentile_alpha")
        print("│")
        print("├── [peterson_curves]")
        print("│   ├── enabled -> show_noise_models")
        print("│   ├── nlnm_color -> peterson_nlnm_color")
        print("│   ├── nhnm_color -> peterson_nhnm_color")
        print("│   ├── nlnm_linewidth -> peterson_linewidth")
        print("│   ├── nlnm_linestyle -> peterson_linestyle")
        print("│   └── nlnm_alpha -> peterson_alpha")
        print("│")
        print("├── [mode_line]")
        print("│   ├── enabled -> show_mode")
        print("│   ├── color -> mode_color")
        print("│   ├── linewidth -> mode_linewidth")
        print("│   ├── linestyle -> mode_linestyle")
        print("│   └── alpha -> mode_alpha")
        print("│")
        print("└── [mean_line]")
        print("    ├── enabled -> show_mean")
        print("    ├── color -> mean_color")
        print("    ├── linewidth -> mean_linewidth")
        print("    ├── linestyle -> mean_linestyle")
        print("    └── alpha -> mean_alpha")


def demonstrate_fine_grouping():
    """演示细致分组配置的使用"""

    config_path = "input/config_plot_fine_grouped.toml"

    print("=== 细致分组配置演示 ===\n")

    # 创建适配器
    adapter = ConfigAdapter(config_path)

    # 显示原始分组结构
    print("1. 原始细致分组结构:")
    raw_config = adapter.raw_config

    for section_name in raw_config:
        print(f"  [{section_name}]")
        section = raw_config[section_name]
        if isinstance(section, dict):
            for key in list(section.keys())[:3]:  # 只显示前3个键
                print(f"    {key} = {section[key]}")
            if len(section) > 3:
                print(f"    ... (还有{len(section) - 3}个参数)")
        else:
            print(f"    {section}")
        print()

    # 显示适配后的配置
    print("2. 适配后的兼容配置（部分）:")
    adapted = adapter.get_config()
    key_examples = [
        'show_percentiles', 'percentiles', 'percentile_color',
        'show_noise_models', 'peterson_nlnm_color',
        'show_mode', 'mode_color',
        'show_mean', 'mean_color'
    ]

    for key in key_examples:
        if key in adapted:
            print(f"  {key} = {adapted[key]}")

    print("\n3. 配置映射关系:")
    adapter.print_mapping()

    # 演示如何直接访问特定功能组
    print("\n4. 直接访问特定功能组:")
    percentiles_config = adapter.get_section('percentiles')
    if percentiles_config:
        print("  百分位数完整配置:")
        for key, value in percentiles_config.items():
            print(f"    {key}: {value}")


if __name__ == "__main__":
    demonstrate_fine_grouping()
