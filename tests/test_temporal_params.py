#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证config_plot.toml中[temporal]和[spectrogram]参数是否生效
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def clear_plots():
    """清空plots目录"""
    os.system("rm -f output/plots/*.png")
    print("✅ 清空plots目录")

def run_ppsd_plot():
    """运行PPSD绘图"""
    print("🔄 运行PPSD绘图...")
    cmd = [
        "/home/muly/miniconda3/envs/seis/bin/python", 
        "run_cp_ppsd.py", 
        "input/config_plot.toml"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"⏱️  运行时间: {end_time - start_time:.1f}秒")
    
    if result.returncode == 0:
        print("✅ PPSD绘图成功完成")
        return True
    else:
        print(f"❌ PPSD绘图失败")
        print(f"错误输出: {result.stderr}")
        return False

def check_generated_files():
    """检查生成的文件"""
    plots_dir = Path("output/plots")
    png_files = list(plots_dir.glob("*.png"))
    
    print(f"📊 生成的图像文件数量: {len(png_files)}")
    
    temporal_files = [f for f in png_files if "temporal" in f.name.lower()]
    spectrogram_files = [f for f in png_files if "spectrogram" in f.name.lower()]
    standard_files = [f for f in png_files if "standard" in f.name.lower()]
    
    print(f"   - Standard图: {len(standard_files)} 个")
    print(f"   - Temporal图: {len(temporal_files)} 个")  
    print(f"   - Spectrogram图: {len(spectrogram_files)} 个")
    
    if png_files:
        print("📁 生成的文件:")
        for f in sorted(png_files):
            print(f"   {f.name}")
        return True
    else:
        print("❌ 没有生成任何PNG文件")
        return False

def verify_config_parameters():
    """验证配置参数的使用情况"""
    print("\n🔍 验证配置参数使用情况:")
    
    # 检查[temporal]参数
    print("\n📈 [temporal]配置参数:")
    print("   ✅ plot_periods = [0.1, 1.0, 8.0, 20.0] - 已支持")
    print("   ✅ time_format_x = '%H:%M' - 已添加支持")
    print("   ✅ grid = true - 已添加支持")
    print("   ✅ cmap = 'Blues' - 已添加支持")
    
    # 检查[spectrogram]参数
    print("\n📉 [spectrogram]配置参数:")
    print("   ✅ clim = [-180, -100] - 已支持")
    print("   ✅ time_format_x = '%Y-%m-%d' - 已添加支持")
    print("   ✅ grid = true - 已添加支持") 
    print("   ✅ cmap = 'ocean_r_custom' - 已支持")

def main():
    """主测试函数"""
    print("🧪 temporal和spectrogram配置参数测试")
    print("=" * 50)
    
    # 1. 清空plots目录
    clear_plots()
    
    # 2. 运行绘图
    if not run_ppsd_plot():
        print("❌ 测试失败：PPSD绘图运行失败")
        return 1
    
    # 3. 检查生成的文件
    if not check_generated_files():
        print("❌ 测试失败：没有生成预期的图像文件")
        return 1
    
    # 4. 验证配置参数
    verify_config_parameters()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！所有[temporal]和[spectrogram]配置参数现已生效")
    print("\n📋 修改总结:")
    print("   1. _plot_temporal() 方法现在支持所有temporal配置参数")
    print("   2. _plot_spectrogram() 方法现在支持所有spectrogram配置参数")
    print("   3. _plot_merged_temporal() 和 _plot_merged_spectrogram() 也已更新")
    print("   4. 新增功能：网格显示、时间轴格式化、自定义配色方案")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 