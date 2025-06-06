#!/usr/bin/env python3
"""
:Author:
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)

数组表配置适配器 - 处理 [[]] 语法的TOML配置

支持多套配置方案的选择和合并
"""

import toml
from typing import Dict, Any, List, Optional


class ArrayConfigAdapter:
    """
    数组表配置适配器类

    专门处理使用 [[]] 语法的TOML配置文件
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
        将数组表配置适配为兼容格式

        Returns:
            适配后的配置字典
        """
        adapted = {}

        # 1. 处理基础配置（非数组表）
        for key, value in self.raw_config.items():
            if not isinstance(value, list):
                if isinstance(value, dict):
                    adapted.update(value)
                else:
                    adapted[key] = value

        # 2. 处理百分位数数组表
        percentiles_configs = self._get_enabled_array_configs('percentiles')
        if percentiles_configs:
            # 选择第一个启用的配置作为主配置
            main_config = percentiles_configs[0]
            adapted.update({
                'show_percentiles': True,
                'percentiles': main_config.get('values', [10, 50, 90]),
                'percentile_color': main_config.get('color', 'lightgray'),
                'percentile_linewidth': main_config.get('linewidth', 1.0),
                'percentile_linestyle': main_config.get('linestyle', '--'),
                'percentile_alpha': main_config.get('alpha', 0.8)
            })
        else:
            adapted['show_percentiles'] = False

        # 3. 处理皮特森曲线数组表
        peterson_configs = self._get_enabled_array_configs('peterson_curves')
        if peterson_configs:
            main_config = peterson_configs[0]
            adapted.update({
                'show_noise_models': True,
                'peterson_nlnm_color': main_config.get('nlnm_color', 'blue'),
                'peterson_nhnm_color': main_config.get('nhnm_color', 'red'),
                'peterson_linewidth': main_config.get('nlnm_linewidth', 1.0),
                'peterson_linestyle': main_config.get('nlnm_linestyle', '--'),
                'peterson_alpha': main_config.get('nlnm_alpha', 0.8)
            })
        else:
            adapted['show_noise_models'] = False

        # 4. 处理统计线数组表
        stat_lines = self._get_enabled_array_configs('statistical_lines')
        mode_config = self._find_config_by_type(stat_lines, 'mode')
        mean_config = self._find_config_by_type(stat_lines, 'mean')

        if mode_config:
            adapted.update({
                'show_mode': True,
                'mode_color': mode_config.get('color', 'orange'),
                'mode_linewidth': mode_config.get('linewidth', 2.0),
                'mode_linestyle': mode_config.get('linestyle', '-'),
                'mode_alpha': mode_config.get('alpha', 0.9)
            })
        else:
            adapted['show_mode'] = False

        if mean_config:
            adapted.update({
                'show_mean': True,
                'mean_color': mean_config.get('color', 'green'),
                'mean_linewidth': mean_config.get('linewidth', 2.0),
                'mean_linestyle': mean_config.get('linestyle', '-'),
                'mean_alpha': mean_config.get('alpha', 0.9)
            })
        else:
            adapted['show_mean'] = False

        # 5. 处理绘图类型数组表
        plot_types = self._get_enabled_array_configs('plot_types')
        enabled_plot_types = [config.get('type') for config in plot_types]
        adapted['plot_types'] = enabled_plot_types

        # 为每种绘图类型设置特定参数
        for plot_config in plot_types:
            plot_type = plot_config.get('type')
            if plot_type == 'standard':
                adapted.update({
                    'show_histogram': plot_config.get('show_histogram', True),
                    'show_percentiles': plot_config.get('show_percentiles', False),
                    'show_noise_models': plot_config.get('show_noise_models', True),
                    'show_mode': plot_config.get('show_mode', True),
                    'show_mean': plot_config.get('show_mean', False),
                    'coverage_alpha': plot_config.get('coverage_alpha', 0.5),
                    'period_lim': plot_config.get('period_lim', [0.01, 1000.0]),
                    'standard_cmap': plot_config.get('cmap', 'viridis'),
                    'grid': plot_config.get('grid', True)
                })
            elif plot_type == 'temporal':
                adapted.update({
                    'plot_periods': plot_config.get('plot_periods', [1.0, 8.0, 20.0]),
                    'time_format_x': plot_config.get('time_format_x', '%H:%M')
                })
            elif plot_type == 'spectrogram':
                adapted.update({
                    'clim': plot_config.get('clim', [-180, -100]),
                    'spectrogram_time_format_x': plot_config.get('time_format_x', '%Y-%m-%d')
                })

        return adapted

    def _get_enabled_array_configs(self, array_name: str) -> List[Dict[str, Any]]:
        """
        获取指定数组表中所有启用的配置

        Args:
            array_name: 数组表名称

        Returns:
            启用的配置列表
        """
        if array_name not in self.raw_config:
            return []

        array_configs = self.raw_config[array_name]
        if not isinstance(array_configs, list):
            return []

        return [config for config in array_configs if config.get('enabled', False)]

    def _find_config_by_type(self, configs: List[Dict[str, Any]],
                             config_type: str) -> Optional[Dict[str, Any]]:
        """
        在配置列表中查找特定类型的配置

        Args:
            configs: 配置列表
            config_type: 配置类型

        Returns:
            匹配的配置字典或None
        """
        for config in configs:
            if config.get('type') == config_type:
                return config
        return None

    def get_config(self) -> Dict[str, Any]:
        """获取适配后的配置"""
        return self.adapted_config

    def get_array_configs(self, array_name: str) -> List[Dict[str, Any]]:
        """获取指定数组表的所有配置"""
        return self.raw_config.get(array_name, [])

    def get_enabled_configs(self, array_name: str) -> List[Dict[str, Any]]:
        """获取指定数组表中启用的配置"""
        return self._get_enabled_array_configs(array_name)

    def enable_config(self, array_name: str, config_name: str) -> bool:
        """
        启用指定的配置方案

        Args:
            array_name: 数组表名称
            config_name: 配置方案名称

        Returns:
            是否成功启用
        """
        if array_name not in self.raw_config:
            return False

        array_configs = self.raw_config[array_name]
        for config in array_configs:
            if config.get('name') == config_name:
                config['enabled'] = True
                # 重新适配配置
                self.adapted_config = self._adapt_config()
                return True
        return False

    def disable_config(self, array_name: str, config_name: str) -> bool:
        """
        禁用指定的配置方案

        Args:
            array_name: 数组表名称
            config_name: 配置方案名称

        Returns:
            是否成功禁用
        """
        if array_name not in self.raw_config:
            return False

        array_configs = self.raw_config[array_name]
        for config in array_configs:
            if config.get('name') == config_name:
                config['enabled'] = False
                # 重新适配配置
                self.adapted_config = self._adapt_config()
                return True
        return False

    def list_available_configs(self) -> Dict[str, List[str]]:
        """
        列出所有可用的配置方案

        Returns:
            配置方案字典，键为数组表名，值为方案名列表
        """
        available = {}

        for key, value in self.raw_config.items():
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], dict) and 'name' in value[0]:
                    available[key] = [config.get('name', 'unnamed') for config in value]

        return available

    def print_config_status(self):
        """打印所有配置方案的状态"""
        print("=== 数组表配置状态 ===\\n")

        available = self.list_available_configs()

        for array_name, config_names in available.items():
            print(f"[{array_name}] 配置方案:")
            array_configs = self.raw_config[array_name]

            for config in array_configs:
                name = config.get('name', 'unnamed')
                enabled = config.get('enabled', False)
                description = config.get('description', '无描述')
                status = "[启用]" if enabled else "[禁用]"
                print(f"  {status} {name}: {description}")
            print()


def demonstrate_array_config():
    """演示数组表配置的使用"""

    config_path = "input/config_plot_array_grouped.toml"

    print("=== 数组表配置演示 ===\\n")

    # 创建适配器
    adapter = ArrayConfigAdapter(config_path)

    # 显示所有可用配置
    print("1. 可用配置方案:")
    available = adapter.list_available_configs()
    for array_name, configs in available.items():
        print(f"  {array_name}: {configs}")

    print("\\n2. 当前配置状态:")
    adapter.print_config_status()

    print("\\n3. 适配后的主要配置:")
    adapted = adapter.get_config()
    key_examples = [
        'show_percentiles', 'percentiles', 'percentile_color',
        'show_noise_models', 'peterson_nlnm_color',
        'show_mode', 'mode_color',
        'show_mean', 'mean_color',
        'plot_types'
    ]

    for key in key_examples:
        if key in adapted:
            print(f"  {key} = {adapted[key]}")

    print("\\n4. 动态配置切换演示:")
    print("  启用详细百分位数配置...")
    success = adapter.enable_config('percentiles', 'detailed')
    if success:
        new_percentiles = adapter.get_config().get('percentiles', [])
        print(f"  新的百分位数: {new_percentiles}")

    print("  启用醒目皮特森曲线样式...")
    success = adapter.enable_config('peterson_curves', 'bold')
    if success:
        new_nlnm_color = adapter.get_config().get('peterson_nlnm_color', 'blue')
        print(f"  新的NLNM颜色: {new_nlnm_color}")


if __name__ == "__main__":
    demonstrate_array_config()
