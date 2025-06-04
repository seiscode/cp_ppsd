#!/usr/bin/env python3
"""
测试自定义皮特森曲线功能的脚本

此脚本用于验证自定义皮特森曲线样式功能是否正常工作。
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from obspy.signal.spectral_estimation import get_nlnm, get_nhnm

def test_peterson_curves_data():
    """测试皮特森曲线数据获取功能"""
    
    print("🔍 测试皮特森曲线数据获取...")
    
    try:
        # 获取NLNM数据
        nlnm_periods, nlnm_psd = get_nlnm()
        print(f"✅ NLNM数据获取成功")
        print(f"   周期数据长度: {len(nlnm_periods)}")
        print(f"   PSD数据长度: {len(nlnm_psd)}")
        print(f"   周期范围: {nlnm_periods.min():.3f} - {nlnm_periods.max():.3f} 秒")
        print(f"   PSD范围: {nlnm_psd.min():.1f} - {nlnm_psd.max():.1f} dB")
        
        # 获取NHNM数据
        nhnm_periods, nhnm_psd = get_nhnm()
        print(f"✅ NHNM数据获取成功")
        print(f"   周期数据长度: {len(nhnm_periods)}")
        print(f"   PSD数据长度: {len(nhnm_psd)}")
        print(f"   周期范围: {nhnm_periods.min():.3f} - {nhnm_periods.max():.3f} 秒")
        print(f"   PSD范围: {nhnm_psd.min():.1f} - {nhnm_psd.max():.1f} dB")
        
        return True
        
    except Exception as e:
        print(f"❌ 皮特森曲线数据获取失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_peterson_curves_plotting():
    """测试皮特森曲线绘制功能"""
    
    print("\n🎨 测试皮特森曲线绘制...")
    
    try:
        # 创建测试图像
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 获取并绘制NLNM
        nlnm_periods, nlnm_psd = get_nlnm()
        ax.plot(nlnm_periods, nlnm_psd, 
               color='red', linewidth=2.0, linestyle='--', alpha=0.8,
               label='NLNM (Custom Style)')
        
        # 获取并绘制NHNM
        nhnm_periods, nhnm_psd = get_nhnm()
        ax.plot(nhnm_periods, nhnm_psd,
               color='blue', linewidth=2.0, linestyle='--', alpha=0.8,
               label='NHNM (Custom Style)')
        
        # 设置图像属性
        ax.set_xscale('log')
        ax.set_xlabel('Period (s)')
        ax.set_ylabel('Power Spectral Density (dB rel. 1 (m/s²)²/Hz)')
        ax.set_title('Custom Peterson Curves Test')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # 保存测试图像
        output_path = './output/plots/peterson_curves_test.png'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        print(f"✅ 皮特森曲线测试图像保存成功: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 皮特森曲线绘制失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主测试函数"""
    print("🧪 开始皮特森曲线功能测试")
    print("=" * 50)
    
    # 测试数据获取
    data_test_passed = test_peterson_curves_data()
    
    # 测试绘制功能
    plot_test_passed = test_peterson_curves_plotting()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"   数据获取测试: {'✅ 通过' if data_test_passed else '❌ 失败'}")
    print(f"   绘制功能测试: {'✅ 通过' if plot_test_passed else '❌ 失败'}")
    
    if data_test_passed and plot_test_passed:
        print("\n🎉 所有测试通过！自定义皮特森曲线功能准备就绪。")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 