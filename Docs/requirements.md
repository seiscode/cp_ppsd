# 项目需求

## 项目名称
PPSD 批量处理与可视化工具

## 项目简介
本项目为地震学数据分析提供命令行工具，支持批量计算和可视化概率功率谱密度（PPSD）。基于 ObsPy，支持数据导入、PPSD 计算、结果保存、批量绘图及交互式分析。

## 主要功能
- 批量导入地震数据文件（如 miniSEED）
- 自动加载仪器响应（如 StationXML）
- 自动检测并复用已存在的 PPSD 数据文件，避免重复计算
- 支持自定义数据格式和输出文件前缀
- 批量绘制标准 PPSD 图、时序图、频谱图，统一色标
- 支持加载单个 PPSD 进入 IPython 交互分析
- 命令行入口支持 add/plot/timeplot/spectrogram/load 子命令
- 所有命令支持参数自动补全和详细帮助信息
- 支持 --pdb 参数，异常时自动进入调试模式
- 关键步骤异常捕获和详细日志输出，日志输出到文件和终端

## 依赖环境
- Python 3.x
- ObsPy
- matplotlib
- tqdm（可选）
- IPython（可选）

## 约束与规范
- 输出文件命名统一（如 ppsd_data_{id}.npz）
- 变量命名具备描述性，代码风格一致
- 需考虑边界情况和异常处理，保证健壮性
- 不允许硬编码魔法数字，需使用常量
- 日志记录详尽，便于追踪

## 安全与性能
- 优先考虑性能，避免重复计算
- 文件操作安全，防止数据丢失或覆盖

## 数学公式说明
### 功率谱（PSD）
```
PSD(f) = (1 / (N * f_s)) * |Σ_{n=0}^{N-1} x[n] * exp(-j * 2π * f * n / f_s)|^2
```
其中：x[n]为离散信号，N为采样点数，f_s为采样频率，f为频率

### 概率功率谱密度（PPSD）
```
PDF(f, p) = （在频率 f 上，功率落入区间 p 的次数）/（总的时间窗口数）
```
其中：f为频率，p为功率区间

## 参考文档
- ObsPy PPSD API: https://docs.obspy.org/packages/autogen/obspy.signal.spectral_estimation.PPSD.html#obspy.signal.spectral_estimation.PPSD
