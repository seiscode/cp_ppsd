#!/usr/bin/env python3
"""
测试plot_type配置解析
"""

import toml
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cp_ppsd.unified_config_adapter import UnifiedConfigAdapter

def test_plot_type_parsing():
    """测试plot_type配置解析"""
    config_path = "input/config_plot.toml"
    
    print("=== plot_type配置解析测试 ===")
    
    # 读取原始TOML
    with open(config_path, 'r', encoding='utf-8') as f:
        raw_config = toml.load(f)
    
    print(f"原始TOML中的plot_type: {raw_config.get('plotting', {}).get('plot_type')}")
    
    # 使用UnifiedConfigAdapter解析
    adapter = UnifiedConfigAdapter(raw_config)
    args = adapter.get_args()
    
    print(f"适配器解析后的plot_type: {args.get('plot_type')}")
    print(f"plot_type类型: {type(args.get('plot_type'))}")
    
    # 检查是否正确转换为列表
    plot_types = args.get('plot_type', ['standard'])
    if isinstance(plot_types, str):
        plot_types = [plot_types]
    
    print(f"最终plot_types列表: {plot_types}")
    
    for i, plot_type in enumerate(plot_types):
        print(f"  {i}: {plot_type} (类型: {type(plot_type)})")

if __name__ == "__main__":
    test_plot_type_parsing() 