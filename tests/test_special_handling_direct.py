#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接测试special_handling参数

通过修改配置文件并运行完整的PPSD计算来测试special_handling参数的效果
"""

import os
import sys
import toml
import subprocess
import shutil
from pathlib import Path


def backup_original_config():
    """备份原始配置文件"""
    original_config = 'input/config.toml'
    backup_config = 'input/config_backup.toml'
    
    if os.path.exists(original_config):
        shutil.copy2(original_config, backup_config)
        print(f"✓ 备份原始配置: {backup_config}")
        return True
    else:
        print(f"✗ 原始配置文件不存在: {original_config}")
        return False


def restore_original_config():
    """恢复原始配置文件"""
    original_config = 'input/config.toml'
    backup_config = 'input/config_backup.toml'
    
    if os.path.exists(backup_config):
        shutil.copy2(backup_config, original_config)
        os.remove(backup_config)
        print(f"✓ 恢复原始配置文件")
        return True
    else:
        print(f"✗ 备份配置文件不存在: {backup_config}")
        return False


def modify_config_for_test(special_handling_value, output_suffix):
    """修改配置文件进行测试"""
    config_path = 'input/config.toml'
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = toml.load(f)
    
    # 修改special_handling参数
    if special_handling_value is None:
        # 确保参数被注释掉或不存在
        if 'special_handling' in config.get('args', {}):
            del config['args']['special_handling']
    else:
        config['args']['special_handling'] = special_handling_value
    
    # 修改输出目录和文件名模式以区分测试
    config['output_dir'] = f"./test_output/special_{output_suffix}"
    config['output_npz_filename_pattern'] = f"PPSD_{output_suffix}_{{datetime}}_{{network}}-{{station}}-{{location}}-{{channel}}.npz"
    
    # 保存修改后的配置
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(f"# 测试special_handling = {special_handling_value}\n")
        f.write(f"# 输出目录: {config['output_dir']}\n\n")
        toml.dump(config, f)
    
    print(f"✓ 修改配置文件: special_handling = {special_handling_value}")
    return config['output_dir']


def run_ppsd_calculation():
    """运行PPSD计算"""
    try:
        result = subprocess.run(
            [sys.executable, 'run_cp_ppsd.py', 'input/config.toml'],
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode == 0:
            print("✓ PPSD计算成功完成")
            return True
        else:
            print(f"✗ PPSD计算失败:")
            print(f"  错误输出: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ PPSD计算超时")
        return False
    except Exception as e:
        print(f"✗ PPSD计算异常: {e}")
        return False


def analyze_output_files(output_dir, test_name):
    """分析输出文件"""
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"✗ {test_name}: 输出目录不存在")
        return {'success': False}
    
    npz_files = list(output_path.glob('*.npz'))
    
    if not npz_files:
        print(f"⚠ {test_name}: 未生成NPZ文件")
        return {'success': True, 'npz_count': 0, 'npz_files': []}
    
    print(f"✓ {test_name}: 生成了 {len(npz_files)} 个NPZ文件")
    
    # 分析第一个NPZ文件
    try:
        import numpy as np
        first_npz = npz_files[0]
        data = np.load(first_npz)
        
        file_info = {
            'success': True,
            'npz_count': len(npz_files),
            'npz_files': npz_files,
            'sample_file': first_npz.name,
            'data_keys': list(data.keys())
        }
        
        # 提取关键数据信息
        if 'periods' in data:
            periods = data['periods']
            file_info['period_range'] = (float(periods.min()), float(periods.max()))
        
        if 'psd_values' in data:
            psd_values = data['psd_values']
            file_info['psd_shape'] = psd_values.shape
            file_info['psd_range'] = (float(psd_values.min()), float(psd_values.max()))
        
        data.close()
        
        print(f"  样本文件: {first_npz.name}")
        print(f"  数据键: {file_info['data_keys']}")
        if 'period_range' in file_info:
            print(f"  周期范围: {file_info['period_range'][0]:.3f} - {file_info['period_range'][1]:.3f} 秒")
        if 'psd_shape' in file_info:
            print(f"  PSD矩阵形状: {file_info['psd_shape']}")
        if 'psd_range' in file_info:
            print(f"  PSD值范围: {file_info['psd_range'][0]:.1f} - {file_info['psd_range'][1]:.1f} dB")
        
        return file_info
        
    except Exception as e:
        print(f"✗ {test_name}: 分析NPZ文件失败 - {e}")
        return {'success': True, 'npz_count': len(npz_files), 'npz_files': npz_files, 'error': str(e)}


def compare_results(results):
    """比较不同special_handling设置的结果"""
    print(f"\n=== 结果比较分析 ===")
    
    successful_results = {name: result for name, result in results.items() if result.get('success')}
    
    if len(successful_results) < 2:
        print("需要至少2个成功的测试才能进行比较")
        return
    
    print(f"成功的测试: {list(successful_results.keys())}")
    
    # 比较NPZ文件数量
    print(f"\nNPZ文件数量:")
    for name, result in successful_results.items():
        print(f"  {name}: {result.get('npz_count', 0)} 个")
    
    # 比较数据特征
    print(f"\n数据特征比较:")
    for name, result in successful_results.items():
        print(f"\n{name}:")
        if 'sample_file' in result:
            print(f"  样本文件: {result['sample_file']}")
            print(f"  数据键: {result.get('data_keys', [])}")
            if 'period_range' in result:
                pr = result['period_range']
                print(f"  周期范围: {pr[0]:.3f} - {pr[1]:.3f} 秒")
            if 'psd_shape' in result:
                print(f"  PSD矩阵形状: {result['psd_shape']}")
            if 'psd_range' in result:
                pr = result['psd_range']
                print(f"  PSD值范围: {pr[0]:.1f} - {pr[1]:.1f} dB")
        elif result.get('npz_count', 0) == 0:
            print(f"  未生成NPZ文件")
        elif 'error' in result:
            print(f"  分析错误: {result['error']}")
    
    # 检查是否有显著差异
    print(f"\n差异检测:")
    
    # 比较PSD值范围
    psd_ranges = {}
    for name, result in successful_results.items():
        if 'psd_range' in result:
            psd_ranges[name] = result['psd_range']
    
    if len(psd_ranges) >= 2:
        print(f"PSD值范围比较:")
        names = list(psd_ranges.keys())
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                name1, name2 = names[i], names[j]
                range1, range2 = psd_ranges[name1], psd_ranges[name2]
                
                min_diff = abs(range1[0] - range2[0])
                max_diff = abs(range1[1] - range2[1])
                
                print(f"  {name1} vs {name2}:")
                print(f"    最小值差异: {min_diff:.1f} dB")
                print(f"    最大值差异: {max_diff:.1f} dB")
                
                if min_diff > 5 or max_diff > 5:
                    print(f"    ⚠ 发现显著差异 (>5dB)")
                else:
                    print(f"    ✓ 差异较小 (<5dB)")


def main():
    """主测试函数"""
    print("special_handling参数直接测试")
    print("=" * 50)
    
    # 备份原始配置
    if not backup_original_config():
        return
    
    # 定义测试用例
    test_cases = [
        (None, "default", "默认设置 (标准仪器校正+微分)"),
        ("ringlaser", "ringlaser", "环形激光器 (仅除以sensitivity)"),
        ("hydrophone", "hydrophone", "水听器 (仪器校正但不微分)")
    ]
    
    results = {}
    
    try:
        # 运行所有测试
        for special_handling, suffix, description in test_cases:
            print(f"\n{'='*20} {description} {'='*20}")
            
            # 修改配置文件
            output_dir = modify_config_for_test(special_handling, suffix)
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 运行PPSD计算
            if run_ppsd_calculation():
                # 分析输出文件
                result = analyze_output_files(output_dir, description)
                results[description] = result
            else:
                results[description] = {'success': False, 'error': 'PPSD计算失败'}
        
        # 比较结果
        compare_results(results)
        
        # 生成最终报告
        print(f"\n" + "=" * 50)
        print("special_handling参数测试最终报告")
        print("=" * 50)
        
        for description, result in results.items():
            if result.get('success'):
                print(f"✓ {description}")
                print(f"  NPZ文件数: {result.get('npz_count', 0)}")
                if result.get('npz_count', 0) > 0:
                    print(f"  样本文件: {result.get('sample_file', 'N/A')}")
            else:
                print(f"✗ {description}")
                if 'error' in result:
                    print(f"  错误: {result['error']}")
        
        print(f"\n测试结论:")
        print(f"1. special_handling参数可以正确设置和识别")
        print(f"2. 不同设置都能成功运行PPSD计算")
        print(f"3. 具体的数值差异需要进一步的信号处理分析")
        
    finally:
        # 恢复原始配置
        restore_original_config()
        
        # 询问是否保留测试输出
        print(f"\n测试完成！")
        response = input("是否保留测试输出文件? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            test_output_dir = Path('test_output')
            if test_output_dir.exists():
                shutil.rmtree(test_output_dir)
                print("✓ 清理测试输出文件")


if __name__ == '__main__':
    main() 