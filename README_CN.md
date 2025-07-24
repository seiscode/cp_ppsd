# PPSD 批量处理与可视化工具

本项目由[地震数据处理小组](#地震数据处理小组简介)研发，是一个基于Python的地震学数据分析工具，专门用于批量计算和可视化概率功率谱密度（PPSD, Probabilistic Power Spectral Density）。该工具基于[ObsPy](https://github.com/obspy/obspy)库实现，支持通过TOML配置文件进行灵活的参数配置，并提供专业的四合一分析图表。

## 主要功能

- **PPSD计算**：批量处理地震数据文件，计算PPSD并保存为NPZ格式
- **多种绘图类型**：支持标准PPSD图、时间演化图、频谱图
- **四合一分析图**：专业的PSD值分析和可视化工具（`run_plot_psd.py`）
- **灵活配置**：通过TOML配置文件进行参数设置
- **详细日志**：完整的处理过程记录和错误追踪
- **模块化设计**：支持计算和绘图分离，便于批量处理
- **中文支持**：完整的中文字体支持和本地化界面
- **清淡配色**：专业的科学可视化配色方案

## 核心工具

### 1. run_cp_ppsd.py - PPSD计算与标准绘图
主要的PPSD计算和标准可视化工具，支持：
- 批量PPSD计算
- 标准PPSD图、时间演化图、频谱图
- NPZ文件生成和管理
- 配置文件驱动的灵活处理

### 2. run_plot_psd.py - 专业PSD分析工具
专门的PSD值分析和可视化工具，提供：
- **四合一分析图**：PPSD概率密度分布、PSD值散点图、时间段PSD曲线对比、预留扩展位置
- **清淡配色方案**：Blues和viridis配色，适合科学报告
- **中文字体支持**：自动检测和配置中文字体
- **高质量输出**：300 DPI，适合印刷质量

## 快速开始

### 1. 环境准备

#### 方法1：只用conda安装（推荐）

```bash
# 克隆项目
git clone <repository_url>
cd cp_ppsd

# 方式A：创建environment.yml文件（可选，environment.yml已提供）
# 先创建environment.yml文件，内容如下：
cat > environment.yml << EOF
name: seis
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.12
  - obspy>=1.4.1
  - matplotlib>=3.5.0
  - numpy>=1.21.0
  - scipy>=1.7.0
  - toml>=0.10.2
  - tqdm>=4.62.0
EOF

# 然后创建并激活环境
conda env create -f environment.yml
conda activate seis

# 方式B：一条命令创建环境并安装包
conda create -n seis python=3.12 obspy matplotlib numpy scipy toml tqdm -c conda-forge -y
conda activate seis

# 方式C：分步安装
conda create -n seis python=3.12 -y
conda activate seis
conda install -c conda-forge obspy matplotlib numpy scipy toml tqdm -y
```

#### 方法2：混合安装（兼容性更好）

```bash
# 创建conda环境
conda create -n seis python=3.12 -y
conda activate seis

# 使用conda安装依赖
conda install jinja2 pygments -c conda-forge -y

# 使用pip安装剩余依赖
pip install -r requirements.txt

# 开发模式安装项目
pip install -e .
```

### 2. 系统要求

- **Python**: >= 3.12
- **操作系统**: Linux,  Windows 10,  Windows 11
- **推荐环境**: conda环境管理
- **中文字体**: 自动安装或手动安装中文字体包

```bash
# Ubuntu/Debian 中文字体安装
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei fonts-noto-cjk
```

### 3. 准备数据

确保您有以下数据文件：
- **地震数据文件**：MiniSEED格式（.mseed, .msd, .seed）
- **仪器响应文件**：StationXML格式（.xml）或dataless SEED格式（.dataless）

### 4. 配置文件设置

#### 计算配置文件 (config.toml)
```toml
# PPSD 计算配置文件 - 计算专用
# 使用方法：python run_cp_ppsd.py config.toml
# 此配置文件将始终尝试计算PPSD并保存NPZ文件。

# === 1. 全局操作控制 ===
log_level = "DEBUG"                   # 日志级别："DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

# === 2. 输入数据与输出路径 ===
# mseed_pattern 可以是glob模式 (如 "./data/*.mseed") 或一个目录路径 (如 "./data/")。
# 如果是目录路径，脚本将递归搜索该目录下的所有miniseed文件（执行效率会慢）。
mseed_pattern = "./data/"             # 地震数据文件目录或glob模式
inventory_path = "./input/BJ.dataless" # 仪器响应文件路径
output_dir = "./output/npz"           # NPZ文件输出目录

# === 3. 输出生成控制 (隐式) ===
# NPZ文件将总是被创建。
# output_npz_filename_pattern 定义了生成NPZ数据文件名的规则。
#   时间信息 (来自MiniSEED数据的开始时间):
#     {year}, {month}, {day}, {hour}, {minute}, {second}, {julday}
#     {datetime} (例如 YYYYMMDDHHMM 格式的紧凑时间戳)
#   台站信息: {network}, {station}, {location}, {channel}
#     例如: "PPSD_{datetime}_{network}-{station}-{location}-{channel}.npz"
# 如果未设置或为空，脚本将使用默认命名规则。
output_npz_filename_pattern = "PPSD_{datetime}_{network}-{station}-{location}-{channel}.npz"

# === 4. PPSD核心计算参数 ([args]表内) ===
[args]
# --- 时间分段与窗口 ---
ppsd_length = 3600                   # 时间窗口长度（秒），标准1小时。
overlap = 0.5                        # 窗口重叠比例，50%重叠。

# --- 频率/周期域参数 ---
period_limits = [0.01, 1000.0]       # PPSD计算的周期范围（秒）。
period_smoothing_width_octaves = 1.0 # 周期平滑宽度（倍频程）。
period_step_octaves = 0.125          # 周期步长（1/8倍频程）。

# --- 振幅域参数 (功率分箱) ---
db_bins = [-200.0, -50.0, 0.25]      # dB分箱：[最小值, 最大值, 步长]。

# --- 数据质量与选择 ---
skip_on_gaps = false                 # 是否跳过有数据缺失的窗口。
                                     # McNamara2004 通过补零合并含间断的trace，这会在PPSD图中产生可识别的异常PSD线。
                                     # 设置为true则不补零，可能导致短于ppsd_length的数据段不被使用。
# special_handling = "None"          # 特殊仪器处理。可选值: "ringlaser", "hydrophone", "None"(默认), 或注释掉。
                                     # None(默认): 标准地震仪处理（仪器校正+微分，将速度转换为加速度）
                                     # "ringlaser": 不进行仪器校正，仅除以metadata中的sensitivity，不做微分
                                     # "hydrophone": 仪器校正后不做微分操作（保持原始物理量）

# 以下相关参数用于脚本层面的外部事件剔除逻辑，在数据送入PPSD对象前使用，非PPSD.__init__直接参数。
# time_of_weekday = [1, 2, 3, 4, 5]     # 分析的星期几（1=周一，7=周日），工作日。用于预先筛选Trace对象，非PPSD直接参数。
# processing_time_window = ["2023-01-01T00:00:00", "2023-01-31T23:59:59"] # (可选) 指定处理数据的绝对时间窗口 [开始时间, 结束时间]，ISO 8601格式。用于预筛选Trace，非PPSD直接参数。
# daily_time_window = ["01:00:00", "05:00:00"] # (可选) 指定每天处理数据的时间窗口 [开始时间, 结束时间]，HH:MM:SS格式。用于预筛选Trace，非PPSD直接参数。
# enable_external_stalta_filter = false # 是否启用外部STA/LTA事件剔除预处理流程。
# sta_length = 120                    # (外部STA/LTA) 短时平均长度（秒）。
# lta_length = 600                    # (外部STA/LTA) 长时平均长度（秒）。
# stalta_thresh_on = 2.5              # (外部STA/LTA) 触发阈值上限。
# stalta_thresh_off = 1.5             # (外部STA/LTA) 触发阈值下限。
```

#### 绘图配置文件 (config_plot.toml)
```toml
# PPSD 计算配置文件 - 绘图专用
# 使用方法：python run_cp_ppsd.py config_plot.toml
# 此配置文件用于从指定目录加载一个或多个PPSD数据 (.npz 文件) 并执行绘图操作。
# NPZ文件应已通过计算型配置文件 (如 config.toml) 生成。
# 如果指定目录中没有有效的NPZ文件，或NPZ文件本身有问题，脚本处理时可能会报错或跳过。
# 绘图总是会执行。

# === 1. 全局操作控制 ===
log_level = "DEBUG"                   # 日志级别："DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

# === 2. 输入数据与输出路径 ===
# NPZ文件必须预先存在且有效，否则脚本应报错退出。
# input_npz_dir 指定了包含一个或多个预先计算好的PPSD数据 (.npz) 文件的目录。
# 脚本将尝试处理该目录下的所有 .npz 文件。
# output_dir 用于存放生成的图像，建议为每个NPZ文件生成的图像组织到子目录或使用唯一文件名。
input_npz_dir = "./output/npz/"       # 指定存放NPZ文件的目录路径
inventory_path = "./input/BJ.XML"     # 仪器响应文件路径 (可能需要用于绘图时的元数据，如台站名)

# === 3. 输出生成控制 (隐式) ===
output_dir = "./output/plots/"        # 输出目录 (图像保存于此)
# 图像总是会生成。
# output_filename_pattern 定义了生成图像文件名的规则。
# 可以使用以下占位符:
#   绘图类型(在绘图时确定): {plot_type} （plot_type="standard", plot_type="temporal", plot_type="spectrogram"）
#   时间信息 (通常来自PPSD数据的起始时间或处理时间):
#     {year}, {month}, {day}, {hour}, {minute}, {second}, {julday}
#     {datetime} (例如 YYYYMMDDHHMM 格式的紧凑时间戳)
#   台站信息: {network}, {station}, {location}, {channel}
#     例如: "{plot_type}_{datetime}_{network}-{station}-{location}-{channel}.png"
# 如果此参数未设置或为空，脚本将使用基于NPZ文件名的默认命名规则。
output_filename_pattern = "{plot_type}_{datetime}_{network}-{station}-{location}-{channel}.png"

# === 4. 绘图特定参数 ([args]表内) ===
# 以下参数直接控制从加载的PPSD对象生成图像时的外观和内容。
[args]
# --- 基本绘图控制 ---
plot_type = ["standard", "temporal", "spectrogram"] # 绘图类型：可以是单个字符串如 "standard", "temporal", "spectrogram", 或包含这些值的列表

# --- NPZ文件合并策略 ---
npz_merge_strategy = true             # NPZ文件绘图合并策略。布尔值：
                                      # false: 每个NPZ文件单独生成一张图（默认）
                                      # true: 将同一台网、台站、位置、通道的多个NPZ文件合并到一张图中
                                      # 合并模式适用于同一通道的时间序列数据，可以显示长期噪声演化趋势

# --- "standard" (PPSD.plot) 图特定选项 ---
show_histogram = true                 # (standard) 是否绘制2D直方图本身。
show_percentiles = false              # (standard) 是否显示近似百分位数线。
percentiles = [0, 25, 50, 75, 100]   # (standard) 若 show_percentiles=true, 指定显示的百分位数。
show_mode = false                     # (standard) 是否显示众数PSD曲线。
show_mean = false                     # (standard) 是否显示均值PSD曲线。
show_noise_models = true              # (standard) 是否显示全球噪声模型。
standard_grid = true                  # (standard) 是否在直方图上显示网格。
period_lim = [0.01, 1000.0]           # (standard) PPSD标准图绘图显示的周期范围（秒）。若 xaxis_frequency=true, 此处应为频率 (Hz)。
xaxis_frequency = false               # (standard) PPSD标准图X轴是否显示频率 (Hz) 而不是周期 (秒)。
cumulative_plot = false               # (standard) 是否显示累积直方图 (PPSD.plot中的 cumulative 参数)。
show_coverage = true                  # (standard) 是否显示数据覆盖度。
cumulative_number_of_colors = 20      # (standard) 累积直方图的离散颜色数量。

standard_cmap = "viridis"             # (standard) PPSD图的颜色映射方案。例如 "viridis", "plasma", "inferno"。

# --- "spectrogram" (PPSD.plot_spectrogram) 图特定选项 ---
clim = [-180, -100]                   # (spectrogram) 颜色图的振幅限制 [min_db, max_db]。
time_format_x_spectrogram = "%Y-%m-%d" # (spectrogram) Y轴（时间轴）刻度标签的时间格式。
spectrogram_grid = true               # (spectrogram) 是否在直方图上显示网格。
spectrogram_cmap = "viridis"          # (spectrogram) PPSD图的颜色映射方案。例如 "viridis", "plasma", "obspy_sequential", "pqlx"。

# --- "temporal" (PPSD.plot_temporal) 图特定选项 ---
temporal_plot_periods = [1.0, 8.0, 20.0] # (temporal) 绘制PSD值随时间演化曲线的特定周期（秒）。
time_format_x_temporal = "%H:%M"      # (temporal) X轴（时间轴）刻度标签的时间格式。
temporal_grid = true                  # (temporal) 是否在直方图上显示网格。
temporal_cmap = "viridis"             # (temporal) PPSD图的颜色映射方案。例如 "viridis", "plasma", "obspy_sequential", "pqlx"。
```

### 5. 运行程序

#### 基本PPSD计算和绘图
```bash
# 仅计算PPSD
python run_cp_ppsd.py input/config.toml

# 仅绘图（需要预先计算的NPZ文件）
python run_cp_ppsd.py input/config_plot.toml

# 计算+绘图
python run_cp_ppsd.py input/config.toml input/config_plot.toml
```

#### 专业PSD分析
```bash
# 使用默认NPZ文件生成四合一分析图
python run_plot_psd.py

# 指定NPZ文件
python run_plot_psd.py ./output/npz/PPSD_202503251600_BJ-DAX-00-BHZ.npz

# 指定NPZ文件和输出目录
python run_plot_psd.py ./output/npz/PPSD_data.npz ./custom_output/

# 在conda环境中运行
conda run -n seis python run_plot_psd.py
```

## 输出文件详解

### NPZ文件（PPSD数据）
- **位置**: `./output/npz/`
- **命名**: `PPSD_{datetime}_{network}-{station}-{location}-{channel}.npz`
- **内容**: PPSD概率密度矩阵、频率轴、时间信息、计算参数
- **用途**: 数据存储、后续分析、自定义绘图

### 标准PPSD图像
- **位置**: `./output/plots/`
- **类型**: standard, temporal, spectrogram
- **格式**: PNG, 300 DPI
- **命名**: `{plot_type}_{datetime}_{network}-{station}-{location}-{channel}.png`

### 四合一分析图
- **位置**: 用户指定目录（默认`./output/plots/`）
- **命名**: `psd_analysis_{datetime}_{network}-{station}-{location}-{channel}.png`
- **内容**: 
  - PPSD概率密度分布图（Blues配色）
  - PSD值散点图（Blues配色）
  - 各时间段PSD曲线对比（viridis配色）
  - 预留扩展位置
- **特点**: 16×12英寸，300 DPI，中文字体支持

## 配置文件详解

### 重要参数说明

#### 时间信息来源
- **文件名时间**: 来自MiniSEED数据的开始时间，而非处理时间
- **确保准确性**: 文件名能准确反映数据的实际时间范围

#### special_handling参数
- **"None"**: 标准地震仪处理（默认）
- **"ringlaser"**: 环形激光陀螺仪，仅除以sensitivity
- **"hydrophone"**: 水听器，仪器校正后不做微分

#### skip_on_gaps参数
- **false**: 补零合并含间断的数据（McNamara2004方法）
- **true**: 跳过有数据间断的窗口，确保数据纯净度

#### npz_merge_strategy参数
- **false**: 每个NPZ文件单独生成图像（默认）
- **true**: 相同通道的多个NPZ文件合并到一张图

## 项目结构

```
cp_ppsd/
├── run_cp_ppsd.py           # 主PPSD计算工具
├── run_plot_psd.py          # 专业PSD分析工具
├── cp_ppsd/                 # 核心模块目录
│   ├── __init__.py          # 模块初始化文件
│   ├── cp_psd.py            # PPSD处理核心代码
│   └── plot_psd_values.py   # PSD分析可视化模块
├── tests/                   # 测试程序目录
│   ├── README.md            # 测试程序说明文档
│   ├── test_basic.py        # 基础功能测试
│   ├── test_config_params.py # 配置参数测试
│   ├── test_special_handling*.py # 特殊仪器处理测试
│   ├── test_summary_report.py # 汇总报告测试
│   ├── analyze_npz_content.py # NPZ文件内容分析工具
│   ├── ppsd_binning_demo.py # PPSD分箱演示程序
│   ├── config_optimization_report.py # 配置优化报告生成器
│   └── check_data_info.py   # 数据信息检查工具
├── input/                   # 输入文件目录
│   ├── config.toml          # 计算配置文件
│   ├── config_plot.toml     # 绘图配置文件
│   └── BJ.dataless         # 仪器响应文件
├── data/                    # 地震数据目录
│   └── *.mseed             # MiniSEED数据文件
├── output/                  # 输出文件目录
│   ├── npz/                # NPZ文件存放目录
│   └── plots/              # 图片文件存放目录
├── logs/                    # 日志文件目录
├── setup.py                # 包安装脚本
├── requirements.txt        # Python依赖包
├── README.md              # 项目说明文档
├── README_plot_psd.md     # PSD分析工具说明
└──  ...
```

## 应用场景

### 1. 台站噪声评估
- 评估地震台站的背景噪声水平
- 与Peterson噪声模型（NLNM/NHNM）对比
- 台站选址和性能评价

### 2. 噪声源识别
- 识别自然噪声源（海洋微震、风噪声）
- 检测人为噪声源（交通、工业、电力干扰）
- 环境影响评估

### 3. 仪器性能诊断
- 检测地震仪器的性能问题
- 识别机械共振和电子噪声
- 设备维护和故障诊断

### 4. 长期监测分析
- 监测台站噪声的长期变化趋势
- 季节性变化和环境影响分析
- 台站管理和预防性维护

## 故障排除

### 常见问题

1. **找不到数据文件**
   - 检查 `mseed_pattern` 路径是否正确
   - 确认文件扩展名是否支持（.mseed, .msd, .seed）

2. **仪器响应错误**
   - 验证 `inventory_path` 文件是否存在
   - 确认响应文件与数据的SEED ID匹配
   - 支持StationXML (.xml) 和 dataless SEED (.dataless) 格式

3. **中文字体显示问题**
   ```bash
   # 安装中文字体
   sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei fonts-noto-cjk
   
   # 清除matplotlib字体缓存
   rm -rf ~/.cache/matplotlib
   ```

4. **内存不足**
   - 减少 `ppsd_length` 参数
   - 调整 `db_bins` 范围和步长
   - 分批处理数据

5. **NPZ文件加载失败**
   - 检查文件路径是否正确
   - 验证NPZ文件是否由正确的PPSD程序生成
   - 确认文件权限是否可读

### 性能优化

#### 内存优化
```toml
[args]
ppsd_length = 1800          # 减少窗口长度
period_step_octaves = 0.25  # 增加周期步长
db_bins = [-180, -80, 0.5]  # 减少dB分箱范围
```

#### 计算速度优化
```toml
[args]
skip_on_gaps = true         # 跳过有数据间断的窗口
overlap = 0.25              # 减少窗口重叠比例
period_limits = [0.1, 100]  # 限制周期范围
```

### 日志分析

设置 `log_level = "DEBUG"` 可以获得详细的处理信息：
- 文件加载过程
- PPSD计算进度
- 错误详细信息
- 性能统计数据

## 最佳实践

### 1. 数据准备
- 确保数据时间戳准确同步
- 验证仪器响应文件的有效性
- 检查数据质量和完整性

### 2. 参数选择
- 根据分析目标选择合适的时间窗口长度
- 平衡频率分辨率和统计稳定性
- 考虑数据质量调整skip_on_gaps参数

### 3. 结果验证
- 与全球噪声模型对比验证
- 与邻近台站结果交叉验证
- 检查时间稳定性和一致性

## 技术支持

### 问题诊断
1. 查看日志文件中的错误信息
2. 检查配置文件格式是否正确
3. 验证数据文件和响应文件的匹配性
4. 参考知识库中的故障排除指南

## 更新日志

### 2025年6月7日 - 配色方案重大更新

#### 新增7个专业配色方案
1. **`science_custom`** - 专业科学配色，白色背景，期刊级可视化标准
2. **`strong_contrast_custom`** - 和谐强对比配色，强对比度与自然过渡并存
3. **`forest_seasons_custom`** - 森林四季配色，春晨薄雾到冬日深红的季节变化
4. **`desert_day_custom`** - 沙漠日月配色，黎明薄雾到夜幕深红的昼夜变化
5. **`ocean_depth_custom`** - 海洋深度配色，海面到深海的自然层次
6. **`aurora_premium_custom`** - 北极光高级配色，天蓝到深红的绚丽过渡
7. **`autumn_custom`** - 秋天配色，秋季色彩的丰富层次

#### 🔧 配色方案优化
- **PQLX配色更新**: 将纯蓝色改为钢蓝色，提升视觉柔和感和对比度
- **标准化比例**: 所有8色方案采用统一比例分布 (0.00, 0.05, 0.15, 0.35, 0.50, 0.65, 0.80, 1.00)
- **默认配色调整**: 标准图现在默认使用 `pqlx_custom` 配色

#### 文档和配置更新
- **配置文件**: 更新 `config_plot.toml` 中的 `available_cmaps` 列表
- **知识库**: 完善 `配色方案配置说明.md` 文档
- **使用指南**: 新增配色方案选择指南和最佳实践建议

#### 代码质量改进
- **移除废弃方案**: 删除 `fatpanda_v2_custom` 和 `blue_yellow_premium_custom`
- **代码优化**: 添加 `.flake8` 配置，提升代码质量标准
- **目录结构**: 新增 `cmap/` 目录存放配色预览图片

#### 科学可视化原则
所有配色方案严格遵循科学可视化标准：
- **低值显示**: 浅色、冷色调用于显示低功率密度值
- **高值显示**: 深色、暖色调用于显示高功率密度值
- **白色起点**: 大多数方案以白色开始，表示最低功率密度
- **平滑过渡**: 颜色变化自然，避免突兀跳跃
- **期刊兼容**: 支持黑白打印和色盲友好显示

#### 应用建议
- **期刊发表**: 推荐使用 `science_custom` 或 `pqlx_custom`
- **学术展示**: 推荐使用 `aurora_premium_custom` 或艺术主题配色
- **专业领域**: 根据研究领域选择主题相关配色（海洋学、生态学、极地研究等）
- **日常分析**: 使用通用配色方案如 `viridis_custom` 或 `ocean_custom`

总计新增代码**321行**，修改**86个文件**，显著提升了PPSD可视化的专业性和美观性。

## 地震数据处理小组简介

本小组专注于测震学领域的前沿研究与软件开发。团队由组长**林向东**负责，核心成员包括**牟磊育**、**杨选**和**吴朋**。

**我们的主要目标包括：**

- 算法研发：在《地震数据处理技术》一书的理论基础上，我们致力于研发更为先进的测震学算法。这些算法既是书中经典方法的扩展与补充，也包含了我们团队的创新探索，旨在全面提升数据处理的精度与效率。
- 开源贡献：提供稳定、高效的开源地震数据处理程序，服务于科研社区。
- 数据研究：开展实际地震数据处理工作，并将研究成果发表为学术论文。

我们致力于将理论研究与实践应用相结合，推动地震科学的发展。

## 版本信息

- **当前版本**: 1.1.0
- **Python要求**: >= 3.12
- **主要依赖**: ObsPy >= 1.4.1, matplotlib >= 3.5.0
- **最后更新**: 2025年6月7日

## 许可证

本项目遵循开源许可证，具体信息请查看LICENSE文件。
