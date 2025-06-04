#!/usr/bin/env python3
"""
PPSD分箱（Binning）概念演示脚本
"""

import numpy as np
import matplotlib.pyplot as plt

def demonstrate_ppsd_binning():
    """演示PPSD分箱的工作原理"""
    
    # 从配置文件读取的分箱参数
    db_min, db_max, db_step = -200.0, -50.0, 0.25
    
    print("=" * 60)
    print("PPSD分箱（Binning）概念详解")
    print("=" * 60)
    
    # 1. 计算分箱边界
    bins = np.arange(db_min, db_max + db_step, db_step)
    print(f"\n1. 分箱基本信息:")
    print(f"   分箱数量: {len(bins)-1} 个")
    print(f"   分箱范围: {db_min} 到 {db_max} dB")
    print(f"   分箱步长: {db_step} dB")
    print(f"   总动态范围: {db_max - db_min} dB")
    
    # 2. 显示分箱边界示例
    print(f"\n2. 分箱边界示例:")
    print(f"   前5个分箱: {bins[:5]}")
    print(f"   中间5个分箱: {bins[len(bins)//2-2:len(bins)//2+3]}")
    print(f"   后5个分箱: {bins[-5:]}")
    
    # 3. 演示PSD值如何分配到分箱
    print(f"\n3. PSD值分箱示例:")
    example_psd_values = [-120.5, -85.3, -67.8, -156.2, -45.0, -250.0, -30.0]
    
    for psd in example_psd_values:
        if psd < db_min:
            bin_idx = 0  # 超出下限，分配到第一个分箱
            status = "(超出下限)"
        elif psd >= db_max:
            bin_idx = len(bins) - 2  # 超出上限，分配到最后一个分箱
            status = "(超出上限)"
        else:
            bin_idx = int((psd - db_min) / db_step)
            status = "(正常范围)"
        
        bin_center = bins[bin_idx] + db_step/2
        print(f"   PSD值 {psd:7.1f} dB → 分箱 {bin_idx:3d} → 中心值 {bin_center:7.2f} dB {status}")
    
    # 4. 解释PPSD矩阵的含义
    print(f"\n4. PPSD矩阵结构:")
    print(f"   - 行（频率轴）: 不同频率/周期点")
    print(f"   - 列（振幅轴）: {len(bins)-1} 个dB分箱")
    print(f"   - 矩阵元素: 每个(频率,dB)组合的出现概率")
    
    # 5. 分箱的物理意义
    print(f"\n5. 分箱的物理意义:")
    print(f"   - 每个分箱代表一个功率谱密度范围")
    print(f"   - 分箱越细（步长越小），分辨率越高")
    print(f"   - 当前设置：0.25 dB步长 = 高精度分析")
    print(f"   - 典型地震噪声范围：-180 到 -90 dB")
    
    # 6. 概率密度函数的构建
    print(f"\n6. 概率密度函数构建:")
    print(f"   - 对每个频率点，统计PSD值落入各分箱的次数")
    print(f"   - 归一化得到概率密度")
    print(f"   - 最终形成2D概率密度矩阵")
    
    # 7. 实际应用示例
    print(f"\n7. 实际应用示例:")
    print(f"   - 如果某频率点的PSD值经常在-120±5 dB范围")
    print(f"   - 则对应的分箱会有较高的概率值")
    print(f"   - PPSD图中该区域会显示为'热点'")
    
    return bins

def create_binning_visualization():
    """创建分箱可视化图"""
    db_min, db_max, db_step = -200.0, -50.0, 0.25
    bins = np.arange(db_min, db_max + db_step, db_step)
    
    # 模拟一些PSD数据
    np.random.seed(42)
    # 模拟两种噪声模式：低频高噪声 + 高频低噪声
    n_samples = 1000
    psd_values_low_freq = np.random.normal(-120, 15, n_samples//2)  # 低频噪声
    psd_values_high_freq = np.random.normal(-140, 10, n_samples//2)  # 高频噪声
    all_psd_values = np.concatenate([psd_values_low_freq, psd_values_high_freq])
    
    # 计算直方图
    hist, bin_edges = np.histogram(all_psd_values, bins=bins, density=True)
    
    plt.figure(figsize=(12, 8))
    
    # 子图1：分箱示意图
    plt.subplot(2, 1, 1)
    plt.bar(bin_edges[:-1], hist, width=db_step*0.8, alpha=0.7, color='skyblue', edgecolor='navy')
    plt.xlabel('功率谱密度 (dB)')
    plt.ylabel('概率密度')
    plt.title('PPSD分箱示例：模拟地震噪声分布')
    plt.grid(True, alpha=0.3)
    plt.xlim(-180, -80)
    
    # 标注几个重要分箱
    important_bins = [-160, -140, -120, -100]
    for db_val in important_bins:
        if db_min <= db_val <= db_max:
            bin_idx = int((db_val - db_min) / db_step)
            plt.axvline(db_val, color='red', linestyle='--', alpha=0.7)
            plt.text(db_val, max(hist)*0.8, f'{db_val} dB\n分箱 {bin_idx}', 
                    ha='center', va='bottom', fontsize=9, 
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # 子图2：累积分布
    plt.subplot(2, 1, 2)
    cumulative = np.cumsum(hist) * db_step
    plt.plot(bin_edges[:-1], cumulative, 'b-', linewidth=2, label='累积概率')
    plt.xlabel('功率谱密度 (dB)')
    plt.ylabel('累积概率')
    plt.title('累积概率分布')
    plt.grid(True, alpha=0.3)
    plt.xlim(-180, -80)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('ppsd_binning_demo.png', dpi=150, bbox_inches='tight')
    print(f"\n可视化图已保存为: ppsd_binning_demo.png")
    
    return hist, bin_edges

if __name__ == "__main__":
    # 运行演示
    bins = demonstrate_ppsd_binning()
    
    # 创建可视化
    try:
        hist, bin_edges = create_binning_visualization()
        print(f"\n分箱演示完成！")
    except ImportError:
        print(f"\n注意：matplotlib未安装，跳过可视化部分")
    
    print(f"\n" + "="*60)
    print("总结：PPSD分箱是将连续的功率谱密度值离散化的过程")
    print("这样可以统计每个dB范围的出现频率，构建概率密度函数")
    print("="*60) 