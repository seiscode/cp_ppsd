#!/usr/bin/env python3
"""
:Author: 
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
"""
PSD值分析和可视化工具 - 主入口脚本

功能说明:
    从NPZ文件中提取PSD值并生成详细的分析图表，包括：
    - PPSD概率密度分布图（清淡配色）
    - PSD值散点图（清淡配色）
    - 各时间段PSD曲线对比
    - PSD时间序列分析图（右下角）

使用方法:
    python run_plot_psd.py                                    # 使用默认NPZ文件
    python run_plot_psd.py path/to/specific.npz               # 指定NPZ文件
    python run_plot_psd.py path/to/specific.npz output_dir/   # 指定NPZ文件和输出目录

输入要求:
    - NPZ文件：由cp_ppsd计算生成的PPSD数据文件
    - 仪器响应文件：用于获取台站元数据（可选）

输出内容:
    - psd_analysis_[STATION].png：四合一分析图表，包含完整的时间序列分析

注意事项:
    - 确保系统已安装中文字体支持
    - NPZ文件必须包含有效的PSD数据
    - 输出图像使用清淡配色方案，适合报告和展示
    - 时间序列分析显示特定频率点的PSD随时间变化
    - 该脚本独立运行，不依赖配置文件
"""

import os
import sys

# 将cp_ppsd模块添加到导入路径
cp_ppsd_path = os.path.dirname(os.path.abspath(__file__))
if cp_ppsd_path not in sys.path:
    sys.path.insert(0, cp_ppsd_path)

# 导入主函数
try:
    from cp_ppsd.plot_psd_values import main
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保cp_ppsd模块在当前目录下")
    sys.exit(1)

if __name__ == "__main__":
    main() 