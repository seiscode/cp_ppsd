#!/usr/bin/env python3
"""
配置解析调试脚本
"""

import toml
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cp_ppsd.unified_config_adapter import UnifiedConfigAdapter


def test_raw_toml_parsing():
    """测试原始TOML解析"""
    config_path = "input/config_plot.toml"
    
    print("=== 原始TOML解析测试 ===")
    with open(config_path, 'r', encoding='utf-8') as f:
        raw_config = toml.load(f)
    
    print("原始配置键:")
    for key in raw_config.keys():
        print(f"  {key}")
    
    print("\n[standard] 节内容:")
    if 'standard' in raw_config:
        standard = raw_config['standard']
        for key, value in standard.items():
            print(f"  {key}: {value}")
    
    print("\n检查嵌套结构:")
    if 'standard' in raw_config:
        standard = raw_config['standard']
        nested_keys = ['percentiles', 'peterson', 'mode', 'mean']
        for key in nested_keys:
            if key in standard:
                print(f"  找到 [standard.{key}]: {standard[key]}")
            else:
                print(f"  未找到 [standard.{key}]")
    

def test_unified_adapter():
    """测试统一配置适配器"""
    config_path = "input/config_plot.toml"
    
    print("\n=== 统一配置适配器测试 ===")
    
    adapter = UnifiedConfigAdapter(config_path)
    
    print(f"检测格式: {adapter.get_format()}")
    print(f"原始配置键: {list(adapter.get_raw_config().keys())}")
    
    adapted_config = adapter.get_config()
    print(f"适配后配置键: {list(adapted_config.keys())}")
    
    if 'args' in adapted_config:
        args = adapted_config['args']
        print("\n参数检查:")
        
        # 检查嵌套配置相关参数
        nested_params = [
            'percentile_color', 'percentile_linewidth', 'percentile_linestyle', 'percentile_alpha',
            'peterson_nlnm_color', 'peterson_nhnm_color', 'peterson_linewidth', 'peterson_linestyle', 'peterson_alpha',
            'mode_color', 'mode_linewidth', 'mode_linestyle', 'mode_alpha',
            'mean_color', 'mean_linewidth', 'mean_linestyle', 'mean_alpha'
        ]
        
        for param in nested_params:
            if param in args:
                print(f"  ✓ {param}: {args[param]}")
            else:
                print(f"  ✗ {param}: 缺失")

if __name__ == "__main__":
    test_raw_toml_parsing()
    test_unified_adapter() 