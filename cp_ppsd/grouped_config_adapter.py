#!/usr/bin/env python3
"""
:Author: 
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
"""
分组配置适配器 - 处理config_plot.toml的嵌套分组结构

本适配器负责将分组结构的TOML配置文件转换为现有代码兼容的扁平结构，
确保在不修改现有代码的情况下使用新的分组配置格式。

主要功能：
1. 解析嵌套分组配置（如 [standard.percentiles]）
2. 转换为现有代码期望的扁平参数格式
3. 提供向后兼容性

处理config_plot.toml的嵌套分组配置文件
"""

import toml
from typing import Dict, Any


class GroupedConfigAdapter:
    """
    分组配置适配器类
    
    处理config_plot.toml的嵌套分组配置文件
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
        """适配分组配置为兼容格式"""
        adapted = {}
        
        # 1. 处理global配置
        if 'global' in self.raw_config:
            global_config = self.raw_config['global']
            adapted['log_level'] = global_config.get('log_level', 'DEBUG')
            adapted['description'] = global_config.get('description', '')
            adapted['version'] = global_config.get('version', '1.0')
        
        # 2. 处理paths配置
        if 'paths' in self.raw_config:
            paths_config = self.raw_config['paths']
            adapted.update({
                'input_npz_dir': paths_config.get('input_npz_dir', './output/npz/'),
                'inventory_path': paths_config.get('inventory_path', './input/BJ.XML'),
                'output_dir': paths_config.get('output_dir', './output/plots/'),
                'output_filename_pattern': paths_config.get('output_filename_pattern', 
                    '{plot_type}_{datetime}_{network}-{station}-{location}-{channel}.png')
            })
        
        # 3. 处理plotting配置
        plotting_args = {}
        if 'plotting' in self.raw_config:
            plotting_config = self.raw_config['plotting']
            adapted.update({
                'plot_types': plotting_config.get('plot_types', ['standard']),
                'npz_merge_strategy': plotting_config.get('npz_merge_strategy', True),
                            # dpi 和 figure_size 已硬编码，不再从配置读取
            })
            
            # 将绘图类型和合并策略也加入args中（程序期望从args获取）
            plotting_args.update({
                'plot_type': plotting_config.get('plot_types', ['standard']),
                'npz_merge_strategy': plotting_config.get('npz_merge_strategy', True)
            })
        
        # 4. 处理standard配置及其子分组 - 包装到args中
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
            elif 'percentile_settings' in standard_config:
                # 处理TOML解析后的实际键名
                percentiles_config = standard_config['percentile_settings']
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
            
            # 处理mode子分组
            if 'mode' in standard_config:
                mode_config = standard_config['mode']
                plotting_args.update({
                    'mode_color': mode_config.get('color', 'orange'),
                    'mode_linewidth': mode_config.get('linewidth', 1.0),
                    'mode_linestyle': mode_config.get('linestyle', '-'),
                    'mode_alpha': mode_config.get('alpha', 0.9)
                })
            
            # 处理mean子分组
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
        
        # 8. 处理advanced配置
        if 'advanced' in self.raw_config:
            advanced_config = self.raw_config['advanced']
            plotting_args.update({
                'matplotlib_backend': advanced_config.get('matplotlib_backend', 'Agg'),
                            'font_family': advanced_config.get('font_family', 'WenQuanYi Micro Hei'),
            'enable_chinese_fonts': advanced_config.get('enable_chinese_fonts', True),
            'font_size': advanced_config.get('font_size', 8),
                'memory_optimization': advanced_config.get('memory_optimization', True),
                'parallel_processing': advanced_config.get('parallel_processing', False)
            })
            
            # 处理compatibility子分组
            if 'compatibility' in advanced_config:
                compatibility_config = advanced_config['compatibility']
                plotting_args.update({
                    'obspy_version': compatibility_config.get('obspy_version', '>=1.4.0'),
                    'numpy_version': compatibility_config.get('numpy_version', '>=1.20.0'),
                    'matplotlib_version': compatibility_config.get('matplotlib_version', '>=3.5.0')
                })
        
        # 7. 处理colors配置（完整映射）
        if 'colors' in self.raw_config:
            colors_config = self.raw_config['colors']
            plotting_args['available_cmaps'] = colors_config.get('available_cmaps', [])
            
            if 'presets' in colors_config:
                presets = colors_config['presets']
                plotting_args.update({
                    'color_primary': presets.get('primary', 'blue'),
                    'color_secondary': presets.get('secondary', 'red'),
                    'color_accent': presets.get('accent', 'orange'),
                    'color_neutral': presets.get('neutral', 'lightgray'),
                    'color_success': presets.get('success', 'green'),
                    'color_warning': presets.get('warning', 'orange'),
                    'color_error': presets.get('error', 'red')
                })
        
        # 将绘图参数包装到args字段中（与现有程序结构兼容）
        adapted['args'] = plotting_args
        
        return adapted
    
    def get_config(self) -> Dict[str, Any]:
        """获取适配后的配置"""
        return self.adapted_config
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取特定分组的配置"""
        return self.raw_config.get(section, {})
    
    def get_subsection(self, section: str, subsection: str) -> Dict[str, Any]:
        """获取特定子分组的配置"""
        if section in self.raw_config:
            section_config = self.raw_config[section]
            # 处理TOML解析的键名映射
            if subsection == 'percentiles' and 'percentile_settings' in section_config:
                return section_config['percentile_settings']
            return section_config.get(subsection, {})
        return {}
    
    def print_structure(self):
        """打印配置结构"""
        print("=== 分组配置结构 ===\n")
        
        print("配置文件结构:")
        print("├── [global] 全局设置")
        print("├── [paths] 路径配置")
        print("├── [plotting] 绘图基础设置")
        print("├── [standard] 标准图配置")
        print("│   ├── [standard.percentiles] 百分位数子配置")
        print("│   ├── [standard.peterson] 皮特森曲线子配置")
        print("│   ├── [standard.mode] 众数线子配置")
        print("│   └── [standard.mean] 均值线子配置")
        print("├── [temporal] 时间演化图配置")
        print("├── [spectrogram] 频谱图配置")
        print("├── [colors] 颜色配置")
        print("│   └── [colors.presets] 颜色预设")
        print("└── [advanced] 高级设置")
        print("    └── [advanced.compatibility] 兼容性设置")
    
    def print_mapping(self):
        """打印配置映射关系"""
        print("\n=== 主要配置映射 ===\n")
        
        mappings = [
            ("[global].log_level", "log_level"),
            ("[paths].input_npz_dir", "input_npz_dir"),
            ("[plotting].plot_types", "plot_types"),
            ("[standard].show_percentiles", "show_percentiles"),
            ("[standard.percentiles].values", "percentiles"),
            ("[standard.percentiles].color", "percentile_color"),
            ("[standard.peterson].nlnm_color", "peterson_nlnm_color"),
            ("[standard.peterson].nhnm_color", "peterson_nhnm_color"),
            ("[temporal].plot_periods", "temporal_plot_periods"),
            ("[spectrogram].clim", "clim"),
        ]
        
        for grouped_path, compat_name in mappings:
            print(f"  {grouped_path:30} -> {compat_name}")


def demonstrate_grouped_config():
    """演示分组配置的使用"""
    
    config_path = "input/config_plot.toml"  # 更新为新的配置文件路径
    
    print("=== 分组配置适配器演示 ===\n")
    
    # 创建适配器
    try:
        adapter = GroupedConfigAdapter(config_path)
    except FileNotFoundError:
        print(f"加载配置文件失败: [Errno 2] No such file or directory: '{config_path}'")
        print("显示配置结构和映射示例...\n")
        adapter = None
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        print("显示配置结构和映射示例...\n")
        adapter = None
    
    # 显示配置结构（即使文件不存在也显示）
    if adapter:
        adapter.print_structure()
        # 显示映射关系
        adapter.print_mapping()
        
        print("\n=== 适配后的关键配置 ===\n")
        adapted = adapter.get_config()
        
        # 显示主要配置
        key_configs = [
            ('log_level', '日志级别'),
            ('plot_types', '绘图类型'),
            ('args', 'args字段')
        ]
        
        for key, desc in key_configs:
            if key in adapted:
                if key == 'args':
                    print(f"  {desc:12}: [包含{len(adapted[key])}个绘图参数]")
                    # 显示args中的关键参数
                    args = adapted[key]
                    important_args = [
                        'show_percentiles', 'percentiles', 'percentile_color',
                        'show_noise_models', 'peterson_nlnm_color', 'peterson_nhnm_color',
                        'show_mode', 'mode_color', 'show_mean', 'mean_color',
                        'standard_cmap'
                    ]
                    for arg_key in important_args:
                        if arg_key in args:
                            print(f"    {arg_key}: {args[arg_key]}")
                else:
                    print(f"  {desc:12}: {adapted[key]}")
        
        print("\n=== 直接访问分组示例 ===\n")
        
        # 访问percentiles子分组
        percentiles_config = adapter.get_subsection('standard', 'percentiles')
        print("百分位数子配置:")
        if percentiles_config:
            for key, value in percentiles_config.items():
                print(f"  {key}: {value}")
        else:
            print("  (未找到百分位数配置)")
        
        print("\n皮特森曲线子配置:")
        peterson_config = adapter.get_subsection('standard', 'peterson')
        if peterson_config:
            for key, value in peterson_config.items():
                print(f"  {key}: {value}")
        else:
            print("  (未找到皮特森配置)")
    else:
        # 显示配置结构（静态版本）
        print("配置文件结构:")
        print("├── [global] 全局设置")
        print("├── [paths] 路径配置")
        print("├── [plotting] 绘图基础设置")
        print("├── [standard] 标准图配置")
        print("│   ├── [standard.percentiles] 百分位数子配置")
        print("│   ├── [standard.peterson] 皮特森曲线子配置")
        print("│   ├── [standard.mode] 众数线子配置")
        print("│   └── [standard.mean] 均值线子配置")
        print("├── [temporal] 时间演化图配置")
        print("├── [spectrogram] 频谱图配置")
        print("├── [colors] 颜色配置")
        print("│   └── [colors.presets] 颜色预设")
        print("└── [advanced] 高级设置")
        print("    └── [advanced.compatibility] 兼容性设置")
        
        print("\n=== 主要配置映射 ===\n")
        
        mappings = [
            ("[global].log_level", "log_level"),
            ("[paths].input_npz_dir", "input_npz_dir"),
            ("[plotting].plot_types", "plot_types"),
            ("[standard].show_percentiles", "show_percentiles"),
            ("[standard.percentiles].values", "percentiles"),
            ("[standard.percentiles].color", "percentile_color"),
            ("[standard.peterson].nlnm_color", "peterson_nlnm_color"),
            ("[standard.peterson].nhnm_color", "peterson_nhnm_color"),
            ("[temporal].plot_periods", "temporal_plot_periods"),
            ("[spectrogram].clim", "clim"),
        ]
        
        for grouped_path, compat_name in mappings:
            print(f"  {grouped_path:30} -> {compat_name}")
        
        print("\n=== 适配后的关键配置 ===\n")
        print("  (配置文件未找到，无法显示实际配置)")


if __name__ == "__main__":
    demonstrate_grouped_config() 