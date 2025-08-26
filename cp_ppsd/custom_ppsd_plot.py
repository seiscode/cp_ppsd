#!/usr/bin/env python3
"""
Author:
    muly (muly@cea-igp.ac.cn)
license:
    MIT License
    (https://opensource.org/licenses/MIT)

自定义PPSD绘图模块

此模块提供自定义的PPSD绘图功能，支持修改统计线条的样式，
包括百分位数线、众数线、均值线的颜色、线宽等属性。

使用方法:
    from cp_ppsd.custom_ppsd_plot import (
        plot_ppsd_with_custom_statistical_lines)

    # 绘制带有自定义统计线条样式的PPSD图
    plot_ppsd_with_custom_statistical_lines(
        ppsd, percentile_color='lightgray', percentile_linewidth=1.0)
"""

import matplotlib.pyplot as plt
from typing import Optional, List, Dict, Any
import logging
import numpy as np


def plot_ppsd_with_custom_statistical_lines(
        ppsd,
        filename: Optional[str] = None,
        show_histogram: bool = True,
        show_percentiles: bool = True,
        percentiles: List[int] = [10, 50, 90],
        show_noise_models: bool = True,
        grid: bool = True,
        show: bool = True,
        max_percentage: Optional[float] = None,
        period_lim: tuple = (0.01, 179),
        show_mode: bool = False,
        show_mean: bool = False,
        cmap=None,
        cumulative: bool = False,
        cumulative_number_of_colors: int = 20,
        xaxis_frequency: bool = False,
        show_earthquakes=None,
        # 自定义百分位数线样式参数
        percentile_color: str = 'lightgray',
        percentile_linewidth: float = 1.0,
        percentile_linestyle: str = '-',
        percentile_alpha: float = 0.8,
        # 自定义众数线样式参数
        mode_color: str = 'orange',
        mode_linewidth: float = 2.0,
        mode_linestyle: str = '-',
        mode_alpha: float = 0.9,
        # 自定义均值线样式参数
        mean_color: str = 'purple',
        mean_linewidth: float = 2.0,
        mean_linestyle: str = '-',
        mean_alpha: float = 0.9) -> Optional[plt.Figure]:
    """
    绘制带有自定义统计线条样式的PPSD图

    支持自定义百分位数线、众数线和均值线的样式。

    Parameters:
        ppsd: ObsPy PPSD对象
        filename: 输出文件名
        show_histogram: 是否显示直方图
        show_percentiles: 是否显示百分位数线
        percentiles: 要显示的百分位数列表
        show_noise_models: 是否显示噪声模型
        grid: 是否显示网格
        show: 是否立即显示图形
        max_percentage: 最大百分比
        period_lim: 周期范围
        show_mode: 是否显示众数
        show_mean: 是否显示均值
        cmap: 颜色映射
        cumulative: 是否显示累积图
        cumulative_number_of_colors: 累积图颜色数量
        xaxis_frequency: X轴是否显示频率
        show_earthquakes: 是否显示地震模型
        percentile_color: 百分位数线颜色
        percentile_linewidth: 百分位数线宽度
        percentile_linestyle: 百分位数线样式
        percentile_alpha: 百分位数线透明度
        mode_color: 众数线颜色
        mode_linewidth: 众数线宽度
        mode_linestyle: 众数线样式
        mode_alpha: 众数线透明度
        mean_color: 均值线颜色
        mean_linewidth: 均值线宽度
        mean_linestyle: 均值线样式
        mean_alpha: 均值线透明度

    Returns:
        matplotlib Figure对象（如果show=False）
    """

    # 使用ObsPy的标准绘图方法，但不显示百分位数线、众数线和均值线
    fig = ppsd.plot(
        filename=None,
        show_coverage=False,  # 禁用 ObsPy 内置的数据覆盖度显示
        show_histogram=show_histogram,
        show_percentiles=False,  # 先不显示百分位数线
        show_noise_models=show_noise_models,
        grid=grid,
        show=False,  # 不立即显示
        max_percentage=max_percentage,
        period_lim=period_lim,
        show_mode=False,        # 先不显示众数线
        show_mean=False,        # 先不显示均值线
        cmap=cmap,
        cumulative=cumulative,
        cumulative_number_of_colors=cumulative_number_of_colors,
        xaxis_frequency=xaxis_frequency,
        show_earthquakes=show_earthquakes)

    # 如果需要显示百分位数线，手动添加自定义样式的百分位数线
    if show_percentiles and percentiles:
        # 获取当前的axes
        ax = fig.axes[0]  # 主要的PPSD图轴

        # 计算并绘制每个百分位数线
        for percentile in percentiles:
            try:
                # 使用PPSD的get_percentile方法获取百分位数数据
                periods, psd_values = ppsd.get_percentile(percentile)

                # 绘制自定义样式的百分位数线
                label_text = (f'{percentile}th percentile'
                              if percentile in [10, 50, 90] else None)
                ax.plot(periods, psd_values,
                        color=percentile_color,
                        linewidth=percentile_linewidth,
                        linestyle=percentile_linestyle,
                        alpha=percentile_alpha,
                        label=label_text,
                        zorder=10)  # 确保线条在前景

            except Exception as e:
                logging.warning(f"无法绘制第{percentile}百分位数线: {e}")

    # 如果需要显示众数线，手动添加自定义样式的众数线
    if show_mode:
        ax = fig.axes[0]  # 主要的PPSD图轴
        try:
            # 计算众数（最频繁出现的PSD值）

            # 获取PPSD的二维直方图数据
            hist_stack = ppsd._current_hist_stack
            if hist_stack is not None and len(hist_stack) > 0:
                # 计算每个频率bin的众数
                periods = ppsd.period_bin_centers
                mode_values: List[float] = []

                for i in range(len(periods)):
                    # 获取该频率bin的PSD分布
                    psd_column = hist_stack[:, i]
                    if np.sum(psd_column) > 0:
                        # 找到概率密度最大的dB值作为众数
                        mode_idx = np.argmax(psd_column)
                        mode_db = ppsd.db_bin_centers[mode_idx]
                        mode_values.append(mode_db)
                    else:
                        mode_values.append(np.nan)

                mode_array = np.array(mode_values)

                # 过滤掉NaN值
                valid_mask = ~np.isnan(mode_array)
                if np.any(valid_mask):
                    ax.plot(periods[valid_mask], mode_array[valid_mask],
                            color=mode_color,
                            linewidth=mode_linewidth,
                            linestyle=mode_linestyle,
                            alpha=mode_alpha,
                            label='Mode (众数)',
                            zorder=12)

        except Exception as e:
            logging.warning(f"无法绘制众数线: {e}")

    # 如果需要显示均值线，手动添加自定义样式的均值线
    if show_mean:
        ax = fig.axes[0]  # 主要的PPSD图轴
        try:
            # 计算均值

            # 获取PPSD的二维直方图数据
            hist_stack = ppsd._current_hist_stack
            if hist_stack is not None and len(hist_stack) > 0:
                # 计算每个频率bin的加权均值
                periods = ppsd.period_bin_centers
                mean_values: List[float] = []

                for i in range(len(periods)):
                    # 获取该频率bin的PSD分布
                    psd_column = hist_stack[:, i]
                    if np.sum(psd_column) > 0:
                        # 计算加权均值
                        weights = psd_column / np.sum(psd_column)
                        mean_db = np.sum(ppsd.db_bin_centers * weights)
                        mean_values.append(mean_db)
                    else:
                        mean_values.append(np.nan)

                mean_array = np.array(mean_values)

                # 过滤掉NaN值
                valid_mask = ~np.isnan(mean_array)
                if np.any(valid_mask):
                    ax.plot(periods[valid_mask], mean_array[valid_mask],
                            color=mean_color,
                            linewidth=mean_linewidth,
                            linestyle=mean_linestyle,
                            alpha=mean_alpha,
                            label='Mean (均值)',
                            zorder=11)

        except Exception as e:
            logging.warning(f"无法绘制均值线: {e}")

    # 保存文件
    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        logging.info(f"PPSD图已保存: {filename}")

    # 显示图形
    if show:
        plt.show()

    return fig


def apply_custom_percentile_style_to_existing_plot(
        fig: plt.Figure,
        ppsd,
        percentiles: List[int] = [10, 50, 90],
        percentile_color: str = 'lightgray',
        percentile_linewidth: float = 1.0,
        percentile_linestyle: str = '-',
        percentile_alpha: float = 0.8) -> plt.Figure:
    """
    对已存在的PPSD图应用自定义百分位数线样式

    Parameters:
        fig: matplotlib Figure对象
        ppsd: ObsPy PPSD对象
        percentiles: 要显示的百分位数列表
        percentile_color: 百分位数线颜色
        percentile_linewidth: 百分位数线宽度
        percentile_linestyle: 百分位数线样式
        percentile_alpha: 百分位数线透明度

    Returns:
        修改后的matplotlib Figure对象
    """

    # 获取主要的PPSD图轴
    ax = fig.axes[0]

    # 移除现有的百分位数线（如果有的话）
    lines_to_remove = []
    for line in ax.lines:
        # 检查是否是百分位数线（通常是黑色的实线）
        if ((line.get_color() == 'k' or line.get_color() == 'black') and
                line.get_linewidth() > 1):
            lines_to_remove.append(line)

    for line in lines_to_remove:
        line.remove()

    # 添加自定义样式的百分位数线
    for percentile in percentiles:
        try:
            # 使用PPSD的get_percentile方法获取百分位数数据
            periods, psd_values = ppsd.get_percentile(percentile)

            # 绘制自定义样式的百分位数线
            label = (f'{percentile}th percentile'
                     if percentile in [10, 50, 90] else None)
            ax.plot(periods, psd_values,
                    color=percentile_color,
                    linewidth=percentile_linewidth,
                    linestyle=percentile_linestyle,
                    alpha=percentile_alpha,
                    label=label,
                    zorder=10)  # 确保线条在前景

        except Exception as e:
            logging.warning(f"无法绘制第{percentile}百分位数线: {e}")

    return fig


def get_available_percentile_styles() -> Dict[str, Dict[str, Any]]:
    """
    获取可用的百分位数线样式预设

    Returns:
        样式预设字典
    """

    styles = {
        'light_gray': {
            'percentile_color': 'lightgray',
            'percentile_linewidth': 1.0,
            'percentile_linestyle': '-',
            'percentile_alpha': 0.8,
            'description': '浅灰色细线，适合大多数配色方案'
        },
        'dark_gray': {
            'percentile_color': 'darkgray',
            'percentile_linewidth': 1.2,
            'percentile_linestyle': '-',
            'percentile_alpha': 0.9,
            'description': '深灰色中等粗细线条，对比度较高'
        },
        'dashed_gray': {
            'percentile_color': 'gray',
            'percentile_linewidth': 1.0,
            'percentile_linestyle': '--',
            'percentile_alpha': 0.7,
            'description': '灰色虚线，不干扰主要数据'
        },
        'thin_black': {
            'percentile_color': 'black',
            'percentile_linewidth': 0.8,
            'percentile_linestyle': '-',
            'percentile_alpha': 0.6,
            'description': '黑色细线，经典样式'
        },
        'blue_accent': {
            'percentile_color': 'steelblue',
            'percentile_linewidth': 1.0,
            'percentile_linestyle': '-',
            'percentile_alpha': 0.8,
            'description': '钢蓝色线条，现代感强'
        },
        'minimal': {
            'percentile_color': 'lightgray',
            'percentile_linewidth': 0.5,
            'percentile_linestyle': '-',
            'percentile_alpha': 0.5,
            'description': '极简样式，最小视觉干扰'
        }
    }

    return styles


def demo_percentile_styles(ppsd,
                           output_dir: str = "./output/plots/") -> None:
    """
    演示不同的百分位数线样式

    Parameters:
        ppsd: ObsPy PPSD对象
        output_dir: 输出目录
    """

    import os

    styles = get_available_percentile_styles()

    print("正在生成百分位数线样式演示...")

    for style_name, style_params in styles.items():
        print(f"生成样式: {style_name} - {style_params['description']}")

        # 移除description键，因为它不是绘图参数
        plot_params = {k: v for k, v in style_params.items()
                       if k != 'description'}

        # 生成图像
        filename = os.path.join(output_dir,
                                f"ppsd_percentile_style_{style_name}.png")

        plot_ppsd_with_custom_statistical_lines(
            ppsd,
            filename=filename,
            show=False,
            **plot_params
        )

        print(f"已保存: {filename}")

    print(f"百分位数线样式演示完成，共生成 {len(styles)} 个样式示例")


if __name__ == "__main__":
    # 演示代码
    print("自定义PPSD绘图模块")
    print("支持的百分位数线样式:")

    styles = get_available_percentile_styles()
    for name, style in styles.items():
        print(f"  {name}: {style['description']}")
