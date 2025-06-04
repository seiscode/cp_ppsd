#!/usr/bin/env python3
"""
简单数据可视化工具

创建基于ASCII字符的数据图表和HTML格式的报告，不依赖外部库。

功能特点：
- 生成ASCII字符图表
- 创建HTML数据报告
- 文件大小和台站信息可视化
- 不依赖matplotlib或ObsPy

Author: AI Assistant
Date: 2025-01-30
"""

import os
import glob
from datetime import datetime
import math


def find_miniseed_files(data_dir):
    """查找数据目录下的miniseed文件"""
    mseed_patterns = ['*.mseed', '*.miniseed', '*.ms']
    files = []
    
    for pattern in mseed_patterns:
        files.extend(glob.glob(os.path.join(data_dir, pattern)))
    
    return sorted(files)


def extract_station_info(filename):
    """从文件名提取台站信息"""
    basename = os.path.basename(filename)
    parts = basename.split('.')
    
    info = {
        'network': parts[0] if len(parts) > 0 else 'Unknown',
        'station': parts[1] if len(parts) > 1 else 'Unknown',
        'location': parts[2] if len(parts) > 2 else '00',
        'channel': parts[3] if len(parts) > 3 else 'Unknown',
        'datetime_str': parts[4] if len(parts) > 4 else 'Unknown',
        'filename': basename
    }
    
    # 解析时间戳
    if info['datetime_str'] and len(info['datetime_str']) >= 14:
        try:
            year = int(info['datetime_str'][:4])
            month = int(info['datetime_str'][4:6])
            day = int(info['datetime_str'][6:8])
            hour = int(info['datetime_str'][8:10])
            minute = int(info['datetime_str'][10:12])
            second = int(info['datetime_str'][12:14])
            
            info['start_time'] = datetime(year, month, day, hour, minute, second)
            info['date_str'] = f"{year}-{month:02d}-{day:02d}"
            info['time_str'] = f"{hour:02d}:{minute:02d}:{second:02d}"
        except (ValueError, IndexError):
            info['start_time'] = None
            info['date_str'] = 'Unknown'
            info['time_str'] = 'Unknown'
    else:
        info['start_time'] = None
        info['date_str'] = 'Unknown'
        info['time_str'] = 'Unknown'
    
    return info


def create_ascii_bar_chart(data, title, width=60):
    """
    创建ASCII字符条形图
    
    Parameters:
    -----------
    data : dict
        数据字典，键为标签，值为数值
    title : str
        图表标题
    width : int
        图表宽度
    """
    if not data:
        return "No data to display"
    
    max_value = max(data.values())
    if max_value == 0:
        return "No data to display"
    
    lines = []
    lines.append(f"\n{title}")
    lines.append("=" * len(title))
    lines.append("")
    
    # 找出最长的标签
    max_label_len = max(len(str(label)) for label in data.keys())
    
    for label, value in data.items():
        # 计算条形长度
        bar_length = int((value / max_value) * (width - max_label_len - 10))
        bar = "█" * bar_length
        
        # 格式化显示
        label_str = f"{label:<{max_label_len}}"
        value_str = f"{value:8.1f}"
        lines.append(f"{label_str} │{bar:<{width-max_label_len-10}} {value_str}")
    
    lines.append("")
    return "\n".join(lines)


def create_ascii_timeline(files_info, width=80):
    """创建时间线图表"""
    if not files_info:
        return "No data to display"
    
    lines = []
    lines.append("\nTimeline Visualization")
    lines.append("=" * 21)
    lines.append("")
    
    # 排序文件按时间
    sorted_files = sorted([f for f in files_info if f['start_time']], 
                         key=lambda x: x['start_time'])
    
    if not sorted_files:
        return "No valid timestamps found"
    
    start_time = sorted_files[0]['start_time']
    
    lines.append(f"Base Time: {start_time}")
    lines.append("")
    lines.append("Station  Channel  Time Offset  File Size")
    lines.append("-" * 45)
    
    for f in sorted_files:
        offset = (f['start_time'] - start_time).total_seconds()
        offset_str = f"+{offset:3.0f}s" if offset > 0 else f"{offset:4.0f}s"
        
        lines.append(f"{f['station']:<8} {f['channel']:<8} {offset_str:<11} {f['size_mb']:6.1f} MB")
    
    return "\n".join(lines)


def create_station_distribution_chart(files_info):
    """创建台站分布图"""
    if not files_info:
        return "No data to display"
    
    # 统计各类型通道
    bh_stations = []
    sh_stations = []
    
    for f in files_info:
        if f['channel'].startswith('BH'):
            bh_stations.append(f['station'])
        elif f['channel'].startswith('SH'):
            sh_stations.append(f['station'])
    
    lines = []
    lines.append("\nStation Distribution by Channel Type")
    lines.append("=" * 38)
    lines.append("")
    
    lines.append("Broadband Stations (BH channels):")
    if bh_stations:
        for station in bh_stations:
            lines.append(f"  ● {station}")
    else:
        lines.append("  (None)")
    
    lines.append("")
    lines.append("Short-period Stations (SH channels):")
    if sh_stations:
        for station in sh_stations:
            lines.append(f"  ● {station}")
    else:
        lines.append("  (None)")
    
    lines.append("")
    lines.append(f"Total: {len(bh_stations)} broadband + {len(sh_stations)} short-period = {len(files_info)} stations")
    
    return "\n".join(lines)


def create_html_report(files_info, output_file):
    """创建HTML格式的详细报告"""
    
    # 计算统计数据
    total_size = sum(f['size_mb'] for f in files_info)
    stations = sorted(set(f['station'] for f in files_info))
    channels = sorted(set(f['channel'] for f in files_info))
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BJ台网MinISEED数据可视化报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .bar {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .bar-label {{
            width: 100px;
            font-weight: bold;
            margin-right: 15px;
        }}
        
        .bar-visual {{
            height: 25px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 3px;
            margin-right: 10px;
            min-width: 20px;
        }}
        
        .bar-value {{
            font-weight: bold;
            color: #667eea;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .data-table th,
        .data-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        .data-table th {{
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }}
        
        .data-table tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .timeline {{
            position: relative;
            padding: 20px 0;
        }}
        
        .timeline-item {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}
        
        .timeline-time {{
            font-weight: bold;
            color: #667eea;
            min-width: 120px;
        }}
        
        .timeline-station {{
            font-weight: bold;
            margin: 0 15px;
            min-width: 60px;
        }}
        
        .timeline-details {{
            flex: 1;
            color: #666;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #333;
            color: white;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>BJ台网MinISEED数据可视化报告</h1>
        <p>数据分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{len(files_info)}</div>
            <div class="stat-label">文件总数</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{total_size:.1f} MB</div>
            <div class="stat-label">数据总量</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(stations)}</div>
            <div class="stat-label">台站数量</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(channels)}</div>
            <div class="stat-label">通道类型</div>
        </div>
    </div>
    
    <div class="chart-container">
        <div class="chart-title">文件大小分布 (MB)</div>
"""
    
    # 添加文件大小条形图
    max_size = max(f['size_mb'] for f in files_info) if files_info else 1
    for f in sorted(files_info, key=lambda x: x['size_mb'], reverse=True):
        width_percent = (f['size_mb'] / max_size) * 100
        html_content += f"""
        <div class="bar">
            <div class="bar-label">{f['station']}</div>
            <div class="bar-visual" style="width: {width_percent}%;"></div>
            <div class="bar-value">{f['size_mb']:.1f} MB</div>
        </div>"""
    
    html_content += """
    </div>
    
    <div class="chart-container">
        <div class="chart-title">台站信息详表</div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>台站</th>
                    <th>通道</th>
                    <th>文件大小</th>
                    <th>开始时间</th>
                    <th>文件名</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # 添加详细数据表
    for f in sorted(files_info, key=lambda x: (x['station'], x['channel'])):
        time_str = f"{f['date_str']} {f['time_str']}" if f['start_time'] else "Unknown"
        html_content += f"""
                <tr>
                    <td><strong>{f['station']}</strong></td>
                    <td>{f['channel']}</td>
                    <td>{f['size_mb']:.1f} MB</td>
                    <td>{time_str}</td>
                    <td><code>{f['filename']}</code></td>
                </tr>"""
    
    html_content += """
            </tbody>
        </table>
    </div>
    
    <div class="chart-container">
        <div class="chart-title">时间线</div>
        <div class="timeline">
"""
    
    # 添加时间线
    sorted_files = sorted([f for f in files_info if f['start_time']], 
                         key=lambda x: x['start_time'])
    
    if sorted_files:
        base_time = sorted_files[0]['start_time']
        for f in sorted_files:
            offset = (f['start_time'] - base_time).total_seconds()
            offset_str = f"+{offset:.0f}s" if offset > 0 else f"{offset:.0f}s"
            
            html_content += f"""
            <div class="timeline-item">
                <div class="timeline-time">{f['time_str']}</div>
                <div class="timeline-station">{f['station']}</div>
                <div class="timeline-details">
                    {f['channel']} 通道 | {f['size_mb']:.1f} MB | 偏移: {offset_str}
                </div>
            </div>"""
    
    html_content += f"""
        </div>
    </div>
    
    <div class="footer">
        <p>数据来源: BJ地震台网 | 生成工具: create_data_visualization.py</p>
        <p>报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
    
    # 保存HTML文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return True
    except Exception as e:
        print(f"Error creating HTML report: {e}")
        return False


def create_svg_chart(files_info, output_file):
    """创建SVG格式的图表"""
    if not files_info:
        return False
    
    # SVG尺寸和设置
    width = 800
    height = 600
    margin = 60
    chart_width = width - 2 * margin
    chart_height = height - 2 * margin
    
    # 准备数据
    stations = [f['station'] for f in files_info]
    sizes = [f['size_mb'] for f in files_info]
    max_size = max(sizes)
    
    bar_width = chart_width / len(stations)
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="barGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- 背景 -->
    <rect width="{width}" height="{height}" fill="#f8f9fa"/>
    
    <!-- 标题 -->
    <text x="{width/2}" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold" fill="#333">
        BJ台网MinISEED文件大小分布
    </text>
    
    <!-- Y轴 -->
    <line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="#333" stroke-width="2"/>
    
    <!-- X轴 -->
    <line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="#333" stroke-width="2"/>
    
    <!-- Y轴刻度和标签 -->
'''
    
    # 添加Y轴刻度
    for i in range(5):
        y_value = (max_size / 4) * i
        y_pos = height - margin - (chart_height / 4) * i
        svg_content += f'''    <line x1="{margin-5}" y1="{y_pos}" x2="{margin+5}" y2="{y_pos}" stroke="#333" stroke-width="1"/>
    <text x="{margin-10}" y="{y_pos+5}" text-anchor="end" font-family="Arial" font-size="12" fill="#666">
        {y_value:.1f}
    </text>
'''
    
    # Y轴标签
    svg_content += f'''    <text x="20" y="{height/2}" text-anchor="middle" font-family="Arial" font-size="14" fill="#333" transform="rotate(-90 20 {height/2})">
        文件大小 (MB)
    </text>
    
    <!-- 条形图 -->
'''
    
    # 添加条形图
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    for i, (station, size) in enumerate(zip(stations, sizes)):
        bar_height = (size / max_size) * chart_height
        x_pos = margin + i * bar_width + bar_width * 0.1
        y_pos = height - margin - bar_height
        bar_w = bar_width * 0.8
        
        color = colors[i % len(colors)]
        
        svg_content += f'''    <rect x="{x_pos}" y="{y_pos}" width="{bar_w}" height="{bar_height}" 
          fill="{color}" opacity="0.8" stroke="#333" stroke-width="1"/>
    
    <!-- 条形图标签 -->
    <text x="{x_pos + bar_w/2}" y="{y_pos - 5}" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="#333">
        {size:.1f}
    </text>
    
    <!-- X轴标签 -->
    <text x="{x_pos + bar_w/2}" y="{height - margin + 20}" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#333">
        {station}
    </text>
'''
    
    svg_content += f'''
    <!-- X轴标题 -->
    <text x="{width/2}" y="{height - 10}" text-anchor="middle" font-family="Arial" font-size="14" fill="#333">
        台站代码
    </text>
    
</svg>'''
    
    # 保存SVG文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        return True
    except Exception as e:
        print(f"Error creating SVG chart: {e}")
        return False


def main():
    """主函数：创建数据可视化"""
    print("=" * 70)
    print("BJ Network MinISEED Data Visualization Tool")
    print("=" * 70)
    
    # 数据目录和输出目录
    data_dir = "../data"
    output_dir = "../output/plots"
    
    # 检查数据目录
    if not os.path.exists(data_dir):
        print(f"Error: Data directory {data_dir} not found")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # 查找并分析文件
    mseed_files = find_miniseed_files(data_dir)
    
    if not mseed_files:
        print(f"No miniseed files found in {data_dir}")
        return
    
    print(f"\nAnalyzing {len(mseed_files)} files...")
    
    # 分析文件信息
    files_info = []
    for file_path in mseed_files:
        try:
            stat = os.stat(file_path)
            station_info = extract_station_info(file_path)
            
            file_info = {
                'size_mb': stat.st_size / (1024 * 1024),
                'size_bytes': stat.st_size,
                **station_info
            }
            files_info.append(file_info)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    if not files_info:
        print("No valid files to visualize")
        return
    
    # 创建ASCII图表
    print("\n" + "=" * 70)
    print("ASCII VISUALIZATIONS")
    print("=" * 70)
    
    # 文件大小条形图
    size_data = {f['station']: f['size_mb'] for f in files_info}
    ascii_chart = create_ascii_bar_chart(size_data, "File Size Distribution (MB)")
    print(ascii_chart)
    
    # 时间线图
    timeline_chart = create_ascii_timeline(files_info)
    print(timeline_chart)
    
    # 台站分布图
    distribution_chart = create_station_distribution_chart(files_info)
    print(distribution_chart)
    
    # 创建HTML报告
    print(f"\n=== Creating HTML Report ===")
    html_file = os.path.join(output_dir, "miniseed_data_report.html")
    if create_html_report(files_info, html_file):
        print(f"HTML report created: {html_file}")
    else:
        print("Failed to create HTML report")
    
    # 创建SVG图表
    print(f"\n=== Creating SVG Chart ===")
    svg_file = os.path.join(output_dir, "miniseed_file_sizes.svg")
    if create_svg_chart(files_info, svg_file):
        print(f"SVG chart created: {svg_file}")
    else:
        print("Failed to create SVG chart")
    
    # 创建文本报告
    print(f"\n=== Creating Text Report ===")
    txt_file = os.path.join(output_dir, "miniseed_visualization.txt")
    try:
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("BJ Network MinISEED Data Visualization Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(ascii_chart)
            f.write("\n")
            f.write(timeline_chart)
            f.write("\n")
            f.write(distribution_chart)
            f.write("\n\nDetailed File Information:\n")
            f.write("-" * 50 + "\n")
            
            for f in files_info:
                f.write(f"Station: {f['station']}\n")
                f.write(f"Channel: {f['channel']}\n")
                f.write(f"Size: {f['size_mb']:.1f} MB\n")
                f.write(f"Time: {f['date_str']} {f['time_str']}\n")
                f.write(f"File: {f['filename']}\n")
                f.write("-" * 30 + "\n")
        
        print(f"Text report created: {txt_file}")
    except Exception as e:
        print(f"Failed to create text report: {e}")
    
    # 生成总结
    print(f"\n=== Visualization Complete ===")
    print(f"Processed {len(files_info)} files")
    print(f"Total data size: {sum(f['size_mb'] for f in files_info):.1f} MB")
    print(f"Stations: {', '.join(sorted(set(f['station'] for f in files_info)))}")
    print(f"Channels: {', '.join(sorted(set(f['channel'] for f in files_info)))}")
    
    # 列出生成的文件
    output_files = []
    for ext in ['.html', '.svg', '.txt']:
        files = glob.glob(os.path.join(output_dir, f"*{ext}"))
        output_files.extend(files)
    
    if output_files:
        print(f"\nGenerated visualization files:")
        for file in sorted(output_files):
            file_size = os.path.getsize(file) / 1024  # KB
            print(f"  {os.path.basename(file)} ({file_size:.1f} KB)")
    
    print(f"\nOpen the HTML report in a web browser to view interactive visualizations!")


if __name__ == "__main__":
    main() 