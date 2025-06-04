# 06_DEPLOYMENT_PROCESS.md - 部署流程

本文档描述了 `cp_ppsd` 项目的部署和分发流程。由于本项目主要是一个命令行工具套件，其"部署"更多地关注于如何让最终用户或协作者能够方便地获取、安装和运行该工具。

## 目录
1.  [概述](#1-概述)
2.  [版本控制与发布](#2-版本控制与发布)
3.  [打包与分发 (潜在方案)](#3-打包与分发-潜在方案)
    *   [3.1 作为 Python 包 (PyPI)](#31-作为-python-包-pypi)
    *   [3.2 直接通过 Git 仓库](#32-直接通过-git-仓库)
    *   [3.3 打包为可执行文件 (例如使用 PyInstaller)](#33-打包为可执行文件-例如使用-pyinstaller)
4.  [当前推荐使用方式](#4-当前推荐使用方式)

---

## 1. 概述

`cp_ppsd` 工具主要通过 Python 脚本 (`run_cp_ppsd.py`) 和相关的配置文件 (`.toml`) 来运行。其部署的核心是确保用户拥有正确的 Python 环境、所有必要的依赖库，以及最新版本的脚本代码和知识库文档。

## 2. 版本控制与发布

*   **版本标签**: 项目遵循 `02_CODING_STANDARDS.md` 中定义的分支策略。每个正式的发布版本都应该在 `main` 分支上打上一个语义化的版本标签 (e.g., `v1.0.0`, `v1.1.0`, `v1.0.1`)。
    ```bash
    git tag -a vX.Y.Z -m "Release version X.Y.Z"
    git push origin vX.Y.Z
    ```
*   **更新日志 (Changelog)**: 对于每个发布版本，建议维护一个 `CHANGELOG.md` 文件（可考虑未来添加此文件到知识库计划中），记录自上一版本以来的主要变化、新功能和 Bug 修复。这有助于用户了解版本的演进。

## 3. 打包与分发 (潜在方案)

以下是一些未来可以考虑或根据项目发展选择的打包与分发方案：

### 3.1 作为 Python 包 (PyPI)

*   **优点**: 
    *   用户可以通过 `pip install cp_ppsd` 轻松安装。
    *   依赖管理由 `pip` 自动处理。
    *   易于版本管理和更新。
*   **步骤 (概览)**:
    1.  **项目结构调整**: 可能需要将项目组织成标准的 Python 包结构 (包含 `setup.py` 或 `pyproject.toml` 使用 `setuptools` 或 `poetry` 等构建工具)。
    2.  **编写 `setup.py` / `pyproject.toml`**: 定义包的元数据、依赖项、入口点 (使 `run_cp_ppsd.py` 作为命令行工具可用)等。
        *   例如，在 `pyproject.toml` 中使用 `[project.scripts]` 定义命令行入口。
    3.  **构建分发包**: 
        ```bash
        python -m pip install --upgrade build
        python -m build
        ```
    4.  **上传到 PyPI**: 使用 `twine` 将构建好的包上传到 Python Package Index (PyPI)。
        ```bash
        python -m pip install --upgrade twine
        twine upload dist/*
        ```
*   **状态**: *未来考虑方向，当前未实施。*

### 3.2 直接通过 Git 仓库

*   **优点**: 
    *   简单直接，无需复杂的打包过程。
    *   用户可以获取到最新的开发版本或特定的标签版本。
*   **步骤**:
    1.  用户克隆项目仓库: `git clone <repository_url>`
    2.  用户检出特定版本 (标签): `git checkout vX.Y.Z` (可选)
    3.  用户按照 `01_DEVELOPMENT_ENVIRONMENT.md` 设置 Python 虚拟环境并安装依赖: `pip install -r requirements.txt`。
    4.  直接运行 `python run_cp_ppsd.py ...`。
*   **状态**: *当前主要推荐的使用方式之一，尤其适用于开发者和有 Python 环境管理经验的用户。*

### 3.3 打包为可执行文件 (例如使用 PyInstaller)

*   **优点**: 
    *   为不熟悉 Python 或不想管理 Python 环境的用户提供便利，可以直接运行可执行文件。
    *   将 Python 解释器和所有依赖项打包在一起。
*   **步骤 (概览，以 PyInstaller 为例)**:
    1.  安装 PyInstaller: `pip install pyinstaller`
    2.  在项目根目录运行 PyInstaller:
        ```bash
        pyinstaller --name cp_ppsd_tool --onefile --noconsole cp_psd.py 
        # --onefile: 打包成单个可执行文件
        # --noconsole: (如果适用) 命令行工具通常需要控制台，GUI应用可能不需要
        # 可能需要通过 .spec 文件处理额外的数据文件 (如默认配置文件示例) 或 ObsPy 的隐藏依赖。
        ```
    3.  生成的可执行文件通常在 `dist/` 目录下。
*   **挑战**: 
    *   ObsPy 及其依赖 (如 NumPy, Matplotlib) 可能会使打包过程复杂化，需要仔细处理隐藏导入和数据文件。
    *   生成的可执行文件通常较大。
    *   跨平台打包可能需要分别在不同操作系统上进行。
*   **状态**: *未来可以探索，但可能需要较多配置和测试。*

## 4. 当前推荐使用方式

目前，对于 `cp_ppsd` 项目，推荐的"部署"或使用方式是**直接通过 Git 仓库获取代码，并结合 Python 虚拟环境进行使用** (如 3.2 节所述)。

**简要步骤**:
1.  **获取代码**: 克隆项目仓库。
    ```bash
    git clone https://your-git-repository-url/cp_ppsd.git
    cd cp_ppsd
    ```
2.  **(可选) 检出特定版本**: 如果需要特定发布的版本，请检出相应的标签。
    ```bash
    git checkout tags/vX.Y.Z -b version-X.Y.Z
    ```
3.  **设置环境**: 遵循 `cursor_project_rules/01_DEVELOPMENT_ENVIRONMENT.md` 的指导：
    *   创建 Python 3.12.x 虚拟环境 (e.g., `python -m venv .venv`)。
    *   激活虚拟环境 (e.g., `source .venv/bin/activate`)。
    *   安装依赖 (`pip install -r requirements.txt`)。
4.  **运行脚本**: 
    ```bash
    python cp_psd.py path/to/your_config.toml [path/to/your_plot_config.toml]
    ```

这种方式确保了环境的一致性，并且用户可以方便地获取更新或切换到不同版本。

---

随着项目的发展，可能会采用更正式的打包和分发机制 (如发布到 PyPI)。届时本文档将进行相应更新。 