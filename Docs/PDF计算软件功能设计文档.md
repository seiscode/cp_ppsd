%%  %%# PDF计算软件功能设计文档

## 1. 概述

本文档详细说明了`cp_psd.py`脚本中PPSD（Probabilistic Power Spectral Density）函数的使用方法。该脚本专门用于地震学中的背景噪声分析，基于ObsPy库实现，支持通过TOML配置文件进行批量地动噪声PPSD计算和可视化。

**主要应用场景**：
- 地震台站背景噪声水平评估
- 台站选址质量分析
- 地震仪器性能评价
- 环境噪声源识别与分析
- 台站网络噪声水平对比

## 2. 程序工作流程

`cp_psd.py` 脚本遵循以下基本工作流程来处理地震数据并生成PPSD结果：

1.  **加载配置与识别操作意图**:
    *   脚本启动时，会读取用户在命令行中指定的一个或多个TOML配置文件。
    *   **操作意图的确定**: 脚本的主要操作模式根据传递的配置文件名或类型进行推断：
        *   如果提供了类似 `config.toml` 或以 `_calc.toml` 结尾的**计算型配置文件**，脚本的主要任务是PPSD计算。这将始终尝试生成并保存 `.npz` 数据文件。
        *   如果提供了类似 `config_plot.toml` 或以 `_plot.toml` 结尾的**绘图型配置文件**，脚本的主要任务是PPSD绘图。这将始终尝试加载PPSD数据（通常是预计算的NPZ文件）并生成图像。
        *   如果同时提供了计算型和绘图型配置文件 (例如 `python cp_psd.py config.toml config_plot.toml`)，脚本将首先响应计算型配置（执行计算、保存NPZ），然后使用这些结果并响应绘图型配置（加载数据、绘图）。
    *   解析所提供配置文件中的所有参数，包括日志级别、文件路径以及PPSD计算和绘图的特定参数。

2.  **设置日志系统**:
    *   根据活动配置文件中的 `log_level` 和 `output_dir` 参数（通常取第一个配置文件或特定规则定义的配置文件的设置），初始化日志系统。
    *   日志信息会同时输出到控制台和指定输出目录下的日志文件。

3.  **PPSD数据处理 (计算阶段 - 由计算型配置文件驱动)**:
    *   **数据准备**: 根据计算型配置文件中的 `mseed_pattern` 和 `inventory_path` 定位输入文件。
    *   **核心计算**: 
        *   当响应计算型配置文件时，脚本执行PPSD核心计算。这包括读取地震波形数据、应用仪器校正、进行谱估计等。计算会使用计算型配置文件 `[args]` 部分的参数。
        *   计算完成后，PPSD结果将**始终**保存为 `.npz` 文件。文件名由计算型配置文件中的 `output_npz_filename_pattern` (如果提供) 或默认规则确定。

4.  **PPSD结果可视化 (绘图阶段 - 由绘图型配置文件驱动)**:
    *   当响应绘图型配置文件时：
        *   脚本会尝试加载PPSD数据。如果之前在同一脚本运行中已通过计算型配置文件生成了数据，则优先使用该内存中的数据；否则，它会尝试从绘图型配置文件中指定的路径（如 `input_npz_dir` 或基于 `output_dir` 的约定）加载预计算的 `.npz` 文件。
        *   根据绘图型配置文件中的 `plot_type` 和其他 `[args]` 下的绘图参数生成图像，图像将**始终**被保存。文件名由绘图型配置文件中的 `output_filename_pattern` (如果提供) 或默认规则确定。

5.  **完成与退出**:
    *   所有请求的操作完成后，记录相应的日志信息，脚本正常退出。
    *   如果过程中发生错误，会记录详细错误信息到日志，并尝试优雅退出。

这个流程允许用户通过选择和组合不同的配置文件来灵活控制计算和绘图任务。

## 3. 配置文件格式

`cp_psd.py` 脚本使用TOML格式的配置文件。为了更清晰地分离计算和绘图任务的参数，推荐使用两个独立的配置文件：
-   `config.toml`: 专注于PPSD核心计算和数据导出（如CSV）的参数。
-   `config_plot.toml`: 专注于PPSD结果可视化（绘图）的参数。

两个文件共享一些通用参数（如全局控制、输入/输出路径），但其核心任务 (`command`) 和特定功能参数会有所不同。

### 3.1 完整配置参数结构

以下是推荐的 `config.toml` 和 `config_plot.toml` 文件结构。

#### 3.1.1 计算配置文件示例 (`config.toml`)

```toml
# PPSD 计算配置文件 - 计算专用
# 使用方法：python cp_psd.py config.toml
# 此配置文件将始终尝试计算PPSD并保存NPZ文件。
# 如果定义了CSV导出相关参数（如[args]下的percentiles），则也会导出CSV。

# === 1. 全局操作控制 ===
# command 参数已移除。
log_level = "DEBUG" # 日志级别："DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

# === 2. 输入数据与输出路径 ===
# mseed_pattern 可以是glob模式 (如 "./data/*.mseed") 或一个目录路径 (如 "./data_directory/")。
# 如果是目录路径，脚本将递归搜索该目录下的所有miniseed文件（执行效率会慢）。
mseed_pattern = "./data_directory/"      # 地震数据文件目录或glob模式
inventory_path = "./data/inventory.xml"  # 仪器响应文件路径
output_dir = "./ppsd_results"            # 输出目录

# === 3. 输出生成控制 (隐式) ===
# NPZ文件将总是被创建。
# output_npz_filename_pattern 定义了生成NPZ数据文件名的规则。
#   时间信息 (通常来自miniseed数据的起始时间或处理时间):
#     {year}, {month}, {day}, {hour}, {minute}, {second}, {julday}
#     {datetime} (例如 YYYYMMDDHHMM 格式的紧凑时间戳)
#   台站信息: {network}, {station}, {location}, {channel}
#     例如: "PPSD_{datetime}_{network}-{station}-{location}-{channel}.npz"
# 如果未设置或为空，脚本将使用默认命名规则。
output_npz_filename_pattern = "PPSD_{datetime}_{network}-{station}-{location}-{channel}.npz"

# === 4. PPSD核心计算参数 ([args]表内) ===
[args]
# --- 时间分段与窗口 ---
ppsd_length = 3600                    # 时间窗口长度（秒），标准1小时。
overlap = 0.5                         # 窗口重叠比例，50%重叠。

# --- 频率/周期域参数 ---
period_limits = [0.01, 1000.0]        # PPSD计算的周期范围（秒）。
period_smoothing_width_octaves = 1.0  # 周期平滑宽度（倍频程）。
period_step_octaves = 0.125           # 周期步长（1/8倍频程）。

# --- 振幅域参数 (功率分箱) ---
db_bins = [-200.0, -50.0, 0.25]       # dB分箱：[最小值, 最大值, 步长]。

# --- 数据质量与选择 ---
skip_on_gaps = false                  # 是否跳过有数据缺失的窗口。
                                      # McNamara2004 通过补零合并含间断的trace，这会在PPSD图中产生可识别的异常PSD线。
                                      # 设置为true则不补零，可能导致短于ppsd_length的数据段不被使用。
special_handling = "None"             # 特殊仪器处理。可选值: "ringlaser", "hydrophone", "None"。
                                      # "ringlaser": 不进行仪器校正，仅除以metadata中的sensitivity。
                                      # "hydrophone": 仪器校正后不做微分操作。
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

#### 3.1.2 `config.toml` 参数详解

本节详细解释 `config.toml` (计算配置文件) 中可用的各项参数。

##### A. 全局操作控制 (顶层参数)

-   **`log_level`** (字符串)
    *   **作用**: 控制日志信息的详细程度。日志会同时输出到控制台和 `output_dir` 中生成的日志文件 (文件名通常包含时间戳，如 `ppsd_processing_YYYYMMDD_HHMMSS.log`)。
    *   **可选值**:
        *   `"DEBUG"`: 输出最详细的日志信息，用于开发和调试。
        *   `"INFO"`: 输出一般性的过程信息，如脚本启动、文件加载、主要步骤完成等。推荐用于常规运行。
        *   `"WARNING"`: 输出警告信息，表示可能存在的问题但不影响当前操作完成。
        *   `"ERROR"`: 输出错误信息，表示某些操作失败但脚本可能仍能继续处理其他部分。
        *   `"CRITICAL"`: 输出严重错误信息，通常表示脚本无法继续执行。
    *   **示例**: `log_level = "DEBUG"`
    *   **默认行为**: 如果未指定，脚本可能会使用如 "INFO" 这样的默认级别。

##### B. 输入数据与输出路径 (顶层参数)

-   **`mseed_pattern`** (字符串)
    *   **作用**: 指定输入地震波形数据文件的路径。
        *   如果提供的是 **glob模式** (例如 `"./data/*.mseed"`)：脚本将按照该模式匹配文件。
        *   如果提供的是 **目录路径** (例如 `"./data_directory/"`)：脚本将递归地搜索该目录及其所有子目录，查找具有常见MiniSEED扩展名（如 `.mseed`, `.msd`, `.seed`，具体列表由脚本内部定义）的数据文件。所有找到的符合条件的文件都将被处理。
        *   **注意**: 递归搜索目录可能会比使用精确的glob模式慢，尤其是在目录层级深或文件数量庞大时。
    *   **示例**: `mseed_pattern = "./data_directory/"`

-   **`inventory_path`** (字符串)
    *   **作用**: 指定仪器响应文件（元数据）的路径。该文件包含了台站坐标、仪器灵敏度、响应函数等关键信息，对于将原始记录数据转换为实际的地面运动单位至关重要。此参数在PPSD计算时用于进行仪器校正。
    *   **支持格式**: ObsPy支持的多种格式，如 FDSN StationXML (`.xml`) 或 dataless SEED。
    *   **示例**: `inventory_path = "./data/inventory.xml"`

-   **`output_dir`** (字符串)
    *   **作用**: 指定所有输出文件（主要是计算生成的 `.npz` PPSD数据文件和 `.log` 日志文件）的根目录。如果目录不存在，脚本会尝试创建它。
    *   **示例**: `output_dir = "./ppsd_results"`

##### C. 输出生成控制 (顶层参数, 隐式)

-   **`output_npz_filename_pattern`** (字符串, 可选)
    *   **作用**: 定义生成 NPZ 数据文件的动态命名规则。当脚本执行PPSD计算并保存NPZ文件时（计算型配置总是会保存NPZ），会使用此模式。
    *   **可用占位符**:
        *   时间信息 (通常来自MiniSEED数据的起始时间或处理时间): `{year}`, `{month}`, `{day}`, `{hour}`, `{minute}`, `{second}`, `{julday}`, `{datetime}` (例如 YYYYMMDDHHMM 格式的紧凑时间戳)
        *   台站信息: `{network}`, `{station}`, `{location}`, `{channel}`
    *   **示例**: `output_npz_filename_pattern = "PPSD_{datetime}_{network}-{station}-{location}-{channel}.npz"`
    *   **默认行为**: 如果此参数未设置或为空，脚本将使用内部定义的默认命名规则。

##### D. PPSD核心计算参数 (`[args]` 表内)

这些参数直接传递给ObsPy的`PPSD`对象初始化或影响其计算过程。

-   **`ppsd_length`** (整数)
    *   **作用**: 单个PSD估计所使用的时间窗口长度（秒）。标准的PPSD分析通常使用3600秒（1小时）。
    *   **ObsPy对应**: `PPSD.__init__(ppsd_length=...)`
    *   **示例**: `ppsd_length = 3600`

-   **`overlap`** (浮点数, 0.0 到 1.0 之间)
    *   **作用**: 相邻时间窗口之间的重叠比例。例如，0.5表示50%的重叠。
    *   **ObsPy对应**: `PPSD.__init__(overlap=...)`
    *   **示例**: `overlap = 0.5`

-   **`period_limits`** (列表/元组, 包含两个数值 `[min_period, max_period]`)
    *   **作用**: PPSD计算的周期范围（秒）。定义了PPSD对象将分析的周期界限。
    *   **ObsPy对应**: `PPSD.__init__(period_limits=...)`
    *   **示例**: `period_limits = [0.01, 1000.0]`

-   **`period_smoothing_width_octaves`** (浮点数)
    *   **作用**: 在倍频程单位下，用于平滑PSD估计的周期（或频率）平滑窗口的宽度。
    *   **ObsPy对应**: `PPSD.__init__(period_smoothing_width_octaves=...)`
    *   **示例**: `period_smoothing_width_octaves = 1.0`

-   **`period_step_octaves`** (浮点数)
    *   **作用**: PPSD对象内部表示周期的步长，以倍频程为单位。例如，0.125表示1/8倍频程。
    *   **ObsPy对应**: `PPSD.__init__(period_step_octaves=...)`
    *   **示例**: `period_step_octaves = 0.125`

-   **`db_bins`** (列表/元组, 格式 `[min_db, max_db, step_db]`)
    *   **作用**: 定义用于对功率谱密度值进行分箱的dB范围和步长。格式为 `[最小值, 最大值, 步长]`。
    *   **ObsPy对应**: `PPSD.__init__(db_bins=...)`
    *   **示例**: `db_bins = [-200.0, -50.0, 0.25]`

-   **`skip_on_gaps`** (布尔值: `true` / `false`)
    *   **作用**: 控制在处理包含数据间断 (gaps) 的时间窗口时的行为。
        *   `false` (默认): McNamara & Buland (2004) 的方法建议通过补零来合并包含间断的trace段。这可能在PPSD图中产生可识别的异常PSD线，但会利用所有数据。
        *   `true`: 如果设置为true，则不进行补零，任何短于 `ppsd_length` 的数据段（由于间断造成）将不被用于PPSD计算。这可以产生更"纯净"的PPSD，但可能会丢弃部分数据。
    *   **ObsPy对应**: `PPSD.__init__(skip_on_gaps=...)`
    *   **示例**: `skip_on_gaps = false`

-   **`special_handling`** (字符串)
    *   **作用**: 为特殊类型的仪器数据指定处理方式。
    *   **可选值**:
        *   `"None"`: 标准处理，应用完整的仪器校正。
        *   `"ringlaser"`: 适用于环形激光陀螺仪等主要输出旋转速率的仪器。不进行完整的仪器校正，仅将数据除以元数据中定义的灵敏度(sensitivity)。
        *   `"hydrophone"`: 适用于水听器。数据在经过仪器校正后，不进行通常地震仪数据会执行的微分操作（如果响应是位移，则不转换为速度）。
    *   **ObsPy对应**: `PPSD.__init__(special_handling=...)`
    *   **示例**: `special_handling = "None"`

##### E. 外部数据预筛选参数 (`[args]` 表内, 非PPSD直接参数)
以下参数用于在数据送入PPSD对象进行核心计算之前，在脚本层面进行外部的事件剔除或时间窗口筛选。这些不是`PPSD.__init__`的直接参数，而是由`cp_psd.py`脚本自身实现的逻辑使用。

-   **`time_of_weekday`** (整数列表, 可选)
    *   **作用**: (用于预筛选Trace) 指定一周中的哪几天的数据需要被分析。星期一为1，星期日为7。如果提供，则仅处理指定星期几的数据。
    *   **示例**: `time_of_weekday = [1, 2, 3, 4, 5]` (仅处理周一到周五的数据)
    *   **默认行为**: 如果未注释掉且未提供或为空列表，则默认处理一周七天所有数据。

-   **`processing_time_window`** (字符串列表, `[startTime, endTime]`, 可选)
    *   **作用**: (用于预筛选Trace) 指定一个绝对的时间窗口来处理数据。只有落在这个时间窗口内的数据段才会被考虑。时间格式为ISO 8601 (例如, `"YYYY-MM-DDTHH:MM:SS"`)。
    *   **示例**: `processing_time_window = ["2023-01-01T00:00:00", "2023-01-31T23:59:59"]`
    *   **默认行为**: 如果未注释掉且未提供或为空列表，则处理所有时间范围内的数据。

-   **`daily_time_window`** (字符串列表, `[startTime, endTime]`, 可选)
    *   **作用**: (用于预筛选Trace) 指定一个每天的时间窗口来处理数据。只有在每天这个时间段内的数据才会被考虑。时间格式为 "HH:MM:SS"。
    *   **示例**: `daily_time_window = ["01:00:00", "05:00:00"]` (仅处理每天凌晨1点到5点之间的数据)
    *   **默认行为**: 如果未注释掉且未提供或为空列表，则处理一天24小时所有数据。

-   **`enable_external_stalta_filter`** (布尔值, 可选)
    *   **作用**: (用于预筛选Trace) 控制是否启用外部的STA/LTA (Short-Term Average / Long-Term Average) 事件剔除预处理流程。如果为 `true`，则在数据送入PPSD计算前，会使用STA/LTA算法识别并尝试移除包含地震事件或其他瞬态信号的时间段。
    *   **示例**: `enable_external_stalta_filter = false`
    *   **依赖参数**: 若为 `true`，则下面的 `sta_length`, `lta_length`, `stalta_thresh_on`, `stalta_thresh_off` 参数将生效。

-   **`sta_length`** (整数, 可选)
    *   **作用**: (外部STA/LTA) 短时平均 (STA) 的窗口长度（秒）。仅当 `enable_external_stalta_filter = true` 时有效。
    *   **示例**: `sta_length = 120`

-   **`lta_length`** (整数, 可选)
    *   **作用**: (外部STA/LTA) 长时平均 (LTA) 的窗口长度（秒）。仅当 `enable_external_stalta_filter = true` 时有效。
    *   **示例**: `lta_length = 600`

-   **`stalta_thresh_on`** (浮点数, 可选)
    *   **作用**: (外部STA/LTA) STA/LTA比率的触发阈值上限。当STA/LTA值超过此阈值时，认为事件开始。仅当 `enable_external_stalta_filter = true` 时有效。
    *   **示例**: `stalta_thresh_on = 2.5`

-   **`stalta_thresh_off`** (浮点数, 可选)
    *   **作用**: (外部STA/LTA) STA/LTA比率的触发阈值下限。当STA/LTA值低于此阈值时，认为事件结束。仅当 `enable_external_stalta_filter = true` 时有效。
    *   **示例**: `stalta_thresh_off = 1.5`

#### 3.2.1 绘图配置文件示例 (`config_plot.toml`)

```toml
# PPSD 计算配置文件 - 绘图专用
# 使用方法：python cp_psd.py config_plot.toml
# 此配置文件用于从指定目录加载一个或多个PPSD数据 (.npz 文件) 并执行绘图操作。
# NPZ文件应已通过计算型配置文件 (如 config.toml) 生成。
# 如果指定目录中没有有效的NPZ文件，或NPZ文件本身有问题，脚本处理时可能会报错或跳过。
# 绘图总是会执行。

# === 1. 全局操作控制 ===
log_level = "DEBUG" # 日志级别："DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

# === 2. 输入数据与输出路径 ===
# NPZ文件必须预先存在且有效，否则脚本应报错退出。
# input_npz_dir 指定了包含一个或多个预先计算好的PPSD数据 (.npz) 文件的目录。
# 脚本将尝试处理该目录下的所有 .npz 文件。
# output_dir 用于存放生成的图像，建议为每个NPZ文件生成的图像组织到子目录或使用唯一文件名。
input_npz_dir = "./ppsd_results/npz_data/" # 指定存放NPZ文件的目录路径
inventory_path = "./data/inventory.xml"    # 仪器响应文件路径 (可能需要用于绘图时的元数据，如台站名)

# === 3. 输出生成控制 (隐式) ===
output_dir = "./ppsd_results/plots/"      # 输出目录 (图像保存于此)
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
plot_type = ["standard", "temporal"] # 绘图类型：可以是单个字符串如 "standard", "temporal", "spectrogram", 或包含这些值的列表。

# --- "standard" (PPSD.plot) 图特定选项 ---
show_histogram = true               # (standard) 是否绘制2D直方图本身。
show_percentiles = false            # (standard) 是否显示近似百分位数线。
percentiles = [0, 25, 50, 75, 100]  # (standard) 若 show_percentiles=true, 指定显示的百分位数。
show_mode = false                   # (standard) 是否显示众数PSD曲线。
show_mean = false                   # (standard) 是否显示均值PSD曲线。
show_noise_models = true            # (standard) 是否显示全球噪声模型。
standard_grid = true                # (standard) 是否在直方图上显示网格。
period_lim = [0.01, 1000.0]         # (standard) PPSD标准图绘图显示的周期范围（秒）。若 xaxis_frequency=true, 此处应为频率 (Hz)。
xaxis_frequency = false             # (standard) PPSD标准图X轴是否显示频率 (Hz) 而不是周期 (秒)。
cumulative_plot = false             # (standard) 是否显示累积直方图 (PPSD.plot中的 cumulative 参数)。
show_coverage = true                # (standard) 是否显示数据覆盖度。
cumulative_number_of_colors = 20    # (standard) 累积直方图的离散颜色数量。
max_num_face_colors = 30            # (standard) PPSD标准图中概率面元的最大颜色数量(此为脚本自定义参数，非直接ObsPy参数)
standard_cmap = "pqlx"              # (standard) PPSD图的颜色映射方案。例如 "viridis", "plasma", "obspy_sequential", "pqlx"。

# --- "spectrogram" (PPSD.plot_spectrogram) 图特定选项 ---
clim = [-180, -100]                      # (spectrogram) 颜色图的振幅限制 [min_db, max_db]。
time_format_x_spectrogram = "%Y-%m-%d"   # (spectrogram) Y轴（时间轴）刻度标签的时间格式。
spectrogram_gri = true                   # (spectrogram) 是否在直方图上显示网格。
spectrogram_cmap = "viridis"             # (spectrogram) PPSD图的颜色映射方案。例如 "viridis", "plasma", "obspy_sequential", "pqlx"。

# --- "temporal" (PPSD.plot_temporal) 图特定选项 ---
temporal_plot_periods = [1.0, 8.0, 20.0] # (temporal) 绘制PSD值随时间演化曲线的特定周期（秒）。
time_format_x_temporal = "%H:%M"         # (temporal) X轴（时间轴）刻度标签的时间格式。
temporal_gri = true                      # (temporal) 是否在直方图上显示网格。
temporal_cmap = "viridis"                # (temporal) PPSD图的颜色映射方案。例如 "viridis", "plasma", "obspy_sequential", "pqlx"。
```


#### 3.2.2 `config_plot.toml` 参数详解

本节详细解释 `config_plot.toml` (绘图配置文件) 中主要定义或具有特定行为的参数。对于在 `config_plot.toml` 和 `config.toml` 中都存在的通用顶层参数（如 `log_level`，以及 `inventory_path` 和 `output_dir` 的通用部分），其详细解释请参考章节 **3.1.1.1 `config.toml` 参数详解**。

#### A. 输入数据与输出路径 (顶层参数)

-   **`input_npz_dir`** (字符串)
    *   **作用**: 指定包含一个或多个预先计算好的PPSD数据 (`.npz` 文件) 的目录路径。脚本将尝试加载并处理该目录下的所有 `.npz` 文件进行绘图。
    *   **注意**: NPZ文件必须是有效的PPSD数据，否则脚本在尝试加载时可能会报错或跳过。
    *   **示例**: `input_npz_dir = "./ppsd_results/npz_data/"`

-   **`inventory_path`** (字符串)
    *   **作用**: 对于绘图配置，此参数可能仍需要。即使PPSD数据是从NPZ文件加载的，某些绘图功能（例如，在图表上正确显示台站、通道等元数据信息）可能仍需要访问原始的仪器响应文件以获取这些详细信息。
    *   **详细解释参考**: 章节 **3.1.1.1 `config.toml` 参数详解** 中关于 `inventory_path` 的说明。
    *   **示例**: `inventory_path = "./data/inventory.xml"`

-   **`output_dir`** (字符串)
    *   **作用**: 对于绘图配置，此目录主要用于存放生成的图像文件。此外，如果脚本为该绘图操作生成单独的日志，日志文件也会存放在此。
    *   **详细解释参考**: 章节 **3.1.1.1 `config.toml` 参数详解** 中关于 `output_dir` 的说明。
    *   **示例**: `output_dir = "./ppsd_results/plots/"`

#### B. 输出生成控制 (顶层参数, 隐式)

-   **`output_filename_pattern`** (字符串, 可选)
    *   **作用**: 定义生成图像文件名的动态命名规则。当脚本执行绘图操作时（绘图型配置总是会尝试绘图），会使用此模式。
    *   **可用占位符**:
        *   绘图类型 (在绘图时确定): `{plot_type}` (例如 "standard", "temporal", "spectrogram") - **此占位符对于区分不同类型的图像输出至关重要，特别是当 `plot_type` 为列表时。**
        *   时间信息 (通常来自PPSD数据的起始时间或处理时间): `{year}`, `{month}`, `{day}`, `{hour}`, `{minute}`, `{second}`, `{julday}`, `{datetime}`
        *   台站信息: `{network}`, `{station}`, `{location}`, `{channel}`
    *   **示例**: `output_filename_pattern = "{plot_type}_{datetime}_{network}-{station}-{location}-{channel}.png"`
    *   **默认行为**: 如果此参数未设置、为空，或者所有占位符都无法从当前PPSD对象的元数据中解析，脚本将回退到其他命名逻辑（例如，基于输入NPZ文件名自动生成）。

#### C. 绘图特定参数 (`[args]` 表内)
这些参数直接控制从加载的PPSD对象生成图像时的外观和内容，大部分对应ObsPy中PPSD对象的各种`plot_`方法的参数。

-   **`plot_type`** (字符串 或 字符串列表)
    *   **作用**: 指定要生成的PPSD图像类型。
    *   **可选值 (单一字符串)**:
        *   `"standard"`: 生成标准的PPSD概率密度图 (由 `PPSD.plot()` 生成)。
        *   `"temporal"`: 生成特定周期PSD值随时间变化的曲线图 (由 `PPSD.plot_temporal()` 生成)。
        *   `"spectrogram"`: 生成PPSD的整体时频谱图 (由 `PPSD.plot_spectrogram()` 生成)。
    *   **可选值 (字符串列表)**:
        *   例如 `["standard", "temporal"]`。脚本会为列表中的每种类型生成一个图像。
    *   **重要**: 当 `plot_type` 是一个列表时，强烈建议在 `output_filename_pattern` 中使用 `{plot_type}` 占位符以确保输出文件名唯一。
    *   **示例**: `plot_type = ["standard", "temporal"]`

**--- "standard" (PPSD.plot) 图特定选项 ---**

-   **`show_histogram`** (布尔值: `true` / `false`)
    *   **作用**: 是否绘制核心的2D概率密度直方图。
    *   **ObsPy对应**: `PPSD.plot(show_histogram=...)`
    *   **示例**: `show_histogram = true`

-   **`show_percentiles`** (布尔值: `true` / `false`)
    *   **作用**: 是否在图上绘制近似的百分位数线。
    *   **ObsPy对应**: `PPSD.plot(show_percentiles=...)`
    *   **示例**: `show_percentiles = false` (若为true, 则下面的`percentiles`参数生效)

-   **`percentiles`** (数值列表, 0到100之间)
    *   **作用**: 当 `show_percentiles = true` 时，指定哪些百分位数线将被计算并绘制。
    *   **ObsPy对应**: `PPSD.plot(percentiles=...)`
    *   **示例**: `percentiles = [0, 25, 50, 75, 100]`

-   **`show_mode`** (布尔值: `true` / `false`)
    *   **作用**: 是否绘制众数PSD（每个周期档位上概率最高的PSD值）曲线。
    *   **ObsPy对应**: `PPSD.plot(show_mode=...)`
    *   **示例**: `show_mode = false`

-   **`show_mean`** (布尔值: `true` / `false`)
    *   **作用**: 是否绘制均值PSD曲线。
    *   **ObsPy对应**: `PPSD.plot(show_mean=...)`
    *   **示例**: `show_mean = false`

-   **`show_noise_models`** (布尔值: `true` / `false`)
    *   **作用**: 是否在图上叠加显示全球背景噪声模型 (如NLNM/NHNM)。
    *   **ObsPy对应**: `PPSD.plot(show_noise_models=...)`
    *   **示例**: `show_noise_models = true`

-   **`standard_grid`** (布尔值: `true` / `false`)
    *   **作用**: 是否在PPSD标准图的直方图上显示网格线。
    *   **ObsPy对应**: `PPSD.plot(grid=...)`
    *   **示例**: `standard_grid = true`

-   **`period_lim`** (列表/元组, 包含两个数值 `[min_val, max_val]`)
    *   **作用**: 控制PPSD标准图在X轴上实际显示的范围。如果 `xaxis_frequency` 为 `false` (默认)，则单位为秒 (周期)；如果为 `true`，则单位为赫兹 (频率)。
    *   **ObsPy对应**: `PPSD.plot(period_lim=...)`
    *   **示例**: `period_lim = [0.01, 1000.0]`

-   **`xaxis_frequency`** (布尔值: `true` / `false`)
    *   **作用**: 若为 `true`，PPSD标准图的X轴将显示频率 (Hz) 而不是周期 (秒)。
    *   **ObsPy对应**: `PPSD.plot(xaxis_frequency=...)`
    *   **示例**: `xaxis_frequency = false`

-   **`cumulative_plot`** (布尔值: `true` / `false`)
    *   **作用**: 是否显示PPSD的累积直方图表示。
    *   **ObsPy对应**: `PPSD.plot(cumulative=...)`
    *   **示例**: `cumulative_plot = false`

-   **`show_coverage`** (布尔值: `true` / `false`)
    *   **作用**: 是否在图的顶部（或图例区域）显示数据覆盖率信息。
    *   **ObsPy对应**: `PPSD.plot(show_coverage=...)`
    *   **示例**: `show_coverage = true`

-   **`cumulative_number_of_colors`** (整数, 可选)
    *   **作用**: 当 `cumulative_plot = true` 时，指定用于累积直方图的离散颜色等级的数量。
    *   **ObsPy对应**: `PPSD.plot(cumulative_number_of_colors=...)`
    *   **示例**: `cumulative_number_of_colors = 20`

-   **`max_num_face_colors`** (整数)
    *   **作用**: (此参数为脚本自定义，非直接ObsPy参数) 用于 `"standard"` PPSD图，建议控制概率密度着色时使用的离散颜色（面元）的最大数量。影响颜色过渡的平滑度。
    *   **示例**: `max_num_face_colors = 30`

-   **`standard_cmap`** (字符串)
    *   **作用**: 指定PPSD标准图的颜色映射方案 (colormap)。
    *   **ObsPy对应**: `PPSD.plot(cmap=...)`
    *   **可选值**: Matplotlib支持的任何颜色映射名称，如 `"viridis"`, `"plasma"`, `"obspy_sequential"`, `"pqlx"` (PQLX类似风格)。
    *   **示例**: `standard_cmap = "pqlx"`

**--- "spectrogram" (PPSD.plot_spectrogram) 图特定选项 ---**

-   **`clim`** (列表/元组, `[min_db, max_db]`, 可选)
    *   **作用**: 为频谱图的颜色映射指定振幅限制 (dB)。
    *   **ObsPy对应**: `PPSD.plot_spectrogram(clim=...)`
    *   **示例**: `clim = [-180, -100]`

-   **`time_format_x_spectrogram`** (字符串, 可选)
    *   **作用**: 自定义频谱图Y轴（时间轴）刻度标签的格式 (strftime格式)。
    *   **ObsPy对应**: `PPSD.plot_spectrogram(time_format_x=...)`
    *   **示例**: `time_format_x_spectrogram = "%Y-%m-%d"`

-   **`spectrogram_grid`** (布尔值: `true` / `false`)
    *   **作用**: 是否在频谱图上显示网格线。
    *   **ObsPy对应**: `PPSD.plot_spectrogram(grid=...)` (通常PPSD.plot_spectrogram没有直接的grid参数，但脚本可以实现此功能)
    *   **示例**: `spectrogram_grid = true`

-   **`spectrogram_cmap`** (字符串)
    *   **作用**: 指定PPSD频谱图的颜色映射方案。
    *   **ObsPy对应**: `PPSD.plot_spectrogram(cmap=...)`
    *   **示例**: `spectrogram_cmap = "viridis"`

**--- "temporal" (PPSD.plot_temporal) 图特定选项 ---**

-   **`temporal_plot_periods`** (数值列表, 单位：秒)
    *   **作用**: **对于 `plot_type` 包含 `"temporal"` 至关重要。** 指定一个或多个特定周期值（秒），脚本将为每个周期绘制PSD值随时间变化的曲线。
    *   **ObsPy对应**: `PPSD.plot_temporal(periods=...)`
    *   **示例**: `temporal_plot_periods = [1.0, 8.0, 20.0]`

-   **`time_format_x_temporal`** (字符串, 可选)
    *   **作用**: 自定义时态图X轴（时间轴）刻度标签的格式 (strftime格式)。
    *   **ObsPy对应**: `PPSD.plot_temporal(time_format_x=...)`
    *   **示例**: `time_format_x_temporal = "%H:%M"`

-   **`temporal_grid`** (布尔值: `true` / `false`)
    *   **作用**: 是否在时态图上显示网格线。
    *   **ObsPy对应**: `PPSD.plot_temporal(grid=...)`
    *   **示例**: `temporal_grid = true`

-   **`temporal_cmap`** (字符串)
    *   **作用**: 指定PPSD时态图的颜色映射方案（通常用于多条周期曲线时的颜色循环）。
    *   **ObsPy对应**: `PPSD.plot_temporal(cmap=...)`
    *   **示例**: `temporal_cmap = "viridis"`

## 4. 结果输出说明

`cp_psd.py`脚本的核心功能是计算和可视化PPSD。脚本根据提供的配置文件类型（计算型或绘图型）来决定执行哪些操作和生成哪些输出。
所有输出文件通常保存在相应配置文件中`output_dir`参数指定的目录下。此外，该目录还会包含一个通用的日志文件（如 `ppsd_processing_YYYYMMDD_HHMMSS.log`）记录处理过程。

### 4.1 绘图输出
-   **触发条件**: 当使用绘图型配置文件 (例如 `config_plot.toml`) 时，图像将**始终**被生成和保存。
-   **功能**: 根据绘图型配置文件`[args]`中的绘图参数（如 `plot_type`, `period_lim` 等）生成PPSD的可视化图像。
-   **主要输出**: PNG或PDF格式的图像文件。文件名由绘图配置文件中的 `output_filename_pattern` (如果提供) 或默认规则确定。示例模式：
    *   `{plot_type}_{network}.{station}.{location}.{channel}.png`
-   **`plot_type` 可选值 (详见3.2节参数详解)**:
    *   `"standard"`: 标准PPSD图，显示概率密度。
    *   `"temporal"`: 特定周期PSD值随时间变化的曲线图。
    *   `"spectrogram"`: PPSD的整体频谱图，显示功率谱密度随时间和周期的变化。
-   **适用场景**: 适用于交互式分析数据、检查PPSD结果的合理性以及报告生成。

### 4.2 NPZ数据文件输出
-   **触发条件**: 当使用计算型配置文件 (例如 `config.toml`) 时，NPZ数据文件将**始终**被计算并保存。
-   **功能**: 将计算得到的PPSD核心数据保存为NumPy的NPZ格式文件。
-   **主要输出**: NPZ文件。文件名由计算配置文件中的 `output_npz_filename_pattern` (如果提供) 或默认规则确定。示例模式：
    *   `PPSD_{network}.{station}.{location}.{channel}_{datetime}.npz`
-   **内容**: NPZ文件通常包含PPSD对象的主要属性，如概率密度函数矩阵、周期/频率轴、dB轴、处理过的时窗数量等，便于后续通过Python (ObsPy, NumPy) 进行加载和进一步分析。
-   **适用场景**: 适用于批量处理、数据预处理，或当用户希望后续使用自定义脚本进行高级分析或绘图，以及希望避免重复计算PPSD的场景。

### 4.3 CSV统计数据导出
-   **触发条件**: 当计算型配置文件或绘图型配置文件的 `[args]` 表中定义了CSV导出相关参数 (主要是 `percentiles`，通常也需要 `cumulative=true`) 时，CSV文件将被导出。
    *   对于计算型配置：在PPSD计算完成后，从新计算的数据中导出。
    *   对于绘图型配置：在加载PPSD数据后，从加载的数据中导出。
-   **功能**: 将PPSD的统计特性（如不同周期的百分位数噪声水平）导出为CSV（逗号分隔值）文件。
-   **主要输出**: CSV文件。文件命名模式示例：
    *   `PPSD_statistics_{network}.{station}.{location}.{channel}.csv` (脚本可能会基于NPZ文件名或PPSD元数据自动生成)
-   **内容**: CSV文件通常包含每个周期点对应的不同百分位数的功率谱密度值（dB）。
-   **依赖参数**: `[args]` 中的 `percentiles` 列表和通常的 `cumulative = true`。
-   **适用场景**: 适用于需要将PPSD统计结果导入电子表格软件（如Excel, Google Sheets）、其他统计分析工具，或进行快速的数据对比和报告。

## 5. 性能优化建议

### 5.1 内存优化
当处理非常大的数据集或在内存受限的环境中运行时，可以调整以下参数以减少内存占用：
```toml
[args]
ppsd_length = 1800          # 减少窗口长度 (会影响低频分辨率)
period_step_octaves = 0.25  # 增加周期步长 (降低频率点密度)
db_bins = [-180, -80, 0.5]  # 减少dB分箱的范围或增大步长 (降低功率分辨率)
max_num_face_colors = 20    # (如果使用绘图配置) 减少标准PPSD图的颜色数量
```
同时，如果主要目的是计算NPZ，确保不传递绘图配置文件，反之亦然，以避免不必要的操作消耗内存。

### 5.2 计算速度优化
为提高PPSD的计算速度，可以考虑（主要适用于计算型配置文件）：
```toml
[args]
skip_on_gaps = true         # 跳过有数据间断的窗口，避免处理不完整数据
overlap = 0.25              # 减少窗口重叠比例 (可能牺牲一些统计平滑度)
period_limits = [0.1, 100]  # 限制PPSD计算的周期/频率范围，仅分析感兴趣的频段
# time_of_weekday = [1,2,3] # (如果适用) 减少分析的天数或时段
```
此外，如果PPSD数据已经计算并保存为NPZ文件，后续仅执行绘图操作（通过提供绘图配置文件）会快得多，因为它们可以直接加载NPZ数据，避免重复计算。

## 6. 常见问题与解决方案

### 6.1 内存不足错误 (MemoryError)
-   **问题**: 在处理大数据集或长时间序列时，脚本因内存耗尽而崩溃。
-   **解决方案**:
    1.  应用 **6.1 内存优化** 中提到的参数调整。
    2.  分块处理数据：如果可能，将大的时间范围或大量台站分批处理。
    3.  增加系统可用内存或使用具有更多内存的机器。
    4.  确保系统中没有其他内存密集型程序同时运行。

### 6.2 计算时间过长
-   **问题**: PPSD计算过程非常耗时。
-   **解决方案**:
    1.  应用 **6.2 计算速度优化** 中提到的参数调整。
    2.  利用已计算的NPZ文件：首次计算时，使用计算型配置文件。后续仅绘图或基于已计算数据导出CSV时，使用绘图型配置文件，脚本应能自动加载之前生成的NPZ文件。
    3.  在多核CPU上，如果脚本或ObsPy内部支持并行处理（需查证ObsPy PPSD的并行特性），可以利用此优势。但当前`cp_psd.py`脚本本身可能需要额外修改以支持多文件并行。
    4.  检查数据读取效率，确保数据存储在快速磁盘上。

### 6.3 输出的周期/频率范围不符合预期
-   **问题**: PPSD图或导出的数据未覆盖期望的周期或频率。
-   **解决方案**:
    1.  检查核心计算参数 `[args].period_limits`：确保它定义了您希望PPSD对象本身包含的完整周期范围。
    2.  如果问题出在绘图上，检查绘图参数 `[args].period_lim`：这个参数控制绘图时显示的X轴范围，可能需要调整以匹配或专注于 `period_limits` 内的某个子集。
    3.  确认输入数据的采样率是否足够高以解析您期望的最短周期（最高频率）。根据奈奎斯特采样定理，最高可解析频率是采样率的一半。

### 6.4 PPSD结果异常或与预期不符
-   **问题**: 计算出的PPSD形状奇怪，噪声水平异常高或低，或者与已知参考（如Peterson模型）差异巨大。
-   **解决方案**:
    1.  **仪器响应文件**: 这是最常见的问题源。确保 `inventory_path` 指向正确且完整的仪器响应文件 (StationXML或dataless SEED)。验证响应的单位、增益、极零点或系数是否准确无误，并且在数据记录的时间段内有效。
    2.  **数据质量**:
        *   检查原始波形数据是否存在明显的异常、尖峰、数据中断或长时间的非物理信号。
        *   尝试设置 `[args].skip_on_gaps = true` 以排除有间断窗口的影响。
        *   考虑使用 `[args].time_of_weekday` 排除特定时段（如周末、夜间）的文化噪声，或仅分析这些时段，以判断噪声源。
    3.  **数据单位**: 确认原始数据单位与仪器响应中定义的输入单位一致。PPSD结果通常以 (m/s²)²/Hz (加速度) 或 (m/s)²/Hz (速度) 为单位，取决于响应。
    4.  **SEED ID匹配**: 确保波形数据中的台网、台站、位置、通道代码 (SEED ID) 与仪器响应文件中的完全一致。
    5.  **预处理步骤**: 虽然PPSD对象内部会进行一些处理，但如果数据质量非常差，可能需要在PPSD计算之前进行额外的预处理（如滤波、去趋势、去均值等），但这通常由ObsPy的 `PPSD.add()` 方法自动处理。

### 6.5 仪器响应问题导致单位或量级错误
-   **问题**: 功率谱密度的单位不正确（例如，期望速度谱却得到原始计数值的谱），或者PPSD的整体电平与预期（例如，与Peterson噪声模型或其他参考台站相比）有数量级差异。
-   **解决方案**:
    *   **核心在于 `inventory_path`**: 绝大多数此类问题源于仪器响应文件。
        *   确保 `inventory_path` 指向的 FDSN StationXML 文件或 SEED Dataless 文件准确描述了正在处理的数据通道的仪器特性。
        *   对于**速度地震计**，响应应能将原始数据转换为速度单位（如 m/s）。PPSD结果的单位将是 (m/s)²/Hz。
        *   对于**加速度地震计**，响应应能将原始数据转换为加速度单位（如 m/s²）。PPSD结果的单位将是 (m/s²)²/Hz。
        *   ObsPy的PPSD函数会根据提供的响应来处理数据并确定输出单位。**不需要**特殊的 `special_handling` 参数来区分速度或加速度计，关键在于Inventory的准确性。
    *   **检查内容**:
        *   **增益(Gain/Sensitivity)**: 这是最常出错的地方。确认总增益是否正确。
        *   **极点和零点 (Poles and Zeros)** 或 **系数 (Coefficients)**: 确保这些参数准确。
        *   **单位**: 响应中定义的输入单位（通常是 'COUNTS'）和输出单位（'M/S', 'M/S**2'）必须正确。
        *   **有效时间**: 确保仪器响应的有效期覆盖了正在处理的数据的时间段。
    *   **验证**:
        *   使用ObsPy的 `read_inventory()` 加载文件，并检查通道的 `response` 属性。
        *   可以将计算出的PPSD与同一地区、相似仪器的其他已知可靠结果进行对比。
        *   与Peterson噪声模型对比时，注意模型本身是以加速度 (m/s²)²/Hz 为单位的。如果您的仪器是速度计，ObsPy在绘图时通常会自动处理单位转换以进行比较，但您需要确保自己的PPSD计算结果确实是物理单位。

## 7. 最佳实践

### 7.1 数据预处理阶段
1.  **数据质量检查**: 在批量运行PPSD计算之前，建议先抽样检查部分原始波形数据的质量，注意是否存在明显的仪器故障、数据污染或时间标记错误。
2.  **时间同步**: 确保所有参与计算的地震数据时间戳准确且同步。
3.  **仪器响应验证**: 这是获得可信PPSD结果的最关键步骤。
    *   务必使用与数据严格对应的最新、最准确的仪器响应文件。
    *   对于每个台站通道，仔细核对台网、台站、位置、通道代码 (SEED ID) 是否与数据完全匹配。
    *   检查响应的有效起止时间是否覆盖数据记录时段。
    *   如果可能，将从仪器响应中提取的理论传递函数与已知的参考进行比较。

### 7.2 参数选择策略
1.  **`ppsd_length` (窗口长度)**:
    *   标准背景噪声分析: `3600` 秒 (1小时) 是良好起点。
    *   关注低频/长周期: 可适当增加，如 `7200` 秒，但注意时间分辨率下降。
    *   关注高频/短时变化: 可适当减少，如 `1800` 秒，但注意低频分辨率下降。
2.  **`overlap` (重叠比例)**:
    *   `0.5` (50%) 是计算效率和统计平滑度之间的常用平衡点。
    *   数据量非常有限时，可适当增加至 `0.75` 以改善统计性，但计算成本增加。
3.  **`period_limits` (计算周期范围)**:
    *   根据分析目标（如微震、地脉动、长周期噪声）和数据采样率（奈奎斯特频率）合理设定，避免不必要的计算。
4.  **`db_bins` (功率分箱)**:
    *   `[-200, -50, 0.25]` 适用于大多数宽频带地震仪。如果噪声特别高或特别低，或者只关注特定功率范围，可以调整范围 `[min_db, max_db]`。步长 `0.25` dB 通常足够精细。
5.  **`time_of_weekday` (时间选择)**:
    *   根据是否需要排除或专门分析特定时间（如工作日/周末，白天/夜晚）的文化噪声来设定。
    *   分析整体背景噪声时，通常不设置此参数或包含所有天。
6.  **`skip_on_gaps` (数据间断处理)**:
    *   数据质量较好、间断少: `false` 可以利用更多数据。
    *   数据间断较多或对PPSD纯净度要求极高: `true` 可以确保每个PSD基于完整窗口数据。

### 7.3 结果验证与解读
1.  **与全球噪声模型对比**:
    *   将生成的PPSD图（特别是启用了 `show_noise_models = true`）与Peterson新低噪声模型 (NLNM) 和新高噪声模型 (NHNM) 进行比较。
    *   健康的台站噪声水平通常应位于NLNM和NHNM之间。持续高于NHNM可能表示台址环境噪声大或仪器问题；持续低于NLNM可能表示仪器响应问题或异常安静的环境（需谨慎确认）。
2.  **与邻近或相似台站对比**:
    *   如果条件允许，将目标台站的PPSD与同一区域、相似地质条件、相似仪器的其他台站进行对比，检查是否存在显著的、无法合理解释的差异。
3.  **时间稳定性检查**:
    *   如果数据跨度足够长，可以分时段（如按年、按季节）计算PPSD，检查噪声水平是否存在长期趋势或周期性变化，这可能与环境变化、仪器老化等因素有关。
    *   使用 `plot_type = "temporal"` 或 `"spectrogram"` 可以帮助识别噪声随时间的变化模式。
4.  **关注特定频段特征**:
    *   **地脉动峰 (Microseismic Peaks)**: 在0.1-1 Hz (1-10秒周期) 范围内通常能观察到由全球海浪活动引起的地脉动双峰结构。检查这些峰的幅度和形态是否合理。
    *   **人为噪声**: 在较高频率（>1 Hz）注意是否存在窄带的、稳定的谱峰，这通常指示特定频率的人为噪声源（如电力线、机械振动）。
    *   **长周期噪声**: 在较长周期（>10-20秒）检查噪声水平是否符合预期，有无异常抬升。

## 8. 参考文档
-   **ObsPy PPSD官方文档**: [https://docs.obspy.org/packages/autogen/obspy.signal.spectral_estimation.PPSD.html](https://docs.obspy.org/packages/autogen/obspy.signal.spectral_estimation.PPSD.html)
-   **Peterson (1993) 噪声模型**: USGS Open-File Report 93-322, "Observations and Modeling of Seismic Background Noise". (这是NLNM/NHNM的原始文献)
-   **McNamara & Buland (2004)**: "Ambient Noise Levels in the Continental United States", Bulletin of the Seismological Society of America (BSSA), Vol. 94, No. 4, pp. 1517-1527. (PPSD方法在地震学中广泛应用的开创性论文之一)
-   项目内部文档: `principle.md` (如果存在，可能包含项目特定的理论基础和算法详解)。 