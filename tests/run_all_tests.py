#!/usr/bin/env python3
"""
:copyright:
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)

PPSD测试套件运行器

此脚本用于批量运行所有测试程序，并生成测试报告。

使用方法:
    python tests/run_all_tests.py [--verbose] [--test-pattern PATTERN]

参数:
    --verbose: 显示详细输出
    --test-pattern: 指定测试文件模式（默认: test_*.py）
"""

import os
import sys
import glob
import subprocess
import argparse
import time
from pathlib import Path


def run_test(test_file, verbose=False):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行测试: {test_file}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        if verbose:
            result = subprocess.run([sys.executable, test_file], 
                                    capture_output=False, 
                                    text=True)
        else:
            result = subprocess.run([sys.executable, test_file], 
                                    capture_output=True, 
                                    text=True)
            
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"[PASS] 测试通过 ({duration:.2f}s)")
            if not verbose and result.stdout:
                print("输出摘要:")
                print(result.stdout[-500:])  # 显示最后500字符
        else:
            print(f"[FAIL] 测试失败 ({duration:.2f}s)")
            if result.stderr:
                print("错误信息:")
                print(result.stderr)
            if result.stdout:
                print("输出信息:")
                print(result.stdout)
                
        return result.returncode == 0, duration
        
    except Exception as e:
        print(f"[ERROR] 运行测试时发生异常: {e}")
        return False, 0


def main():
    parser = argparse.ArgumentParser(description='PPSD测试套件运行器')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细输出')
    parser.add_argument('--test-pattern', '-p', default='test_*.py',
                        help='测试文件模式（默认: test_*.py）')
    parser.add_argument('--tests-dir', '-d', default='tests',
                        help='测试目录（默认: tests）')
    
    args = parser.parse_args()
    
    # 确保在项目根目录运行
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    # 查找测试文件
    test_pattern = os.path.join(args.tests_dir, args.test_pattern)
    test_files = glob.glob(test_pattern)
    test_files.sort()
    
    if not test_files:
        print(f"[ERROR] 未找到匹配模式 '{test_pattern}' 的测试文件")
        return 1
    
    print("开始运行测试套件")
    print(f"测试目录: {args.tests_dir}")
    print(f"测试模式: {args.test_pattern}")
    print(f"找到 {len(test_files)} 个测试文件")
    
    # 运行测试
    results = []
    total_duration = 0
    
    for test_file in test_files:
        success, duration = run_test(test_file, args.verbose)
        results.append((test_file, success, duration))
        total_duration += duration
    
    # 生成测试报告
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    
    print(f"总测试数: {len(results)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总耗时: {total_duration:.2f}s")
    print(f"成功率: {passed/len(results)*100:.1f}%")
    
    print("\n详细结果:")
    for test_file, success, duration in results:
        status = "[PASS]" if success else "[FAIL]"
        basename = os.path.basename(test_file)
        print(f"  {basename:30} {status:8} ({duration:.2f}s)")
    
    # 失败的测试
    if failed > 0:
        print("\n失败的测试:")
        for test_file, success, duration in results:
            if not success:
                print(f"  - {test_file}")
    
    print(f"\n{'='*60}")
    if failed == 0:
        print("所有测试都通过了!")
        return 0
    else:
        print(f"有 {failed} 个测试失败，请检查上述错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 