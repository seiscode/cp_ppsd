#!/usr/bin/env python3
"""
Author:
    muly (muly@cea-igp.ac.cn)
license:
    MIT License
    (https://opensource.org/licenses/MIT)

演示如何读取分组的TOML配置文件

展示TOML分组配置的读取方法和最佳实践
"""

import toml
from typing import Dict, Any
import os

def read_grouped_config(config_path: str) -> Dict[str, Any]:
    """
    读取分组的TOML配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = toml.load(f)
        return config
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return {}

def demonstrate_config_access():
    """演示各种配置访问方式"""
    
    config_path = "../input/config_plot.toml"
    
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
        return
    
    config = read_grouped_config(config_path)
    
    print("=== TOML分组配置读取演示 ===\n")
    
    # 1. 访问顶级分组
    print("1. 顶级分组访问:")
    print(f"  全局日志级别: {config.get('global', {}).get('log_level', 'INFO')}")
    print(f"  输入目录: {config.get('paths', {}).get('input_npz_dir', 'N/A')}")
    print(f"  输出目录: {config.get('paths', {}).get('output_dir', 'N/A')}")
    print()
    
    # 2. 访问嵌套分组
    print("2. 嵌套分组访问:")
    standard_config = config.get('standard', {})
    print(f"  标准图显示直方图: {standard_config.get('show_histogram', False)}")
    print(f"  标准图配色方案: {standard_config.get('standard_cmap', 'default')}")
    
    # 访问深层嵌套
    percentile_config = standard_config.get('percentile_settings', {})
    print(f"  百分位数值: {percentile_config.get('values', [])}")
    print(f"  百分位数颜色: {percentile_config.get('color', 'black')}")
    
    peterson_config = standard_config.get('peterson', {})
    print(f"  NLNM颜色: {peterson_config.get('nlnm_color', 'blue')}")
    print(f"  NHNM颜色: {peterson_config.get('nhnm_color', 'red')}")
    print()
    
    # 3. 批量访问同类配置
    print("3. 批量访问配置:")
    
    # 获取所有绘图类型的配置
    plot_configs = {}
    for plot_type in ['standard', 'temporal', 'spectrogram']:
        if plot_type in config:
            plot_configs[plot_type] = config[plot_type]
            print(f"  {plot_type}图配置项数量: {len(plot_configs[plot_type])}")
    print()
    
    # 4. 安全访问方法（使用get避免KeyError）
    print("4. 安全访问方法:")
    
    def safe_get(data: dict, *keys, default=None):
        """安全获取嵌套字典的值"""
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default
        return data
    
    # 示例：安全获取深层嵌套的值
    nlnm_color = safe_get(config, 'standard', 'peterson', 'nlnm_color', default='blue')
    percentile_alpha = safe_get(config, 'standard', 'percentile_settings', 'alpha', default=0.8)
    font_family = safe_get(config, 'advanced', 'font_family', default='Arial')
    
    print(f"  NLNM颜色（安全获取）: {nlnm_color}")
    print(f"  百分位数透明度（安全获取）: {percentile_alpha}")
    print(f"  字体系列（安全获取）: {font_family}")
    print()
    
    # 5. 配置验证和默认值
    print("5. 配置验证:")
    required_sections = ['paths', 'plotting', 'standard']
    missing_sections = [section for section in required_sections if section not in config]
    
    if missing_sections:
        print(f"  ⚠️  缺失必需的配置分组: {missing_sections}")
    else:
        print("  ✅ 所有必需的配置分组都存在")
    
    # 6. 配置合并（覆盖默认值）
    print("\n6. 配置合并示例:")
    
    # 默认配置
    default_standard_config = {
        'show_histogram': True,
        'show_percentiles': False,
        'standard_cmap': 'viridis',
        'percentile_settings': {
            'values': [25, 50, 75],
            'color': 'black',
            'linewidth': 1.0,
            'alpha': 1.0
        }
    }
    
    # 合并用户配置
    user_standard_config = config.get('standard', {})
    merged_config = {**default_standard_config, **user_standard_config}
    
    # 对于嵌套字典，需要递归合并
    if 'percentile_settings' in user_standard_config:
        merged_config['percentile_settings'] = {
            **default_standard_config['percentile_settings'],
            **user_standard_config['percentile_settings']
        }
    
    print(f"  合并后的百分位数值: {merged_config['percentile_settings']['values']}")
    print(f"  合并后的百分位数颜色: {merged_config['percentile_settings']['color']}")

def create_config_builder():
    """演示配置构建器模式"""
    
    class ConfigBuilder:
        """配置构建器类"""
        
        def __init__(self):
            self.config = {}
        
        def add_global_settings(self, log_level="INFO", description=""):
            """添加全局设置"""
            self.config['global'] = {
                'log_level': log_level,
                'description': description
            }
            return self
        
        def add_paths(self, input_dir, output_dir, inventory_path=""):
            """添加路径设置"""
            self.config['paths'] = {
                'input_npz_dir': input_dir,
                'output_dir': output_dir,
                'inventory_path': inventory_path
            }
            return self
        
        def add_standard_config(self, cmap="viridis", show_percentiles=True):
            """添加标准图配置"""
            self.config['standard'] = {
                'standard_cmap': cmap,
                'show_percentiles': show_percentiles,
                'percentile_settings': {
                    'values': [10, 50, 90],
                    'color': 'lightgray',
                    'alpha': 0.8
                }
            }
            return self
        
        def save_to_file(self, filepath):
            """保存到文件"""
            with open(filepath, 'w', encoding='utf-8') as f:
                toml.dump(self.config, f)
            return self
        
        def get_config(self):
            """获取配置字典"""
            return self.config
    
    print("\n=== 配置构建器演示 ===")
    
    # 使用构建器创建配置
    builder = ConfigBuilder()
    config = (builder
              .add_global_settings(log_level="DEBUG", description="动态生成的配置")
              .add_paths("./input/", "./output/", "./metadata.xml")
              .add_standard_config(cmap="hot_r_custom", show_percentiles=True)
              .get_config())
    
    print("构建器生成的配置:")
    print(toml.dumps(config))

if __name__ == "__main__":
    # 运行演示
    demonstrate_config_access()
    create_config_builder() 
