#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试脚本：config_plot.toml中standard组参数功能验证
"""

import os
import shutil
import subprocess
import time
from pathlib import Path

class StandardParamsTest:
    def __init__(self):
        self.original_config = "input/config_plot.toml"
        self.backup_config = "input/config_plot_backup.toml"
        self.test_results = []
        
    def run_ppsd_and_check(self, test_name, config_modifications=None):
        """运行PPSD绘图并检查结果"""
        print(f"\n🧪 测试: {test_name}")
        
        # 清空plots目录
        os.system("rm -f output/plots/*.png")
        
        # 修改配置文件（如果有修改）
        if config_modifications:
            self.modify_config(config_modifications)
        
        # 运行绘图程序
        start_time = time.time()
        try:
            result = subprocess.run([
                "bash", "-c", 
                "source ~/miniconda3/etc/profile.d/conda.sh && conda activate seis && python run_cp_ppsd.py input/config_plot.toml"
            ], capture_output=True, text=True, timeout=60)
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                # 检查生成的文件
                plot_files = list(Path("output/plots").glob("*.png"))
                file_count = len(plot_files)
                
                if file_count > 0:
                    # 获取文件大小信息
                    file_sizes = [f.stat().st_size for f in plot_files]
                    avg_size = sum(file_sizes) / len(file_sizes) if file_sizes else 0
                    
                    result_info = {
                        'test_name': test_name,
                        'status': 'SUCCESS',
                        'file_count': file_count,
                        'avg_file_size': f"{avg_size/1024:.1f} KB",
                        'execution_time': f"{execution_time:.2f}s",
                        'modifications': config_modifications or "None",
                        'error': None
                    }
                    print(f"✅ 成功: 生成 {file_count} 个文件, 平均大小 {avg_size/1024:.1f} KB")
                else:
                    result_info = {
                        'test_name': test_name,
                        'status': 'FAILED',
                        'file_count': 0,
                        'avg_file_size': "0 KB",
                        'execution_time': f"{execution_time:.2f}s",
                        'modifications': config_modifications or "None",
                        'error': "No output files generated"
                    }
                    print(f"❌ 失败: 未生成输出文件")
            else:
                result_info = {
                    'test_name': test_name,
                    'status': 'ERROR',
                    'file_count': 0,
                    'avg_file_size': "0 KB", 
                    'execution_time': f"{execution_time:.2f}s",
                    'modifications': config_modifications or "None",
                    'error': result.stderr[-200:] if result.stderr else "Unknown error"
                }
                print(f"❌ 错误: {result.stderr[-100:] if result.stderr else 'Unknown error'}")
                
        except subprocess.TimeoutExpired:
            result_info = {
                'test_name': test_name,
                'status': 'TIMEOUT',
                'file_count': 0,
                'avg_file_size': "0 KB",
                'execution_time': ">60s",
                'modifications': config_modifications or "None",
                'error': "Process timeout after 60 seconds"
            }
            print(f"⏰ 超时: 进程执行超过60秒")
        
        self.test_results.append(result_info)
        
        # 恢复原配置
        if config_modifications:
            shutil.copy2(self.backup_config, self.original_config)
    
    def modify_config(self, modifications):
        """修改配置文件"""
        with open(self.original_config, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 应用修改
        for old_value, new_value in modifications.items():
            content = content.replace(old_value, new_value)
        
        with open(self.original_config, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始自动化参数测试")
        print("=" * 60)
        
        # 测试1: 基线测试（当前配置）
        self.run_ppsd_and_check("基线测试 - 当前配置")
        
        # 测试2: 显示百分位数线
        self.run_ppsd_and_check(
            "百分位数线显示测试",
            {"show_percentiles = false": "show_percentiles = true"}
        )
        
        # 测试3: 隐藏皮特森曲线
        self.run_ppsd_and_check(
            "隐藏皮特森曲线测试", 
            {"show_noise_models = true": "show_noise_models = false"}
        )
        
        # 测试4: 显示数据覆盖度
        self.run_ppsd_and_check(
            "数据覆盖度显示测试",
            {"show_coverage = false": "show_coverage = true"}
        )
        
        # 测试5: 隐藏众数线
        self.run_ppsd_and_check(
            "隐藏众数线测试",
            {"show_mode = true": "show_mode = false"}
        )
        
        # 测试6: 显示均值线
        self.run_ppsd_and_check(
            "均值线显示测试",
            {"show_mean = false": "show_mean = true"}
        )
        
        # 测试7: 频率轴显示
        self.run_ppsd_and_check(
            "频率轴显示测试",
            {"xaxis_frequency = false": "xaxis_frequency = true"}
        )
        
        # 测试8: 累积直方图
        self.run_ppsd_and_check(
            "累积直方图测试",
            {"cumulative_plot = false": "cumulative_plot = true"}
        )
        
        # 测试9: 不同配色方案
        self.run_ppsd_and_check(
            "配色方案测试 - viridis",
            {'standard_cmap = "hot_r_custom"': 'standard_cmap = "viridis_custom"'}
        )
        
        # 测试10: 调整周期范围
        self.run_ppsd_and_check(
            "周期范围调整测试",
            {"period_lim = [0.01, 50.0]": "period_lim = [0.1, 10.0]"}
        )
        
        # 测试11: 皮特森曲线样式测试
        self.run_ppsd_and_check(
            "皮特森曲线样式测试",
            {
                'nlnm_color = "lightgray"': 'nlnm_color = "black"',
                'nhnm_color = "lightgray"': 'nhnm_color = "red"',
                'linewidth = 1.0': 'linewidth = 2.0'
            }
        )
        
        # 测试12: 众数线样式测试
        self.run_ppsd_and_check(
            "众数线样式测试",
            {
                'color = "orange"': 'color = "red"',
                'linewidth = 1.0': 'linewidth = 3.0',
                'linestyle = "-"': 'linestyle = "--"'
            }
        )
        
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        
        success_count = sum(1 for r in self.test_results if r['status'] == 'SUCCESS')
        total_count = len(self.test_results)
        
        print(f"总测试数: {total_count}")
        print(f"成功数: {success_count}")
        print(f"失败数: {total_count - success_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%")
        print()
        
        # 详细结果
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
            print(f"{status_icon} {result['test_name']}")
            print(f"   状态: {result['status']}")
            print(f"   文件数: {result['file_count']}")
            print(f"   执行时间: {result['execution_time']}")
            if result['error']:
                print(f"   错误: {result['error']}")
            print()
        
        # 保存详细报告
        with open("standard_params_test_report.txt", "w", encoding="utf-8") as f:
            f.write("PPSD Standard参数测试报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总测试数: {total_count}\n")
            f.write(f"成功数: {success_count}\n")
            f.write(f"成功率: {success_count/total_count*100:.1f}%\n\n")
            
            for result in self.test_results:
                f.write(f"测试: {result['test_name']}\n")
                f.write(f"状态: {result['status']}\n")
                f.write(f"文件数: {result['file_count']}\n")
                f.write(f"平均文件大小: {result['avg_file_size']}\n")
                f.write(f"执行时间: {result['execution_time']}\n")
                f.write(f"修改内容: {result['modifications']}\n")
                if result['error']:
                    f.write(f"错误信息: {result['error']}\n")
                f.write("-" * 30 + "\n\n")
        
        print(f"📄 详细报告已保存: standard_params_test_report.txt")

if __name__ == "__main__":
    tester = StandardParamsTest()
    tester.run_all_tests()
    tester.generate_report() 