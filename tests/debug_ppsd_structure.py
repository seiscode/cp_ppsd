#!/usr/bin/env python3
"""
调试PPSD对象数据结构
"""

import numpy as np
import glob


def debug_ppsd_structure():
    """调试PPSD对象的数据结构"""
    
    # 找到一个NPZ文件
    npz_files = glob.glob("./output/npz/*.npz")
    if not npz_files:
        print("没有找到NPZ文件")
        return
    
    # 加载一个NPZ文件
    npz_file = npz_files[0]
    print(f"调试文件: {npz_file}")
    
    try:
        from obspy.signal.spectral_estimation import PPSD
        from obspy import read_inventory
        
        # 读取inventory
        inventory = read_inventory("./input/BJ.XML")
        
        # 加载PPSD
        ppsd = PPSD.load_npz(npz_file, allow_pickle=True)
        
        print(f"\nPPSD基本信息:")
        print(f"  - period_bin_centers形状: {ppsd.period_bin_centers.shape}")
        print(f"  - period_bin_centers: {ppsd.period_bin_centers[:10]}...")
        
        # 检查percentile方法
        print("\n测试get_percentile方法:")
        for percentile in [10, 50, 90]:
            try:
                result = ppsd.get_percentile(percentile)
                print(f"  - {percentile}th percentile类型: {type(result)}")
                if isinstance(result, tuple):
                    print(f"    元组长度: {len(result)}")
                    for i, item in enumerate(result):
                        print(f"    元素{i}类型: {type(item)}")
                        if hasattr(item, 'shape'):
                            print(f"    元素{i}形状: {item.shape}")
                        elif hasattr(item, '__len__'):
                            print(f"    元素{i}长度: {len(item)}")
            except Exception as e:
                print(f"  - {percentile}th percentile失败: {e}")
        
        # 检查其他方法
        print(f"\n检查其他统计方法:")
        methods_to_check = ['get_mode', 'get_mean']
        for method_name in methods_to_check:
            if hasattr(ppsd, method_name):
                try:
                    method = getattr(ppsd, method_name)
                    result = method()
                    print(f"  - {method_name}形状: {result.shape}")
                    print(f"  - {method_name}类型: {type(result)}")
                except Exception as e:
                    print(f"  - {method_name}失败: {e}")
            else:
                print(f"  - {method_name}: 方法不存在")
        
        # 检查内部数据结构
        print(f"\n内部数据结构:")
        if hasattr(ppsd, '_psd_matrix'):
            print(f"  - _psd_matrix形状: {ppsd._psd_matrix.shape if ppsd._psd_matrix is not None else 'None'}")
        if hasattr(ppsd, 'psd_values'):
            print(f"  - psd_values形状: {ppsd.psd_values.shape if ppsd.psd_values is not None else 'None'}")
        
        # 尝试手动计算统计量
        print(f"\n尝试手动计算统计量:")
        if hasattr(ppsd, '_psd_matrix') and ppsd._psd_matrix is not None:
            psd_matrix = np.array(ppsd._psd_matrix)
            print(f"  - PSD matrix形状: {psd_matrix.shape}")
            
            # 计算百分位数
            for percentile in [10, 50, 90]:
                try:
                    pct_values = np.nanpercentile(psd_matrix, percentile, axis=0)
                    print(f"  - 手动计算{percentile}th percentile形状: {pct_values.shape}")
                except Exception as e:
                    print(f"  - 手动计算{percentile}th percentile失败: {e}")
            
            # 计算均值
            try:
                mean_values = np.nanmean(psd_matrix, axis=0)
                print(f"  - 手动计算均值形状: {mean_values.shape}")
            except Exception as e:
                print(f"  - 手动计算均值失败: {e}")
        
        print(f"\n调试完成!")
        
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ppsd_structure() 