#!/usr/bin/env python3

import toml

# 直接读取配置文件
with open("input/config_plot.toml", 'r', encoding='utf-8') as f:
    config = toml.load(f)

print("Raw plot_type from TOML:", config.get('plotting', {}).get('plot_type'))

# 模拟处理逻辑
plot_types = config.get('plotting', {}).get('plot_type', ['standard'])
if isinstance(plot_types, str):
    plot_types = [plot_types]

print("Processed plot_types:", plot_types)
print("Length:", len(plot_types))

for i, pt in enumerate(plot_types):
    print(f"  {i}: {pt}") 