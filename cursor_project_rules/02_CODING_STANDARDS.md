# 02_CODING_STANDARDS.md - 编码规范

本文档规定了 `cp_ppsd` 项目的编码标准、代码审查流程、分支策略以及提交信息规范，旨在确保代码的一致性、可读性、可维护性和协作效率。所有项目贡献者应遵循这些规范。

## 1. 代码风格

### 1.1 PEP8 合规性
严格遵守 [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)。建议使用自动化工具（如 `flake8`, `pylint`, `black`, `autopep8`）来辅助检查和格式化代码。

### 1.2 Pythonic 代码
优先采用符合 Python 风格习惯的写法，以增强代码的简洁性和可读性：
*   **列表推导式 (List Comprehensions)** 和 **生成器表达式 (Generator Expressions)**: 替代 `for` 循环和 `append`。
*   **字典推导式 (Dictionary Comprehensions)**。
*   **上下文管理器 (`with` 语句)**: 用于管理资源，如文件操作，确保资源正确释放。
*   **`enumerate()`**: 在迭代序列时同时获取索引和值。
*   **`zip()`**: 并行迭代多个序列。
*   避免不必要的 C 风格循环（例如，手动管理索引）。

### 1.3 命名约定
*   **变量名**: 使用小写字母，单词间用下划线分隔 (snake_case)。
    *   地球物理相关变量应清晰表意并包含单位（如果适用且不易从上下文推断）：
        *   `seismic_trace_raw`
        *   `gravity_anomaly_mgal` (毫伽)
        *   `travel_time_seconds`
        *   `sampling_rate_hz` (赫兹)
        *   `psd_data_db` (分贝)
*   **函数名**: 与变量名规则相同 (snake_case)。
    *   例如: `calculate_ppsd()`, `plot_temporal_evolution()`, `load_miniseed_data()`。
*   **类名**: 使用驼峰命名法 (CapWords/PascalCase)。
    *   例如: `PPSDProcessor`, `ConfigManager`, `SeismicPlotter`。
*   **常量名**: 使用全大写字母，单词间用下划线分隔 (UPPER_SNAKE_CASE)。
    *   例如: `DEFAULT_PPSD_LENGTH = 3600`, `NLNM_MODEL_PATH = "data/nlnm.txt"`。
*   **模块名**: 简短、小写，可使用下划线（但不推荐，除非必要）。
*   **私有成员**: 以单下划线 `_` 开头表示内部使用（弱"私有"指示）。以双下划线 `__` 开头（但不以双下划线结尾）会触发名称修饰 (name mangling)，用于避免子类意外覆盖。

### 1.4 类型提示 (Python 3.10+)
*   在函数签名（参数和返回类型）和重要变量声明中添加类型提示。
*   使用 `typing` 模块中的类型，如 `List`, `Dict`, `Tuple`, `Optional`, `Any`。
*   对于 NumPy 数组，使用 `np.ndarray`。对于 Pandas DataFrame，使用 `pd.DataFrame`。对于 Xarray DataArray，使用 `xr.DataArray`。
    ```python
    from typing import List, Tuple, Optional
    import numpy as np

    def process_data(data: np.ndarray, threshold: float = 0.5) -> Optional[np.ndarray]:
        # ...
        pass

    raw_traces: List[np.ndarray] = []
    ```

### 1.5 文档字符串 (Docstrings)
*   所有公共模块、类、函数和方法都必须包含清晰、信息丰富的文档字符串。
*   推荐使用 **Google 风格** 或 **reStructuredText (Sphinx 兼容)** 格式。
*   文档字符串应解释代码的*功能*、其*参数* (包括类型和含义)、*返回值* (包括类型和含义)，以及任何可能抛出的*主要异常*。
    ```python
    def calculate_travel_time(distance_km: float, velocity_km_s: float) -> float:
        """Calculates the travel time given distance and velocity.

        Args:
            distance_km: The distance in kilometers.
            velocity_km_s: The velocity in kilometers per second.

        Returns:
            The travel time in seconds.

        Raises:
            ValueError: If velocity_km_s is zero or negative.
        """
        if velocity_km_s <= 0:
            raise ValueError("Velocity must be positive.")
        return distance_km / velocity_km_s
    ```

### 1.6 注释
*   **块注释**: `#` 开头，用于解释复杂代码段的逻辑或不明显的决策。避免复述代码本身。
*   **行内注释**: `#` 开头，在代码行尾部，简要说明。少用，仅在必要时。
*   **TODO 注释**: 使用 `# TODO: Description` 格式标记待办事项。

### 1.7 字符串格式化
*   优先使用 **f-strings (Formatted String Literals)** (Python 3.6+)，因其简洁和高效。
    ```python
    station = "ABC"
    channel = "BHZ"
    message = f"Processing {station}.{channel}..."
    ```

### 1.8 导入规范
*   导入语句应位于文件顶部，仅在模块注释和文档字符串之后，全局变量之前。
*   导入顺序：
    1.  标准库导入 (e.g., `os`, `sys`)
    2.  第三方库导入 (e.g., `numpy`, `obspy`)
    3.  本项目内部模块导入
*   每个导入组之间空一行。
*   避免使用 `from <module> import *`，以防止命名空间污染。

## 2. 代码审查流程

### 2.1 目的
*   提高代码质量和健壮性。
*   确保代码符合项目规范和最佳实践。
*   促进知识共享和团队学习。
*   尽早发现潜在的缺陷和设计问题。

### 2.2 流程步骤
1.  **功能开发/Bug修复**: 开发者在本地特性分支 (feature branch) 或修复分支 (hotfix/bugfix branch) 上完成代码编写和初步测试。
2.  **发起合并请求 (Pull Request / Merge Request)**:
    *   将本地分支推送到远程仓库。
    *   在代码托管平台（如 GitHub, GitLab）上创建一个从特性分支到 `develop` 分支（或 `main` 分支，取决于分支策略）的合并请求。
    *   合并请求的描述应清晰说明更改的目的、内容以及如何测试。如果关联到特定的 issue，应进行链接。
3.  **指定审查者**: 根据项目配置或团队约定，至少指定一到两名审查者。
4.  **代码审查**:
    *   审查者检查代码的正确性、可读性、性能、安全性、是否符合编码规范、以及测试覆盖情况。
    *   审查者通过合并请求的评论功能提供反馈、提出问题或建议修改。
5.  **讨论与修改**:
    *   代码作者回应审查者的评论，进行必要的讨论，并根据反馈修改代码。
    *   修改后，作者将更新推送到特性分支，合并请求会自动更新。
6.  **批准与合并**:
    *   当所有审查者对代码满意并批准合并请求后，由具有合并权限的成员（通常是项目维护者或主要开发者）将特性分支合并到目标分支。
    *   合并后，通常会删除已被合并的特性分支。
7.  **CI/CD (可选)**: 如果项目配置了持续集成/持续部署，合并操作可能会触发自动化构建、测试和部署流程。

### 2.3 审查者职责
*   **及时性**: 尽快审查分配给自己的代码。
*   **建设性**: 提供清晰、具体、有建设性的反馈，专注于代码本身，而非针对个人。
*   **全面性**: 关注代码逻辑、错误处理、边界条件、可读性、性能、安全性、测试覆盖以及是否符合项目规范。
*   **鼓励**: 提出改进建议，并认可好的实践。

### 2.4 作者职责
*   **准备充分**: 在提交审查前，确保代码已通过本地测试，并符合基本的编码规范。
*   **清晰描述**: 在合并请求中提供清晰的上下文和更改说明。
*   **积极响应**: 及时回应审查者的反馈，耐心解释设计决策，并根据合理建议进行修改。
*   **保持开放**: 以学习和改进的心态接受反馈。

## 3. 分支策略

本项目推荐使用 **Gitflow 工作流** 或其简化版本。

### 3.1 主要分支
*   **`main` (或 `master`)**:
    *   用于存放稳定、已发布的版本。
    *   此分支的代码应始终处于可部署状态。
    *   不允许直接向 `main` 分支提交代码，所有更改都应通过合并 `release` 分支或 `hotfix` 分支进行。
    *   每次合并到 `main` 分支时，都应打上版本标签 (e.g., `v1.0.0`, `v1.0.1`)。
*   **`develop`**:
    *   作为集成分支，用于汇集所有已完成的特性和修复，是下一个版本的开发基础。
    *   此分支的代码应代表项目最新的开发进展。
    *   当 `develop` 分支达到稳定状态并准备发布时，从中创建 `release` 分支。

### 3.2 支持分支
*   **特性分支 (`feature/name-of-feature`)**:
    *   用于开发新功能。
    *   从 `develop` 分支创建。
    *   命名应具有描述性，例如 `feature/ppsd-temporal-plot`。
    *   完成开发和初步测试后，合并回 `develop` 分支（通过代码审查流程）。
    *   特性分支不应直接与 `main` 分支交互。
*   **发布分支 (`release/version-number`)**:
    *   用于准备新版本的发布。允许进行最后的 Bug 修复、文档生成和其他面向发布的任务。
    *   从 `develop` 分支创建，当 `develop` 分支的功能足够成熟，准备发布时。
    *   例如 `release/v1.1.0`。
    *   发布分支完成后，必须同时合并到 `main` 分支 (打上版本标签) 和 `develop` 分支 (以确保 `develop` 也包含这些修复)。
    *   合并后，发布分支通常会被删除。
*   **修复分支 (`hotfix/issue-description` 或 `bugfix/issue-description`)**:
    *   用于紧急修复已发布版本 (`main` 分支) 中的关键 Bug。
    *   直接从 `main` 分支创建。
    *   例如 `hotfix/critical-memory-leak-v1.0.1`。
    *   修复完成后，必须同时合并到 `main` 分支 (更新版本标签，如 `v1.0.2`) 和 `develop` 分支 (或当前活动的 `release` 分支，如果存在的话)，以确保修复包含在后续开发中。
    *   合并后，修复分支通常会被删除。

### 3.3 基本流程示例
1.  从 `develop` 创建 `feature/my-new-feature`。
2.  在 `feature/my-new-feature`上开发，提交。
3.  完成特性后，发起合并请求到 `develop`。
4.  代码审查通过后，合并到 `develop`。
5.  当 `develop` 准备好发布时，从 `develop` 创建 `release/vX.Y.Z`。
6.  在 `release` 分支上进行最终测试和修复。
7.  将 `release/vX.Y.Z` 合并到 `main` (打标签 `vX.Y.Z`) 并合并回 `develop`。
8.  如果 `main` 上发现紧急 Bug，从 `main` 创建 `hotfix/bug-fix-name`。
9.  修复后，将 `hotfix` 合并到 `main` (打新标签) 和 `develop`。

## 4. 提交信息规范

为了保持提交历史的清晰和可追溯性，本项目推荐使用 **Conventional Commits** 规范 ([https://www.conventionalcommits.org/](https://www.conventionalcommits.org/))。

### 4.1 格式
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

*   **Header**:
    *   **`<type>`**: 描述提交的类型。常见的类型包括：
        *   `feat`: 新功能 (feature)。
        *   `fix`: Bug 修复。
        *   `docs`: 文档相关的更改。
        *   `style`: 代码风格调整（不影响代码逻辑，如格式化、缺少分号等）。
        *   `refactor`: 代码重构（既不是新功能也不是 Bug 修复）。
        *   `perf`: 性能改进。
        *   `test`: 添加或修改测试代码。
        *   `build`: 影响构建系统或外部依赖的更改 (例如: `requirements.txt`, `setup.py`)。
        *   `ci`: CI/CD 配置文件和脚本的更改 (例如: GitHub Actions, GitLab CI)。
        *   `chore`: 其他不修改源码或测试文件的提交 (例如: 更新 `.gitignore`)。
    *   **`[optional scope]`**: 括号内，描述提交影响的范围（可选）。例如 `feat(plot): Add temporal plot functionality`。
    *   **`<description>`**: 简明扼要地描述本次提交的内容。使用现在时态，首字母小写（除非是专有名词），末尾不加句号。
*   **Body (可选)**:
    *   对提交的详细描述，解释更改的动机和与之前行为的对比。每行不超过72个字符。
*   **Footer (可选)**:
    *   包含关于破坏性变更 (Breaking Changes) 的信息，或关闭的 Issue 编号。
    *   **Breaking Change**: 以 `BREAKING CHANGE:` 或 `BREAKING-CHANGE:` 开头，后跟对破坏性变更的描述。
    *   **关闭 Issue**: 例如 `Closes #123`, `Fixes #456`。

### 4.2 示例
```
feat: Add PPSD spectrogram plotting capability

Implemented the `plot_spectrogram` function based on ObsPy's PPSD.plot_spectrogram.
Allows users to generate spectrogram views of PPSD data using the
`config_plot.toml` configuration.

Closes #42
```

```
fix(config): Correct default value for ppsd_length

The default `ppsd_length` in `config.toml` was incorrectly set to 1800.
This commit changes it to the standard 3600 seconds.
```

```
docs: Update README with installation instructions
```

```
style: Format code with Black
```

```
refactor(core): Improve efficiency of data loading module
```

```
test(plot): Add unit tests for standard PPSD plotting
```

---

遵循这些编码规范将有助于 `cp_ppsd` 项目的长期健康发展。 