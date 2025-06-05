#!/usr/bin/env python3
"""
:Author: 
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""

"""
简单配置适配器 - 处理按绘图类型分组的TOML配置

将按绘图类型分组的配置转换为现有代码兼容的格式
"""

import toml
from typing import Dict, Any


class SimpleConfigAdapter:
    """
    简单配置适配器类
    
    处理按绘图类型分组的配置文件
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
        将分组配置适配为兼容格式
        
        Returns:
            适配后的配置字典
        """
        adapted = {}
        
        # 1. 复制全局配置（非分组配置）
        for key, value in self.raw_config.items():
            if not isinstance(value, dict):
                adapted[key] = value
        
        # 2. 处理standard分组
        if 'standard' in self.raw_config:
            standard_config = self.raw_config['standard']
            # 将standard分组的参数复制到顶级
            for key, value in standard_config.items():
                # 为standard特有的参数添加前缀（如果需要）
                if key in ['cmap']:
                    adapted[f'standard_{key}'] = value
                elif key in ['grid']:
                    adapted[f'standard_{key}'] = value
                else:
                    adapted[key] = value
        
        # 3. 处理temporal分组
        if 'temporal' in self.raw_config:
            temporal_config = self.raw_config['temporal']
            # 为temporal参数添加前缀或映射到特定键名
            for key, value in temporal_config.items():
                if key == 'plot_periods':
                    adapted['temporal_plot_periods'] = value
                elif key == 'time_format_x':
                    adapted['time_format_x_temporal'] = value

                elif key == 'cmap':
                    adapted['temporal_cmap'] = value
                else:
                    adapted[f'temporal_{key}'] = value
        
        # 4. 处理spectrogram分组
        if 'spectrogram' in self.raw_config:
            spectrogram_config = self.raw_config['spectrogram']
            # 为spectrogram参数添加前缀或映射到特定键名
            for key, value in spectrogram_config.items():
                if key == 'time_format_x':
                    adapted['time_format_x_spectrogram'] = value
                elif key == 'grid':
                    adapted['spectrogram_grid'] = value
                elif key == 'cmap':
                    adapted['spectrogram_cmap'] = value
                else:
                    adapted[f'spectrogram_{key}'] = value
        
        return adapted
    
    def get_config(self) -> Dict[str, Any]:
        """获取适配后的配置"""
        return self.adapted_config
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取特定分组的配置"""
        return self.raw_config.get(section, {})
    
    def print_mapping(self):
        """打印配置映射关系"""
        print("=== 简单分组配置映射 ===\n")
        
        print("分组结构:")
        print("├── 全局配置")
        print("│   ├── log_level")
        print("│   ├── input_npz_dir")
        print("│   ├── plot_types")
        print("│   └── npz_merge_strategy")
        print("│")
        print("├── [standard] 标准图配置")
        print("│   ├── 基础显示: show_histogram, show_coverage, grid")
        print("│   ├── 百分位数: show_percentiles, percentiles, percentile_*")
        print("│   ├── 皮特森曲线: show_noise_models, peterson_*")
        print("│   ├── 众数线: show_mode, mode_*")
        print("│   └── 均值线: show_mean, mean_*")
        print("│")
        print("├── [temporal] 时间演化图配置")
        print("│   ├── plot_periods -> temporal_plot_periods")
        print("│   ├── time_format_x -> time_format_x_temporal")
        print("│   └── cmap -> temporal_cmap")
        print("│")
        print("└── [spectrogram] 频谱图配置")
        print("    ├── clim -> spectrogram_clim")
        print("    ├── time_format_x -> time_format_x_spectrogram")
        print("    ├── grid -> spectrogram_grid")
        print("    └── cmap -> spectrogram_cmap")


def demonstrate_simple_config():
    """演示简单分组配置的使用"""
    
    config_path = "input/config_plot_simple_grouped.toml"
    
    print("=== 简单分组配置演示 ===\n")
    
    # 创建适配器
    adapter = SimpleConfigAdapter(config_path)
    
    print("1. 原始分组结构:")
    raw_config = adapter.raw_config
    
    # 显示全局配置
    print("  全局配置:")
    global_keys = [key for key, value in raw_config.items() 
                   if not isinstance(value, dict)]
    for key in global_keys[:5]:  # 显示前5个
        print(f"    {key} = {raw_config[key]}")
    if len(global_keys) > 5:
        print(f"    ... (还有{len(global_keys)-5}个)")
    
    # 显示各分组
    for section in ['standard', 'temporal', 'spectrogram']:
        if section in raw_config:
            print(f"  [{section}] 配置:")
            section_config = raw_config[section]
            for key in list(section_config.keys())[:3]:  # 显示前3个
                print(f"    {key} = {section_config[key]}")
            if len(section_config) > 3:
                print(f"    ... (还有{len(section_config)-3}个参数)")
    
    print("\n2. 适配后的兼容配置:")
    adapted = adapter.get_config()
    
    # 显示关键配置
    key_examples = [
        'plot_types', 'show_percentiles', 'percentiles',
        'show_noise_models', 'peterson_nlnm_color',
        'temporal_plot_periods', 'time_format_x_temporal',
        'spectrogram_clim', 'time_format_x_spectrogram'
    ]
    
    for key in key_examples:
        if key in adapted:
            print(f"  {key} = {adapted[key]}")
    
    print("\n3. 配置映射关系:")
    adapter.print_mapping()
    
    # 演示如何访问特定分组
    print("\n4. 直接访问特定分组:")
    standard_config = adapter.get_section('standard')
    print("  [standard] 百分位数配置:")
    percentile_keys = [k for k in standard_config.keys() 
                       if 'percentile' in k]
    for key in percentile_keys:
        print(f"    {key}: {standard_config[key]}")


if __name__ == "__main__":
    demonstrate_simple_config() 