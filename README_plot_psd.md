# PSD值分析和可视化工具

## 概述

`run_plot_psd.py` 是一个专门用于分析和可视化PPSD（Probabilistic Power Spectral Density）数据的工具。它从NPZ文件中提取PSD值并生成详细的分析图表。

## 功能特性

- **PPSD概率密度分布图**：使用清淡的Blues配色方案，显示噪声功率谱密度的概率分布
- **PSD值散点图**：使用清淡配色，展示PSD值的分布特征
- **各时间段PSD曲线对比**：显示不同时间段的PSD曲线，便于识别时间变化
- **中文字体支持**：自动检测和配置中文字体，确保图表标签正确显示

## 使用方法

### 基本用法

```bash
# 使用默认NPZ文件（如果存在）
python run_plot_psd.py

# 指定特定的NPZ文件
python run_plot_psd.py path/to/your/file.npz

# 指定NPZ文件和输出目录
python run_plot_psd.py path/to/your/file.npz ./custom_output/
```

### 在conda环境中使用

```bash
# 激活seis环境并运行
conda run -n seis python run_plot_psd.py

# 或者先激活环境再运行
conda activate seis
python run_plot_psd.py
```

## 输入要求

- **NPZ文件**：由`run_cp_ppsd.py`计算生成的PPSD数据文件
- **仪器响应文件**：用于获取台站元数据（程序会自动查找）

## 输出内容

- **psd_analysis_{datetime}_{STATION}.png**：四合一分析图表，包含：
  - PPSD概率密度分布（清淡配色）
  - PSD值散点图（清淡配色）
  - 各时间段PSD曲线对比
  - 预留的时间序列分析位置（功能已移除）
- **chinese_font_test.png**：中文字体测试图（调试用）

### 文件命名规则

输出文件名格式：`psd_analysis_{datetime}_{network}-{station}-{location}-{channel}.png`

其中：
- `{datetime}`：数据开始时间，格式为YYYYMMDDHHMM（如：202503260000）
- `{network}`：台网代码（如：BJ）
- `{station}`：台站代码（如：DAX）
- `{location}`：位置代码（如：00）
- `{channel}`：通道代码（如：BHZ）

示例文件名：`psd_analysis_202503260000_BJ-DAX-00-BHZ.png`

## 配色方案

- **清淡风格**：PPSD概率密度分布和散点图使用Blues配色方案，提供柔和的视觉体验
- **对比鲜明**：时间段PSD曲线使用viridis配色，确保不同曲线易于区分
- **专业外观**：适合科学报告和学术展示

## 文件结构

```
项目根目录/
├── run_plot_psd.py          # 主调用程序
├── cp_ppsd/
│   ├── plot_psd_values.py   # 核心分析模块
│   ├── cp_psd.py           # PPSD计算模块
│   └── __init__.py
├── output/
│   ├── npz/                # NPZ数据文件目录
│   └── plots/              # 图像输出目录
└── input/
    └── *.dataless          # 仪器响应文件
```

## 错误处理

程序具有完善的错误处理机制：

- **文件不存在**：自动列出可用的NPZ文件
- **数据无效**：提供详细的错误信息和建议
- **参数错误**：显示正确的使用方法

## 技术特性

- **自动字体检测**：支持多种中文字体，确保跨平台兼容性
- **内存优化**：高效处理大型NPZ文件
- **模块化设计**：核心功能与调用接口分离，便于维护和扩展

## 示例

```bash
# 分析特定台站的数据
python run_plot_psd.py ./output/npz/PPSD_202503251600_BJ-DAX-00-BHZ.npz

# 将结果保存到自定义目录
python run_plot_psd.py ./output/npz/PPSD_202503251600_BJ-DAX-00-BHZ.npz ./my_analysis/

# 批量处理（使用shell脚本）
for file in ./output/npz/*.npz; do
    python run_plot_psd.py "$file" "./analysis_results/"
done
```

## 注意事项

- 确保系统已安装中文字体支持
- NPZ文件必须包含有效的PPSD数据
- 输出目录会自动创建（如果不存在）
- 建议在conda seis环境中运行以确保依赖完整

## 相关工具

- `run_cp_ppsd.py`：PPSD计算和标准绘图工具
- `analyze_npz_content.py`：NPZ文件内容分析工具
- `ppsd_binning_demo.py`：PPSD分箱演示工具 