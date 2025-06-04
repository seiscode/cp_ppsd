# 01_DEVELOPMENT_ENVIRONMENT.md - 开发环境搭建

本文档指导如何为 `cp_ppsd` 项目设置一致的开发环境。遵循这些步骤有助于减少因环境差异导致的问题，并确保代码在不同开发者之间的兼容性。

## 1. Python 版本

本项目推荐并主要使用 **Python 3.12.x** 版本进行开发和测试。

*   **检查现有版本**: 打开终端或命令提示符，输入以下命令检查您当前的 Python 版本：
    ```bash
    python --version
    # 或者，如果您同时安装了 Python 2 和 Python 3
    python3 --version
    ```
*   **安装 Python 3.12**: 如果您没有安装 Python 3.12 或更高版本，请从 [Python 官方网站](https://www.python.org/downloads/) 下载并安装适合您操作系统的最新 3.12.x 版本。
    *   在安装过程中，特别是在 Windows 上，请确保勾选 "Add Python to PATH" 或类似的选项，以便在命令行中直接使用 `python` 命令。

## 2. 依赖管理

项目使用 `pip` 和 `requirements.txt` 文件来管理 Python 依赖项。

*   **`requirements.txt`**: 此文件位于项目根目录下（如果尚不存在，后续会创建），列出了项目运行所需的所有第三方库及其精确版本。这种方式可以确保所有开发者使用相同版本的依赖，避免潜在的兼容性问题。
    *   核心依赖包括：`obspy`, `toml`, `numpy`, `matplotlib` (通常作为 ObsPy 的依赖自动安装)。

*   **安装依赖**: 在设置好虚拟环境（见下一节）后，进入项目根目录，并运行以下命令来安装所有必需的依赖项：
    ```bash
    pip install -r requirements.txt
    ```

*   **更新依赖**: 如果 `requirements.txt` 文件有更新，或者您添加了新的依赖，其他开发者需要重新运行上述命令来同步他们的环境。

*   **添加新依赖**: 当您为项目添加新的库时：
    1.  首先在您的虚拟环境中安装它： `pip install <library_name>`
    2.  然后更新 `requirements.txt` 文件： `pip freeze > requirements.txt`
    3.  将更新后的 `requirements.txt` 提交到版本控制系统。

## 3. 虚拟环境

强烈建议使用 Python 虚拟环境来隔离项目依赖，避免与系统全局 Python 环境或其他项目的依赖发生冲突。

*   **推荐工具**: Python 内置的 `venv` 模块。

*   **创建虚拟环境**:
    1.  打开终端或命令提示符，导航到您的项目根目录 `cp_ppsd/`。
    2.  运行以下命令创建一个名为 `.venv` 的虚拟环境（`.venv` 是一个常用的虚拟环境目录名，通常会被添加到 `.gitignore` 中）：
        ```bash
        python -m venv .venv
        ```
        (在某些系统上，您可能需要使用 `python3` 替代 `python`)

*   **激活虚拟环境**:
    *   **Windows (cmd.exe)**:
        ```bash
        .venv\Scripts\activate.bat
        ```
    *   **Windows (PowerShell)**:
        ```bash
        .venv\Scripts\Activate.ps1
        ```
        (如果执行策略阻止脚本运行，您可能需要先运行 `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`)
    *   **macOS / Linux (bash/zsh)**:
        ```bash
        source .venv/bin/activate
        ```
    激活后，您的命令提示符通常会显示虚拟环境的名称 (例如 `(.venv) Your-Computer-Name:cp_ppsd user$`)。

*   **在虚拟环境中工作**: 激活虚拟环境后，您安装的所有包 (`pip install ...`) 都将安装到此环境中，不会影响全局 Python 安装。运行 Python 脚本 (`python run_cp_ppsd.py ...`) 也会使用此虚拟环境中的 Python 解释器和库。

*   **停用虚拟环境**: 当您完成工作后，可以使用以下命令停用虚拟环境：
    ```bash
    deactivate
    ```
    这将使您的终端会话恢复到系统默认的 Python 环境。

## 4. 必要工具

以下是一些推荐的开发工具：

*   **Git**: 用于版本控制。确保您已安装 Git 并熟悉基本的 Git 命令（`clone`, `add`, `commit`, `push`, `pull`, `branch`, `merge`）。
    *   官方网站: [https://git-scm.com/](https://git-scm.com/)

*   **代码编辑器 / 集成开发环境 (IDE)**: 选择一个您喜欢的代码编辑器或 IDE，它应具备良好的 Python 支持，例如语法高亮、代码补全、调试功能等。
    *   **Visual Studio Code (VS Code)**: 轻量级且功能强大的编辑器，拥有丰富的 Python 扩展 (如 Microsoft 的 Python 扩展)。
        *   官方网站: [https://code.visualstudio.com/](https://code.visualstudio.com/)
        *   推荐配置: 安装 Python 扩展后，VS Code 通常能自动检测并使用项目中的虚拟环境。
    *   **PyCharm**: JetBrains 公司出品的功能完备的 Python IDE，有免费的社区版和付费的专业版。
        *   官方网站: [https://www.jetbrains.com/pycharm/](https://www.jetbrains.com/pycharm/)
        *   推荐配置: PyCharm 具有出色的虚拟环境管理和项目依赖集成功能。

*   **终端 / 命令行工具**: 熟悉使用您操作系统内置的终端（如 macOS的Terminal, Linux的各种终端模拟器, Windows的CMD或PowerShell）或第三方终端工具。

## 5. `.gitignore` 文件

项目根目录下应包含一个 `.gitignore` 文件，用于告诉 Git 哪些文件或目录不应被追踪和提交到版本库。至少应包含：

```
# 虚拟环境
.venv/

# Python 编译文件
__pycache__/
*.py[cod]
*$py.class

# IDE 和编辑器特定文件
.vscode/
.idea/
*.DS_Store

# 输出目录 (如果不想追踪生成的结果)
# ppsd_results/ # 根据项目策略决定是否追踪

# 日志文件
*.log
```
确保根据项目的具体情况调整 `.gitignore`。

---

遵循以上步骤可以帮助您快速搭建起 `cp_ppsd` 项目的开发环境。如果在搭建过程中遇到任何问题，请查阅相应工具的官方文档或与团队成员讨论。 