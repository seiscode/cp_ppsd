#!/usr/bin/env python3
"""
:Author: 
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
"""
CP-PPSD 主入口脚本

使用方法:
    python run_cp_ppsd.py input/config.toml                    # 仅计算PPSD
    python run_cp_ppsd.py input/config_plot.toml               # 仅绘图
    python run_cp_ppsd.py input/config.toml input/config_plot.toml   # 计算+绘图
"""

import os
import sys

# 添加当前目录到Python路径，确保可以导入cp_ppsd模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cp_ppsd.cp_psd import main

if __name__ == "__main__":
    main()
