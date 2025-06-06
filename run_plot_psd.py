#!/usr/bin/env python3

import os
import sys

"""
:Author:
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
"""
PPSD绘图脚本

从已计算的NPZ文件生成PPSD图像

Date: 2025-01-30
"""

# 检查和修改系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入主函数
from cp_ppsd.plot_psd_values import main  # noqa: E402


def print_usage():
    """打印使用说明"""
    print("PPSD绘图脚本使用方法:")
    print("  python run_plot_psd.py config_plot.toml")
    print()
    print("参数说明:")
    print("  config_plot.toml: 绘图配置文件")
    print()
    print("示例:")
    print("  python run_plot_psd.py input/config_plot.toml")


if __name__ == "__main__":
    main()
