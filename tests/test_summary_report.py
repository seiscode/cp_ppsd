#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PPSD项目完整测试总结报告

汇总所有测试结果，提供项目状态概览。
"""

import os
import sys
import subprocess
import toml
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_project_structure():
    """检查项目结构完整性"""
    print("=== 项目结构检查 ===")
    
    required_files = [
        'run_cp_ppsd.py',
        'cp_ppsd/cp_psd.py',
        'input/config.toml',
        'input/config_plot.toml',
        'input/config_optimized.toml',
        'requirements.txt',
        'README.md',
        'test_basic.py',
        'test_config_params.py',
        'config_optimization_report.py'
    ]
    
    required_dirs = [
        'cp_ppsd',
        'input',
        'output/npz',
        'output/plots',
        'logs',
        'data',
        'cursor_project_rules'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            missing_files.append(file_path)
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/")
            missing_dirs.append(dir_path)
    
    return len(missing_files) == 0 and len(missing_dirs) == 0


def check_dependencies():
    """检查依赖库"""
    print("\n=== 依赖库检查 ===")
    
    required_packages = [
        'obspy', 'numpy', 'matplotlib', 'toml', 'tqdm'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0


def check_data_files():
    """检查数据文件"""
    print("\n=== 数据文件检查 ===")
    
    data_dir = Path('./data/')
    mseed_files = list(data_dir.rglob('*.mseed'))
    
    inventory_file = Path('./input/BJ.XML')
    
    print(f"✓ 数据文件: {len(mseed_files)} 个")
    
    if inventory_file.exists():
        file_size = inventory_file.stat().st_size
        print(f"✓ 仪器响应文件: {inventory_file} ({file_size} bytes)")
    else:
        print(f"✗ 仪器响应文件: {inventory_file}")
        return False
    
    return len(mseed_files) > 0


def check_configuration_files():
    """检查配置文件"""
    print("\n=== 配置文件检查 ===")
    
    configs = [
        'input/config.toml',
        'input/config_plot.toml',
        'input/config_optimized.toml'
    ]
    
    all_valid = True
    
    for config_path in configs:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = toml.load(f)
                
                # 检查关键参数
                if 'args' in config:
                    args = config['args']
                    ppsd_length = args.get('ppsd_length', 0)
                    period_limits = args.get('period_limits', [])
                    
                    print(f"✓ {config_path}")
                    print(f"  - PPSD长度: {ppsd_length}s")
                    print(f"  - 周期范围: {period_limits}")
                else:
                    print(f"⚠ {config_path} (缺少[args]部分)")
                    
            except Exception as e:
                print(f"✗ {config_path} (解析失败: {e})")
                all_valid = False
        else:
            print(f"✗ {config_path} (文件不存在)")
            all_valid = False
    
    return all_valid


def check_output_files():
    """检查输出文件"""
    print("\n=== 输出文件检查 ===")
    
    npz_dir = Path('./output/npz/')
    plots_dir = Path('./output/plots/')
    logs_dir = Path('./logs/')
    
    npz_files = list(npz_dir.glob('*.npz')) if npz_dir.exists() else []
    plot_files = list(plots_dir.glob('*.png')) if plots_dir.exists() else []
    log_files = list(logs_dir.glob('*.log')) if logs_dir.exists() else []
    
    print(f"✓ NPZ文件: {len(npz_files)} 个")
    print(f"✓ 图像文件: {len(plot_files)} 个")
    print(f"✓ 日志文件: {len(log_files)} 个")
    
    # 检查最新文件
    if npz_files:
        latest_npz = max(npz_files, key=lambda x: x.stat().st_mtime)
        print(f"  最新NPZ: {latest_npz.name}")
    
    if plot_files:
        latest_plot = max(plot_files, key=lambda x: x.stat().st_mtime)
        print(f"  最新图像: {latest_plot.name}")
    
    return len(npz_files) > 0


def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 基本功能测试 ===")
    
    try:
        # 测试帮助信息
        result = subprocess.run(
            [sys.executable, 'run_cp_ppsd.py', '--help'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            print("✓ 帮助信息输出正常")
        else:
            print(f"✗ 帮助信息输出异常: {result.stderr}")
            return False
        
        # 测试PPSDProcessor导入
        try:
            from cp_ppsd import PPSDProcessor
            print("✓ PPSDProcessor类导入成功")
        except ImportError as e:
            print(f"✗ PPSDProcessor类导入失败: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False


def test_configuration_optimization():
    """测试配置优化功能"""
    print("\n=== 配置优化测试 ===")
    
    try:
        # 检查优化配置是否存在
        optimized_config = 'input/config_optimized.toml'
        if os.path.exists(optimized_config):
            print("✓ 优化配置文件存在")
            
            # 比较原始配置和优化配置
            with open('input/config.toml', 'r', encoding='utf-8') as f:
                original = toml.load(f)
            
            with open(optimized_config, 'r', encoding='utf-8') as f:
                optimized = toml.load(f)
            
            orig_period = original.get('args', {}).get('period_limits', [])
            opt_period = optimized.get('args', {}).get('period_limits', [])
            
            if orig_period != opt_period:
                print(f"✓ 周期范围已优化: {orig_period} → {opt_period}")
            else:
                print("⚠ 周期范围未发生变化")
            
            return True
        else:
            print("✗ 优化配置文件不存在")
            return False
            
    except Exception as e:
        print(f"✗ 配置优化测试失败: {e}")
        return False


def generate_performance_metrics():
    """生成性能指标"""
    print("\n=== 性能指标 ===")
    
    try:
        # 统计文件数量
        npz_files = list(Path('./output/npz/').glob('*.npz'))
        plot_files = list(Path('./output/plots/').glob('*.png'))
        
        # 计算文件大小
        total_npz_size = sum(f.stat().st_size for f in npz_files) / 1024 / 1024  # MB
        total_plot_size = sum(f.stat().st_size for f in plot_files) / 1024 / 1024  # MB
        
        print(f"NPZ文件统计:")
        print(f"  - 数量: {len(npz_files)} 个")
        print(f"  - 总大小: {total_npz_size:.1f} MB")
        print(f"  - 平均大小: {total_npz_size/len(npz_files):.2f} MB" if npz_files else "  - 平均大小: 0 MB")
        
        print(f"\n图像文件统计:")
        print(f"  - 数量: {len(plot_files)} 个")
        print(f"  - 总大小: {total_plot_size:.1f} MB")
        print(f"  - 平均大小: {total_plot_size/len(plot_files):.2f} MB" if plot_files else "  - 平均大小: 0 MB")
        
        # 检查处理的台站数
        stations = set()
        for npz_file in npz_files:
            # 从文件名提取台站信息
            parts = npz_file.stem.split('_')
            if len(parts) >= 3:
                station_info = parts[2]  # 格式: BJ-JIZ-00-SHZ
                stations.add(station_info)
        
        print(f"\n处理统计:")
        print(f"  - 台站数: {len(stations)} 个")
        print(f"  - 台站列表: {', '.join(sorted(stations))}")
        
        return True
        
    except Exception as e:
        print(f"✗ 性能指标生成失败: {e}")
        return False


def check_knowledge_base():
    """检查知识库完整性"""
    print("\n=== 知识库检查 ===")
    
    kb_dir = Path('./cursor_project_rules/')
    if not kb_dir.exists():
        print("✗ 知识库目录不存在")
        return False
    
    kb_files = list(kb_dir.glob('*.md')) + list(kb_dir.glob('*.mdc'))
    
    important_files = [
        '00_PROJECT_OVERVIEW.md',
        'implementation-plan.mdc',
        'README.md'
    ]
    
    all_present = True
    for file_name in important_files:
        file_path = kb_dir / file_name
        if file_path.exists():
            print(f"✓ {file_name}")
        else:
            print(f"✗ {file_name}")
            all_present = False
    
    print(f"\n知识库统计:")
    print(f"  - 总文件数: {len(kb_files)} 个")
    print(f"  - 核心文件: {len([f for f in important_files if (kb_dir/f).exists()])} / {len(important_files)} 个")
    
    return all_present


def main():
    """主函数"""
    print("PPSD项目完整测试总结报告")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 执行所有测试
    tests = [
        ("项目结构", check_project_structure),
        ("依赖库", check_dependencies),
        ("数据文件", check_data_files),
        ("配置文件", check_configuration_files),
        ("输出文件", check_output_files),
        ("基本功能", test_basic_functionality),
        ("配置优化", test_configuration_optimization),
        ("知识库", check_knowledge_base)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name}测试异常: {e}")
            results[test_name] = False
    
    # 生成性能指标
    generate_performance_metrics()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:12} : {status}")
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！项目状态良好。")
        print("\n项目已准备就绪，可以正常使用:")
        print("  - 计算PPSD: python run_cp_ppsd.py input/config.toml")
        print("  - 生成图像: python run_cp_ppsd.py input/config_plot.toml")
        print("  - 使用优化配置: python run_cp_ppsd.py input/config_optimized.toml")
        print("  - 组合使用: python run_cp_ppsd.py input/config.toml input/config_plot.toml")
    else:
        print("⚠ 部分测试失败，请检查相关问题。")
        failed_tests = [name for name, result in results.items() if not result]
        print(f"失败的测试: {', '.join(failed_tests)}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main() 