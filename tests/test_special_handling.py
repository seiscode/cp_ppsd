#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试special_handling参数的影响

测试不同special_handling设置对PPSD计算的影响：
- null (默认): 标准仪器校正和微分
- "ringlaser": 仅除以sensitivity，不做仪器校正
- "hydrophone": 仪器校正但不做微分
"""

import os
import sys
import toml
import tempfile
import shutil
import numpy as np
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from cp_ppsd import PPSDProcessor
    print("✓ 成功导入PPSDProcessor")
except ImportError as e:
    print(f"✗ 导入PPSDProcessor失败: {e}")
    sys.exit(1)


def create_test_config(special_handling_value, output_suffix):
    """创建测试配置文件"""
    # 读取基础配置
    with open('input/config.toml', 'r', encoding='utf-8') as f:
        config = toml.load(f)
    
    # 修改special_handling参数
    if special_handling_value is None:
        # 确保参数被注释掉或不存在
        if 'special_handling' in config.get('args', {}):
            del config['args']['special_handling']
    else:
        config['args']['special_handling'] = special_handling_value
    
    # 修改输出目录以区分不同测试
    config['output_dir'] = f"./test_output/special_handling_{output_suffix}"
    
    # 修改文件名模式
    config['output_npz_filename_pattern'] = f"PPSD_{output_suffix}_{{datetime}}_{{network}}-{{station}}-{{location}}-{{channel}}.npz"
    
    # 创建临时配置文件
    temp_config_path = f"input/config_special_{output_suffix}.toml"
    with open(temp_config_path, 'w', encoding='utf-8') as f:
        # 添加注释说明
        f.write(f"# 测试special_handling = {special_handling_value}\n")
        f.write(f"# 输出目录: {config['output_dir']}\n\n")
        toml.dump(config, f)
    
    return temp_config_path


def run_ppsd_test(config_path, test_name):
    """运行PPSD测试"""
    print(f"\n=== 测试 {test_name} ===")
    
    try:
        # 创建输出目录
        with open(config_path, 'r', encoding='utf-8') as f:
            config = toml.load(f)
        output_dir = config['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        
        # 运行PPSDProcessor
        processor = PPSDProcessor([config_path])
        print(f"✓ {test_name}: PPSDProcessor初始化成功")
        
        # 检查配置加载
        if processor.configs:
            loaded_config = processor.configs[0]
            args = loaded_config.get('args', {})
            special_handling = args.get('special_handling', None)
            print(f"✓ {test_name}: special_handling = {special_handling}")
            
            # 检查输出文件
            npz_files = list(Path(output_dir).glob('*.npz'))
            print(f"✓ {test_name}: 生成了 {len(npz_files)} 个NPZ文件")
            
            return {
                'success': True,
                'special_handling': special_handling,
                'output_dir': output_dir,
                'npz_count': len(npz_files),
                'npz_files': npz_files
            }
        else:
            print(f"✗ {test_name}: 配置加载失败")
            return {'success': False}
            
    except Exception as e:
        print(f"✗ {test_name}: 测试失败 - {e}")
        return {'success': False, 'error': str(e)}


def analyze_ppsd_differences(results):
    """分析不同special_handling设置的PPSD差异"""
    print(f"\n=== PPSD结果分析 ===")
    
    successful_tests = {name: result for name, result in results.items() if result.get('success')}
    
    if len(successful_tests) < 2:
        print("需要至少2个成功的测试才能进行比较")
        return
    
    print(f"成功的测试: {list(successful_tests.keys())}")
    
    # 比较NPZ文件数量
    print(f"\nNPZ文件数量比较:")
    for name, result in successful_tests.items():
        print(f"  {name}: {result['npz_count']} 个文件")
    
    # 尝试加载和比较第一个NPZ文件的内容
    print(f"\n尝试比较NPZ文件内容:")
    
    npz_data = {}
    for name, result in successful_tests.items():
        if result['npz_files']:
            try:
                # 加载第一个NPZ文件
                npz_file = result['npz_files'][0]
                data = np.load(npz_file)
                
                # 提取关键信息
                npz_data[name] = {
                    'file': npz_file.name,
                    'keys': list(data.keys()),
                    'periods': data.get('periods', None),
                    'psd_values': data.get('psd_values', None)
                }
                
                print(f"  {name}: {npz_file.name}")
                print(f"    数据键: {list(data.keys())}")
                if 'periods' in data:
                    periods = data['periods']
                    print(f"    周期范围: {periods.min():.3f} - {periods.max():.3f} 秒")
                if 'psd_values' in data:
                    psd_values = data['psd_values']
                    print(f"    PSD矩阵形状: {psd_values.shape}")
                    print(f"    PSD值范围: {psd_values.min():.1f} - {psd_values.max():.1f} dB")
                
                data.close()
                
            except Exception as e:
                print(f"  {name}: 读取NPZ文件失败 - {e}")
    
    # 比较不同设置的差异
    if len(npz_data) >= 2:
        print(f"\n差异分析:")
        names = list(npz_data.keys())
        
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                name1, name2 = names[i], names[j]
                data1, data2 = npz_data[name1], npz_data[name2]
                
                print(f"\n{name1} vs {name2}:")
                
                # 比较数据键
                keys1, keys2 = set(data1['keys']), set(data2['keys'])
                if keys1 == keys2:
                    print(f"  ✓ 数据键相同: {keys1}")
                else:
                    print(f"  ⚠ 数据键不同:")
                    print(f"    {name1}: {keys1}")
                    print(f"    {name2}: {keys2}")
                
                # 比较周期范围
                if data1['periods'] is not None and data2['periods'] is not None:
                    periods1, periods2 = data1['periods'], data2['periods']
                    if np.allclose(periods1, periods2):
                        print(f"  ✓ 周期范围相同")
                    else:
                        print(f"  ⚠ 周期范围不同")
                
                # 比较PSD值
                if data1['psd_values'] is not None and data2['psd_values'] is not None:
                    psd1, psd2 = data1['psd_values'], data2['psd_values']
                    if psd1.shape == psd2.shape:
                        print(f"  ✓ PSD矩阵形状相同: {psd1.shape}")
                        
                        # 计算差异统计
                        diff = psd1 - psd2
                        print(f"  PSD差异统计:")
                        print(f"    平均差异: {diff.mean():.3f} dB")
                        print(f"    标准差: {diff.std():.3f} dB")
                        print(f"    最大差异: {diff.max():.3f} dB")
                        print(f"    最小差异: {diff.min():.3f} dB")
                    else:
                        print(f"  ⚠ PSD矩阵形状不同: {psd1.shape} vs {psd2.shape}")


def cleanup_test_files():
    """清理测试文件"""
    print(f"\n=== 清理测试文件 ===")
    
    # 删除临时配置文件
    config_files = list(Path('input').glob('config_special_*.toml'))
    for config_file in config_files:
        try:
            config_file.unlink()
            print(f"✓ 删除配置文件: {config_file}")
        except Exception as e:
            print(f"✗ 删除配置文件失败 {config_file}: {e}")
    
    # 删除测试输出目录
    test_output_dir = Path('test_output')
    if test_output_dir.exists():
        try:
            shutil.rmtree(test_output_dir)
            print(f"✓ 删除测试输出目录: {test_output_dir}")
        except Exception as e:
            print(f"✗ 删除测试输出目录失败: {e}")


def main():
    """主测试函数"""
    print("special_handling参数测试")
    print("=" * 50)
    
    # 定义测试用例
    test_cases = [
        (None, "default", "默认设置 (标准仪器校正+微分)"),
        ("ringlaser", "ringlaser", "环形激光器 (仅除以sensitivity)"),
        ("hydrophone", "hydrophone", "水听器 (仪器校正但不微分)")
    ]
    
    results = {}
    
    # 运行所有测试
    for special_handling, suffix, description in test_cases:
        print(f"\n准备测试: {description}")
        
        try:
            # 创建测试配置
            config_path = create_test_config(special_handling, suffix)
            print(f"✓ 创建配置文件: {config_path}")
            
            # 运行测试
            result = run_ppsd_test(config_path, description)
            results[description] = result
            
        except Exception as e:
            print(f"✗ 测试准备失败: {e}")
            results[description] = {'success': False, 'error': str(e)}
    
    # 分析结果
    analyze_ppsd_differences(results)
    
    # 生成测试报告
    print(f"\n" + "=" * 50)
    print("special_handling参数测试报告")
    print("=" * 50)
    
    for description, result in results.items():
        if result.get('success'):
            print(f"✓ {description}")
            print(f"  special_handling: {result.get('special_handling')}")
            print(f"  NPZ文件数: {result.get('npz_count', 0)}")
            print(f"  输出目录: {result.get('output_dir', 'N/A')}")
        else:
            print(f"✗ {description}")
            if 'error' in result:
                print(f"  错误: {result['error']}")
    
    # 询问是否清理测试文件
    print(f"\n测试完成！")
    response = input("是否清理测试文件? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        cleanup_test_files()
    else:
        print("保留测试文件，可手动检查结果")


if __name__ == '__main__':
    main() 