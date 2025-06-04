#!/usr/bin/env python3
"""
简化的百分位数线样式测试脚本

此脚本通过修改配置文件来测试不同的百分位数线样式。

使用方法:
    python tests/test_percentile_styles_simple.py
"""

import os
import shutil
import subprocess


def test_percentile_styles():
    """测试不同的百分位数线样式"""
    
    print("=" * 60)
    print("百分位数线样式测试")
    print("=" * 60)
    
    # 备份原始配置文件
    original_config = "input/config_plot.toml"
    backup_config = "input/config_plot_backup.toml"
    
    if os.path.exists(original_config):
        shutil.copy2(original_config, backup_config)
        print(f"✅ 已备份原始配置文件: {backup_config}")
    else:
        print("❌ 原始配置文件不存在")
        return
    
    # 测试样式配置
    test_styles = {
        'lightgray_thin': {
            'color': 'lightgray',
            'linewidth': 1.0,
            'linestyle': '-',
            'alpha': 0.8,
            'description': '浅灰色细线（推荐）'
        },
        'darkgray_medium': {
            'color': 'darkgray',
            'linewidth': 1.2,
            'linestyle': '-',
            'alpha': 0.7,
            'description': '深灰色中等线宽'
        },
        'steelblue_dashed': {
            'color': 'steelblue',
            'linewidth': 0.8,
            'linestyle': '--',
            'alpha': 0.6,
            'description': '钢蓝色虚线'
        }
    }
    
    # 测试每种样式
    for style_name, style_config in test_styles.items():
        print(f"\n🎨 测试样式: {style_name} - {style_config['description']}")
        
        try:
            # 修改配置文件
            modify_config_for_style(original_config, style_config, style_name)
            
            # 运行绘图程序
            result = subprocess.run(
                ['python', 'run_cp_ppsd.py', original_config],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"  ✅ {style_name} 样式测试完成")
                # 重命名生成的文件以区分不同样式
                rename_output_files(style_name)
            else:
                print(f"  ❌ {style_name} 样式测试失败")
                print(f"     错误信息: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {style_name} 样式测试超时")
        except Exception as e:
            print(f"  ❌ {style_name} 样式测试异常: {e}")
    
    # 恢复原始配置文件
    if os.path.exists(backup_config):
        shutil.copy2(backup_config, original_config)
        os.remove(backup_config)
        print(f"\n✅ 已恢复原始配置文件")
    
    print(f"\n📊 测试完成！请检查 output/plots/ 目录中的对比图像")
    print("\n生成的文件命名规则:")
    for style_name, style_config in test_styles.items():
        print(f"  - *_{style_name}_*.png: {style_config['description']}")


def modify_config_for_style(config_file, style_config, style_name):
    """修改配置文件以应用指定的百分位数线样式"""
    
    # 读取原始配置文件
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换百分位数线样式参数
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.strip().startswith('percentile_color ='):
            new_lines.append(f'percentile_color = "{style_config["color"]}"      # 百分位数线颜色')
        elif line.strip().startswith('percentile_linewidth ='):
            new_lines.append(f'percentile_linewidth = {style_config["linewidth"]}          # 百分位数线宽度')
        elif line.strip().startswith('percentile_linestyle ='):
            new_lines.append(f'percentile_linestyle = "{style_config["linestyle"]}"          # 百分位数线样式')
        elif line.strip().startswith('percentile_alpha ='):
            new_lines.append(f'percentile_alpha = {style_config["alpha"]}              # 百分位数线透明度')
        elif 'output_filename_pattern =' in line:
            # 修改输出文件名模式以包含样式标识
            new_lines.append(line.replace('.png', f'_{style_name}.png'))
        else:
            new_lines.append(line)
    
    # 写回配置文件
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"  📝 已更新配置文件，应用 {style_name} 样式")


def rename_output_files(style_name):
    """重命名输出文件以区分不同样式"""
    
    output_dir = "output/plots/"
    if not os.path.exists(output_dir):
        return
    
    # 查找最新生成的文件
    files = [f for f in os.listdir(output_dir) if f.endswith(f'_{style_name}.png')]
    
    print(f"  📁 为 {style_name} 样式生成了 {len(files)} 个文件")


if __name__ == "__main__":
    test_percentile_styles() 