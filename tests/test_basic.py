#!/usr/bin/env python3
"""
:copyright:
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""

# -*- coding: utf-8 -*-
"""
基本功能测试脚本

用于验证cp_psd.py的基本功能是否正常工作。
"""

import os
import sys
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import toml
    print("✓ 所有必需的库都已正确安装")
except ImportError as e:
    print(f"✗ 缺少必需的库: {e}")
    print("请运行: pip install -r requirements.txt")
    sys.exit(1)

def test_config_loading():
    """测试配置文件加载"""
    print("\n=== 测试配置文件加载 ===")
    
    # 测试计算配置文件
    if os.path.exists('config.toml'):
        try:
            with open('config.toml', 'r', encoding='utf-8') as f:
                config = toml.load(f)
            print("✓ config.toml 加载成功")
            print(f"  - 日志级别: {config.get('log_level', 'INFO')}")
            print(f"  - 输出目录: {config.get('output_dir', './ppsd_results')}")
        except Exception as e:
            print(f"✗ config.toml 加载失败: {e}")
    else:
        print("✗ config.toml 文件不存在")
    
    # 测试绘图配置文件
    if os.path.exists('config_plot.toml'):
        try:
            with open('config_plot.toml', 'r', encoding='utf-8') as f:
                config = toml.load(f)
            print("✓ config_plot.toml 加载成功")
            plot_type = config.get('args', {}).get('plot_type', [])
            print(f"  - 绘图类型: {plot_type}")
        except Exception as e:
            print(f"✗ config_plot_toml 加载失败: {e}")
    else:
        print("✗ config_plot.toml 文件不存在")

def test_ppsd_processor_import():
    """测试PPSDProcessor类导入"""
    print("\n=== 测试PPSDProcessor类导入 ===")
    
    try:
        from cp_ppsd import PPSDProcessor
        print("✓ PPSDProcessor 类导入成功")
        
        # 测试基本初始化
        temp_config = tempfile.NamedTemporaryFile(
            mode='w', suffix='.toml', delete=False)
        temp_config.write("""
log_level = "INFO"
output_dir = "./test_output"

[args]
ppsd_length = 3600
""")
        temp_config.close()
        
        try:
            PPSDProcessor([temp_config.name])
            print("✓ PPSDProcessor 初始化成功")
        except Exception as e:
            print(f"✗ PPSDProcessor 初始化失败: {e}")
        finally:
            os.unlink(temp_config.name)
            
    except ImportError as e:
        print(f"✗ PPSDProcessor 类导入失败: {e}")

def test_directory_structure():
    """测试目录结构"""
    print("\n=== 测试目录结构 ===")
    
    required_files = [
        'cp_ppsd/cp_psd.py',
        'input/config.toml', 
        'input/config_plot.toml',
        'requirements.txt',
        'README.md',
        'run_cp_ppsd.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} 存在")
        else:
            print(f"✗ {file} 不存在")
    
    # 检查知识库目录
    if os.path.exists('cursor_project_rules'):
        print("✓ cursor_project_rules 目录存在")
        kb_files = os.listdir('cursor_project_rules')
        print(f"  - 包含 {len(kb_files)} 个文件")
    else:
        print("✗ cursor_project_rules 目录不存在")

def test_help_output():
    """测试帮助输出"""
    print("\n=== 测试帮助输出 ===")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, 'run_cp_ppsd.py', '--help'], 
            capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ 帮助信息输出正常")
            print("  前几行输出:")
            lines = result.stdout.split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"    {line}")
        else:
            print(f"✗ 帮助信息输出异常: {result.stderr}")
    except Exception as e:
        print(f"✗ 无法测试帮助输出: {e}")

def main():
    """主测试函数"""
    print("PPSD 批量处理与可视化工具 - 基本功能测试")
    print("=" * 50)
    
    test_config_loading()
    test_ppsd_processor_import()
    test_directory_structure()
    test_help_output()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n如果所有测试都通过，您可以开始使用该工具。")
    print("如果有测试失败，请检查相应的问题并修复。")
    print("\n使用示例:")
    print("  python run_cp_ppsd.py input/config.toml")
    print("  python run_cp_ppsd.py input/config_plot.toml")
    print("  python run_cp_ppsd.py input/config.toml input/config_plot.toml")

if __name__ == '__main__':
    main() 