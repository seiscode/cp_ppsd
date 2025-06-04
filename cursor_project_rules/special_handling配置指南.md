# special_handling 参数配置指南

基于2025-06-04系统性测试的配置建议

## 🎯 参数概述

`special_handling` 参数控制特殊仪器的数据处理方式，主要影响：
- **仪器校正**: 是否执行完整的仪器响应校正
- **微分操作**: 是否将速度转换为加速度
- **物理量输出**: 最终PPSD的物理意义和单位

## 📊 支持的模式

| 模式 | 仪器校正 | 微分操作 | 输出物理量 | 适用仪器 |
|------|----------|----------|------------|----------|
| **未设置/None** | ✅ 完整校正 | ✅ 速度→加速度 | 加速度PSD | 标准地震仪 |
| **"ringlaser"** | ❌ 仅除以sensitivity | ❌ 无微分 | 原始计数PSD | 环形激光仪 |
| **"hydrophone"** | ✅ 完整校正 | ❌ 无微分 | 压力PSD | 水听器 |

## 🔧 配置方法

### 1. 标准地震仪 (推荐默认)

```toml
# 方法1: 注释掉参数（推荐）
# special_handling = "None"

# 方法2: 显式设置为None
special_handling = "None"
```

**适用场景**:
- 宽频地震仪 (BB, BH通道)
- 短周期地震仪 (SH, EH通道)
- 强震仪 (HN, HL通道)

**输出特征**:
- 物理量: 加速度功率谱密度 (m²/s⁴/Hz)
- 符合McNamara & Buland (2004)标准
- 可与全球噪声模型比较

### 2. 环形激光干涉仪

```toml
special_handling = "ringlaser"
```

**适用场景**:
- 环形激光干涉仪
- 需要保持原始信号特征的特殊仪器

**输出特征**:
- 物理量: 原始计数功率谱密度
- 绕过ObsPy标准处理流程
- 仅除以sensitivity，保持原始动态范围

**注意事项**:
- 需要StationXML中包含正确的sensitivity值
- 结果不能与标准地震噪声模型比较

### 3. 水听器/压力传感器

```toml
special_handling = "hydrophone"
```

**适用场景**:
- 海底水听器
- 压力传感器
- 需要压力量测量的应用

**输出特征**:
- 物理量: 压力功率谱密度 (Pa²/Hz)
- 执行仪器校正但不转换为加速度
- 保持压力的物理意义

## ⚠️ 重要警告

### 1. 结果不可比性
```
❌ 错误: 混合比较不同special_handling模式的结果
✅ 正确: 确保所有数据使用相同模式
```

### 2. 仪器匹配
```
❌ 错误: 对标准地震仪使用ringlaser模式
✅ 正确: 根据实际仪器类型选择模式
```

### 3. 物理意义
```
❌ 错误: 忽略不同模式的物理量差异
✅ 正确: 明确记录使用的模式和输出物理量
```

## 🔍 配置验证

### 检查NPZ文件中的设置
```bash
python -c "
import numpy as np
with np.load('your_file.npz') as f:
    print(f'special_handling: {f[\"special_handling\"].item()}')
"
```

### 验证仪器类型匹配
```python
# 检查StationXML中的仪器信息
from obspy import read_inventory
inv = read_inventory('your_inventory.xml')
for net in inv:
    for sta in net:
        for cha in sta:
            print(f"{cha.code}: {cha.sensor.description}")
```

## 📈 性能影响

基于测试结果的性能对比：

| 模式 | 处理时间 | 相对性能 | 文件大小 |
|------|----------|----------|----------|
| None (默认) | ~30s | 基准 | 217.5 KB |
| ringlaser | ~30s | 相同 | 217.0 KB |
| hydrophone | ~45s | +50% | 217.1 KB |

**性能建议**:
- hydrophone模式处理时间较长，适合离线分析
- ringlaser模式性能最优，适合实时处理
- 文件大小差异很小，存储影响可忽略

## 🎯 应用场景

### 1. 地震台网监测
```toml
# 标准配置 - 适用于大多数地震台站
# special_handling = "None"  # 注释掉使用默认
```

### 2. 海底观测网
```toml
# 水听器配置 - 适用于海底压力传感器
special_handling = "hydrophone"
```

### 3. 精密重力测量
```toml
# 环形激光仪配置 - 适用于高精度旋转测量
special_handling = "ringlaser"
```

### 4. 多仪器对比研究
```toml
# 分别为不同仪器类型创建独立配置文件
# config_seismometer.toml: special_handling = "None"
# config_hydrophone.toml: special_handling = "hydrophone"
# config_ringlaser.toml: special_handling = "ringlaser"
```

## 🚨 常见错误与解决

### 错误1: sensitivity提取失败
```
错误信息: "ringlaser模式下无法提取sensitivity"
解决方案: 检查StationXML文件是否包含完整的仪器响应信息
```

### 错误2: 结果数值异常
```
错误信息: PSD值异常大或异常小
解决方案: 确认special_handling模式与实际仪器类型匹配
```

### 错误3: 无法比较结果
```
错误信息: 不同数据集的PSD值差异巨大
解决方案: 检查是否使用了相同的special_handling设置
```

## 📚 技术细节

### ObsPy PPSD内部处理
```python
# None模式: 标准处理流程
metadata = inventory  # 完整StationXML
# → 仪器校正 → 微分 → 加速度PSD

# ringlaser模式: 简化处理
metadata = {'sensitivity': value}  # 仅sensitivity
# → 除以sensitivity → 原始计数PSD

# hydrophone模式: 校正但不微分
metadata = inventory  # 完整StationXML
# → 仪器校正 → 压力PSD
```

### 代码实现位置
- 文件: `cp_ppsd/cp_psd.py`
- 函数: `_process_single_merged_trace_to_npz()`
- 行号: 500-530

## 📝 最佳实践清单

在使用special_handling参数前，请确认：

- [ ] 已确认实际仪器类型
- [ ] 选择了正确的special_handling模式
- [ ] StationXML包含必要的仪器信息
- [ ] 同一研究中保持模式一致性
- [ ] 在文档中记录了使用的模式
- [ ] 理解输出物理量的含义
- [ ] 不会混合比较不同模式的结果

---

**基于**: special_handling参数测试报告 v1.0  
**更新**: 2025-06-04  
**适用**: cp_ppsd v1.x 