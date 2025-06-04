# BJ台网MinISEED数据波形+频谱+频谱图绘制工具

一个用于绘制地震波形和频谱分析图的Python工具，专门处理BJ台网的MinISEED格式数据。提供三重分析视图：时域波形、频域频谱和时频频谱图。

## 功能特点

- **自动检测**: 自动扫描指定目录下的MinISEED文件
- **三重显示**: 在同一图像中显示时域波形图（上）、频域频谱图（中）和时频频谱图（下）
- **智能采样**: 数据采样优化，减少绘图点数，显著提升绘图速度
- **Gap处理**: 使用ObsPy Stream.merge方法自动检测并填充数据间隙
- **对数坐标**: 频谱图使用对数坐标，频谱图频率限制0.1-50Hz
- **高质量输出**: 生成150 DPI (快速模式) 或200 DPI (质量模式) 的PNG图像
- **性能模式**: 支持快速模式和质量模式，平衡速度与质量
- **命令行友好**: 支持命令行参数，灵活指定输入和输出目录
- **简洁文件名**: 统一的文件命名格式，不含模式标识
- **详细信息**: 在图上显示台站信息、采样率、数据点数、Gap统计等技术参数

## 安装要求

### Python版本
- Python 3.7+

### 依赖包
```bash
pip install obspy matplotlib numpy
```

### 系统要求
- Linux/macOS/Windows
- 建议内存: 8GB+ (处理大型地震数据时)

## 使用方法

### 基本语法
```bash
python plot_waveform_spectrum.py [data_directory] [-o OUTPUT_DIRECTORY] [-q]
```

### 参数说明

#### 位置参数
- **`data_directory`** (可选): MinISEED文件所在目录
  - 默认值: `./data`
  - 支持绝对路径和相对路径

#### 可选参数
- **`-o, --output`**: 输出图片目录
  - 默认值: `./output/waveforms`
- **`-q, --quality`**: 使用质量模式（较慢但图像质量更好）
- **`-h, --help`**: 显示帮助信息

### 使用示例

#### 1. 使用默认设置（快速模式）
```bash
python plot_waveform_spectrum.py
```
- 数据目录: `./data`
- 输出目录: `./output/waveforms`
- 性能模式: 快速

#### 2. 质量模式
```bash
python plot_waveform_spectrum.py -q
```
- 更高质量图像 (200 DPI)
- 更多绘图点数
- 处理速度较慢

#### 3. 指定数据目录
```bash
python plot_waveform_spectrum.py /path/to/seismic/data
```

#### 4. 指定数据和输出目录
```bash
python plot_waveform_spectrum.py data -o ./results/waveforms
```

#### 5. 使用相对路径和质量模式
```bash
python plot_waveform_spectrum.py ../seismic_data --output ../analysis_results -q
```

## 支持的数据格式

- **MinISEED** (*.mseed, *.miniseed, *.ms)

## 输出结果

### 文件命名规则
```
{网络代码}_{台站代码}_{通道代码}_{开始时间}.png
```

例如: 
- `BJ_BBS_BHZ_20250325_160001.png`
- `BJ_DSQ_SHZ_20250325_160001.png`

其中时间格式为：YYYYMMDD_HHMMSS

**注意**: 无论使用快速模式还是质量模式，文件名格式保持一致，模式信息仅在图像内部显示。

### 图像内容

#### 上图: 时域波形图
- X轴: 时间 (HH:MM格式)
- Y轴: 振幅 (counts)
- 显示完整的24小时连续波形数据
- 数据采样优化（快速模式最大10,000点，质量模式最大50,000点）

#### 中图: 频域频谱图
- X轴: 频率 (Hz, 对数坐标)
- Y轴: 振幅 (counts, 对数坐标)
- FFT优化计算（快速模式最大8,192点，质量模式最大16,384点）

#### 下图: 时频频谱图（Spectrogram）
- X轴: 时间 (s)
- Y轴: 频率 (Hz, 对数坐标，限制0.1-50Hz)
- 颜色条: 功率 (Power)
- NFFT窗口大小（快速模式512点，质量模式1024点）
- 颜色条位置优化，与上面两图右边缘对齐

#### 信息标注
- **波形图信息框**:
  - 台站名称和通道
  - 采样率 (Hz)
  - 数据时长和点数
  - 性能模式
  - Gap统计信息

## 性能优化特性

### 数据预处理
- 使用 `obspy.Stream.merge(method=0, fill_value=0)` 合并数据段
- 自动检测和填充数据gaps，显示详细gap统计
- 支持多段数据自动拼接

### 绘图优化
- **智能数据采样**: 根据性能模式自动调整绘图点数
- **FFT优化**: 限制FFT计算点数以提升速度
- **光栅化渲染**: 快速模式使用光栅化以减少文件大小
- **内存管理**: 及时释放图形对象

### 性能模式对比

| 特性 | 快速模式 (默认) | 质量模式 (-q) |
|------|----------------|---------------|
| 图像尺寸 | 10×12 inches | 12×14 inches |
| DPI | 150 | 200 |
| 最大波形点数 | 10,000 | 50,000 |
| FFT最大点数 | 8,192 | 16,384 |
| 频谱图NFFT | 512 | 1024 |
| 光栅化 | 是 | 否 |
| 处理速度 | 快 (~3.5s/文件) | 较慢 |
| 图像质量 | 良好 | 优秀 |

## 示例运行输出

```
======================================================================
BJ Network MinISEED Waveform + Spectrum + Spectrogram Tool
======================================================================
Performance mode: FAST
Data directory: ./data
Output directory: ./output/waveforms

Found 5 miniseed files:
  BJ.BBS.00.BHZ.20250326000001.mseed (16.9 MB)
  BJ.DAX.00.BHZ.20250326000001.mseed (10.9 MB)
  BJ.DSQ.00.SHZ.20250326000001.mseed (9.8 MB)
  BJ.FHY.00.BHZ.20250326000003.mseed (5.9 MB)
  BJ.JIZ.00.SHZ.20250326000000.mseed (17.4 MB)

=== Processing with FAST mode ===

Processing: BJ.BBS.00.BHZ.20250326000001.mseed
  Read 23 traces
  Detected 22 gaps:
    BJ.BBS.00.BHZ: 2025-03-25T19:32:59.990000Z to 2025-03-25T19:33:20.000000Z (duration: 20.00s)
    [详细gap信息...]
  Original traces: 23
  After gap filling: 1 traces
  ✓ Filled 22 gaps with zeros
    BJ.BBS.00.BHZ: 8639963 points, 100.0 Hz
    Performance mode: fast
    Image size: (10, 12), DPI: 150
    Waveform points: 10,012 (original: 8,639,963)
    FFT points: 8,198
    Spectrogram NFFT: 512
    Plot completed in 3.43s: BJ_BBS_BHZ_20250325_160001.png
  File processed in 3.90s

[其他文件处理...]

=== Performance Summary ===
Total processing time: 17.31s
Average time per file: 3.46s
Successful plots: 5/5
Performance mode: fast
Output directory: ./output/waveforms
```

## 数据处理流程

1. **文件发现**: 扫描指定目录查找MinISEED文件
2. **数据读取**: 使用ObsPy读取地震数据
3. **Gap检测**: 自动检测数据间隙并统计
4. **数据预处理**: 合并数据段，零填充gaps
5. **智能采样**: 根据性能模式优化数据点数
6. **波形绘制**: 生成时域波形图
7. **频谱计算**: FFT变换计算频域特征
8. **频谱绘制**: 生成对数坐标频谱图
9. **频谱图生成**: 生成时频频谱图，限制频率范围0.1-50Hz
10. **图像保存**: 输出高质量PNG文件

## 技术亮点

### Gap处理优化
- **自动检测**: 使用`Stream.get_gaps()`检测数据间隙
- **零填充**: 使用`Stream.merge(method=0, fill_value=0)`进行补零
- **统计显示**: 在图像中显示gap数量和处理状态

### 频谱图优化
- **频率限制**: 纵轴限制在0.1-50Hz，突出低频段细节
- **颜色条对齐**: 精确控制颜色条位置，与上面两图右边缘对齐
- **紧凑布局**: 优化间距设置（2%宽度，0.05间距）

### 布局美化
- **一致对齐**: 三个子图右边缘完美对齐
- **信息丰富**: 详细的处理参数和数据统计
- **视觉平衡**: 优化的颜色条和标签布局

## 故障排除

### 常见问题

#### 1. 找不到数据文件
```
Error: Data directory ./data not found
```
**解决方案**: 检查数据目录路径是否正确

#### 2. 内存不足
**症状**: 处理大文件时程序崩溃
**解决方案**: 
- 使用快速模式 (默认)
- 增加系统内存
- 分批处理数据文件

#### 3. Gap处理错误
**症状**: Gap检测或填充失败
**解决方案**: 
- 检查数据文件完整性
- 使用backup合并方法 (method=-1)

#### 4. 绘图速度慢
**症状**: 处理时间过长
**解决方案**: 
- 使用快速模式 (默认)
- 减少数据文件大小
- 关闭质量模式

#### 5. 字体警告
**症状**: matplotlib字体相关警告
**解决方案**: 
- 安装中文字体包
- 忽略警告 (不影响功能)

## 版本历史

### v2.0 (当前版本)
- 添加时频频谱图（三子图布局）
- 智能数据采样优化
- Gap自动检测和填充
- 性能模式选择
- 频率范围限制 (0.1-50Hz)
- 颜色条布局优化

### v1.0 (已废弃)
- 基础波形+频谱双图布局
- 基本gap处理