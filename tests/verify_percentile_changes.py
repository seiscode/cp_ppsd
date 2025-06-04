#!/usr/bin/env python3
"""
验证百分位数线样式变化的脚本

此脚本通过生成不同样式的PPSD图来验证百分位数线样式功能是否正常工作。
"""

import os
import sys
import shutil
import subprocess
import toml

def create_test_configs():
    """创建测试配置文件"""
    
    # 基础配置
    base_config = {
        'log_level': 'INFO',
        'input_npz_dir': './output/npz/',
        'inventory_path': './input/BJ.XML',
        'output_dir': './output/plots/',
        'args': {
            'plot_type': ['standard'],  # 只生成标准图进行对比
            'npz_merge_strategy': True,
            'show_histogram': True,
            'show_percentiles': True,
            'percentiles': [10, 50, 90],
            'show_noise_models': True,
            'standard_grid': True,
            'period_lim': [0.01, 1000.0],
            'xaxis_frequency': False,
            'cumulative_plot': False,
            'show_coverage': True,
            'standard_cmap': 'hot_r_custom'
        }
    }
    
    # 配置1：默认样式（不包含自定义百分位数线参数）
    config1 = base_config.copy()
    config1['output_filename_pattern'] = "{plot_type}_{datetime}_{network}-{station}-{location}-{channel}_default.png"
    
    # 配置2：浅灰色实线
    config2 = base_config.copy()
    config2['output_filename_pattern'] = "{plot_type}_{datetime}_{network}-{station}-{location}-{channel}_lightgray_solid.png"
    config2['args'].update({
        'percentile_color': 'lightgray',
        'percentile_linewidth': 1.0,
        'percentile_linestyle': '-',
        'percentile_alpha': 0.8
    })
    
    # 配置3：浅灰色超细虚线
    config3 = base_config.copy()
    config3['output_filename_pattern'] = "{plot_type}_{datetime}_{network}-{station}-{location}-{channel}_lightgray_dashed_thin.png"
    config3['args'].update({
        'percentile_color': 'lightgray',
        'percentile_linewidth': 0.4,
        'percentile_linestyle': '--',
        'percentile_alpha': 0.8
    })
    
    # 配置4：钢蓝色虚线
    config4 = base_config.copy()
    config4['output_filename_pattern'] = "{plot_type}_{datetime}_{network}-{station}-{location}-{channel}_steelblue_dashed.png"
    config4['args'].update({
        'percentile_color': 'steelblue',
        'percentile_linewidth': 1.2,
        'percentile_linestyle': '--',
        'percentile_alpha': 0.7
    })
    
    return {
        'default': config1,
        'lightgray_solid': config2,
        'lightgray_dashed_thin': config3,
        'steelblue_dashed': config4
    }

def run_test_config(config_name, config_data):
    """运行单个测试配置"""
    
    print(f"\n🎨 测试配置: {config_name}")
    
    # 保存临时配置文件
    temp_config_file = f"temp_config_{config_name}.toml"
    
    try:
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            toml.dump(config_data, f)
        
        # 运行绘图程序
        result = subprocess.run(
            ['python', 'run_cp_ppsd.py', temp_config_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"  ✅ {config_name} 配置测试成功")
            return True
        else:
            print(f"  ❌ {config_name} 配置测试失败")
            print(f"     错误: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ⏰ {config_name} 配置测试超时")
        return False
    except Exception as e:
        print(f"  ❌ {config_name} 配置测试异常: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_config_file):
            os.remove(temp_config_file)

def main():
    """主函数"""
    
    print("=" * 60)
    print("百分位数线样式变化验证测试")
    print("=" * 60)
    
    # 检查NPZ文件
    if not os.path.exists('./output/npz/'):
        print("❌ NPZ目录不存在，请先运行PPSD计算")
        return
    
    npz_files = [f for f in os.listdir('./output/npz/') if f.endswith('.npz')]
    if not npz_files:
        print("❌ 没有找到NPZ文件，请先运行PPSD计算")
        return
    
    print(f"✅ 找到 {len(npz_files)} 个NPZ文件")
    
    # 创建测试配置
    test_configs = create_test_configs()
    
    # 运行所有测试配置
    success_count = 0
    for config_name, config_data in test_configs.items():
        if run_test_config(config_name, config_data):
            success_count += 1
    
    print(f"\n📊 测试完成！")
    print(f"   成功: {success_count}/{len(test_configs)} 个配置")
    print(f"   输出目录: ./output/plots/")
    
    # 列出生成的文件
    print(f"\n📁 生成的对比文件:")
    plot_files = [f for f in os.listdir('./output/plots/') if f.startswith('standard_') and f.endswith('.png')]
    for f in sorted(plot_files):
        if any(style in f for style in ['default', 'lightgray', 'steelblue']):
            print(f"   - {f}")
    
    print(f"\n💡 提示:")
    print(f"   - default: ObsPy默认黑色粗线")
    print(f"   - lightgray_solid: 浅灰色实线")
    print(f"   - lightgray_dashed_thin: 浅灰色超细虚线")
    print(f"   - steelblue_dashed: 钢蓝色虚线")

if __name__ == "__main__":
    main() 