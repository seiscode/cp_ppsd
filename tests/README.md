# 测试程序目录

本目录包含用于测试和验证PPSD计算与绘图功能的各种测试程序。

## 测试文件列表

### 1. 基础功能测试
- **test_basic.py** - 基础功能测试程序
  - 测试PPSD计算的基本功能
  - 验证配置文件加载和参数解析
  - 检查输出文件生成

### 2. 配置参数测试
- **test_config_params.py** - 配置参数验证测试
  - 测试各种配置参数的有效性
  - 验证参数边界条件
  - 检查配置文件格式正确性

### 3. 配置示例程序
- **example_read_grouped_config.py** - 分组配置文件读取演示
  - 演示如何直接读取TOML分组配置文件
  - 展示各种配置访问方法和最佳实践
  - 包含安全访问方法和配置验证示例
  - 提供配置构建器模式演示

- **example_use_grouped_config.py** - 分组配置适配器使用演示
  - 演示如何使用GroupedConfigAdapter处理嵌套分组配置
  - 展示config_plot.toml的嵌套分组结构使用方法
  - 说明配置映射和兼容性处理
  - 提供详细的使用示例和最佳实践

- **example_use_simple_grouped_config.py** - 简单分组配置使用演示
  - 演示简单分组配置的使用方法
  - 对比传统配置和分组配置的优势
  - 展示配置结构的改进和参数关联性
  - 提供清晰的配置迁移指导

- **example_merge_npz.py** - NPZ文件合并演示程序
  - 演示如何使用ObsPy的PPSD.add_npz()方法正确合并NPZ文件
  - 提供手动NPZ文件合并的最佳实践
  - 展示单文件模式生成的NPZ文件的合并策略
  - 包含错误处理和数据验证示例
  - 作为NPZ合并功能的参考实现和教学工具

### 4. 特殊处理测试
- **test_special_handling_hydrophone.py** - 水听器特殊处理测试
  - 测试水听器数据的特殊处理逻辑
  - 验证仪器校正但不微分的处理流程

- **test_special_handling_ringlaser.py** - 环形激光器特殊处理测试
  - 测试环形激光器数据的特殊处理逻辑
  - 验证不进行仪器校正的处理流程

- **test_special_handling_standard.py** - 标准地震仪处理测试
  - 测试标准地震仪数据处理逻辑
  - 验证仪器校正+微分的标准流程

### 5. 报告生成测试
- **test_summary_report.py** - 摘要报告生成测试
  - 测试处理结果摘要报告的生成
  - 验证统计信息的准确性
  - 检查报告格式和内容

### 6. 数据分析工具
- **analyze_npz_content.py** - NPZ文件内容分析工具
  - 分析PPSD计算生成的NPZ文件结构
  - 显示文件中包含的数据类型和维度
  - 验证数据完整性

- **ppsd_binning_demo.py** - PPSD分箱演示程序
  - 演示PPSD频率和功率分箱机制
  - 可视化分箱策略和参数影响
  - 教学和调试用途

### 7. 配置优化工具
- **config_optimization_report.py** - 配置优化报告生成器
  - 分析当前配置的性能特征
  - 提供配置优化建议
  - 生成详细的配置分析报告

### 8. 数据信息检查
- **check_data_info.py** - 数据信息检查工具
  - 检查输入数据的基本信息
  - 验证数据格式和完整性
  - 显示台站和通道信息

### 9. 配色方案工具
- **custom_colormap_comparison.py** - 自定义配色方案PPSD对比工具（新增）
  - 展示自定义配色方案在PPSD图中的效果
  - 提供viridis_custom, ocean_custom, plasma_custom等6个自定义配色方案对比
  - 基于现有配色方案的优化版本，针对地球物理数据可视化
  - 生成自定义vs原始配色方案效果对比图
  - 提供详细的自定义配色方案推荐报告和技术说明
  - 说明自定义配色的实现原理、优缺点和适用场景

- **qualitative_colormap_comparison.py** - 定性配色方案PPSD对比工具
  - 展示定性配色方案(Qualitative colormaps)在PPSD图中的效果
  - 提供Set1, Set2, Paired, tab10等定性配色方案对比
  - 生成定性vs连续配色方案效果对比图
  - 提供详细的配色方案推荐报告和使用建议
  - 说明定性配色的特点、优缺点和适用场景

- **white_background_colormap_comparison.py** - 白色背景PPSD配色方案对比工具
  - 专门展示白色背景的配色方案效果
  - 适合科技报告和学术论文的配色选择
  - 提供打印友好的配色方案推荐
  - 生成专业的配色方案分析报告

- **ppsd_colormap_comparison.py** - PPSD配色方案对比工具
  - 生成多种配色方案的对比图
  - 帮助选择最适合的PPSD图配色
  - 提供配色方案推荐报告
  - 支持参考图片配色匹配

### 10. 百分位数线样式测试工具（新增）
- **test_percentile_line_styles.py** - 百分位数线样式功能测试（完整版）
  - 测试自定义百分位数线样式功能的完整实现
  - 对比默认样式和多种自定义样式的视觉效果
  - 验证颜色、线宽、线型、透明度等参数的正确应用
  - 生成详细的样式对比报告和技术说明
  - 适用于功能验证和样式选择参考

- **test_percentile_styles_simple.py** - 百分位数线样式测试（简化版）
  - 通过修改配置文件测试不同百分位数线样式
  - 包含浅灰色细线、深灰色中等线宽、钢蓝色虚线等预设样式
  - 自动备份和恢复配置文件，确保测试安全
  - 为每种样式生成独立的输出文件便于对比
  - 适用于快速样式测试和效果预览

### 11. 测试套件运行器
- **run_all_tests.py** - 批量测试运行器
  - 自动运行所有测试程序
  - 提供详细的测试结果报告
  - 支持测试模式选择和进度跟踪

## 使用方法

### 运行单个测试
```bash
# 运行基础功能测试
python tests/test_basic.py

# 运行配置参数测试
python tests/test_config_params.py

# 运行配置示例演示
python tests/example_read_grouped_config.py
python tests/example_use_grouped_config.py
python tests/example_use_simple_grouped_config.py

# 运行NPZ合并演示
python tests/example_merge_npz.py

# 运行NPZ文件分析
python tests/analyze_npz_content.py

# 运行配色方案对比
python tests/custom_colormap_comparison.py

# 运行配色方案对比
python tests/ppsd_colormap_comparison.py
```

### 运行所有测试
```bash
# 运行完整测试套件
python tests/run_all_tests.py

# 运行测试套件（详细模式）
python tests/run_all_tests.py --verbose

# 运行特定模式的测试
python tests/run_all_tests.py --pattern "test_*"
```

## 测试环境要求

- Python 3.8+
- ObsPy >= 1.4.0
- matplotlib >= 3.5.0
- numpy >= 1.21.0
- toml >= 0.10.2

## 注意事项

1. **数据依赖**: 某些测试需要在`./data/`目录中有有效的地震数据文件
2. **配置文件**: 测试程序会使用`./input/`目录中的配置文件
3. **输出目录**: 测试结果会保存在`./output/`相关子目录中
4. **日志文件**: 测试过程的日志会保存在`./logs/`目录中

## 故障排除

如果测试失败，请检查：
- 数据文件是否存在且格式正确
- 配置文件是否有效
- 输出目录是否有写入权限
- 依赖库是否正确安装

## 贡献指南

### 添加新测试

1. 在`tests/`目录创建新的测试文件
2. 遵循命名约定：`test_[功能名].py`
3. 包含详细的文档字符串和注释
4. 更新本README文件

### 测试最佳实践

1. **独立性**: 每个测试应该独立运行
2. **可重复性**: 测试结果应该可重复
3. **清理**: 测试后清理临时文件
4. **文档**: 提供清晰的测试说明

## 相关文档

- [项目主文档](../README.md)
- [产品说明文档](../cursor_project_rules/产品说明文档：PDF计算软件.md)
- [PSD分析工具说明](../cursor_project_rules/run_plot_psd使用说明.md)
- [配置文件参考](../input/)

---

**注意**: 运行测试前请确保已正确安装所有依赖包，并准备好必要的测试数据。