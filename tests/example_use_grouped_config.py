#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: 
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)

使用分组配置适配器的演示

展示如何使用config_plot.toml的嵌套分组结构
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cp_ppsd.grouped_config_adapter import GroupedConfigAdapter

def main():
    """演示分组配置的使用"""
    print("=== 模拟 run_cp_ppsd.py 使用分组配置 ===")
    print()
    
    # 配置文件路径
    config_path = "input/config_plot.toml"  # 现在主配置文件就是分组配置
    
    # 尝试加载配置
    try:
        adapter = GroupedConfigAdapter(config_path)
        config = adapter.get_config()
        
        print("1. 配置加载成功")
        print(f"   配置文件: {config_path}")
        print(f"   版本: {config.get('version', 'N/A')}")
        print(f"   描述: {config.get('description', 'N/A')}")
        print()
        
        print("2. 路径配置:")
        print(f"   输入目录: {config.get('input_npz_dir')}")
        print(f"   输出目录: {config.get('output_dir')}")
        print(f"   仪器响应: {config.get('inventory_path')}")
        print()
        
        print("3. 绘图设置:")
        args = config.get('args', {})
        print(f"   绘图类型: {args.get('plot_type', [])}")
        print(f"   图像尺寸: {args.get('figure_size', [12, 8])}")
        print(f"   DPI: {args.get('dpi', 150)}")
        print()
        
        # 显示高级设置
        print("--- 高级设置 ---")
        print(f"字体支持: {args.get('enable_chinese_fonts', False)}")
        print(f"字体族: {args.get('font_family', 'Arial')}")
        print(f"内存优化: {args.get('memory_optimization', False)}")
        print(f"并行处理: {args.get('parallel_processing', False)}")
        print()
        
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        
    # 演示分组配置的优势
    print("=== 分组配置优势演示 ===")
    print()
    print("1. 结构化分组:")
    print("   ✅ [global] - 全局设置清晰")
    print("   ✅ [paths] - 路径配置集中")
    print("   ✅ [standard] - 标准图参数分组")
    print("   ✅ [standard.percentiles] - 百分位数子配置")
    print("   ✅ [standard.peterson] - 皮特森曲线子配置")
    print()
    
    print("2. 分组配置的优势:")
    print("   [√] [global] - 全局设置清晰")
    print("   [√] [paths] - 路径配置集中")
    print("   [√] [standard] - 标准图参数分组")
    print("   [√] [standard.percentiles] - 百分位数子配置")
    print("   [√] [standard.peterson] - 皮特森曲线子配置")
    
    print("\n3. 参数关联性:")
    print("   [√] 百分位数相关参数全部在 [standard.percentiles] 中")
    print("   [√] 皮特森曲线参数全部在 [standard.peterson] 中")
    print("   [√] 不同绘图类型参数独立分组")
    
    print("\n4. 维护便利性:")
    print("   [√] 添加新的百分位数参数时位置明确")
    print("   [√] 修改皮特森曲线样式时一目了然")
    print("   [√] 扩展新的子配置组很简单")
    
    print("\n5. 兼容性:")
    print("   [√] 适配器自动转换为现有格式")
    print("   [√] 现有代码无需任何修改")
    print("   [√] 支持逐步迁移")
    
    # 使用指南
    print("=== 在 run_cp_ppsd.py 中的使用方法 ===")
    print()
    print("方法1: 直接使用主配置文件")
    print("```bash")
    print("python run_cp_ppsd.py input/config_plot.toml")
    print("```")
    print()
    print("方法2: 在代码中使用适配器")
    print("```python")
    print("from cp_ppsd.grouped_config_adapter import GroupedConfigAdapter")
    print()
    print("# 在run_cp_ppsd.py中")
    print("def load_config(config_path):")
    print("    if 'grouped' in config_path:")
    print("        adapter = GroupedConfigAdapter(config_path)")
    print("        return adapter.get_config()")
    print("    else:")
    print("        # 原有的配置加载方式")
    print("        return original_load_config(config_path)")
    print("```")
    print()
    
    print("配置文件选择建议:")
    print("- config_plot.toml: 主配置文件（现为精细分组配置）")
    print("- config_plot_backup.toml: 原始简单配置（备份）")
    print("- config_plot_simple_grouped.toml: 简单分组配置")
    print("- config_plot_fine_grouped.toml: 更细粒度分组配置")

if __name__ == "__main__":
    main() 