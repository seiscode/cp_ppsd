#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试special_handling参数的效果比较

根据ObsPy PPSD文档，special_handling参数支持以下值：
- None (默认): 标准地震仪处理（仪器校正+微分）
- "ringlaser": 不进行仪器校正，仅除以sensitivity
- "hydrophone": 仪器校正但不微分

测试结果将保存到不同的输出目录中进行比较。
"""

import os
import sys
import toml
import shutil
import subprocess
from pathlib import Path

def backup_config():
    """备份原始配置文件"""
    if os.path.exists('input/config.toml'):
        shutil.copy2('input/config.toml', 'input/config_backup.toml')
        print("✓ 备份原始配置文件")
        return True
    return False

def restore_config():
    """恢复原始配置文件"""
    if os.path.exists('input/config_backup.toml'):
        shutil.copy2('input/config_backup.toml', 'input/config.toml')
        print("✓ 恢复原始配置文件")
        return True
    return False

def create_test_config(special_handling_value, output_suffix):
    """创建测试配置文件"""
    # 读取基础配置
    with open('input/config.toml', 'r', encoding='utf-8') as f:
        config = toml.load(f)
    
    # 修改special_handling参数
    if special_handling_value is None:
        # 注释掉special_handling行
        config['args'].pop('special_handling', None)
    else:
        config['args']['special_handling'] = special_handling_value
    
    # 修改输出目录
    config['output_dir'] = f"./test_output/special_{output_suffix}"
    
    # 保存测试配置
    test_config_path = f'input/config_test_{output_suffix}.toml'
    with open(test_config_path, 'w', encoding='utf-8') as f:
        toml.dump(config, f)
    
    return test_config_path

def run_ppsd_calculation(config_path, test_name):
    """运行PPSD计算"""
    print(f"\n{'='*50}")
    print(f"测试: {test_name}")
    print(f"配置文件: {config_path}")
    print(f"{'='*50}")
    
    try:
        # 运行计算
        result = subprocess.run(
            ['conda', 'run', '-n', 'seis', 'python', 'run_cp_ppsd.py', config_path],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"✓ {test_name} 运行成功")
            return True
        else:
            print(f"✗ {test_name} 运行失败")
            print(f"错误输出: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ {test_name} 运行超时")
        return False
    except Exception as e:
        print(f"✗ {test_name} 运行异常: {e}")
        return False

def analyze_results():
    """分析测试结果"""
    print(f"\n{'='*50}")
    print("测试结果分析")
    print(f"{'='*50}")
    
    test_dirs = [
        ('test_output/special_default', 'None (默认模式)'),
        ('test_output/special_ringlaser', 'ringlaser模式'),
        ('test_output/special_hydrophone', 'hydrophone模式')
    ]
    
    for test_dir, test_name in test_dirs:
        if os.path.exists(test_dir):
            npz_files = list(Path(test_dir).glob('*.npz'))
            total_size = sum(f.stat().st_size for f in npz_files)
            print(f"\n{test_name}:")
            print(f"  - NPZ文件数量: {len(npz_files)}")
            print(f"  - 总大小: {total_size/1024/1024:.2f} MB")
            print(f"  - 输出目录: {test_dir}")
            
            if npz_files:
                # 显示前几个文件
                print(f"  - 示例文件:")
                for f in npz_files[:3]:
                    print(f"    * {f.name} ({f.stat().st_size/1024:.1f} KB)")
        else:
            print(f"\n{test_name}: 未找到输出目录")

def main():
    """主函数"""
    print("special_handling参数效果比较测试")
    print("="*50)
    
    # 备份原始配置
    if not backup_config():
        print("✗ 无法备份配置文件")
        return
    
    try:
        # 测试配置列表
        test_configs = [
            (None, 'default', 'None (默认模式)'),
            ('ringlaser', 'ringlaser', 'ringlaser模式'),
            ('hydrophone', 'hydrophone', 'hydrophone模式')
        ]
        
        results = {}
        
        # 运行每个测试
        for special_handling, suffix, description in test_configs:
            # 创建测试配置
            config_path = create_test_config(special_handling, suffix)
            
            # 创建输出目录
            output_dir = f"./test_output/special_{suffix}"
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # 运行测试
            success = run_ppsd_calculation(config_path, description)
            results[description] = success
            
            # 清理测试配置文件
            if os.path.exists(config_path):
                os.remove(config_path)
        
        # 分析结果
        analyze_results()
        
        # 总结
        print(f"\n{'='*50}")
        print("测试总结")
        print(f"{'='*50}")
        for test_name, success in results.items():
            status = "✓ 成功" if success else "✗ 失败"
            print(f"{test_name}: {status}")
        
        print(f"\n根据ObsPy文档，special_handling参数的作用：")
        print(f"- None (默认): 标准地震仪处理（仪器校正+微分）")
        print(f"- ringlaser: 不进行仪器校正，仅除以sensitivity")
        print(f"- hydrophone: 仪器校正但不微分")
        
    finally:
        # 恢复原始配置
        restore_config()

if __name__ == "__main__":
    main() 