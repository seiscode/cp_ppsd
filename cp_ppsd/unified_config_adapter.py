#!/usr/bin/env python3
"""
:Author: 
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
"""
统一配置适配器 - 支持两种格式的config_plot.toml配置

本适配器能够自动检测并处理两种不同的配置格式：
1. 简单分组格式：按绘图类型分组的配置（[standard], [temporal], [spectrogram]）
2. 精细分组格式：多层嵌套的配置（[standard.percentiles], [standard.peterson]等）

主要功能：
- 自动检测配置文件格式类型
- 统一适配为现有代码兼容的格式
- 提供格式转换和验证功能
- 支持配置文件格式升级迁移

使用方法：
    from cp_ppsd.unified_config_adapter import UnifiedConfigAdapter
    
    adapter = UnifiedConfigAdapter("config_plot.toml")
    config = adapter.get_config()
"""

import toml
from typing import Dict, Any
import logging


class UnifiedConfigAdapter:
    """
    统一配置适配器类
    
    支持两种格式的config_plot.toml配置文件
    """
    
    def __init__(self, config_path: str):
        """
        初始化适配器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.raw_config = self._load_config()
        self.config_format = self._detect_format()
        self.adapted_config = self._adapt_config()
        
        # 设置日志
        self.logger = logging.getLogger('unified_config_adapter')
    
    def _load_config(self) -> Dict[str, Any]:
        """加载原始配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def _detect_format(self) -> str:
        """
        检测配置文件格式
        
        Returns:
            "grouped": 精细分组格式（嵌套结构）
            "simple": 简单分组格式
            "flat": 扁平格式（传统格式）
        """
        # 检查精细分组格式的特征
        has_global = 'global' in self.raw_config
        has_paths = 'paths' in self.raw_config
        has_plotting = 'plotting' in self.raw_config
        
        # 检查嵌套结构
        has_nested_structure = False
        if 'standard' in self.raw_config:
            standard_section = self.raw_config['standard']
            if isinstance(standard_section, dict):
                has_nested_structure = any(
                    key in standard_section 
                    for key in ['percentiles', 'peterson', 'mode', 'mean']
                )
        
        # 检查简单分组格式的特征
        has_simple_groups = any(
            key in self.raw_config 
            for key in ['standard', 'temporal', 'spectrogram']
        )
        
        # 判断格式类型
        if (has_global and has_paths and has_plotting and 
                has_nested_structure):
            return "grouped"
        elif has_simple_groups and not (has_global or has_paths or 
                                        has_plotting):
            return "simple"
        else:
            return "flat"
    
    def _adapt_config(self) -> Dict[str, Any]:
        """根据检测到的格式适配配置"""
        if self.config_format == "grouped":
            return self._adapt_grouped_config()
        elif self.config_format == "simple":
            return self._adapt_simple_config()
        else:
            return self._adapt_flat_config()
    
    def _adapt_grouped_config(self) -> Dict[str, Any]:
        """适配精细分组格式配置"""
        adapted = {}
        
        # 1. 处理global配置
        if 'global' in self.raw_config:
            global_config = self.raw_config['global']
            adapted['log_level'] = global_config.get('log_level', 'DEBUG')
            adapted['description'] = global_config.get('description', '')
            adapted['version'] = global_config.get('version', '2.0')
        
        # 2. 处理paths配置
        if 'paths' in self.raw_config:
            paths_config = self.raw_config['paths']
            adapted.update({
                'input_npz_dir': paths_config.get(
                    'input_npz_dir', './output/npz/'),
                'inventory_path': paths_config.get(
                    'inventory_path', './input/BJ.XML'),
                'output_dir': paths_config.get(
                    'output_dir', './output/plots/'),
                'output_filename_pattern': paths_config.get(
                    'output_filename_pattern',
                    '{plot_type}_{datetime}_{network}-{station}-{location}-'
                    '{channel}.png')
            })
        
        # 3. 处理plotting配置和args
        plotting_args = {}
        if 'plotting' in self.raw_config:
            plotting_config = self.raw_config['plotting']
            adapted.update({
                'plot_type': plotting_config.get('plot_type', ['standard']),
                'npz_merge_strategy': plotting_config.get(
                    'npz_merge_strategy', True),
                            # dpi 和 figure_size 已硬编码，不再从配置读取
            })
            
            # 将关键参数加入args
            plotting_args.update({
                'plot_type': plotting_config.get('plot_type', ['standard']),
                'npz_merge_strategy': plotting_config.get(
                    'npz_merge_strategy', True)
            })
        
        # 4. 处理standard配置及其子分组
        if 'standard' in self.raw_config:
            standard_config = self.raw_config['standard']
            
            # 基础standard配置
            plotting_args.update({
                'show_histogram': standard_config.get('show_histogram', True),
                'show_coverage': standard_config.get('show_coverage', False),
                'coverage_alpha': standard_config.get('coverage_alpha', 0.5),
                'standard_grid': standard_config.get('standard_grid', True),
                'period_lim': standard_config.get('period_lim', [0.01, 1000.0]),
                'xaxis_frequency': standard_config.get('xaxis_frequency', False),
                'cumulative_plot': standard_config.get('cumulative_plot', False),
                'cumulative_number_of_colors': standard_config.get('cumulative_number_of_colors', 25),
                'standard_cmap': standard_config.get('standard_cmap', 'viridis')
            })
            
            # 显示开关
            plotting_args.update({
                'show_percentiles': standard_config.get('show_percentiles', True),
                'show_noise_models': standard_config.get('show_noise_models', True),
                'show_mode': standard_config.get('show_mode', False),
                'show_mean': standard_config.get('show_mean', False)
            })
            
            # 处理percentiles子分组
            if 'percentiles' in standard_config:
                percentiles_config = standard_config['percentiles']
                plotting_args.update({
                    'percentiles': percentiles_config.get('values', [10, 50, 90]),
                    'percentile_color': percentiles_config.get('color', 'lightgray'),
                    'percentile_linewidth': percentiles_config.get('linewidth', 1.0),
                    'percentile_linestyle': percentiles_config.get('linestyle', '--'),
                    'percentile_alpha': percentiles_config.get('alpha', 0.8)
                })
            
            # 处理peterson子分组
            if 'peterson' in standard_config:
                peterson_config = standard_config['peterson']
                plotting_args.update({
                    'peterson_nlnm_color': peterson_config.get('nlnm_color', 'blue'),
                    'peterson_nhnm_color': peterson_config.get('nhnm_color', 'red'),
                    'peterson_linewidth': peterson_config.get('linewidth', 1.0),
                    'peterson_linestyle': peterson_config.get('linestyle', '--'),
                    'peterson_alpha': peterson_config.get('alpha', 0.8)
                })
            
            # 处理mode和mean子分组
            if 'mode' in standard_config:
                mode_config = standard_config['mode']
                plotting_args.update({
                    'mode_color': mode_config.get('color', 'orange'),
                    'mode_linewidth': mode_config.get('linewidth', 1.0),
                    'mode_linestyle': mode_config.get('linestyle', '-'),
                    'mode_alpha': mode_config.get('alpha', 0.9)
                })
            
            if 'mean' in standard_config:
                mean_config = standard_config['mean']
                plotting_args.update({
                    'mean_color': mean_config.get('color', 'green'),
                    'mean_linewidth': mean_config.get('linewidth', 1.0),
                    'mean_linestyle': mean_config.get('linestyle', '-'),
                    'mean_alpha': mean_config.get('alpha', 0.9)
                })
        
        # 5. 处理temporal配置
        if 'temporal' in self.raw_config:
            temporal_config = self.raw_config['temporal']
            plotting_args.update({
                'temporal_plot_periods': temporal_config.get('plot_periods', [1.0, 8.0, 20.0]),
                'time_format_x_temporal': temporal_config.get('time_format_x', '%H:%M'),
                'temporal_grid': temporal_config.get('grid', True),
                'temporal_cmap': temporal_config.get('cmap', 'Blues')
            })
        
        # 6. 处理spectrogram配置
        if 'spectrogram' in self.raw_config:
            spectrogram_config = self.raw_config['spectrogram']
            plotting_args.update({
                'clim': spectrogram_config.get('clim', [-180, -100]),
                'time_format_x_spectrogram': spectrogram_config.get('time_format_x', '%Y-%m-%d'),
                'spectrogram_grid': spectrogram_config.get('spectrogram_grid', True),
                'spectrogram_cmap': spectrogram_config.get('spectrogram_cmap', 'viridis')
            })
        
        # 7. 处理advanced配置
        if 'advanced' in self.raw_config:
            advanced_config = self.raw_config['advanced']
            # 添加到顶层配置
            adapted['advanced'] = advanced_config
            # 同时也添加到args中以保持兼容性
            plotting_args.update({
                'matplotlib_backend': advanced_config.get('matplotlib_backend', 'Agg'),
                            'font_family': advanced_config.get('font_family', 'WenQuanYi Micro Hei'),
            'enable_chinese_fonts': advanced_config.get('enable_chinese_fonts', True),
            'font_size': advanced_config.get('font_size', 8),
                'memory_optimization': advanced_config.get('memory_optimization', True),
                'parallel_processing': advanced_config.get('parallel_processing', False)
            })
        
        # 将args添加到适配后的配置中
        adapted['args'] = plotting_args
        
        return adapted
    
    def _adapt_simple_config(self) -> Dict[str, Any]:
        """适配简单分组格式配置"""
        adapted = {}
        
        # 1. 复制全局配置（非分组配置）
        for key, value in self.raw_config.items():
            if not isinstance(value, dict):
                adapted[key] = value
        
        # 设置默认值
        plotting_args = {
            'plot_type': adapted.get('plot_type', ['standard']),
            'npz_merge_strategy': adapted.get('npz_merge_strategy', True)
        }
        
        # 2. 处理standard分组
        if 'standard' in self.raw_config:
            standard_config = self.raw_config['standard']
            
            # 基础配置
            plotting_args.update({
                'show_histogram': standard_config.get('show_histogram', True),
                'show_coverage': standard_config.get('show_coverage', False),
                'show_percentiles': standard_config.get('show_percentiles', True),
                'show_noise_models': standard_config.get('show_noise_models', True),
                'show_mode': standard_config.get('show_mode', False),
                'show_mean': standard_config.get('show_mean', False),
                'percentiles': standard_config.get('percentiles', [10, 50, 90]),
                'period_lim': standard_config.get('period_lim', [0.01, 1000.0]),
                'xaxis_frequency': standard_config.get('xaxis_frequency', False),
                'cumulative_plot': standard_config.get('cumulative_plot', False)
            })
            
            # 处理特殊映射
            if 'grid' in standard_config:
                plotting_args['standard_grid'] = standard_config['grid']
            if 'cmap' in standard_config:
                plotting_args['standard_cmap'] = standard_config['cmap']
        
        # 3. 处理temporal分组
        if 'temporal' in self.raw_config:
            temporal_config = self.raw_config['temporal']
            plotting_args.update({
                'temporal_plot_periods': temporal_config.get('plot_periods', [1.0, 8.0, 20.0]),
                'time_format_x_temporal': temporal_config.get('time_format_x', '%H:%M'),
                'temporal_grid': temporal_config.get('grid', True),
                'temporal_cmap': temporal_config.get('cmap', 'viridis')
            })
        
        # 4. 处理spectrogram分组
        if 'spectrogram' in self.raw_config:
            spectrogram_config = self.raw_config['spectrogram']
            plotting_args.update({
                'clim': spectrogram_config.get('clim', [-180, -100]),
                'time_format_x_spectrogram': spectrogram_config.get('time_format_x', '%Y-%m-%d'),
                'spectrogram_grid': spectrogram_config.get('spectrogram_grid', True),
                'spectrogram_cmap': spectrogram_config.get('spectrogram_cmap', 'viridis')
            })
        
        # 将args添加到适配后的配置中
        adapted['args'] = plotting_args
        
        return adapted
    
    def _adapt_flat_config(self) -> Dict[str, Any]:
        """适配扁平格式配置（传统格式）"""
        # 扁平格式直接返回，假设已经是兼容格式
        return self.raw_config.copy()
    
    def get_config(self) -> Dict[str, Any]:
        """获取适配后的配置"""
        return self.adapted_config
    
    def get_format(self) -> str:
        """获取配置文件格式"""
        return self.config_format
    
    def get_raw_config(self) -> Dict[str, Any]:
        """获取原始配置"""
        return self.raw_config
    
    def print_format_info(self):
        """打印配置格式信息"""
        format_descriptions = {
            "grouped": "精细分组格式 - 多层嵌套结构（推荐）",
            "simple": "简单分组格式 - 按绘图类型分组",
            "flat": "扁平格式 - 传统单层结构"
        }
        
        print(f"配置文件格式: {format_descriptions.get(self.config_format, '未知格式')}")
        print(f"配置文件路径: {self.config_path}")
        
        if self.config_format == "grouped":
            print("✅ 当前使用最新的分组配置格式")
        elif self.config_format == "simple":
            print("⚠️  使用简单分组格式，建议升级到精细分组格式")
        else:
            print("⚠️  使用传统扁平格式，建议升级到分组格式")
    
    def convert_to_grouped_format(self) -> Dict[str, Any]:
        """将当前配置转换为精细分组格式"""
        if self.config_format == "grouped":
            return self.raw_config.copy()
        
        # 构建精细分组格式配置
        grouped_config = {
            'global': {
                'log_level': self.raw_config.get('log_level', 'DEBUG'),
                'description': 'PPSD绘图配置文件 - 分组结构版本',
                'version': '2.0'
            },
            'paths': {
                'input_npz_dir': self.raw_config.get('input_npz_dir', './output/npz/'),
                'inventory_path': self.raw_config.get('inventory_path', './input/BJ.XML'),
                'output_dir': self.raw_config.get('output_dir', './output/plots/'),
                'output_filename_pattern': self.raw_config.get('output_filename_pattern',
                    '{plot_type}_{datetime}_{network}-{station}-{location}-{channel}.png')
            },
            'plotting': {
                'plot_types': self.raw_config.get('plot_types', ['standard']),
                'npz_merge_strategy': self.raw_config.get('npz_merge_strategy', True),
                            # dpi 和 figure_size 已硬编码，不再从配置读取
            }
        }
        
        # 转换standard配置
        if 'standard' in self.raw_config or any(key.startswith('show_') for key in self.raw_config):
            standard_config = self.raw_config.get('standard', {})
            
            grouped_config['standard'] = {
                'show_histogram': standard_config.get('show_histogram', self.raw_config.get('show_histogram', True)),
                'show_percentiles': standard_config.get('show_percentiles', self.raw_config.get('show_percentiles', True)),
                'show_noise_models': standard_config.get('show_noise_models', self.raw_config.get('show_noise_models', True)),
                'show_coverage': standard_config.get('show_coverage', self.raw_config.get('show_coverage', False)),
                'show_mode': standard_config.get('show_mode', self.raw_config.get('show_mode', False)),
                'show_mean': standard_config.get('show_mean', self.raw_config.get('show_mean', False)),
                'standard_grid': standard_config.get('grid', self.raw_config.get('standard_grid', True)),
                'period_lim': standard_config.get('period_lim', self.raw_config.get('period_lim', [0.01, 1000.0])),
                'xaxis_frequency': standard_config.get('xaxis_frequency', self.raw_config.get('xaxis_frequency', False)),
                'cumulative_plot': standard_config.get('cumulative_plot', self.raw_config.get('cumulative_plot', False)),
                'standard_cmap': standard_config.get('cmap', self.raw_config.get('standard_cmap', 'viridis')),
                'percentiles': {
                    'values': standard_config.get('percentiles', self.raw_config.get('percentiles', [10, 50, 90])),
                    'color': 'lightgray',
                    'linewidth': 1.0,
                    'linestyle': '--',
                    'alpha': 0.8
                },
                'peterson': {
                    'nlnm_color': 'blue',
                    'nhnm_color': 'red',
                    'linewidth': 1.0,
                    'linestyle': '--',
                    'alpha': 0.8
                }
            }
        
        # 转换temporal配置
        if 'temporal' in self.raw_config:
            temporal_config = self.raw_config['temporal']
            grouped_config['temporal'] = {
                'plot_periods': temporal_config.get('plot_periods', [1.0, 8.0, 20.0]),
                'time_format_x': temporal_config.get('time_format_x', '%H:%M'),
                'temporal_grid': temporal_config.get('temporal_grid', True),
                'temporal_cmap': temporal_config.get('temporal_cmap', 'Blues')
            }
        
        # 转换spectrogram配置
        if 'spectrogram' in self.raw_config:
            spectrogram_config = self.raw_config['spectrogram']
            grouped_config['spectrogram'] = {
                'clim': spectrogram_config.get('clim', [-180, -100]),
                'time_format_x': spectrogram_config.get('time_format_x', '%Y-%m-%d'),
                'spectrogram_grid': spectrogram_config.get('spectrogram_grid', True),
                'spectrogram_cmap': spectrogram_config.get('spectrogram_cmap', 'viridis')
            }
        
        return grouped_config
    
    def save_as_grouped_format(self, output_path: str):
        """将配置保存为精细分组格式"""
        grouped_config = self.convert_to_grouped_format()
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                toml.dump(grouped_config, f)
            print(f"配置已保存为精细分组格式: {output_path}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")


def demonstrate_unified_adapter():
    """演示统一配置适配器的使用"""
    
    config_path = "input/config_plot.toml"
    
    print("=== 统一配置适配器演示 ===\n")
    
    # 创建适配器
    adapter = UnifiedConfigAdapter(config_path)
    
    # 显示格式信息
    print("1. 配置格式检测:")
    adapter.print_format_info()
    
    print(f"\n2. 检测到的配置格式: {adapter.get_format()}")
    
    print("\n3. 适配后的配置样例:")
    adapted_config = adapter.get_config()
    
    # 显示关键配置
    key_examples = [
        'log_level', 'input_npz_dir', 'output_dir',
        'plot_types', 'npz_merge_strategy'
    ]
    
    for key in key_examples:
        if key in adapted_config:
            print(f"  {key}: {adapted_config[key]}")
    
    # 显示args中的关键配置
    if 'args' in adapted_config:
        print("\n  args 配置:")
        args_examples = [
            'show_percentiles', 'percentiles', 'show_noise_models',
            'temporal_plot_periods', 'clim'
        ]
        
        for key in args_examples:
            if key in adapted_config['args']:
                print(f"    {key}: {adapted_config['args'][key]}")
    
    print("\n4. 配置格式转换演示:")
    if adapter.get_format() != "grouped":
        print("  转换为精细分组格式...")
        grouped_config = adapter.convert_to_grouped_format()
        print("  ✅ 转换成功")
        print(f"  转换后包含 {len(grouped_config)} 个主要分组")
    else:
        print("  ✅ 当前已是精细分组格式，无需转换")


if __name__ == "__main__":
    demonstrate_unified_adapter() 