#!/usr/bin/env python3
"""
Author: 
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""

# -*- coding: utf-8 -*-
"""
详细配置参数测试脚本

用于验证config.toml中所有参数的有效性、合理性和兼容性。
"""

import os
import sys
import toml
import tempfile
import shutil
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from cp_ppsd import PPSDProcessor
    print("✓ 成功导入PPSDProcessor")
except ImportError as e:
    print(f"✗ 导入PPSDProcessor失败: {e}")
    sys.exit(1)


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = toml.load(f)
        print(f"✓ 成功加载配置文件: {config_path}")
        return config
    except Exception as e:
        print(f"✗ 加载配置文件失败: {e}")
        return {}


def test_global_parameters(config: dict):
    """测试全局参数"""
    print("\n=== 测试全局参数 ===")
    
    # 测试日志级别
    log_level = config.get('log_level', 'INFO')
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level in valid_levels:
        print(f"✓ log_level: {log_level} (有效)")
    else:
        print(f"✗ log_level: {log_level} (无效，应为: {valid_levels})")
    
    # 测试输入数据路径
    mseed_pattern = config.get('mseed_pattern', '')
    if mseed_pattern:
        if os.path.exists(mseed_pattern):
            if os.path.isdir(mseed_pattern):
                mseed_files = list(Path(mseed_pattern).rglob('*.mseed'))
                print(f"✓ mseed_pattern: {mseed_pattern} (目录存在，包含{len(mseed_files)}个mseed文件)")
            else:
                print(f"✓ mseed_pattern: {mseed_pattern} (文件存在)")
        else:
            print(f"✗ mseed_pattern: {mseed_pattern} (路径不存在)")
    else:
        print("✗ mseed_pattern: 未设置")
    
    # 测试仪器响应文件
    inventory_path = config.get('inventory_path', '')
    if inventory_path:
        if os.path.exists(inventory_path):
            file_size = os.path.getsize(inventory_path)
            print(f"✓ inventory_path: {inventory_path} (文件存在，大小: {file_size} bytes)")
        else:
            print(f"✗ inventory_path: {inventory_path} (文件不存在)")
    else:
        print("✗ inventory_path: 未设置")
    
    # 测试输出目录
    output_dir = config.get('output_dir', './output/npz')
    if os.path.exists(output_dir):
        if os.path.isdir(output_dir):
            npz_files = list(Path(output_dir).glob('*.npz'))
            print(f"✓ output_dir: {output_dir} (目录存在，包含{len(npz_files)}个npz文件)")
        else:
            print(f"✗ output_dir: {output_dir} (不是目录)")
    else:
        print(f"⚠ output_dir: {output_dir} (目录不存在，将自动创建)")
    
    # 测试输出文件名模式
    filename_pattern = config.get('output_npz_filename_pattern', '')
    if filename_pattern:
        # 检查模式中的占位符
        placeholders = ['{year}', '{month}', '{day}', '{hour}', '{minute}', 
                       '{second}', '{julday}', '{datetime}', '{network}', 
                       '{station}', '{location}', '{channel}']
        found_placeholders = [p for p in placeholders if p in filename_pattern]
        print(f"✓ output_npz_filename_pattern: {filename_pattern}")
        print(f"  包含占位符: {found_placeholders}")
    else:
        print("⚠ output_npz_filename_pattern: 未设置，将使用默认模式")


def test_ppsd_core_parameters(config: dict):
    """测试PPSD核心计算参数"""
    print("\n=== 测试PPSD核心计算参数 ===")
    
    args = config.get('args', {})
    if not args:
        print("✗ [args] 部分未找到")
        return
    
    # 测试时间窗口参数
    ppsd_length = args.get('ppsd_length', 3600)
    if isinstance(ppsd_length, (int, float)) and ppsd_length > 0:
        print(f"✓ ppsd_length: {ppsd_length}秒 ({ppsd_length/3600:.2f}小时)")
    else:
        print(f"✗ ppsd_length: {ppsd_length} (应为正数)")
    
    overlap = args.get('overlap', 0.5)
    if isinstance(overlap, (int, float)) and 0 <= overlap < 1:
        print(f"✓ overlap: {overlap} ({overlap*100:.1f}%)")
    else:
        print(f"✗ overlap: {overlap} (应在0-1之间)")
    
    # 测试周期域参数
    period_limits = args.get('period_limits', [0.01, 1000.0])
    if isinstance(period_limits, list) and len(period_limits) == 2:
        if period_limits[0] < period_limits[1] and period_limits[0] > 0:
            print(f"✓ period_limits: {period_limits}秒 (周期范围合理)")
        else:
            print(f"✗ period_limits: {period_limits} (范围不合理)")
    else:
        print(f"✗ period_limits: {period_limits} (应为[最小值, 最大值])")
    
    period_smoothing_width_octaves = args.get('period_smoothing_width_octaves', 1.0)
    if isinstance(period_smoothing_width_octaves, (int, float)) and period_smoothing_width_octaves > 0:
        print(f"✓ period_smoothing_width_octaves: {period_smoothing_width_octaves}")
    else:
        print(f"✗ period_smoothing_width_octaves: {period_smoothing_width_octaves} (应为正数)")
    
    period_step_octaves = args.get('period_step_octaves', 0.125)
    if isinstance(period_step_octaves, (int, float)) and period_step_octaves > 0:
        print(f"✓ period_step_octaves: {period_step_octaves} (1/{1/period_step_octaves:.0f}倍频程)")
    else:
        print(f"✗ period_step_octaves: {period_step_octaves} (应为正数)")
    
    # 测试振幅域参数
    db_bins = args.get('db_bins', [-200.0, -50.0, 0.25])
    if isinstance(db_bins, list) and len(db_bins) == 3:
        min_db, max_db, step_db = db_bins
        if min_db < max_db and step_db > 0:
            num_bins = int((max_db - min_db) / step_db)
            print(f"✓ db_bins: {db_bins} (范围: {min_db}到{max_db}dB，步长: {step_db}dB，共{num_bins}个分箱)")
        else:
            print(f"✗ db_bins: {db_bins} (参数不合理)")
    else:
        print(f"✗ db_bins: {db_bins} (应为[最小值, 最大值, 步长])")
    
    # 测试数据质量参数
    skip_on_gaps = args.get('skip_on_gaps', False)
    print(f"✓ skip_on_gaps: {skip_on_gaps} ({'跳过有间断的数据' if skip_on_gaps else '补零处理间断'})")
    
    special_handling = args.get('special_handling', None)
    valid_special = [None, 'ringlaser', 'hydrophone']
    if special_handling in valid_special:
        print(f"✓ special_handling: {special_handling}")
    else:
        print(f"✗ special_handling: {special_handling} (应为: {valid_special})")


def test_optional_parameters(config: dict):
    """测试可选参数"""
    print("\n=== 测试可选参数 ===")
    
    args = config.get('args', {})
    
    # 测试时间筛选参数
    time_of_weekday = args.get('time_of_weekday', None)
    if time_of_weekday is not None:
        if isinstance(time_of_weekday, list) and all(1 <= day <= 7 for day in time_of_weekday):
            weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            selected_days = [weekdays[day-1] for day in time_of_weekday]
            print(f"✓ time_of_weekday: {time_of_weekday} ({', '.join(selected_days)})")
        else:
            print(f"✗ time_of_weekday: {time_of_weekday} (应为1-7的列表)")
    else:
        print("⚠ time_of_weekday: 未设置 (将处理所有星期)")
    
    processing_time_window = args.get('processing_time_window', None)
    if processing_time_window is not None:
        if isinstance(processing_time_window, list) and len(processing_time_window) == 2:
            print(f"✓ processing_time_window: {processing_time_window}")
        else:
            print(f"✗ processing_time_window: {processing_time_window} (应为[开始时间, 结束时间])")
    else:
        print("⚠ processing_time_window: 未设置 (将处理所有时间)")
    
    daily_time_window = args.get('daily_time_window', None)
    if daily_time_window is not None:
        if isinstance(daily_time_window, list) and len(daily_time_window) == 2:
            print(f"✓ daily_time_window: {daily_time_window}")
        else:
            print(f"✗ daily_time_window: {daily_time_window} (应为[开始时间, 结束时间])")
    else:
        print("⚠ daily_time_window: 未设置 (将处理全天数据)")
    
    # 测试STA/LTA参数
    enable_stalta = args.get('enable_external_stalta_filter', False)
    print(f"✓ enable_external_stalta_filter: {enable_stalta}")
    
    if enable_stalta:
        sta_length = args.get('sta_length', 120)
        lta_length = args.get('lta_length', 600)
        stalta_thresh_on = args.get('stalta_thresh_on', 2.5)
        stalta_thresh_off = args.get('stalta_thresh_off', 1.5)
        
        if sta_length > 0 and lta_length > sta_length:
            print(f"✓ STA/LTA长度: STA={sta_length}s, LTA={lta_length}s")
        else:
            print(f"✗ STA/LTA长度不合理: STA={sta_length}s, LTA={lta_length}s")
        
        if stalta_thresh_off < stalta_thresh_on:
            print(f"✓ STA/LTA阈值: ON={stalta_thresh_on}, OFF={stalta_thresh_off}")
        else:
            print(f"✗ STA/LTA阈值不合理: ON={stalta_thresh_on}, OFF={stalta_thresh_off}")


def test_parameter_compatibility(config: dict):
    """测试参数兼容性"""
    print("\n=== 测试参数兼容性 ===")
    
    args = config.get('args', {})
    
    # 测试时间窗口与重叠的兼容性
    ppsd_length = args.get('ppsd_length', 3600)
    overlap = args.get('overlap', 0.5)
    
    effective_step = ppsd_length * (1 - overlap)
    print(f"✓ 有效时间步长: {effective_step}秒 (窗口长度: {ppsd_length}s, 重叠: {overlap*100:.1f}%)")
    
    # 测试周期范围与采样率的兼容性
    period_limits = args.get('period_limits', [0.01, 1000.0])
    min_period, max_period = period_limits
    
    # 假设常见采样率
    common_sample_rates = [1, 20, 40, 50, 100, 200, 250, 500, 1000]
    print("✓ 周期范围与采样率兼容性检查:")
    for sr in common_sample_rates:
        nyquist_period = 2.0 / sr  # 奈奎斯特周期
        if min_period >= nyquist_period:
            status = "✓"
        else:
            status = "⚠"
        print(f"  {status} 采样率{sr}Hz: 奈奎斯特周期={nyquist_period:.3f}s, 最小分析周期={min_period}s")
    
    # 测试dB分箱的合理性
    db_bins = args.get('db_bins', [-200.0, -50.0, 0.25])
    if len(db_bins) == 3:
        min_db, max_db, step_db = db_bins
        num_bins = int((max_db - min_db) / step_db)
        if num_bins > 1000:
            print(f"⚠ dB分箱数量较多: {num_bins}个 (可能影响性能)")
        elif num_bins < 50:
            print(f"⚠ dB分箱数量较少: {num_bins}个 (可能精度不足)")
        else:
            print(f"✓ dB分箱数量合理: {num_bins}个")


def test_config_with_processor(config_path: str):
    """使用PPSDProcessor测试配置"""
    print("\n=== 使用PPSDProcessor测试配置 ===")
    
    try:
        # 创建临时输出目录
        temp_dir = tempfile.mkdtemp()
        
        # 修改配置以使用临时目录
        with open(config_path, 'r', encoding='utf-8') as f:
            config = toml.load(f)
        
        original_output_dir = config.get('output_dir', './output/npz')
        config['output_dir'] = temp_dir
        
        # 创建临时配置文件
        temp_config_path = os.path.join(temp_dir, 'test_config.toml')
        with open(temp_config_path, 'w', encoding='utf-8') as f:
            toml.dump(config, f)
        
        # 测试PPSDProcessor初始化
        try:
            processor = PPSDProcessor([temp_config_path])
            print("✓ PPSDProcessor初始化成功")
            
            # 测试配置加载
            if hasattr(processor, 'configs') and processor.configs:
                loaded_config = processor.configs[0]
                print("✓ 配置加载到PPSDProcessor成功")
                
                # 验证关键参数
                args = loaded_config.get('args', {})
                ppsd_length = args.get('ppsd_length', 3600)
                overlap = args.get('overlap', 0.5)
                period_limits = args.get('period_limits', [0.01, 1000.0])
                
                print(f"  - PPSD长度: {ppsd_length}s")
                print(f"  - 重叠比例: {overlap}")
                print(f"  - 周期范围: {period_limits}s")
                
            else:
                print("✗ 配置未正确加载到PPSDProcessor")
                
        except Exception as e:
            print(f"✗ PPSDProcessor初始化失败: {e}")
        
        # 清理临时文件
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")


def generate_test_report(config: dict):
    """生成测试报告"""
    print("\n=== 配置参数测试报告 ===")
    
    args = config.get('args', {})
    
    print("配置概要:")
    print(f"  - 日志级别: {config.get('log_level', 'INFO')}")
    print(f"  - 数据源: {config.get('mseed_pattern', '未设置')}")
    print(f"  - 仪器响应: {config.get('inventory_path', '未设置')}")
    print(f"  - 输出目录: {config.get('output_dir', '未设置')}")
    
    print("\nPPSD计算参数:")
    print(f"  - 时间窗口: {args.get('ppsd_length', 3600)}秒")
    print(f"  - 重叠比例: {args.get('overlap', 0.5)*100:.1f}%")
    print(f"  - 周期范围: {args.get('period_limits', [0.01, 1000.0])}秒")
    print(f"  - 周期步长: {args.get('period_step_octaves', 0.125)}倍频程")
    print(f"  - dB分箱: {args.get('db_bins', [-200.0, -50.0, 0.25])}")
    print(f"  - 跳过间断: {args.get('skip_on_gaps', False)}")
    
    # 计算预期性能指标
    ppsd_length = args.get('ppsd_length', 3600)
    overlap = args.get('overlap', 0.5)
    period_limits = args.get('period_limits', [0.01, 1000.0])
    period_step = args.get('period_step_octaves', 0.125)
    db_bins = args.get('db_bins', [-200.0, -50.0, 0.25])
    
    # 计算频率分箱数
    import numpy as np
    min_freq = 1.0 / period_limits[1]
    max_freq = 1.0 / period_limits[0]
    freq_bins = int(np.log2(max_freq / min_freq) / period_step) + 1
    
    # 计算dB分箱数
    if len(db_bins) == 3:
        db_bin_count = int((db_bins[1] - db_bins[0]) / db_bins[2])
    else:
        db_bin_count = 0
    
    print(f"\n预期PPSD矩阵大小:")
    print(f"  - 频率分箱: ~{freq_bins}个")
    print(f"  - dB分箱: {db_bin_count}个")
    print(f"  - 矩阵大小: {freq_bins} × {db_bin_count}")
    
    # 计算处理效率
    effective_step = ppsd_length * (1 - overlap)
    print(f"\n处理效率:")
    print(f"  - 有效时间步长: {effective_step}秒")
    print(f"  - 每小时数据窗口数: {3600/effective_step:.1f}个")
    print(f"  - 每天数据窗口数: {24*3600/effective_step:.0f}个")


def main():
    """主测试函数"""
    print("PPSD配置参数详细测试")
    print("=" * 50)
    
    config_path = "input/config.toml"
    
    if not os.path.exists(config_path):
        print(f"✗ 配置文件不存在: {config_path}")
        return
    
    # 加载配置
    config = load_config(config_path)
    if not config:
        return
    
    # 执行各项测试
    test_global_parameters(config)
    test_ppsd_core_parameters(config)
    test_optional_parameters(config)
    test_parameter_compatibility(config)
    test_config_with_processor(config_path)
    generate_test_report(config)
    
    print("\n" + "=" * 50)
    print("配置参数测试完成！")
    print("\n建议:")
    print("1. 确保所有路径都存在且可访问")
    print("2. 根据数据特性调整周期范围和分箱参数")
    print("3. 根据计算资源调整时间窗口和重叠参数")
    print("4. 启用适当的数据质量控制选项")


if __name__ == '__main__':
    main() 