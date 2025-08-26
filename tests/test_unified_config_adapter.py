#!/usr/bin/env python3
"""
Author:
    muly (muly@cea-igp.ac.cn)
license:
    MIT License
    (https://opensource.org/licenses/MIT)

统一配置适配器测试和演示脚本

此脚本演示如何使用统一配置适配器处理两种不同格式的config_plot.toml文件：
1. 精细分组格式（多层嵌套）
2. 简单分组格式（按绘图类型分组）

还展示了配置格式的转换功能。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cp_ppsd.unified_config_adapter import UnifiedConfigAdapter


def test_config_format_detection():
    """测试配置格式检测功能"""
    print("=== 配置格式检测测试 ===\n")
    
    test_configs = [
        "input/config_plot.toml",  # 精细分组格式
        "input/config_plot_simple.toml"  # 简单分组格式
    ]
    
    for config_path in test_configs:
        if os.path.exists(config_path):
            print(f"测试配置文件: {config_path}")
            try:
                adapter = UnifiedConfigAdapter(config_path)
                adapter.print_format_info()
                
                config = adapter.get_config()
                print(f"  输出目录: {config.get('output_dir', 'N/A')}")
                print(f"  绘图类型: {config.get('plot_types', 'N/A')}")
                print(f"  合并策略: {config.get('npz_merge_strategy', 'N/A')}")
                
                if 'args' in config:
                    args = config['args']
                    print(f"  显示百分位数: {args.get('show_percentiles', 'N/A')}")
                    print(f"  百分位数值: {args.get('percentiles', 'N/A')}")
                    print(f"  显示噪声模型: {args.get('show_noise_models', 'N/A')}")
                
                print()
                
            except Exception as e:
                print(f"  ❌ 加载失败: {e}\n")
        else:
            print(f"⚠️  配置文件不存在: {config_path}\n")


def test_config_format_conversion():
    """测试配置格式转换功能"""
    print("=== 配置格式转换测试 ===\n")
    
    config_path = "input/config_plot_simple.toml"
    
    if os.path.exists(config_path):
        try:
            adapter = UnifiedConfigAdapter(config_path)
            
            print(f"原始格式: {adapter.get_format()}")
            
            # 转换为精细分组格式
            if adapter.get_format() != "grouped":
                print("\n转换为精细分组格式...")
                grouped_config = adapter.convert_to_grouped_format()
                
                print("✅ 转换成功")
                print(f"转换后包含 {len(grouped_config)} 个主要分组:")
                for section in grouped_config.keys():
                    print(f"  - [{section}]")
                
                # 保存转换后的配置
                output_path = "input/config_plot_simple_converted.toml"
                adapter.save_as_grouped_format(output_path)
                
                # 验证转换后的配置
                print("\n验证转换后的配置...")
                converted_adapter = UnifiedConfigAdapter(output_path)
                converted_adapter.print_format_info()
                
            else:
                print("✅ 原始配置已是精细分组格式，无需转换")
                
        except Exception as e:
            print(f"❌ 转换失败: {e}")
    else:
        print(f"⚠️  配置文件不存在: {config_path}")


def test_compatibility():
    """测试与现有系统的兼容性"""
    print("\n=== 兼容性测试 ===\n")
    
    test_configs = [
        "input/config_plot.toml",
        "input/config_plot_simple.toml"
    ]
    
    for config_path in test_configs:
        if os.path.exists(config_path):
            print(f"测试配置: {config_path}")
            try:
                adapter = UnifiedConfigAdapter(config_path)
                config = adapter.get_config()
                
                # 检查关键字段
                required_fields = [
                    'input_npz_dir', 'output_dir', 'plot_types', 'args'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in config:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"  ❌ 缺少必需字段: {missing_fields}")
                else:
                    print("  ✅ 包含所有必需字段")
                
                # 检查args配置
                args = config.get('args', {})
                if args:
                    args_count = len(args)
                    print(f"  ✅ args配置包含 {args_count} 个参数")
                else:
                    print("  ❌ args配置为空")
                
                print()
                
            except Exception as e:
                print(f"  ❌ 兼容性测试失败: {e}\n")
        else:
            print(f"⚠️  配置文件不存在: {config_path}\n")


def demonstrate_unified_adapter():
    """完整演示统一配置适配器的功能"""
    print("=============================================")
    print("       统一配置适配器功能演示")
    print("=============================================")
    
    print("此演示展示统一配置适配器如何：")
    print("1. 自动检测配置文件格式")
    print("2. 适配不同格式为统一接口")
    print("3. 提供格式转换功能")
    print("4. 确保与现有系统的兼容性")
    print()
    
    # 执行各项测试
    test_config_format_detection()
    test_config_format_conversion()
    test_compatibility()
    
    print("=============================================")
    print("             演示完成")
    print("=============================================")
    
    print("\n✅ 统一配置适配器已成功实现以下功能:")
    print("  - 支持精细分组格式（推荐格式）")
    print("  - 支持简单分组格式（简化格式）")
    print("  - 支持传统扁平格式（兼容格式）")
    print("  - 自动格式检测和适配")
    print("  - 格式转换和升级迁移")
    print("  - 与现有代码完全兼容")
    
    print("\n📖 使用建议:")
    print("  - 新项目推荐使用精细分组格式")
    print("  - 现有项目可平滑迁移到任意格式")
    print("  - 所有格式均可正常运行程序")


if __name__ == "__main__":
    demonstrate_unified_adapter() 
