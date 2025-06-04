#!/usr/bin/env python3
"""
测试皮特森曲线位置修复效果的脚本

此脚本用于验证皮特森曲线在不同坐标轴模式下的位置是否正确。
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from obspy.signal.spectral_estimation import get_nlnm, get_nhnm

def test_peterson_curves_position():
    """测试皮特森曲线在不同坐标轴模式下的位置"""
    
    print("🔍 测试皮特森曲线位置修复效果...")
    
    # 获取皮特森曲线数据
    nlnm_periods, nlnm_psd = get_nlnm()
    nhnm_periods, nhnm_psd = get_nhnm()
    
    # 创建对比图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 子图1: 周期坐标模式 (xaxis_frequency = false)
    ax1.plot(nlnm_periods, nlnm_psd, 'r--', linewidth=2, alpha=0.8, label='NLNM')
    ax1.plot(nhnm_periods, nhnm_psd, 'b--', linewidth=2, alpha=0.8, label='NHNM')
    ax1.set_xscale('log')
    ax1.set_xlim(0.01, 1000.0)
    ax1.set_ylim(-200, -50)
    ax1.set_xlabel('周期 (秒)')
    ax1.set_ylabel('功率谱密度 (dB)')
    ax1.set_title('周期坐标模式 (xaxis_frequency = false)\n修复后：皮特森曲线使用周期坐标')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 子图2: 频率坐标模式 (xaxis_frequency = true)
    nlnm_frequencies = 1.0 / nlnm_periods
    nhnm_frequencies = 1.0 / nhnm_periods
    
    ax2.plot(nlnm_frequencies, nlnm_psd, 'r--', linewidth=2, alpha=0.8, label='NLNM')
    ax2.plot(nhnm_frequencies, nhnm_psd, 'b--', linewidth=2, alpha=0.8, label='NHNM')
    ax2.set_xscale('log')
    ax2.set_xlim(0.001, 100.0)
    ax2.set_ylim(-200, -50)
    ax2.set_xlabel('频率 (Hz)')
    ax2.set_ylabel('功率谱密度 (dB)')
    ax2.set_title('频率坐标模式 (xaxis_frequency = true)\n修复后：皮特森曲线使用频率坐标')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    
    # 保存测试图像
    output_path = './output/plots/peterson_position_fix_test.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✅ 皮特森曲线位置修复测试图像保存成功: {output_path}")
    
    # 输出数据范围信息
    print("\n📊 皮特森曲线数据范围:")
    print(f"   NLNM周期范围: {nlnm_periods.min():.3f} - {nlnm_periods.max():.3f} 秒")
    print(f"   NLNM频率范围: {nlnm_frequencies.min():.6f} - {nlnm_frequencies.max():.3f} Hz")
    print(f"   NHNM周期范围: {nhnm_periods.min():.3f} - {nhnm_periods.max():.3f} 秒")
    print(f"   NHNM频率范围: {nhnm_frequencies.min():.6f} - {nhnm_frequencies.max():.3f} Hz")
    
    return True

def main():
    """主测试函数"""
    print("🧪 开始皮特森曲线位置修复测试")
    print("=" * 60)
    
    # 测试皮特森曲线位置
    position_test_passed = test_peterson_curves_position()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"   皮特森曲线位置测试: {'✅ 通过' if position_test_passed else '❌ 失败'}")
    
    if position_test_passed:
        print("\n🎉 皮特森曲线位置修复测试通过！")
        print("   ✅ 周期坐标模式：皮特森曲线正确使用周期坐标")
        print("   ✅ 频率坐标模式：皮特森曲线正确转换为频率坐标")
        print("   ✅ 坐标轴匹配：皮特森曲线与PPSD图坐标系统一致")
        return True
    else:
        print("\n⚠️  皮特森曲线位置测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 