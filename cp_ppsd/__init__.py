"""
Author:
    muly (muly@cea-igp.ac.cn)
license:
    MIT License
    (https://opensource.org/licenses/MIT)
"""
"""
CP-PPSD: 概率功率谱密度计算与可视化工具包

这是一个基于ObsPy的地震学数据分析工具，用于批量计算和可视化概率功率谱密度（PPSD）。

主要功能：
- 批量处理MiniSEED格式的地震数据
- 计算概率功率谱密度（PPSD）
- 生成多种类型的PPSD可视化图件
- 支持TOML配置文件
- 支持计算和绘图分离的工作流程
"""


from .cp_psd import PPSDProcessor
__version__ = "1.0.0"
__author__ = "muly"
__email__ = ""
__description__ = "概率功率谱密度计算与可视化工具包"

__all__ = [
    "PPSDProcessor",
]
