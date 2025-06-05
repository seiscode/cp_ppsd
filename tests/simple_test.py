#!/usr/bin/env python3
import os
import time

# 测试列表
tests = [
    ("基线测试", {}),
    ("百分位数显示", {"show_percentiles = false": "show_percentiles = true"}),
    ("隐藏皮特森曲线", {"show_noise_models = true": "show_noise_models = false"}),
    ("显示覆盖度", {"show_coverage = false": "show_coverage = true"}), 
    ("隐藏众数线", {"show_mode = true": "show_mode = false"}),
    ("显示均值线", {"show_mean = false": "show_mean = true"}),
    ("频率轴", {"xaxis_frequency = false": "xaxis_frequency = true"}),
    ("累积图", {"cumulative_plot = false": "cumulative_plot = true"}),
]

def run_test(name, modifications):
    print(f"\n🧪 {name}")
    
    # 备份并修改配置
    if modifications:
        os.system("cp input/config_plot.toml input/config_plot_temp.toml")
        with open("input/config_plot.toml", "r") as f:
            content = f.read()
        for old, new in modifications.items():
            content = content.replace(old, new)
        with open("input/config_plot.toml", "w") as f:
            f.write(content)
    
    # 清空plots并运行
    os.system("rm -f output/plots/*.png")
    start = time.time()
    cmd = ("/home/muly/miniconda3/envs/seis/bin/python run_cp_ppsd.py "
           "input/config_plot.toml")
    result = os.system(f"timeout 30 {cmd}")
    duration = time.time() - start
    
    # 检查结果
    files = len([f for f in os.listdir("output/plots") if f.endswith(".png")])
    
    if result == 0 and files > 0:
        print(f"✅ 成功: {files}文件, {duration:.1f}s")
    else:
        print(f"❌ 失败: 返回码{result}, {files}文件")
    
    # 恢复配置
    if modifications:
        os.system("cp input/config_plot_temp.toml input/config_plot.toml")
    
    return result == 0 and files > 0

# 运行测试
success = 0
total = len(tests)

for name, mods in tests:
    if run_test(name, mods):
        success += 1

print(f"\n📊 结果: {success}/{total} 成功 ({success/total*100:.1f}%)") 