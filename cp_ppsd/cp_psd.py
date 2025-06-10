#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Author:
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
"""
PPSD 批量处理与可视化工具

本脚本用于地震学中的背景噪声分析，基于ObsPy库实现，支持通过TOML配置文件
进行批量地动噪声PPSD计算和可视化。

主要功能：
- 支持计算型配置文件进行PPSD计算并保存NPZ文件
- 支持绘图型配置文件加载NPZ数据并生成可视化图像
- 支持多种绘图类型：standard、temporal、spectrogram
- 支持分组配置文件（config_plot_grouped.toml）自动适配
- 详细的日志记录和错误处理

使用方法：
    python run_cp_ppsd.py config.toml                    # 仅计算
    python run_cp_ppsd.py config_plot.toml               # 仅绘图
    python run_cp_ppsd.py config.toml config_plot.toml   # 计算+绘图
"""

import matplotlib.pyplot as plt
import matplotlib
from typing import Dict, List
from pathlib import Path
from datetime import datetime
import traceback
import sys
import os
import logging
import argparse
import glob

matplotlib.use('Agg')  # 使用非交互式后端，不显示图片


try:
    import toml
except ImportError:
    print("错误：未安装 toml 库，请运行: pip install toml")
    sys.exit(1)

try:
    from obspy import read, read_inventory, UTCDateTime
    from obspy.signal import PPSD
    from obspy.core import Trace, Stream
    import numpy as np
except ImportError:
    print("错误：未安装 ObsPy 库，请运行: pip install obspy")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    # 如果没有tqdm，使用简单的替代
    def tqdm(iterable, *args, **kwargs):
        return iterable

# 检查可选依赖的导入
try:
    from .grouped_config_adapter import GroupedConfigAdapter
    GROUPED_CONFIG_ADAPTER_AVAILABLE = True
except ImportError:
    GROUPED_CONFIG_ADAPTER_AVAILABLE = False
    print("警告: grouped_config_adapter 不可用")

try:
    from .unified_config_adapter import UnifiedConfigAdapter
    UNIFIED_CONFIG_ADAPTER_AVAILABLE = True
except ImportError:
    UNIFIED_CONFIG_ADAPTER_AVAILABLE = False
    print("警告: unified_config_adapter 不可用")

try:
    from .custom_colormaps import (register_custom_colormaps,
                                   get_custom_colormap)
    CUSTOM_COLORMAPS_AVAILABLE = True
except ImportError:
    CUSTOM_COLORMAPS_AVAILABLE = False


class PPSDProcessor:
    """PPSD处理器主类"""

    def __init__(self, config_files: List[str]):
        """
        初始化PPSD处理器

        Args:
            config_files: 配置文件路径列表
        """
        self.config_files = config_files
        self.configs = []
        self.logger = None
        self.ppsd_data = {}  # 存储计算的PPSD数据

        # 加载配置文件
        self._load_configs()

        # 设置日志
        self._setup_logging()

        # 注册自定义配色方案
        self._register_custom_colormaps()

        # 设置全局字体大小（减小2号）
        plt.rcParams['font.size'] = 10

    def _load_configs(self):
        """加载所有配置文件（支持统一配置适配器）"""
        for config_file in self.config_files:
            if not os.path.exists(config_file):
                print(f"错误：配置文件 {config_file} 不存在")
                sys.exit(1)

            try:
                # 优先使用统一配置适配器
                if UNIFIED_CONFIG_ADAPTER_AVAILABLE:
                    print(f"使用统一配置适配器加载: {config_file}")

                    adapter = UnifiedConfigAdapter(config_file)
                    config = adapter.get_config()

                    # 显示格式信息
                    format_type = adapter.get_format()
                    format_descriptions = {
                        "grouped": "精细分组格式",
                        "simple": "简单分组格式",
                        "flat": "扁平格式"
                    }

                    print(f"检测到配置格式: {format_descriptions.get(format_type, '未知格式')}")
                    if hasattr(adapter, 'adapted_config') and 'version' in config:
                        print(f"配置版本: {config.get('version', 'N/A')}")
                    if hasattr(adapter, 'adapted_config') and 'description' in config:
                        print(f"配置描述: {config.get('description', 'N/A')}")

                elif GROUPED_CONFIG_ADAPTER_AVAILABLE:
                    # 备用：使用分组配置适配器
                    with open(config_file, 'r', encoding='utf-8') as f:
                        raw_config = toml.load(f)

                    is_grouped = self._is_grouped_config_structure(raw_config)

                    if is_grouped:
                        print(f"检测到分组配置文件: {config_file}")
                        print("使用分组配置适配器进行解析...")

                        adapter = GroupedConfigAdapter(config_file)
                        config = adapter.get_config()

                        print("配置适配成功")
                        print(f"配置版本: {config.get('version', 'N/A')}")
                        print(f"配置描述: {config.get('description', 'N/A')}")
                    else:
                        config = raw_config

                else:
                    # 最后备用：直接加载TOML
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = toml.load(f)
                    print(f"直接加载配置文件: {config_file}")

                config['_file_path'] = config_file
                self.configs.append(config)

            except Exception as e:
                print(f"错误：无法加载配置文件 {config_file}: {e}")
                print("提示：请检查配置文件格式是否正确")
                sys.exit(1)

    def _setup_logging(self):
        """设置日志系统"""
        # 从第一个配置文件获取日志设置
        log_level = self.configs[0].get('log_level', 'INFO')

        # 设置日志目录为项目根目录下的logs
        log_dir = './logs'

        # 创建日志目录
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # 设置日志格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        # 创建logger
        self.logger = logging.getLogger('cp_ppsd')
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # 清除已有的处理器
        self.logger.handlers.clear()

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_formatter = logging.Formatter(log_format)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # 文件处理器
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f'ppsd_processing_{timestamp}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        self.logger.info(f"日志系统初始化完成，日志文件: {log_file}")

    def _register_custom_colormaps(self):
        """注册自定义配色方案"""
        if CUSTOM_COLORMAPS_AVAILABLE:
            try:
                register_custom_colormaps()
                self.logger.info("自定义配色方案注册成功")
            except Exception as e:
                self.logger.warning(f"自定义配色方案注册失败: {e}")
        else:
            self.logger.debug("自定义配色方案模块不可用")

    def _is_calculation_config(self, config: Dict) -> bool:
        """判断是否为计算型配置文件"""
        file_path = config.get('_file_path', '')
        return (file_path.endswith('_calc.toml') or
                file_path.endswith('config.toml') or
                'mseed_pattern' in config)

    def _is_plot_config(self, config: Dict) -> bool:
        """判断是否为绘图型配置文件"""
        file_path = config.get('_file_path', '')
        return (file_path.endswith('_plot.toml') or
                'input_npz_dir' in config or
                'plot_type' in config.get('args', {}))

    def _find_mseed_files(self, pattern: str) -> List[str]:
        """查找MiniSEED文件"""
        if os.path.isdir(pattern):
            # 如果是目录，递归搜索
            extensions = ['*.mseed', '*.msd', '*.seed']
            files = []
            for ext in extensions:
                files.extend(
                    glob.glob(
                        os.path.join(
                            pattern,
                            '**',
                            ext),
                        recursive=True))
            return sorted(files)
        else:
            # 如果是glob模式
            return sorted(glob.glob(pattern))

    def _generate_filename(
            self,
            pattern: str,
            metadata: Dict,
            plot_type: str = None,
            data_starttime=None,
            data_endtime=None) -> str:
        """生成文件名"""
        if not pattern:
            # 使用默认命名规则
            if plot_type:
                return f"{plot_type}_{metadata.get('network', 'XX')}.{metadata.get('station', 'XXXX')}.{metadata.get('location', '')}.{metadata.get('channel', 'XXX')}.png"
            else:
                return f"PPSD_{metadata.get('network', 'XX')}.{metadata.get('station', 'XXXX')}.{metadata.get('location', '')}.{metadata.get('channel', 'XXX')}.npz"

        # 使用数据开始时间或当前时间
        if data_starttime is not None:
            # 使用MiniSEED数据的开始时间
            start_dt = data_starttime.datetime
            self.logger.debug(f"使用数据开始时间生成文件名: {start_dt}")
        else:
            # 回退到当前时间
            start_dt = datetime.now()
            self.logger.debug("使用当前时间生成文件名")

        # 使用数据结束时间（如果提供）
        if data_endtime is not None:
            end_dt = data_endtime.datetime
            self.logger.debug(f"使用数据结束时间生成文件名: {end_dt}")
        else:
            # 如果没有结束时间，使用开始时间
            end_dt = start_dt
            self.logger.debug("未提供结束时间，使用开始时间")

        # 替换占位符
        replacements = {
            'network': metadata.get('network', 'XX'),
            'station': metadata.get('station', 'XXXX'),
            'location': metadata.get('location', ''),
            'channel': metadata.get('channel', 'XXX'),
            # 开始时间相关变量
            'start_datetime': start_dt.strftime('%Y%m%d%H%M'),
            'start_year': str(start_dt.year),
            'start_month': f"{start_dt.month:02d}",
            'start_day': f"{start_dt.day:02d}",
            'start_hour': f"{start_dt.hour:02d}",
            'start_minute': f"{start_dt.minute:02d}",
            'start_second': f"{start_dt.second:02d}",
            'start_julday': f"{start_dt.timetuple().tm_yday:03d}",
            # 结束时间相关变量
            'end_datetime': end_dt.strftime('%Y%m%d%H%M'),
            'end_year': str(end_dt.year),
            'end_month': f"{end_dt.month:02d}",
            'end_day': f"{end_dt.day:02d}",
            'end_hour': f"{end_dt.hour:02d}",
            'end_minute': f"{end_dt.minute:02d}",
            'end_second': f"{end_dt.second:02d}",
            'end_julday': f"{end_dt.timetuple().tm_yday:03d}",
            # 兼容性变量 (等同于开始时间)
            'datetime': start_dt.strftime('%Y%m%d%H%M'),
            'year': str(start_dt.year),
            'month': f"{start_dt.month:02d}",
            'day': f"{start_dt.day:02d}",
            'hour': f"{start_dt.hour:02d}",
            'minute': f"{start_dt.minute:02d}",
            'second': f"{start_dt.second:02d}",
            'julday': f"{start_dt.timetuple().tm_yday:03d}",
        }

        if plot_type:
            replacements['plot_type'] = plot_type

        filename = pattern
        for key, value in replacements.items():
            filename = filename.replace(f'{{{key}}}', str(value))

        return filename

    def calculate_ppsd(self, config: Dict):
        """执行PPSD计算 - 每个MiniSEED文件生成一个NPZ文件，正确处理间隙"""
        self.logger.info("开始PPSD计算（单文件模式，支持间隙处理）")

        # 获取参数
        mseed_pattern = config.get('mseed_pattern')
        inventory_path = config.get('inventory_path')
        output_dir = config.get('output_dir', './ppsd_results')
        args = config.get('args', {})

        if not mseed_pattern or not inventory_path:
            raise ValueError("计算配置文件必须包含 mseed_pattern 和 inventory_path")

        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 读取仪器响应
        self.logger.info(f"读取仪器响应文件: {inventory_path}")
        try:
            inventory = read_inventory(inventory_path)
        except Exception as e:
            self.logger.error(f"无法读取仪器响应文件: {e}")
            raise

        # 查找数据文件
        mseed_files = self._find_mseed_files(mseed_pattern)
        if not mseed_files:
            raise ValueError(f"未找到匹配的数据文件: {mseed_pattern}")

        self.logger.info(f"找到 {len(mseed_files)} 个数据文件")

        # 获取间隙处理参数
        skip_on_gaps = args.get('skip_on_gaps', False)
        merge_fill_value = args.get('merge_fill_value', None)  # None表示使用masked array

        # 处理字符串形式的 "None"
        if isinstance(
                merge_fill_value,
                str) and merge_fill_value.lower() in [
                'none',
                'null']:
            merge_fill_value = None

        # ObsPy merge方法：0=standard, 1=interpolation, -1=cleanup
        merge_method = args.get('merge_method', 0)

        # 如果skip_on_gaps=True，强制不补零，保持原始间隙
        if skip_on_gaps:
            merge_fill_value = None
            self.logger.info(
                f"间隙处理设置: skip_on_gaps={skip_on_gaps} (强制不补零), fill_value={merge_fill_value}, method={merge_method}")
        else:
            self.logger.info(
                f"间隙处理设置: skip_on_gaps={skip_on_gaps}, fill_value={merge_fill_value}, method={merge_method}")

        # 逐个处理每个MiniSEED文件
        successful_files = 0
        failed_files = 0

        for mseed_file in tqdm(mseed_files, desc="处理MiniSEED文件"):
            try:
                self.logger.debug(f"处理文件: {mseed_file}")

                # 读取整个文件的Stream
                stream = read(mseed_file)
                self.logger.debug(f"文件包含 {len(stream)} 个trace")

                # 按通道分组trace（同一通道的不同时间段需要合并）
                channel_groups = {}
                for trace in stream:
                    trace_id = f"{
                        trace.stats.network}.{
                        trace.stats.station}.{
                        trace.stats.location}.{
                        trace.stats.channel}"
                    if trace_id not in channel_groups:
                        channel_groups[trace_id] = []
                    channel_groups[trace_id].append(trace)

                self.logger.debug(f"按通道分组后得到 {len(channel_groups)} 个通道组")

                # 处理每个通道组
                for channel_id, traces in channel_groups.items():
                    try:
                        self.logger.debug(f"处理通道 {channel_id}，包含 {len(traces)} 个trace段")

                        # 创建新的Stream并添加该通道的所有traces
                        channel_stream = Stream()
                        for trace in traces:
                            channel_stream.append(trace)

                        # 根据skip_on_gaps决定是否合并traces
                        if skip_on_gaps:
                            # skip_on_gaps=True: 不合并，每个连续段独立处理
                            self.logger.debug(
                                f"skip_on_gaps=True，保持 {
                                    len(channel_stream)} 个独立trace段，不进行合并")
                            traces_to_process = channel_stream.traces  # 使用原始的独立trace段
                        else:
                            # skip_on_gaps=False: 合并所有段
                            try:
                                self.logger.debug(
                                    f"skip_on_gaps=False，合并前: {
                                        len(channel_stream)} 个trace段")
                                if len(channel_stream) > 1:
                                    # 打印合并前的时间信息
                                    for i, tr in enumerate(channel_stream):
                                        self.logger.debug(
                                            f"  Trace {i}: {tr.stats.starttime} - {tr.stats.endtime} ({tr.stats.npts} 样本)")

                                    # 执行合并
                                    channel_stream.merge(
                                        method=merge_method,
                                        fill_value=merge_fill_value,
                                        interpolation_samples=0
                                    )

                                    self.logger.debug(
                                        f"合并后: {len(channel_stream)} 个trace段")
                                    for i, tr in enumerate(channel_stream):
                                        self.logger.debug(
                                            f"  合并Trace {i}: {tr.stats.starttime} - {tr.stats.endtime} ({tr.stats.npts} 样本)")
                                        # 检查是否包含masked array（表示存在间隙）
                                        if hasattr(tr.data, 'mask'):
                                            masked_count = tr.data.mask.sum() if tr.data.mask is not False else 0
                                            self.logger.debug(
                                                f"    包含 {masked_count} 个masked样本点（间隙）")
                                else:
                                    self.logger.debug("单个trace，无需合并")

                            except Exception as merge_error:
                                self.logger.error(
                                    f"合并trace失败 {channel_id}: {merge_error}")
                                # 如果合并失败，使用原始traces
                                self.logger.warning(f"回退到使用原始traces处理 {channel_id}")

                            traces_to_process = channel_stream.traces  # 使用合并后的trace(s)

                        # 处理trace(s)
                        for trace in traces_to_process:
                            try:
                                # 检查是否包含间隙（masked array）
                                has_gaps = hasattr(
                                    trace.data, 'mask') and trace.data.mask is not False
                                if has_gaps:
                                    gap_count = trace.data.mask.sum() if hasattr(trace.data, 'mask') else 0
                                    gap_percentage = (gap_count / len(trace.data)) * 100
                                    self.logger.info(
                                        f"Trace {
                                            trace.id} 包含间隙: {gap_count} 样本 ({
                                            gap_percentage:.1f}%)")
                                    self.logger.info(f"处理包含间隙的trace（合并模式）: {trace.id}")
                                else:
                                    if skip_on_gaps:
                                        self.logger.info(
                                            f"处理独立连续trace段（不合并模式）: {trace.id} ({trace.stats.starttime} - {trace.stats.endtime})")
                                    else:
                                        self.logger.info(f"处理连续trace: {trace.id}")

                                # 为每个trace生成唯一的NPZ文件
                                self._process_single_merged_trace_to_npz(
                                    trace, inventory, args, output_dir, config, mseed_file)
                                successful_files += 1

                            except Exception as e:
                                self.logger.error(
                                    f"处理合并后的trace失败 {
                                        trace.id} 从文件 {mseed_file}: {e}")
                                failed_files += 1
                                continue

                    except Exception as e:
                        self.logger.error(f"处理通道组失败 {channel_id} 从文件 {mseed_file}: {e}")
                        failed_files += 1
                        continue

            except Exception as e:
                self.logger.error(f"读取文件失败 {mseed_file}: {e}")
                failed_files += 1
                continue

        self.logger.info(f"PPSD计算完成 - 成功: {successful_files}, 失败: {failed_files}")

    def _process_single_merged_trace_to_npz(
            self,
            trace: Trace,
            inventory,
            args: Dict,
            output_dir: str,
            config: Dict,
            original_file: str):
        """为单个合并后的trace生成独立的NPZ文件"""
        # 获取PPSD参数
        special_handling = args.get('special_handling', None)
        # 处理字符串"None"的情况，转换为Python的None
        if special_handling == "None" or special_handling == "none" or special_handling == "null":
            special_handling = None

        ppsd_params = {
            'ppsd_length': args.get('ppsd_length', 3600),
            'overlap': args.get('overlap', 0.5),
            'period_smoothing_width_octaves': args.get('period_smoothing_width_octaves', 1.0),
            'period_step_octaves': args.get('period_step_octaves', 0.125),
            'period_limits': args.get('period_limits', [0.01, 1000.0]),
            'db_bins': args.get('db_bins', [-200.0, -50.0, 0.25]),
            'skip_on_gaps': args.get('skip_on_gaps', False),
            'special_handling': special_handling
        }

        # 根据special_handling类型准备metadata
        if special_handling == "ringlaser":
            # ringlaser模式：不进行仪器校正，仅除以sensitivity
            try:
                sensitivity = self._extract_sensitivity_from_inventory(trace, inventory)
                metadata = {'sensitivity': sensitivity}
                self.logger.debug(f"使用ringlaser模式，sensitivity: {sensitivity}")
            except Exception as e:
                self.logger.error(f"ringlaser模式下无法提取sensitivity {trace.id}: {e}")
                raise
        elif special_handling == "hydrophone":
            # hydrophone模式：仪器校正但不微分
            metadata = inventory
            self.logger.debug("使用hydrophone模式")
        elif special_handling is None:
            # 默认模式：标准地震仪处理（仪器校正+微分）
            metadata = inventory
            self.logger.debug("使用默认模式（标准地震仪处理）")
        else:
            # 其他模式使用完整的inventory
            metadata = inventory
            self.logger.warning(f"未知的special_handling值: {special_handling}，使用默认处理")

        # 创建PPSD对象
        try:
            ppsd = PPSD(trace.stats, metadata=metadata, **ppsd_params)
        except Exception as e:
            self.logger.error(f"创建PPSD对象失败 {trace.id}: {e}")
            raise

        # 添加数据（这里skip_on_gaps参数会正确工作）
        try:
            # 记录添加前的状态
            has_gaps = hasattr(trace.data, 'mask') and trace.data.mask is not False
            if has_gaps:
                gap_count = trace.data.mask.sum()
                self.logger.debug(f"向PPSD添加包含 {gap_count} 个间隙样本的trace: {trace.id}")

            ppsd.add(trace)

            # 记录PPSD处理结果
            n_segments = len(
                ppsd.times_processed) if hasattr(
                ppsd, 'times_processed') else 0
            self.logger.debug(f"PPSD处理结果: {n_segments} 个时间段")

        except Exception as e:
            self.logger.error(f"添加数据到PPSD失败 {trace.id}: {e}")
            # 如果是由于skip_on_gaps引起的错误，记录更详细的信息
            if 'gap' in str(e).lower():
                self.logger.info("由于skip_on_gaps=True，跳过了包含间隙的数据段")
            raise

        # 生成唯一的文件名（包含文件来源信息）
        metadata_dict = {
            'network': trace.stats.network,
            'station': trace.stats.station,
            'location': trace.stats.location,
            'channel': trace.stats.channel
        }

        # 获取原始文件名（不含路径和扩展名）
        original_filename = Path(original_file).stem

        # 生成文件名模式
        npz_pattern = config.get('output_npz_filename_pattern', '')
        if not npz_pattern:
            # 如果没有自定义模式，使用包含原始文件信息的默认模式
            npz_filename = f"PPSD_{original_filename}.npz"
        else:
            # 严格按照自定义模式生成文件名
            npz_filename = self._generate_filename(
                npz_pattern,
                metadata_dict,
                data_starttime=trace.stats.starttime,
                data_endtime=trace.stats.endtime)

        npz_path = os.path.join(output_dir, npz_filename)

        # 检查PPSD处理结果，只有存在有效时间段时才保存NPZ文件
        n_segments = len(ppsd.times_processed) if hasattr(
            ppsd, 'times_processed') and ppsd.times_processed else 0

        if n_segments == 0:
            self.logger.warning(f"PPSD处理结果为0个时间段，跳过NPZ文件保存: {trace.id}")
            self.logger.info("可能原因: 1) 找不到仪器响应信息, 2) 数据质量问题, 3) 数据长度不足")
            return

        # 保存NPZ文件
        try:
            ppsd.save_npz(npz_path)
            self.logger.info(f"保存NPZ文件: {npz_path}")

            # 记录详细统计信息
            self.logger.debug(
                f"NPZ文件统计 - 时间段数: {n_segments}, trace长度: {trace.stats.npts} 样本点")

            # 如果有间隙且成功处理，记录相关信息
            if has_gaps and n_segments > 0:
                self.logger.info(f"成功处理含间隙数据: {n_segments} 个有效时间段")

        except Exception as e:
            self.logger.error(f"保存NPZ文件失败 {npz_path}: {e}")
            raise

    def _extract_sensitivity_from_inventory(self, trace: Trace, inventory) -> float:
        """从StationXML inventory中提取sensitivity值"""
        try:
            # 获取trace的网络、台站、位置和通道信息
            network = trace.stats.network
            station = trace.stats.station
            location = trace.stats.location
            channel = trace.stats.channel
            starttime = trace.stats.starttime

            # 从inventory中获取响应信息
            response = inventory.get_response(
                network + '.' + station + '.' + location + '.' + channel, starttime)

            # 获取总体sensitivity
            sensitivity = response.instrument_sensitivity.value

            self.logger.debug(f"从StationXML提取sensitivity: {sensitivity} for {trace.id}")
            return sensitivity

        except Exception as e:
            self.logger.error(f"无法从StationXML提取sensitivity for {trace.id}: {e}")
            raise

    def plot_ppsd(self, config: Dict):
        """执行PPSD绘图 - 正确使用ObsPy的add_npz()方法合并文件"""
        self.logger.info("开始PPSD绘图")

        # 设置当前配置的字体大小
        self._current_font_size = config.get('font_size', 8)

        # 获取参数
        input_npz_dir = config.get('input_npz_dir')
        output_dir = config.get('output_dir', './ppsd_results/plots')
        inventory_path = config.get('inventory_path')
        args = config.get('args', {})

        if not input_npz_dir or not os.path.exists(input_npz_dir):
            raise ValueError(f"NPZ输入目录不存在: {input_npz_dir}")

        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 读取仪器响应（如果需要）
        inventory = None
        if inventory_path and os.path.exists(inventory_path):
            try:
                inventory = read_inventory(inventory_path)
                self.logger.info(f"成功读取仪器响应文件: {inventory_path}")
            except Exception as e:
                self.logger.warning(f"无法读取仪器响应文件: {e}")

        # 查找NPZ文件
            npz_files = glob.glob(os.path.join(input_npz_dir, '*.npz'))
        if not npz_files:
            raise ValueError(f"在 {input_npz_dir} 中未找到NPZ文件")

            self.logger.info(f"在 {input_npz_dir} 中找到 {len(npz_files)} 个NPZ文件")

        # 获取合并策略
        npz_merge_strategy = args.get('npz_merge_strategy', True)  # True: 合并, False: 单独

        if not npz_merge_strategy:  # False 表示单独绘图
            # 每个NPZ文件单独绘图
            self._plot_individual_npz_files(
                npz_files, inventory, args, output_dir, config)
        else:  # True 表示合并绘图
            # 按SEED ID分组并合并绘图
            self._plot_merged_npz_files(npz_files, inventory, args, output_dir, config)

        self.logger.info("PPSD绘图完成")

    def _plot_individual_npz_files(
            self,
            npz_files: List[str],
            inventory,
            args: Dict,
            output_dir: str,
            config: Dict):
        """每个NPZ文件单独绘图"""
        self.logger.info("使用单独模式绘图 - 每个NPZ文件单独处理")

        plot_types = args.get('plot_type', ['standard'])
        if isinstance(plot_types, str):
            plot_types = [plot_types]

        for npz_file in npz_files:
            try:
                # 加载单个PPSD对象
                ppsd = self._load_single_ppsd_from_npz(npz_file, inventory)

                # 生成trace ID用于文件命名
                trace_id = f"{
                    ppsd.network}.{
                    ppsd.station}.{
                    ppsd.location}.{
                    ppsd.channel}"
                npz_basename = os.path.basename(npz_file).replace('.npz', '')
                unique_trace_id = f"{trace_id}_{npz_basename}"

                # 为每种绘图类型生成图像
                for plot_type in plot_types:
                    try:
                        # 使用专门的单个文件绘图方法
                        self._create_plot(
                            ppsd, plot_type, unique_trace_id, args, output_dir, config)
                    except Exception as e:
                        self.logger.error(f"绘图失败 {unique_trace_id} - {plot_type}: {e}")
                        continue

            except Exception as e:
                self.logger.error(f"加载NPZ文件失败 {npz_file}: {e}")
                continue

    def _plot_merged_npz_files(
            self,
            npz_files: List[str],
            inventory,
            args: Dict,
            output_dir: str,
            config: Dict):
        """按SEED ID分组并使用add_npz()方法合并绘图"""
        self.logger.info("使用合并模式绘图 - 按SEED ID分组并合并")

        # 按SEED ID分组NPZ文件
        seed_groups = self._group_npz_files_by_seed_id(npz_files)
        self.logger.info(f"找到 {len(seed_groups)} 个不同的SEED ID组")

        plot_types = args.get('plot_type', ['standard'])
        if isinstance(plot_types, str):
            plot_types = [plot_types]

        self.logger.info(f"要处理的绘图类型: {plot_types}")

        # 为每个SEED ID组创建合并的PPSD对象
        for seed_id, file_list in seed_groups.items():
            try:
                self.logger.info(f"处理SEED ID: {seed_id}，包含 {len(file_list)} 个NPZ文件")

                # 使用ObsPy的正确方法创建合并的PPSD对象
                merged_ppsd = self._create_merged_ppsd_with_add_npz(
                    file_list, inventory)

                # 为每种绘图类型生成图像
                for plot_type in plot_types:
                    try:
                        self.logger.info(f"正在为 {seed_id} 创建 {plot_type} 图像")
                        # 使用SEED ID作为trace ID，文件名会包含"merged"标识
                        self._create_merged_plot_for_seed(
                            merged_ppsd, plot_type, seed_id, args, output_dir, config, len(file_list))
                    except Exception as e:
                        self.logger.error(f"合并绘图失败 {seed_id} - {plot_type}: {e}")
                        # 打印详细错误信息
                        import traceback
                        self.logger.error(f"详细错误信息: {traceback.format_exc()}")
                        continue

            except Exception as e:
                self.logger.error(f"创建合并PPSD失败 {seed_id}: {e}")
                continue

    def _group_npz_files_by_seed_id(self, npz_files: List[str]) -> Dict[str, List[str]]:
        """按SEED ID分组NPZ文件"""
        seed_groups = {}

        for npz_file in npz_files:
            try:
                # 尝试从文件名推断SEED ID
                # 假设文件名格式类似: original_filename_PPSD_datetime_NET-STA-LOC-CHA.npz
                basename = os.path.basename(npz_file)

                # 先尝试从NPZ文件中读取metadata来获取准确的SEED ID
                try:
                    npz_data = np.load(npz_file, allow_pickle=True)
                    # 优先使用 id 字段
                    if 'id' in npz_data:
                        seed_id = str(npz_data['id'])
                        self.logger.debug(
                            f"从NPZ id字段获取SEED ID: {seed_id} for {basename}")
                    elif '_network' in npz_data and '_station' in npz_data:
                        network = str(npz_data['_network'])
                        station = str(npz_data['_station'])
                        location = str(
                            npz_data['_location']) if '_location' in npz_data else ""
                        channel = str(
                            npz_data['_channel']) if '_channel' in npz_data else "XXX"
                        seed_id = f"{network}.{station}.{location}.{channel}"
                        self.logger.debug(
                            f"从NPZ metadata获取SEED ID: {seed_id} for {basename}")
                    else:
                        # 回退到文件名解析
                        seed_id = self._extract_seed_id_from_filename(basename)
                        self.logger.debug(f"从文件名推断SEED ID: {seed_id} for {basename}")
                except Exception as e:
                    # 如果读取NPZ失败，回退到文件名解析
                    seed_id = self._extract_seed_id_from_filename(basename)
                    self.logger.debug(
                        f"NPZ读取失败，从文件名推断SEED ID: {seed_id} for {basename} ({e})")

                if seed_id not in seed_groups:
                    seed_groups[seed_id] = []
                seed_groups[seed_id].append(npz_file)

            except Exception as e:
                self.logger.warning(f"无法确定文件的SEED ID {npz_file}: {e}")
                # 使用文件名作为唯一ID
                unique_id = os.path.basename(npz_file).replace('.npz', '')
                seed_groups[unique_id] = [npz_file]

        return seed_groups

    def _extract_seed_id_from_filename(self, filename: str) -> str:
        """从文件名提取SEED ID"""
        # 移除.npz扩展名
        basename = filename.replace('.npz', '')

        # 尝试多种文件名格式
        # 格式1: original_filename_PPSD_datetime_NET-STA-LOC-CHA.npz
        if '_PPSD_' in basename:
            parts = basename.split('_')
            # 查找最后一个看起来像SEED ID的部分 (NET-STA-LOC-CHA)
            for part in reversed(parts):
                if '-' in part and len(part.split('-')) >= 3:
                    # 将连字符替换为点号
                    return part.replace('-', '.')

        # 格式2: PPSD_NET.STA.LOC.CHA_datetime.npz
        if basename.startswith('PPSD_'):
            without_prefix = basename[5:]  # 移除'PPSD_'
            parts = without_prefix.split('_')
            if len(parts) > 0:
                # 第一部分应该是SEED ID
                candidate = parts[0]
                if candidate.count('.') >= 2:  # 至少包含network.station.location
                    return candidate

        # 如果无法解析，返回原始文件名
        self.logger.warning(f"无法从文件名解析SEED ID: {filename}")
        return basename

    def _load_single_ppsd_from_npz(self, npz_file: str, inventory) -> PPSD:
        """加载单个NPZ文件为PPSD对象"""
        try:
            if inventory:
                ppsd = PPSD.load_npz(npz_file, metadata=inventory)
            else:
                ppsd = PPSD.load_npz(npz_file)

            # 验证PPSD对象
            if not hasattr(ppsd, 'times_processed') or len(ppsd.times_processed) == 0:
                self.logger.warning(f"PPSD对象没有数据: {npz_file}")

            return ppsd

        except Exception as e:
            self.logger.error(f"加载PPSD对象失败 {npz_file}: {e}")
            raise

    def _create_merged_ppsd_with_add_npz(self, npz_files: List[str], inventory) -> PPSD:
        """使用ObsPy的add_npz()方法正确创建合并的PPSD对象"""
        if not npz_files:
            raise ValueError("没有NPZ文件可以合并")

        # 按文件名排序，确保一致的处理顺序
        sorted_files = sorted(npz_files)

        self.logger.info(f"开始合并 {len(sorted_files)} 个NPZ文件")
        self.logger.debug(f"文件列表: {[os.path.basename(f) for f in sorted_files]}")

        # 第一步：加载第一个文件作为基础
        base_file = sorted_files[0]
        try:
            if inventory:
                merged_ppsd = PPSD.load_npz(base_file, metadata=inventory)
            else:
                merged_ppsd = PPSD.load_npz(base_file)

            self.logger.info(f"基础PPSD加载成功: {os.path.basename(base_file)}")
            self.logger.debug(f"基础PPSD包含 {len(merged_ppsd.times_processed)} 个时间段")

        except Exception as e:
            self.logger.error(f"加载基础PPSD失败 {base_file}: {e}")
            raise

        # 第二步：使用add_npz()方法添加其他文件
        if len(sorted_files) > 1:
            for additional_file in sorted_files[1:]:
                try:
                    self.logger.debug(f"添加NPZ文件: {os.path.basename(additional_file)}")

                    # 记录添加前的时间段数量
                    before_count = len(merged_ppsd.times_processed)

                    # 使用add_npz方法添加文件
                    merged_ppsd.add_npz(additional_file, allow_pickle=False)

                    # 记录添加后的时间段数量
                    after_count = len(merged_ppsd.times_processed)
                    added_count = after_count - before_count

                    self.logger.info(
                        f"成功添加 {
                            os.path.basename(additional_file)}: +{added_count} 个时间段 (总计: {after_count})")

                except Exception as e:
                    self.logger.error(f"添加NPZ文件失败 {additional_file}: {e}")
                    # 继续处理其他文件，不中断整个合并过程
                    continue

        # 验证最终结果
        final_count = len(merged_ppsd.times_processed)
        self.logger.info(f"NPZ合并完成: 最终包含 {final_count} 个时间段")

        if final_count == 0:
            self.logger.warning("合并后的PPSD对象没有数据！")

        return merged_ppsd

    def _create_plot(
            self,
            ppsd: PPSD,
            plot_type: str,
            trace_id: str,
            args: Dict,
            output_dir: str,
            config: Dict):
        """为单个PPSD对象创建图像"""
        self.logger.debug(f"创建 {plot_type} 图像: {trace_id}")

        # 检查PPSD对象是否有数据
        if len(ppsd.times_processed) == 0:
            self.logger.warning(f"跳过 {trace_id} - {plot_type}: PPSD对象没有数据")
            return

        # 生成文件名
        metadata = {
            'network': ppsd.network,
            'station': ppsd.station,
            'location': ppsd.location,
            'channel': ppsd.channel
        }

        # 获取数据的开始和结束时间用于文件命名
        if ppsd.times_processed:
            data_start_time = min(ppsd.times_processed)
            data_end_time = max(ppsd.times_processed)
            self.logger.debug(f"使用数据时间范围生成文件名: {data_start_time} - {data_end_time}")
        else:
            data_start_time = None
            data_end_time = None
            self.logger.debug("没有时间信息，将使用当前时间")

        filename_pattern = config.get('output_filename_pattern', '')
        if filename_pattern:
            filename = self._generate_filename(
                filename_pattern,
                metadata,
                plot_type,
                data_start_time,
                data_end_time)
        else:
            # 使用默认文件命名
            if data_start_time and data_end_time:
                start_str = data_start_time.strftime('%Y%m%d%H%M')
                end_str = data_end_time.strftime('%Y%m%d%H%M')
                filename = f"{plot_type}_{start_str}_{end_str}_{
                    ppsd.network}.{
                    ppsd.station}.{
                    ppsd.location}.{
                    ppsd.channel}.png"
            else:
                filename = f"{plot_type}_{
                    ppsd.network}.{
                    ppsd.station}.{
                    ppsd.location}.{
                    ppsd.channel}.png"

        filepath = os.path.join(output_dir, filename)

        # 生成个别绘图模式的标题：第一行是SEED ID，第二行是时间范围
        seed_id = f"{ppsd.network}.{ppsd.station}.{ppsd.location}.{ppsd.channel}"
        if data_start_time and data_end_time:
            formatted_title = f"{seed_id}\n{
                data_start_time.strftime('%Y-%m-%d %H:%M')} - {
                data_end_time.strftime('%Y-%m-%d %H:%M')}"
        else:
            formatted_title = seed_id

        # 调用通用绘图方法，传递格式化的标题
        self._draw_plot(ppsd, plot_type, args, formatted_title, is_merged=False)

        # 保存图像（保持硬编码的dpi=150）
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        self.logger.info(f"保存图像: {os.path.basename(filename)}")

    def _draw_plot(
            self,
            ppsd: PPSD,
            plot_type: str,
            args: Dict,
            title_prefix: str,
            is_merged: bool = False):
        """通用绘图方法，处理实际的绘图逻辑"""
        if plot_type == 'standard':
            self._plot_standard(ppsd, args)
            if is_merged:
                # 合并图的标题包含时间范围
                start_time = min(ppsd.times_processed)
                end_time = max(ppsd.times_processed)
                title = f"{title_prefix}\n{
                    start_time.strftime('%Y-%m-%d %H:%M')} - {
                    end_time.strftime('%Y-%m-%d %H:%M')}"
            else:
                # 单个文件的标题
                title = title_prefix
            plt.title(title, fontsize=self._current_font_size + 1)

        elif plot_type == 'temporal':
            self._plot_temporal(ppsd, args)
            if is_merged:
                start_time = min(ppsd.times_processed)
                end_time = max(ppsd.times_processed)
                title = (f"{title_prefix}\n"
                         f"{start_time.strftime('%Y-%m-%d %H:%M')} - "
                         f"{end_time.strftime('%Y-%m-%d %H:%M')}")
            else:
                title = title_prefix
            plt.title(title, fontsize=self._current_font_size + 1)

        elif plot_type == 'spectrogram':
            self._plot_spectrogram(ppsd, args)
            if is_merged:
                start_time = min(ppsd.times_processed)
                end_time = max(ppsd.times_processed)
                title = (f"{title_prefix}\n"
                         f"{start_time.strftime('%Y-%m-%d %H:%M')} - "
                         f"{end_time.strftime('%Y-%m-%d %H:%M')}")
            else:
                title = title_prefix
            plt.title(title, fontsize=self._current_font_size + 1)

        else:
            raise ValueError(f"不支持的绘图类型: {plot_type}")

    def _create_merged_plot_for_seed(
            self,
            ppsd: PPSD,
            plot_type: str,
            seed_id: str,
            args: Dict,
            output_dir: str,
            config: Dict,
            file_count: int):
        """为合并的PPSD对象创建图像"""
        self.logger.debug(f"创建合并 {plot_type} 图像: {seed_id} (来自{file_count}个文件)")

        # 检查PPSD对象是否有数据
        if len(ppsd.times_processed) == 0:
            self.logger.warning(f"跳过 {seed_id} - {plot_type}: 合并后的PPSD对象没有数据")
            return

        # 生成文件名，标明是合并的结果
        metadata = {
            'network': ppsd.network,
            'station': ppsd.station,
            'location': ppsd.location,
            'channel': ppsd.channel
        }

        # 获取时间范围用于文件命名
        start_time = min(ppsd.times_processed)
        end_time = max(ppsd.times_processed)

        # 生成合并文件名
        start_str = start_time.strftime('%Y%m%d%H%M')
        end_str = end_time.strftime('%Y%m%d%H%M')

        filename_pattern = config.get('output_filename_pattern', '')
        if filename_pattern:
            # 修改模式以体现合并特性
            modified_pattern = filename_pattern.replace(
                '{datetime}', f'merged_{start_str}-{end_str}')
            filename = self._generate_filename(
                modified_pattern, metadata, plot_type, start_time, end_time)
        else:
            # 使用默认的合并文件命名
            filename = f"{plot_type}_merged_{start_str}-{end_str}_{
                ppsd.network}.{
                ppsd.station}.{
                ppsd.location}.{
                ppsd.channel}_({file_count}files).png"

        filepath = os.path.join(output_dir, filename)

        # 调用通用绘图方法
        self._draw_plot(ppsd, plot_type, args, seed_id, is_merged=True)

        # 保存图像（保持硬编码的dpi=150）
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        self.logger.info(f"保存合并图像: {filename}")

    def _plot_merged_ppsd(
            self,
            ppsd_objects: Dict,
            plot_types: List[str],
            args: Dict,
            output_dir: str,
            config: Dict):
        """合并绘图：将相同SEED ID的PPSD对象合并到一张图中"""
        self.logger.info("使用合并模式绘图")

        # 按SEED ID分组PPSD对象
        seed_groups = {}
        for trace_id, ppsd in ppsd_objects.items():
            seed_id = f"{ppsd.network}.{ppsd.station}.{ppsd.location}.{ppsd.channel}"
            if seed_id not in seed_groups:
                seed_groups[seed_id] = []
            seed_groups[seed_id].append((trace_id, ppsd))

        self.logger.info(f"找到 {len(seed_groups)} 个不同的SEED ID组")

        # 为每个SEED ID组和每种绘图类型生成合并图像
        for seed_id, ppsd_list in seed_groups.items():
            for plot_type in plot_types:
                try:
                    self._create_merged_plot(
                        ppsd_list, plot_type, seed_id, args, output_dir, config)
                except Exception as e:
                    self.logger.error(f"合并绘图失败 {seed_id} - {plot_type}: {e}")
                    continue

    def _create_merged_plot(
            self,
            ppsd_list: List,
            plot_type: str,
            seed_id: str,
            args: Dict,
            output_dir: str,
            config: Dict):
        """创建合并的图像"""
        self.logger.debug(f"创建合并 {plot_type} 图像: {seed_id}")

        if not ppsd_list:
            self.logger.warning(f"跳过 {seed_id} - {plot_type}: 没有PPSD数据")
            return

        # 使用第一个PPSD对象的元数据
        first_ppsd = ppsd_list[0][1]
        metadata = {
            'network': first_ppsd.network,
            'station': first_ppsd.station,
            'location': first_ppsd.location,
            'channel': first_ppsd.channel
        }

        # 获取时间范围
        all_times = []
        for trace_id, ppsd in ppsd_list:
            if hasattr(ppsd, 'times_processed') and len(ppsd.times_processed) > 0:
                all_times.extend(ppsd.times_processed)

        # 生成合并文件名
        if all_times:
            start_time = min(all_times)
            end_time = max(all_times)
            # 使用时间范围生成文件名
            filename_pattern = config.get('output_filename_pattern', '')
            if filename_pattern:
                # 修改文件名模式以反映合并特性
                if '{datetime}' in filename_pattern:
                    # 替换为时间范围
                    start_str = start_time.strftime('%Y%m%d%H%M')
                    end_str = end_time.strftime('%Y%m%d%H%M')
                    filename_pattern = filename_pattern.replace(
                        '{datetime}', f'merged_{start_str}-{end_str}')
                filename = self._generate_filename(
                    filename_pattern, metadata, plot_type, start_time, end_time)
            else:
                # 默认合并文件名
                start_str = start_time.strftime('%Y%m%d%H%M')
                end_str = end_time.strftime('%Y%m%d%H%M')
                filename = f"{plot_type}_merged_{start_str}-{end_str}_{seed_id}.png"
        else:
            # 如果没有时间信息，使用简单的合并文件名
            filename = f"{plot_type}_longterm_{seed_id}.png"

        filepath = os.path.join(output_dir, filename)

        # 绘制图像
        if plot_type == 'standard':
            self._plot_merged_standard(ppsd_list, args)
        elif plot_type == 'temporal':
            self._plot_merged_temporal(ppsd_list, args)
        elif plot_type == 'spectrogram':
            self._plot_merged_spectrogram(ppsd_list, args)
        else:
            raise ValueError(f"不支持的绘图类型: {plot_type}")

        # 保存图像（保持硬编码的dpi=150）
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        self.logger.info(f"保存合并图像: {filepath}")

    def _merge_ppsd_objects(self, ppsd_objects: List[PPSD]) -> PPSD:
        """合并多个PPSD对象"""
        if not ppsd_objects:
            raise ValueError("没有PPSD对象可以合并")

        if len(ppsd_objects) == 1:
            return ppsd_objects[0]

        # 使用第一个PPSD作为基础
        base_ppsd = ppsd_objects[0]

        # 创建一个新的PPSD对象，复制第一个的设置
        merged_ppsd = PPSD(
            stats=base_ppsd.stats,
            metadata=base_ppsd.metadata,
            ppsd_length=base_ppsd.ppsd_length,
            overlap=base_ppsd.overlap,
            period_smoothing_width_octaves=base_ppsd.period_smoothing_width_octaves,
            period_step_octaves=base_ppsd.period_step_octaves,
            period_limits=base_ppsd.period_limits,
            db_bins=base_ppsd.db_bins,
            special_handling=base_ppsd.special_handling,
            skip_on_gaps=base_ppsd.skip_on_gaps
        )

        # 合并所有PPSD的数据
        for ppsd in ppsd_objects:
            # 将每个PPSD的直方图数据添加到合并的PPSD中
            if hasattr(ppsd, '_binned_psds') and len(ppsd._binned_psds) > 0:
                for binned_psd in ppsd._binned_psds:
                    merged_ppsd._binned_psds.append(binned_psd)

            # 合并时间信息
            if hasattr(ppsd, 'times_processed'):
                merged_ppsd.times_processed.extend(ppsd.times_processed)

            # 合并其他相关数据
            if hasattr(ppsd, 'times_data'):
                merged_ppsd.times_data.extend(ppsd.times_data)

        # 重新计算直方图
        if hasattr(merged_ppsd, '_calculate_histogram'):
            merged_ppsd._calculate_histogram()

        return merged_ppsd

    def _plot_merged_standard(self, ppsd_list: List, args: Dict):
        """绘制合并的标准PPSD图"""
        if not ppsd_list:
            return

        # 准备绘图参数
        plot_params = {
            'period_lim': args.get('period_lim', [0.01, 1000.0]),
            'show_coverage': False  # 禁用 ObsPy 内置的数据覆盖度显示
        }

        # 添加配色方案支持
        if 'standard_cmap' in args:
            cmap_name = args['standard_cmap']
            # 首先尝试从自定义配色方案中获取
            if CUSTOM_COLORMAPS_AVAILABLE:
                custom_cmap = get_custom_colormap(cmap_name)
                if custom_cmap is not None:
                    plot_params['cmap'] = custom_cmap
                else:
                    # 如果不是自定义配色方案，则使用matplotlib标准配色方案
                    plot_params['cmap'] = plt.get_cmap(cmap_name)
            else:
                plot_params['cmap'] = plt.get_cmap(cmap_name)

        # 检查是否需要自定义百分位数线样式
        custom_percentile_style = (
            'percentile_color' in args or
            'percentile_linewidth' in args or
            'percentile_linestyle' in args or
            'percentile_alpha' in args
        )

        # 检查是否需要自定义皮特森曲线样式
        custom_peterson_style = (
            'peterson_linewidth' in args or
            'peterson_linestyle' in args or
            'peterson_alpha' in args or
            'peterson_nlnm_color' in args or
            'peterson_nhnm_color' in args
        )

        # 检查是否需要自定义mode和mean线样式
        custom_mode_style = (
            'mode_color' in args or
            'mode_linewidth' in args or
            'mode_linestyle' in args or
            'mode_alpha' in args
        )

        custom_mean_style = (
            'mean_color' in args or
            'mean_linewidth' in args or
            'mean_linestyle' in args or
            'mean_alpha' in args
        )

        # 如果需要自定义皮特森曲线样式，先不显示噪声模型
        if custom_peterson_style and args.get('show_noise_models', True):
            plot_params['show_noise_models'] = False
            show_custom_peterson = True
        else:
            # 使用标准皮特森曲线
            plot_params['show_noise_models'] = args.get('show_noise_models', True)
            show_custom_peterson = False

        # 如果需要自定义mode和mean线样式，先不显示
        if custom_mode_style and args.get('show_mode', False):
            plot_params['show_mode'] = False
            show_custom_mode = True
        else:
            # 使用标准mode线
            plot_params['show_mode'] = args.get('show_mode', False)
            show_custom_mode = False

        if custom_mean_style and args.get('show_mean', False):
            plot_params['show_mean'] = False
            show_custom_mean = True
        else:
            # 使用标准mean线
            plot_params['show_mean'] = args.get('show_mean', False)
            show_custom_mean = False

        # 如果需要自定义百分位数线样式，先不显示百分位数线
        if custom_percentile_style and args.get('show_percentiles', False):
            plot_params['show_percentiles'] = False
            show_custom_percentiles = True
            percentiles = args.get('percentiles', [10, 50, 90])
        else:
            # 使用标准百分位数线
            if 'show_percentiles' in args:
                plot_params['show_percentiles'] = args['show_percentiles']
            if 'percentiles' in args:
                plot_params['percentiles'] = args['percentiles']
            show_custom_percentiles = False

        # 添加其他标准图参数（只包含ObsPy支持的参数）
        # 注意：如果已经设置了自定义样式，就不要覆盖这些设置
        if 'show_histogram' in args:
            plot_params['show_histogram'] = args['show_histogram']
        if 'show_mode' in args and not custom_mode_style:
            plot_params['show_mode'] = args['show_mode']
        if 'show_mean' in args and not custom_mean_style:
            plot_params['show_mean'] = args['show_mean']
        if 'xaxis_frequency' in args:
            plot_params['xaxis_frequency'] = args['xaxis_frequency']
        if 'cumulative_plot' in args:
            plot_params['cumulative'] = args['cumulative_plot']
            self.logger.debug(f"设置累积模式: cumulative_plot={args['cumulative_plot']}")
        if 'cumulative_number_of_colors' in args:
            plot_params['cumulative_number_of_colors'] = args['cumulative_number_of_colors']
            self.logger.debug(f"设置累积颜色数量: {args['cumulative_number_of_colors']}")

        self.logger.debug(f"最终plot_params包含的参数: {list(plot_params.keys())}")
        if 'cumulative' in plot_params:
            self.logger.debug(f"将传递给ObsPy的cumulative参数: {plot_params['cumulative']}")

        # 如果只有一个PPSD，直接绘制
        if len(ppsd_list) == 1:
            main_ppsd = ppsd_list[0][1]
            main_ppsd.plot(**plot_params)
            # 设置小字体
            self._set_font_size()

            # 处理网格显示
            if 'standard_grid' in args:
                ax = plt.gca()
                ax.grid(args['standard_grid'])
                self.logger.debug(f"设置网格显示: {args['standard_grid']}")

            # 如果需要自定义皮特森曲线样式，手动添加
            if show_custom_peterson:
                self._add_custom_peterson_curves(args)

            # 如果需要自定义百分位数线样式，手动添加
            if show_custom_percentiles:
                self._add_custom_percentile_lines(main_ppsd, percentiles, args)

            # 如果需要自定义mode线样式，手动添加
            if show_custom_mode:
                self._add_custom_mode_line(main_ppsd, args)

            # 如果需要自定义mean线样式，手动添加
            if show_custom_mean:
                self._add_custom_mean_line(main_ppsd, args)

            return

        # 多个PPSD的情况：创建一个新的合并PPSD对象
        try:
            merged_ppsd = self._merge_ppsd_objects([ppsd[1] for ppsd in ppsd_list])
            merged_ppsd.plot(**plot_params)
            # 设置小字体
            self._set_font_size()

            # 处理网格显示
            if 'standard_grid' in args:
                ax = plt.gca()
                ax.grid(args['standard_grid'])
                self.logger.debug(f"设置网格显示: {args['standard_grid']}")

            # 如果需要自定义皮特森曲线样式，手动添加
            if show_custom_peterson:
                self._add_custom_peterson_curves(args)

            # 如果需要自定义百分位数线样式，手动添加
            if show_custom_percentiles:
                self._add_custom_percentile_lines(merged_ppsd, percentiles, args)

            # 如果需要自定义mode线样式，手动添加
            if show_custom_mode:
                self._add_custom_mode_line(merged_ppsd, args)

            # 如果需要自定义mean线样式，手动添加
            if show_custom_mean:
                self._add_custom_mean_line(merged_ppsd, args)

            # 设置标题
            plt.title(f"{merged_ppsd.network}.{merged_ppsd.station}."
                      f"{merged_ppsd.location}.{merged_ppsd.channel}",
                      fontsize=self._current_font_size + 1)

        except Exception as e:
            self.logger.warning(f"PPSD合并失败，使用第一个PPSD: {e}")
            # 回退到使用第一个PPSD
            main_ppsd = ppsd_list[0][1]
            main_ppsd.plot(**plot_params)
            # 设置小字体
            self._set_font_size()

            # 处理网格显示
            if 'standard_grid' in args:
                ax = plt.gca()
                ax.grid(args['standard_grid'])
                self.logger.debug(f"设置网格显示: {args['standard_grid']}")

            # 如果需要自定义皮特森曲线样式，手动添加
            if show_custom_peterson:
                self._add_custom_peterson_curves(args)

            # 如果需要自定义百分位数线样式，手动添加
            if show_custom_percentiles:
                self._add_custom_percentile_lines(main_ppsd, percentiles, args)

            # 如果需要自定义mode线样式，手动添加
            if show_custom_mode:
                self._add_custom_mode_line(main_ppsd, args)

            # 如果需要自定义mean线样式，手动添加
            if show_custom_mean:
                self._add_custom_mean_line(main_ppsd, args)

            plt.title(f"{main_ppsd.network}.{main_ppsd.station}."
                      f"{main_ppsd.location}.{main_ppsd.channel}",
                      fontsize=self._current_font_size + 1)

    def _plot_merged_temporal(self, ppsd_list: List, args: Dict):
        """绘制合并的时间演化图"""
        if not ppsd_list:
            return

        # 获取temporal配置参数
        periods = args.get('temporal_plot_periods', [1.0, 8.0, 20.0])
        time_format = args.get('time_format_x_temporal', '%H:%M')
        cmap = args.get('temporal_cmap', 'Blues')

        # 构建ObsPy plot_temporal支持的参数
        plot_params = {}

        # color参数 - ObsPy原生支持
        temporal_color = args.get('temporal_color', None)
        if temporal_color:
            plot_params['color'] = temporal_color

        # linestyle参数 - ObsPy原生支持
        temporal_linestyle = args.get('temporal_linestyle', '-')
        if temporal_linestyle:
            plot_params['linestyle'] = temporal_linestyle

        # linewidth参数 - 保存供后续处理使用（ObsPy可能不原生支持）
        temporal_linewidth = args.get('temporal_linewidth', 1.0)

        # marker参数 - ObsPy原生支持
        temporal_marker = args.get('temporal_marker', None)
        if temporal_marker:
            plot_params['marker'] = temporal_marker

        # marker_size参数 - 保存供后续处理使用
        temporal_marker_size = args.get('temporal_marker_size', 4.0)

        # 对于时间演化图，合并多个PPSD的时间序列数据
        # 这里使用第一个PPSD作为基础
        main_ppsd = ppsd_list[0][1]
        main_ppsd.plot_temporal(periods, **plot_params)

        # 在ObsPy绘图完成后手动调整线条属性
        import matplotlib.pyplot as plt
        ax = plt.gca()

        # 调整标记大小
        if temporal_marker:
            for line in ax.get_lines():
                if line.get_marker() != 'None':
                    line.set_markersize(temporal_marker_size)  # 使用配置的标记大小

        # 调整线条宽度
        if temporal_linewidth and temporal_linewidth != 1.0:
            for line in ax.get_lines():
                line.set_linewidth(temporal_linewidth)

        # 设置小字体
        self._set_font_size()

        # 尝试手动设置配色方案
        try:
            # 获取当前图形的colorbar或imshow对象，尝试应用自定义配色
            ax = plt.gca()
            for im in ax.get_images():
                if hasattr(im, 'set_cmap'):
                    im.set_cmap(cmap)
        except Exception as e:
            # 这里无法使用self.logger，因为这是类方法，但没有logger引用
            pass

        # 设置时间轴格式
        try:
            import matplotlib.dates as mdates
            ax = plt.gca()
            # 强制应用时间格式
            formatter = mdates.DateFormatter(time_format)
            ax.xaxis.set_major_formatter(formatter)
            # 自动旋转标签以避免重叠
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            # 确保时间轴标签重新计算
            ax.figure.canvas.draw_idle()
        except Exception as e:
            self.logger.debug(f"merged temporal时间格式应用失败: {e}")

        # 获取时间范围并设置标题
        all_times = []
        for trace_id, ppsd in ppsd_list:
            if hasattr(ppsd, 'times_processed') and len(ppsd.times_processed) > 0:
                all_times.extend(ppsd.times_processed)

        seed_id = f"{
            main_ppsd.network}.{
            main_ppsd.station}.{
            main_ppsd.location}.{
                main_ppsd.channel}"

        if all_times:
            start_time = min(all_times)
            end_time = max(all_times)

            title = (f"{seed_id}\n"
                     f"{start_time.strftime('%Y-%m-%d %H:%M')} - "
                     f"{end_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            title = f"{seed_id}"

        plt.title(title)

    def _plot_temporal(self, ppsd: PPSD, args: Dict):
        """绘制时间演化图

        基于ObsPy API，plot_temporal支持的参数：
        - period: 要绘制的周期值
        - color: 线条颜色
        - legend: 是否显示图例
        - grid: 是否显示网格
        - linestyle: 线条样式
        - marker: 线条标记
        - filename: 输出文件名(由框架处理)
        - show: 是否显示图像(由框架处理)
        """
        # 获取temporal配置参数
        periods = args.get('temporal_plot_periods', [1.0, 8.0, 20.0])

        # 构建ObsPy plot_temporal支持的参数
        plot_params = {}

        # color参数 - ObsPy原生支持
        # 注意：对于多个周期，color应该是颜色列表或None
        temporal_color = args.get('temporal_color', None)
        if temporal_color:
            plot_params['color'] = temporal_color

        # linestyle参数 - ObsPy原生支持
        temporal_linestyle = args.get('temporal_linestyle', '-')
        if temporal_linestyle:
            plot_params['linestyle'] = temporal_linestyle

        # linewidth参数 - 保存供后续处理使用（ObsPy可能不原生支持）
        temporal_linewidth = args.get('temporal_linewidth', 1.0)

        # marker参数 - ObsPy原生支持
        temporal_marker = args.get('temporal_marker', None)
        if temporal_marker:
            plot_params['marker'] = temporal_marker

        # marker_size参数 - 保存供后续处理使用
        temporal_marker_size = args.get('temporal_marker_size', 4.0)

        # 使用ObsPy的plot_temporal方法
        ppsd.plot_temporal(periods, **plot_params)

        # 在ObsPy绘图完成后手动调整线条属性
        ax = plt.gca()

        # 调整标记大小
        if temporal_marker:
            for line in ax.get_lines():
                if line.get_marker() != 'None':
                    line.set_markersize(temporal_marker_size)  # 使用配置的标记大小

        # 调整线条宽度
        if temporal_linewidth and temporal_linewidth != 1.0:
            for line in ax.get_lines():
                line.set_linewidth(temporal_linewidth)

        # 设置小字体
        self._set_font_size()

        # 添加包含时间范围的标题
        if hasattr(ppsd, 'times_processed') and len(ppsd.times_processed) > 0:
            start_time = min(ppsd.times_processed)
            end_time = max(ppsd.times_processed)
            n_segments = len(ppsd.times_processed)

            seed_id = f"{ppsd.network}.{ppsd.station}.{ppsd.location}.{ppsd.channel}"
            title = (f"{seed_id}\n"
                     f"{start_time.strftime('%Y-%m-%d %H:%M')} - "
                     f"{end_time.strftime('%Y-%m-%d %H:%M')}")
            plt.title(title, fontsize=self._current_font_size + 1)

        # 手动应用时间格式 (ObsPy不直接支持)
        time_format = args.get('time_format_x_temporal', '%H:%M')
        try:
            import matplotlib.dates as mdates
            ax = plt.gca()
            # 强制应用时间格式，不管是否为默认格式
            ax.xaxis.set_major_formatter(mdates.DateFormatter(time_format))
            # 确保时间轴标签重新计算
            ax.figure.canvas.draw_idle()
        except Exception as e:
            self.logger.debug(f"应用temporal时间格式失败: {e}")

    def _plot_spectrogram(self, ppsd: PPSD, args: Dict):
        """绘制频谱图

        基于ObsPy API，plot_spectrogram支持的参数：
        - cmap: 颜色映射
        - clim: 颜色限制范围 [min, max]
        - grid: 是否显示网格
        - filename: 输出文件名(由框架处理)
        - show: 是否显示图像(由框架处理)
        """
        # 构建ObsPy plot_spectrogram支持的参数
        plot_params = {}

        # cmap参数 - ObsPy原生支持
        spectrogram_cmap = args.get('spectrogram_cmap', 'viridis')
        if spectrogram_cmap:
            # 首先尝试从自定义配色方案中获取
            if CUSTOM_COLORMAPS_AVAILABLE:
                custom_cmap = get_custom_colormap(spectrogram_cmap)
                if custom_cmap is not None:
                    plot_params['cmap'] = custom_cmap
                    self.logger.debug(f"使用自定义spectrogram配色方案: {spectrogram_cmap}")
                else:
                    # 如果不是自定义配色方案，则使用matplotlib标准配色方案
                    plot_params['cmap'] = spectrogram_cmap
                    self.logger.debug(f"使用标准spectrogram配色方案: {spectrogram_cmap}")
            else:
                plot_params['cmap'] = spectrogram_cmap
                self.logger.debug(f"使用spectrogram配色方案: {spectrogram_cmap}")

        # clim参数 - ObsPy原生支持
        clim = args.get('clim', [-180, -100])
        if clim:
            plot_params['clim'] = clim

        # grid参数 - ObsPy原生支持
        if 'spectrogram_grid' in args:
            plot_params['grid'] = args['spectrogram_grid']

        # 使用ObsPy的plot_spectrogram方法
        ppsd.plot_spectrogram(**plot_params)

        # 设置小字体
        self._set_font_size()

        # 立即在ObsPy绘图完成后应用时间格式 - 修正：应用到X轴而不是Y轴
        time_format = args.get('time_format_x_spectrogram', '%Y-%m-%d')
        try:
            import matplotlib.dates as mdates
            ax = plt.gca()
            # 修正：spectrogram的时间轴是X轴，不是Y轴！
            self.logger.debug(f"应用spectrogram时间格式到X轴: {time_format}")
            formatter = mdates.DateFormatter(time_format)
            ax.xaxis.set_major_formatter(formatter)  # 修正：应用到X轴

            # 强制重新计算和刷新时间轴标签
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')  # X轴标签旋转
            ax.figure.canvas.draw_idle()

            # 额外的强制刷新步骤
            plt.draw()
            ax.relim()
            ax.autoscale_view()

            self.logger.debug("spectrogram时间格式应用成功")
        except Exception as e:
            self.logger.debug(f"应用spectrogram时间格式失败: {e}")

        # 添加包含时间范围的标题
        if hasattr(ppsd, 'times_processed') and len(ppsd.times_processed) > 0:
            start_time = min(ppsd.times_processed)
            end_time = max(ppsd.times_processed)

            seed_id = f"{ppsd.network}.{ppsd.station}.{ppsd.location}.{ppsd.channel}"
            title = (f"{seed_id}\n"
                     f"{start_time.strftime('%Y-%m-%d %H:%M')} - "
                     f"{end_time.strftime('%Y-%m-%d %H:%M')}")
            plt.title(title, fontsize=self._current_font_size + 1)

    def _plot_merged_spectrogram(self, ppsd_list: List, args: Dict):
        """绘制合并的频谱图"""
        if not ppsd_list:
            return

        # 获取spectrogram配置参数
        cmap = args.get('spectrogram_cmap', 'viridis')
        clim = args.get('clim', [-180, -100])
        time_format = args.get('time_format_x_spectrogram', '%Y-%m-%d')
        show_grid = args.get('spectrogram_grid', True)

        # 构建绘图参数
        plot_params = {}

        # 处理配色方案
        if cmap:
            # 首先尝试从自定义配色方案中获取
            if CUSTOM_COLORMAPS_AVAILABLE:
                custom_cmap = get_custom_colormap(cmap)
                if custom_cmap is not None:
                    plot_params['cmap'] = custom_cmap
                    self.logger.debug(f"使用自定义merged spectrogram配色方案: {cmap}")
                else:
                    # 如果不是自定义配色方案，则使用matplotlib标准配色方案
                    plot_params['cmap'] = cmap
                    self.logger.debug(f"使用标准merged spectrogram配色方案: {cmap}")
            else:
                plot_params['cmap'] = cmap
                self.logger.debug(f"使用merged spectrogram配色方案: {cmap}")

        if clim:
            plot_params['clim'] = clim

        # 对于频谱图，使用第一个PPSD
        main_ppsd = ppsd_list[0][1]
        main_ppsd.plot_spectrogram(**plot_params)

        # 设置小字体
        self._set_font_size()

        # 立即在ObsPy绘图完成后应用时间格式 - 修正：应用到X轴
        self.logger.debug(f"merged spectrogram时间格式设置: {time_format}")
        try:
            import matplotlib.dates as mdates
            ax = plt.gca()
            # 修正：spectrogram的时间轴是X轴，不是Y轴！
            self.logger.debug(f"正在应用merged spectrogram时间格式到X轴: {time_format}")
            formatter = mdates.DateFormatter(time_format)
            ax.xaxis.set_major_formatter(formatter)  # 修正：应用到X轴

            # 强制重新计算和刷新时间轴标签
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')  # X轴标签旋转
            ax.figure.canvas.draw_idle()

            # 额外的强制刷新步骤
            plt.draw()
            ax.relim()
            ax.autoscale_view()

            self.logger.debug("merged spectrogram时间格式应用成功")
        except Exception as e:
            self.logger.error(f"设置merged spectrogram时间轴格式失败: {e}")

        # 应用网格设置
        if show_grid:
            plt.grid(True, alpha=0.3)

        # 添加包含时间范围的标题
        all_times = []
        for trace_id, ppsd in ppsd_list:
            if hasattr(ppsd, 'times_processed') and len(ppsd.times_processed) > 0:
                all_times.extend(ppsd.times_processed)

        seed_id = f"{
            main_ppsd.network}.{
            main_ppsd.station}.{
            main_ppsd.location}.{
                main_ppsd.channel}"

        if all_times:
            start_time = min(all_times)
            end_time = max(all_times)

            title = (f"{seed_id}\n"
                     f"{start_time.strftime('%Y-%m-%d %H:%M')} - "
                     f"{end_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            title = f"{seed_id}"

        plt.title(title, fontsize=self._current_font_size + 1)

    def _set_font_size(self):
        """强制设置图中所有文字元素为配置的字体大小"""
        try:
            # 获取字体大小配置，默认为8
            font_size = getattr(self, '_current_font_size', 8)

            # 获取当前的axes
            ax = plt.gca()

            # 设置坐标轴标签字体
            ax.xaxis.label.set_fontsize(font_size)
            ax.yaxis.label.set_fontsize(font_size)

            # 设置坐标轴刻度标签字体
            ax.tick_params(axis='both', which='major', labelsize=font_size)
            ax.tick_params(axis='both', which='minor', labelsize=font_size - 1)

            # 设置标题字体
            title = ax.get_title()
            if title:
                ax.set_title(title, fontsize=font_size + 1)

            # 设置图例字体
            legend = ax.get_legend()
            if legend:
                for text in legend.get_texts():
                    text.set_fontsize(font_size)

            # 设置colorbar字体（如果存在）
            fig = plt.gcf()
            for ax_item in fig.get_axes():
                # 检查是否是colorbar的axes
                if hasattr(ax_item, 'yaxis') and ax_item != ax:
                    try:
                        ax_item.tick_params(
                            axis='both', which='major', labelsize=font_size)
                        if ax_item.get_ylabel():
                            ax_item.yaxis.label.set_fontsize(font_size)
                    except BaseException:
                        pass

            self.logger.debug(f"已设置字体大小: {font_size}")
        except Exception as e:
            self.logger.debug(f"设置小字体失败: {e}")

    def _add_custom_percentile_lines(
            self,
            ppsd: PPSD,
            percentiles: List[float],
            args: Dict):
        """添加自定义样式的百分位数线

        Parameters:
            ppsd: PPSD对象
            percentiles: 百分位数列表
            args: 绘图参数，包含自定义样式设置
        """
        try:
            # 获取自定义样式参数
            color = args.get('percentile_color', 'lightgray')
            linewidth = args.get('percentile_linewidth', 1.0)
            linestyle = args.get('percentile_linestyle', '--')
            alpha = args.get('percentile_alpha', 0.8)

            # 检查是否需要显示频率而非周期
            xaxis_frequency = args.get('xaxis_frequency', False)

            # 计算百分位数
            try:
                # 获取当前坐标轴
                ax = plt.gca()

                # 绘制每条百分位数线 - 逐个计算百分位数
                for percentile in percentiles:
                    try:
                        # ObsPy的get_percentile返回(periods, psd_values)元组
                        periods, psd_values = ppsd.get_percentile(percentile)

                        # 如果需要显示频率，转换周期为频率
                        if xaxis_frequency:
                            x_values = 1.0 / periods  # frequency = 1 / period
                        else:
                            x_values = periods

                        # 绘制百分位数线
                        ax.plot(x_values, psd_values,
                                color=color, linewidth=linewidth,
                                linestyle=linestyle, alpha=alpha,
                                label=f'{percentile}th percentile')

                        self.logger.debug(f"成功添加 {percentile}th 百分位数线")

                    except Exception as e:
                        self.logger.warning(f"计算 {percentile}th 百分位数失败: {e}")
                        continue

                self.logger.debug(f"完成自定义百分位数线绘制: {percentiles}")

            except Exception as e:
                self.logger.warning(f"计算百分位数失败: {e}")

        except Exception as e:
            self.logger.warning(f"添加自定义百分位数线失败: {e}")

    def _add_custom_peterson_curves(self, args: Dict):
        """添加自定义样式的皮特森噪声模型曲线

        Parameters:
            args: 绘图参数，包含自定义样式设置
        """
        try:
            # 获取自定义样式参数
            nlnm_color = args.get('peterson_nlnm_color', 'blue')
            nhnm_color = args.get('peterson_nhnm_color', 'red')
            linewidth = args.get('peterson_linewidth', 1.0)
            linestyle = args.get('peterson_linestyle', '--')
            alpha = args.get('peterson_alpha', 0.8)

            # 检查是否需要显示频率而非周期
            xaxis_frequency = args.get('xaxis_frequency', False)

            # 导入ObsPy的噪声模型
            try:
                from obspy.signal.spectral_estimation import get_nlnm, get_nhnm

                # 获取NLNM和NHNM数据
                nlnm_periods, nlnm_psd = get_nlnm()
                nhnm_periods, nhnm_psd = get_nhnm()

                # 如果需要显示频率，转换周期为频率
                if xaxis_frequency:
                    nlnm_x = 1.0 / nlnm_periods  # frequency = 1 / period
                    nhnm_x = 1.0 / nhnm_periods
                else:
                    nlnm_x = nlnm_periods
                    nhnm_x = nhnm_periods

                # 获取当前坐标轴
                ax = plt.gca()

                # 绘制NLNM曲线
                ax.plot(nlnm_x, nlnm_psd,
                        color=nlnm_color, linewidth=linewidth,
                        linestyle=linestyle, alpha=alpha,
                        label='NLNM')

                # 绘制NHNM曲线
                ax.plot(nhnm_x, nhnm_psd,
                        color=nhnm_color, linewidth=linewidth,
                        linestyle=linestyle, alpha=alpha,
                        label='NHNM')

                self.logger.debug("成功添加自定义皮特森曲线")

            except ImportError:
                self.logger.warning("无法导入ObsPy噪声模型，跳过皮特森曲线绘制")

        except Exception as e:
            self.logger.warning(f"添加自定义皮特森曲线失败: {e}")

    def _add_custom_mode_line(self, ppsd: PPSD, args: Dict):
        """添加自定义样式的众数线

        Parameters:
            ppsd: PPSD对象
            args: 绘图参数，包含自定义样式设置
        """
        try:
            # 获取自定义样式参数
            color = args.get('mode_color', 'orange')
            linewidth = args.get('mode_linewidth', 1.0)
            linestyle = args.get('mode_linestyle', '-')
            alpha = args.get('mode_alpha', 0.9)

            # 计算众数PSD
            try:
                # 尝试使用不同的方法获取众数数据
                mode_psd = None
                periods = ppsd.period_bin_centers  # 使用PPSD的周期数据

                # 方法1: 尝试get_mode方法 (ObsPy可能返回元组)
                if hasattr(ppsd, 'get_mode'):
                    try:
                        mode_result = ppsd.get_mode()
                        # 检查是否返回元组
                        if isinstance(mode_result, tuple) and len(mode_result) == 2:
                            periods, mode_psd = mode_result
                        else:
                            mode_psd = mode_result
                            periods = ppsd.period_bin_centers
                    except Exception as e:
                        self.logger.debug(f"get_mode方法失败: {e}")
                        mode_psd = None

                # 方法2: 如果没有get_mode方法，尝试从psd_matrix计算
                elif hasattr(ppsd, '_psd_matrix') and ppsd._psd_matrix is not None:
                    import numpy as np
                    from scipy import stats

                    # 计算每个频率bins的众数
                    psd_matrix = np.array(ppsd._psd_matrix)
                    if len(psd_matrix.shape) == 2:
                        # 对每个频率计算众数
                        mode_psd = []
                        for freq_idx in range(psd_matrix.shape[1]):
                            freq_data = psd_matrix[:, freq_idx]
                            freq_data = freq_data[~np.isnan(freq_data)]  # 移除NaN值
                            if len(freq_data) > 0:
                                mode_val = stats.mode(freq_data, keepdims=False)
                                mode_psd.append(
                                    mode_val.mode if hasattr(
                                        mode_val, 'mode') else mode_val[0])
                            else:
                                mode_psd.append(np.nan)
                        mode_psd = np.array(mode_psd)

                if mode_psd is not None:
                    # 处理多维数组
                    if hasattr(mode_psd, 'shape') and len(mode_psd.shape) > 1:
                        if mode_psd.shape[0] > 0:
                            mode_psd = mode_psd[0]
                        else:
                            mode_psd = mode_psd.flatten()

                    # 检查是否需要显示频率而非周期
                    xaxis_frequency = args.get('xaxis_frequency', False)
                    if xaxis_frequency:
                        x_values = 1.0 / periods  # frequency = 1 / period
                    else:
                        x_values = periods

                    # 获取当前坐标轴
                    ax = plt.gca()

                    # 绘制众数线
                    ax.plot(x_values, mode_psd,
                            color=color, linewidth=linewidth,
                            linestyle=linestyle, alpha=alpha,
                            label='Mode')

                    self.logger.debug("成功添加自定义众数线")
                else:
                    self.logger.warning("无法计算众数PSD，跳过众数线绘制")

            except Exception as e:
                self.logger.warning(f"计算众数PSD失败: {e}")

        except Exception as e:
            self.logger.warning(f"添加自定义众数线失败: {e}")

    def _add_custom_mean_line(self, ppsd: PPSD, args: Dict):
        """添加自定义样式的均值线

        Parameters:
            ppsd: PPSD对象
            args: 绘图参数，包含自定义样式设置
        """
        try:
            # 获取自定义样式参数
            color = args.get('mean_color', 'green')
            linewidth = args.get('mean_linewidth', 1.0)
            linestyle = args.get('mean_linestyle', '-')
            alpha = args.get('mean_alpha', 0.9)

            # 计算均值PSD
            try:
                # 尝试使用不同的方法获取均值数据
                mean_psd = None
                periods = ppsd.period_bin_centers  # 使用PPSD的周期数据

                # 方法1: 尝试get_mean方法 (ObsPy可能返回元组)
                if hasattr(ppsd, 'get_mean'):
                    try:
                        mean_result = ppsd.get_mean()
                        # 检查是否返回元组
                        if isinstance(mean_result, tuple) and len(mean_result) == 2:
                            periods, mean_psd = mean_result
                        else:
                            mean_psd = mean_result
                            periods = ppsd.period_bin_centers
                    except Exception as e:
                        self.logger.debug(f"get_mean方法失败: {e}")
                        mean_psd = None

                # 方法2: 如果没有get_mean方法，尝试从psd_matrix计算
                elif hasattr(ppsd, '_psd_matrix') and ppsd._psd_matrix is not None:
                    import numpy as np

                    # 计算每个频率bins的均值
                    psd_matrix = np.array(ppsd._psd_matrix)
                    if len(psd_matrix.shape) == 2:
                        # 对每个频率计算均值，忽略NaN值
                        mean_psd = np.nanmean(psd_matrix, axis=0)

                if mean_psd is not None:
                    # 处理多维数组
                    if hasattr(mean_psd, 'shape') and len(mean_psd.shape) > 1:
                        if mean_psd.shape[0] > 0:
                            mean_psd = mean_psd[0]
                        else:
                            mean_psd = mean_psd.flatten()

                    # 检查是否需要显示频率而非周期
                    xaxis_frequency = args.get('xaxis_frequency', False)
                    if xaxis_frequency:
                        x_values = 1.0 / periods  # frequency = 1 / period
                    else:
                        x_values = periods

                    # 获取当前坐标轴
                    ax = plt.gca()

                    # 绘制均值线
                    ax.plot(x_values, mean_psd,
                            color=color, linewidth=linewidth,
                            linestyle=linestyle, alpha=alpha,
                            label='Mean')

                    self.logger.debug("成功添加自定义均值线")
                else:
                    self.logger.warning("无法计算均值PSD，跳过均值线绘制")

            except Exception as e:
                self.logger.warning(f"计算均值PSD失败: {e}")

        except Exception as e:
            self.logger.warning(f"添加自定义均值线失败: {e}")

    def _is_grouped_config_structure(self, config: Dict) -> bool:
        """检查配置文件是否为分组结构

        检查配置是否包含分组配置的特征结构：
        - [global] 节
        - [paths] 节
        - [standard] 或 [standard.percentiles] 等嵌套节
        """
        # 检查是否包含分组配置的特征节
        has_global = 'global' in config
        has_paths = 'paths' in config
        has_plotting = 'plotting' in config
        has_standard = 'standard' in config

        # 检查是否有嵌套结构
        has_nested_structure = False
        if has_standard:
            standard_section = config['standard']
            if isinstance(standard_section, dict):
                # 检查是否有 percentiles, peterson 等子节
                has_nested_structure = (
                    'percentiles' in standard_section or
                    'peterson' in standard_section or
                    'mode' in standard_section or
                    'mean' in standard_section
                )

        # 如果有多个特征节存在，认为是分组配置
        structure_score = sum([has_global, has_paths, has_plotting,
                              has_standard, has_nested_structure])

        return structure_score >= 3  # 至少有3个特征才认为是分组配置

    def run(self):
        """运行主处理流程"""
        try:
            self.logger.info("开始PPSD处理流程")
            self.logger.info(f"加载了 {len(self.configs)} 个配置文件")

            # 分离计算型和绘图型配置
            calc_configs = [c for c in self.configs if self._is_calculation_config(c)]
            plot_configs = [c for c in self.configs if self._is_plot_config(c)]

            self.logger.info(f"计算型配置: {len(calc_configs)} 个")
            self.logger.info(f"绘图型配置: {len(plot_configs)} 个")

            # 执行计算
            for config in calc_configs:
                try:
                    self.calculate_ppsd(config)
                except Exception as e:
                    self.logger.error(f"计算失败: {e}")
                    if len(calc_configs) == 1:  # 如果只有一个计算配置，抛出异常
                        raise

            # 执行绘图
            for config in plot_configs:
                try:
                    self.plot_ppsd(config)
                except Exception as e:
                    self.logger.error(f"绘图失败: {e}")
                    if len(plot_configs) == 1:  # 如果只有一个绘图配置，抛出异常
                        raise

            self.logger.info("PPSD处理流程完成")

        except Exception as e:
            self.logger.error(f"处理流程失败: {e}")
            self.logger.debug(traceback.format_exc())
            raise

    def _plot_standard(self, ppsd: PPSD, args: Dict):
        """绘制标准PPSD图（单个PPSD对象）

        基于ObsPy API，plot支持的参数：
        - period_lim: 周期范围限制
        - show_coverage: 是否显示数据覆盖度
        - show_percentiles: 是否显示百分位数线
        - percentiles: 百分位数值列表
        - show_noise_models: 是否显示皮特森噪声模型
        - show_mode: 是否显示mode线
        - show_mean: 是否显示mean线
        - cmap: 颜色映射
        - xaxis_frequency: X轴是否使用频率而不是周期
        - cumulative: 是否显示累积图
        """
        # 调试：输出接收到的参数
        self.logger.debug(f"_plot_standard 接收到的参数数量: {len(args)}")

        # 检查自定义样式相关参数
        style_params = [
            'percentile_color',
            'percentile_linewidth',
            'percentile_linestyle',
            'percentile_alpha',
            'peterson_nlnm_color',
            'peterson_nhnm_color',
            'peterson_linewidth',
            'peterson_linestyle',
            'peterson_alpha',
            'mode_color',
            'mode_linewidth',
            'mode_linestyle',
            'mode_alpha',
            'mean_color',
            'mean_linewidth',
            'mean_linestyle',
            'mean_alpha']

        found_style_params = [param for param in style_params if param in args]
        if found_style_params:
            self.logger.info(f"发现自定义样式参数: {found_style_params}")
        else:
            self.logger.warning("未发现任何自定义样式参数")

        # 输出关键开关参数状态
        self.logger.debug(f"显示开关 - percentiles: {args.get('show_percentiles')}, "
                          f"noise_models: {args.get('show_noise_models')}, "
                          f"mode: {args.get('show_mode')}, "
                          f"mean: {args.get('show_mean')}")
        # 准备绘图参数
        plot_params = {
            'period_lim': args.get('period_lim', [0.01, 1000.0]),
            'show_coverage': False  # 禁用 ObsPy 内置的数据覆盖度显示
        }

        # 添加配色方案支持
        if 'standard_cmap' in args:
            cmap_name = args['standard_cmap']
            # 首先尝试从自定义配色方案中获取
            if CUSTOM_COLORMAPS_AVAILABLE:
                custom_cmap = get_custom_colormap(cmap_name)
                if custom_cmap is not None:
                    plot_params['cmap'] = custom_cmap
                    self.logger.debug(f"使用自定义standard配色方案: {cmap_name}")
                else:
                    # 如果不是自定义配色方案，则使用matplotlib标准配色方案
                    plot_params['cmap'] = plt.get_cmap(cmap_name)
                    self.logger.debug(f"使用标准配色方案: {cmap_name}")
            else:
                plot_params['cmap'] = plt.get_cmap(cmap_name)
                self.logger.debug(f"使用配色方案: {cmap_name}")

        # 检查是否需要自定义百分位数线样式
        custom_percentile_style = (
            'percentile_color' in args or
            'percentile_linewidth' in args or
            'percentile_linestyle' in args or
            'percentile_alpha' in args
        )

        # 检查是否需要自定义皮特森曲线样式
        custom_peterson_style = (
            'peterson_linewidth' in args or
            'peterson_linestyle' in args or
            'peterson_alpha' in args or
            'peterson_nlnm_color' in args or
            'peterson_nhnm_color' in args
        )

        # 检查是否需要自定义mode和mean线样式
        custom_mode_style = (
            'mode_color' in args or
            'mode_linewidth' in args or
            'mode_linestyle' in args or
            'mode_alpha' in args
        )

        custom_mean_style = (
            'mean_color' in args or
            'mean_linewidth' in args or
            'mean_linestyle' in args or
            'mean_alpha' in args
        )

        # 如果需要自定义皮特森曲线样式，先不显示噪声模型
        if custom_peterson_style and args.get('show_noise_models', True):
            plot_params['show_noise_models'] = False
            show_custom_peterson = True
        else:
            # 使用标准皮特森曲线
            plot_params['show_noise_models'] = args.get('show_noise_models', True)
            show_custom_peterson = False

        # 如果需要自定义mode和mean线样式，先不显示
        if custom_mode_style and args.get('show_mode', False):
            plot_params['show_mode'] = False
            show_custom_mode = True
        else:
            # 使用标准mode线
            plot_params['show_mode'] = args.get('show_mode', False)
            show_custom_mode = False

        if custom_mean_style and args.get('show_mean', False):
            plot_params['show_mean'] = False
            show_custom_mean = True
        else:
            # 使用标准mean线
            plot_params['show_mean'] = args.get('show_mean', False)
            show_custom_mean = False

        # 如果需要自定义百分位数线样式，先不显示百分位数线
        if custom_percentile_style and args.get('show_percentiles', False):
            plot_params['show_percentiles'] = False
            show_custom_percentiles = True
            percentiles = args.get('percentiles', [10, 50, 90])
        else:
            # 使用标准百分位数线
            if 'show_percentiles' in args:
                plot_params['show_percentiles'] = args['show_percentiles']
            if 'percentiles' in args:
                plot_params['percentiles'] = args['percentiles']
            show_custom_percentiles = False

        # 添加其他标准图参数（只包含ObsPy支持的参数）
        if 'show_histogram' in args:
            plot_params['show_histogram'] = args['show_histogram']
        if 'show_mode' in args and not custom_mode_style:
            plot_params['show_mode'] = args['show_mode']
        if 'show_mean' in args and not custom_mean_style:
            plot_params['show_mean'] = args['show_mean']
        if 'xaxis_frequency' in args:
            plot_params['xaxis_frequency'] = args['xaxis_frequency']
        if 'cumulative_plot' in args:
            plot_params['cumulative'] = args['cumulative_plot']
            self.logger.debug(f"设置累积模式: cumulative_plot={args['cumulative_plot']}")
        if 'cumulative_number_of_colors' in args:
            plot_params['cumulative_number_of_colors'] = args['cumulative_number_of_colors']
            self.logger.debug(f"设置累积颜色数量: {args['cumulative_number_of_colors']}")

        self.logger.debug(f"最终plot_params包含的参数: {list(plot_params.keys())}")
        if 'cumulative' in plot_params:
            self.logger.debug(f"将传递给ObsPy的cumulative参数: {plot_params['cumulative']}")

        # 使用ObsPy的plot方法
        ppsd.plot(**plot_params)

        # ObsPy绘图完成后，强制设置所有文字元素的字体大小
        self._set_font_size()

        # 处理网格显示
        if 'standard_grid' in args:
            ax = plt.gca()
            ax.grid(args['standard_grid'])
            self.logger.debug(f"设置网格显示: {args['standard_grid']}")

        # 如果需要自定义皮特森曲线样式，手动添加
        if show_custom_peterson:
            self.logger.info("调用自定义皮特森曲线绘制")
            self._add_custom_peterson_curves(args)

        # 如果需要自定义百分位数线样式，手动添加
        if show_custom_percentiles:
            self.logger.info(f"调用自定义百分位数线绘制: {percentiles}")
            self._add_custom_percentile_lines(ppsd, percentiles, args)

        # 如果需要自定义mode线样式，手动添加
        if show_custom_mode:
            self.logger.info("调用自定义众数线绘制")
            self._add_custom_mode_line(ppsd, args)

        # 如果需要自定义mean线样式，手动添加
        if show_custom_mean:
            self.logger.info("调用自定义均值线绘制")
            self._add_custom_mean_line(ppsd, args)

        # 添加包含时间范围的标题
        if hasattr(ppsd, 'times_processed') and len(ppsd.times_processed) > 0:
            start_time = min(ppsd.times_processed)
            end_time = max(ppsd.times_processed)

            seed_id = f"{ppsd.network}.{ppsd.station}.{ppsd.location}.{ppsd.channel}"
            title = (f"{seed_id}\n"
                     f"{start_time.strftime('%Y-%m-%d %H:%M')} - "
                     f"{end_time.strftime('%Y-%m-%d %H:%M')}")
            plt.title(title, fontsize=self._current_font_size + 1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='PPSD 批量处理与可视化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run_cp_ppsd.py config.toml                    # 仅计算
  python run_cp_ppsd.py config_plot.toml               # 仅绘图
  python run_cp_ppsd.py config_plot.toml               # 绘图（分组配置）
  python run_cp_ppsd.py config.toml config_plot.toml   # 计算+绘图

配置文件说明:
  - 计算型配置文件 (如 config.toml): 包含 mseed_pattern, inventory_path 等
  - 绘图型配置文件 (如 config_plot.toml): 包含 input_npz_dir, plot_type 等
        """
    )

    parser.add_argument(
        'config_files',
        nargs='+',
        help='TOML配置文件路径（可指定多个）'
    )

    parser.add_argument(
        '--pdb',
        action='store_true',
        help='出错时进入调试模式'
    )

    args = parser.parse_args()

    try:
        # 创建处理器并运行
        processor = PPSDProcessor(args.config_files)
        processor.run()

    except KeyboardInterrupt:
        print("\n用户中断程序")
        sys.exit(1)
    except Exception as e:
        print(f"程序执行失败: {e}")
        if args.pdb:
            import pdb
            pdb.post_mortem()
        sys.exit(1)


if __name__ == '__main__':
    main()
