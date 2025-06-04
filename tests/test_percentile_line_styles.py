#!/usr/bin/env python3
"""
百分位数线样式测试脚本

此脚本测试自定义百分位数线样式功能，对比默认样式和自定义样式的效果。

使用方法:
    python tests/test_percentile_line_styles.py
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import toml

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cp_ppsd.cp_psd import PPSDProcessor


def test_percentile_line_styles():
    """测试百分位数线样式功能"""
    
    print("=" * 60)
    print("百分位数线样式测试")
    print("=" * 60)
    
    # 检查是否有NPZ文件
    npz_dir = "./output/npz/"
    if not os.path.exists(npz_dir):
        print("❌ NPZ目录不存在，请先运行PPSD计算")
        return
    
    npz_files = [f for f in os.listdir(npz_dir) if f.endswith('.npz')]
    if not npz_files:
        print("❌ 没有找到NPZ文件，请先运行PPSD计算")
        return
    
    print(f"✅ 找到 {len(npz_files)} 个NPZ文件")
    
    # 创建测试配置
    test_configs = {
        'default_style': {
            'show_percentiles': True,
            'percentiles': [10, 50, 90],
            # 不包含自定义样式参数，使用默认黑色粗线
        },
        'custom_light_gray': {
            'show_percentiles': True,
            'percentiles': [10, 50, 90],
            'percentile_color': 'lightgray',
            'percentile_linewidth': 1.0,
            'percentile_linestyle': '-',
            'percentile_alpha': 0.8
        },
        'custom_thin_blue': {
            'show_percentiles': True,
            'percentiles': [10, 50, 90],
            'percentile_color': 'steelblue',
            'percentile_linewidth': 0.8,
            'percentile_linestyle': '--',
            'percentile_alpha': 0.7
        },
        'custom_dotted_red': {
            'show_percentiles': True,
            'percentiles': [10, 50, 90],
            'percentile_color': 'darkred',
            'percentile_linewidth': 1.2,
            'percentile_linestyle': ':',
            'percentile_alpha': 0.9
        }
    }
    
    # 基础配置
    base_config = {
        'npz_input_dir': npz_dir,
        'output_dir': './output/plots/',
        'output_filename_pattern': 'test_percentile_{style}_{network}-{station}-{location}-{channel}.png',
        'args': {
            'plot_type': 'standard',
            'npz_merge_strategy': False,  # 单独绘制每个文件
            'show_histogram': True,
            'show_noise_models': True,
            'standard_grid': True,
            'period_lim': [0.01, 1000.0],
            'xaxis_frequency': False,
            'cumulative_plot': False,
            'show_coverage': True,
            'standard_cmap': 'hot_r_custom'
        }
    }
    
    # 测试每种样式
    for style_name, style_config in test_configs.items():
        print(f"\n🎨 测试样式: {style_name}")
        
        # 合并配置
        test_config = base_config.copy()
        test_config['args'].update(style_config)
        
        # 修改输出文件名模式以包含样式名称
        test_config['output_filename_pattern'] = test_config['output_filename_pattern'].replace(
            '{style}', style_name
        )
        
        try:
            # 创建处理器并运行
            processor = PPSDProcessor()
            processor.process_configs([test_config])
            
            print(f"  ✅ {style_name} 样式测试完成")
            
        except Exception as e:
            print(f"  ❌ {style_name} 样式测试失败: {e}")
    
    print(f"\n📊 测试完成！请检查 {base_config['output_dir']} 目录中的对比图像")
    print("\n样式说明:")
    print("  - default_style: ObsPy默认黑色粗线")
    print("  - custom_light_gray: 浅灰色细线（推荐）")
    print("  - custom_thin_blue: 钢蓝色虚线")
    print("  - custom_dotted_red: 深红色点线")


def create_style_comparison_report():
    """创建样式对比报告"""
    
    report_content = """
# 百分位数线样式测试报告

## 测试目的
验证自定义百分位数线样式功能，对比不同样式的视觉效果。

## 测试样式

### 1. default_style (默认样式)
- **颜色**: 黑色
- **线宽**: ObsPy默认（通常为2.0）
- **线型**: 实线
- **透明度**: 1.0（不透明）
- **特点**: 醒目但可能过于突出

### 2. custom_light_gray (浅灰色细线 - 推荐)
- **颜色**: lightgray
- **线宽**: 1.0
- **线型**: 实线 (-)
- **透明度**: 0.8
- **特点**: 低调不抢夺主图注意力，适合科学论文

### 3. custom_thin_blue (钢蓝色虚线)
- **颜色**: steelblue
- **线宽**: 0.8
- **线型**: 虚线 (--)
- **透明度**: 0.7
- **特点**: 专业感强，虚线样式便于区分

### 4. custom_dotted_red (深红色点线)
- **颜色**: darkred
- **线宽**: 1.2
- **线型**: 点线 (:)
- **透明度**: 0.9
- **特点**: 高对比度，适合演示展示

## 配置方法

在 `config_plot.toml` 中添加以下参数：

```toml
# 百分位数线样式配置（自定义参数）
percentile_color = "lightgray"      # 百分位数线颜色
percentile_linewidth = 1.0          # 百分位数线宽度
percentile_linestyle = "-"          # 百分位数线样式 ("-", "--", "-.", ":")
percentile_alpha = 0.8              # 百分位数线透明度 (0.0-1.0)
```

## 推荐设置

对于科学论文和正式报告，推荐使用：
- **颜色**: "lightgray" 或 "darkgray"
- **线宽**: 1.0 或 0.8
- **线型**: "-" (实线)
- **透明度**: 0.8

这样的设置既能显示百分位数信息，又不会干扰主要的PPSD数据可视化。
"""
    
    # 保存报告
    report_file = "./output/plots/percentile_style_test_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📝 样式对比报告已保存: {report_file}")


if __name__ == "__main__":
    test_percentile_line_styles()
    create_style_comparison_report() 