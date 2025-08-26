#!/usr/bin/env python3

from cp_ppsd.cp_psd import main
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


"""
Author:
    muly (muly@cea-igp.ac.cn)
license:
    MIT License
    (https://opensource.org/licenses/MIT)
"""
"""
CP-PPSD主程序

使用方法:
    python run_cp_ppsd.py config.toml                        # 仅计算
    python run_cp_ppsd.py config_plot.toml                   # 仅绘图
    python run_cp_ppsd.py config.toml config_plot.toml       # 计算+绘图
"""


if __name__ == "__main__":
    main()
