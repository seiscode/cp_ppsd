#!/usr/bin/env python3
"""
调试百分位数线功能的脚本

此脚本用于检查自定义百分位数线功能是否正常工作。
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from obspy import read_inventory
from obspy.signal import PPSD

def test_ppsd_percentile_methods():
    """测试PPSD对象的百分位数相关方法"""
    
    print("🔍 检查NPZ文件...")
    npz_dir = "./output/npz/"
    if not os.path.exists(npz_dir):
        print("❌ NPZ目录不存在")
        return
    
    npz_files = [f for f in os.listdir(npz_dir) if f.endswith('.npz')]
    if not npz_files:
        print("❌ 没有找到NPZ文件")
        return
    
    print(f"✅ 找到 {len(npz_files)} 个NPZ文件")
    
    # 加载第一个NPZ文件
    npz_file = os.path.join(npz_dir, npz_files[0])
    print(f"📁 测试文件: {npz_file}")
    
    try:
        # 加载PPSD对象
        ppsd = PPSD.load_npz(npz_file)
        print(f"✅ 成功加载PPSD对象")
        print(f"   数据点数: {len(ppsd._times_processed)}")
        print(f"   频率范围: {ppsd.period_bin_centers.min():.3f} - {ppsd.period_bin_centers.max():.3f} 秒")
        
        # 检查PPSD对象的方法
        print(f"\n🔍 检查PPSD对象的方法:")
        methods = [attr for attr in dir(ppsd) if not attr.startswith('_')]
        percentile_methods = [m for m in methods if 'percentile' in m.lower()]
        print(f"   百分位数相关方法: {percentile_methods}")
        
        # 测试不同的百分位数获取方法
        print(f"\n🧪 测试百分位数获取方法:")
        
        # 方法1: 尝试get_percentile
        try:
            periods, psd_values = ppsd.get_percentile(50)
            print(f"   ✅ get_percentile(50) 成功")
            print(f"      periods 长度: {len(periods)}")
            print(f"      psd_values 长度: {len(psd_values)}")
        except Exception as e:
            print(f"   ❌ get_percentile(50) 失败: {e}")
        
        # 方法2: 尝试直接从数据计算百分位数
        try:
            # 获取PPSD的原始数据
            hist = ppsd._binned_psds
            print(f"   原始数据形状: {hist.shape}")
            
            # 计算百分位数
            percentiles = [10, 50, 90]
            for p in percentiles:
                # 对每个频率bin计算百分位数
                psd_percentile = np.percentile(hist, p, axis=0)
                print(f"   ✅ 第{p}百分位数计算成功，长度: {len(psd_percentile)}")
                
        except Exception as e:
            print(f"   ❌ 直接计算百分位数失败: {e}")
        
        # 方法3: 测试绘图功能
        print(f"\n🎨 测试绘图功能:")
        
        # 创建测试图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 子图1: 默认百分位数线
        ppsd.plot(ax=ax1, show_percentiles=True, percentiles=[10, 50, 90])
        ax1.set_title("默认百分位数线")
        
        # 子图2: 自定义百分位数线
        ppsd.plot(ax=ax2, show_percentiles=False)
        
        # 手动添加自定义百分位数线
        try:
            periods = ppsd.period_bin_centers
            hist = ppsd._binned_psds
            
            for p in [10, 50, 90]:
                psd_percentile = np.percentile(hist, p, axis=0)
                ax2.plot(periods, psd_percentile, 
                        color='lightgray', 
                        linewidth=0.4, 
                        linestyle='--', 
                        alpha=0.8,
                        label=f'{p}th percentile')
            
            ax2.set_title("自定义百分位数线")
            ax2.legend()
            
            print(f"   ✅ 自定义百分位数线绘制成功")
            
        except Exception as e:
            print(f"   ❌ 自定义百分位数线绘制失败: {e}")
        
        # 保存测试图
        test_output = "./output/plots/debug_percentile_test.png"
        plt.tight_layout()
        plt.savefig(test_output, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"   💾 测试图保存到: {test_output}")
        
    except Exception as e:
        print(f"❌ 加载PPSD失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("=" * 60)
    print("百分位数线功能调试测试")
    print("=" * 60)
    
    test_ppsd_percentile_methods()

if __name__ == "__main__":
    main() 