#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

"""
CP-PPSD 安装脚本

使用方法:
    pip install -e .  # 开发模式安装
    pip install .     # 正常安装
"""
"""
Author:
    muly (muly@cea-igp.ac.cn)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""


# 读取README文件
def read_readme():
    """读取README.md文件内容"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


# 读取requirements.txt文件
def read_requirements():
    """读取requirements.txt文件内容"""
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            requirements = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
            return requirements
    return []


setup(
    name="cp-ppsd",
    version="1.0.0",
    author="地球物理Python编程助手",
    author_email="",
    description="概率功率谱密度计算与可视化工具包",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "cp-ppsd=cp_ppsd.cp_psd:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cp_ppsd": ["*.py"],
    },
    keywords="seismology, PPSD, power spectral density, ObsPy, earthquake",
    project_urls={
        "Documentation": "",
        "Source": "",
        "Tracker": "",
    },
)
