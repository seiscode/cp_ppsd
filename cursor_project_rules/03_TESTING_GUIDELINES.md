# 03_TESTING_GUIDELINES.md - 测试指南

本文档为 `cp_ppsd` 项目提供测试相关的指南，包括测试策略、如何编写和运行测试，以及测试覆盖率的要求。遵循这些指南有助于确保代码的质量、可靠性和可维护性。

## 1. 测试策略

项目的测试策略结合了不同层级的测试，以确保各个方面的正确性。

### 1.1 单元测试 (Unit Tests)
*   **目标**: 验证项目中最小的可测试单元（通常是函数或方法）的行为是否符合预期。
*   **范围**: 专注于隔离测试，模拟外部依赖（如文件系统、网络、复杂对象），确保测试的快速和稳定。
*   **工具**: 推荐使用 Python 内置的 `unittest` 模块或更现代的 `pytest` 框架。
*   **重点**:
    *   核心算法的正确性（例如PPSD计算中的数学逻辑片段）。
    *   参数验证和边界条件处理。
    *   辅助函数和工具类的功能。
    *   配置文件解析逻辑。

### 1.2 集成测试 (Integration Tests)
*   **目标**: 验证项目中多个组件或模块协同工作时的行为是否符合预期。
*   **范围**: 测试模块间的接口、数据流和交互。可能涉及真实的文件I/O或对ObsPy等核心库的实际调用。
*   **工具**: `pytest` 非常适合编写集成测试，因其fixture机制和灵活性。
*   **重点**:
    *   从读取MiniSEED和StationXML到生成PPSD对象并保存为NPZ文件的完整流程。
    *   从加载NPZ文件到生成各种绘图的流程。
    *   配置文件参数如何正确影响计算和绘图结果的端到端路径。
    *   日志记录是否按预期在不同操作阶段生成。

### 1.3 端到端测试 (End-to-End Tests) - (视项目复杂度酌情考虑)
*   **目标**: 从用户角度验证整个应用程序（`cp_psd.py` 脚本）在真实或接近真实环境中的行为。
*   **范围**: 通过命令行接口调用脚本，使用示例配置文件和真实（或模拟的真实）数据，检查输出文件（NPZ, PNG, LOG）是否符合预期。
*   **工具**: 可以使用 `subprocess` 模块结合文件系统检查和结果比对，或者使用专门的E2E测试框架。
*   **重点**:
    *   不同命令行参数组合的正确性。
    *   脚本在处理不同类型配置文件（计算型、绘图型、组合型）时的行为。
    *   错误处理和用户反馈（例如，错误日志的生成）。

## 2. 编写测试

### 2.1 测试框架选择
*   **`pytest`**: 推荐作为主要的测试框架，因其简洁的语法、强大的fixture系统、插件生态和良好的社区支持。
*   **`unittest`**: 如果团队更熟悉或项目已有部分基于`unittest`的测试，也可以继续使用，`pytest` 可以兼容运行 `unittest` 测试用例。

### 2.2 测试文件和结构
*   测试文件应放置在项目根目录下的 `tests/` 目录中。
*   单元测试文件名通常以 `test_` 开头，后跟被测试模块的名称 (e.g., `tests/test_core_utils.py`, `tests/test_config_parser.py`)。
*   测试函数/方法名也应以 `test_` 开头 (e.g., `def test_calculate_psd_segment():`)。
*   可以根据需要创建子目录来组织测试，例如 `tests/unit/` 和 `tests/integration/`。

### 2.3 良好测试的原则 (Arrange-Act-Assert)
每个测试用例应遵循清晰的结构：
1.  **准备 (Arrange)**: 设置测试所需的前提条件。这可能包括创建对象实例、准备输入数据（例如，创建临时的MiniSEED文件、模拟的StationXML对象、PPSD对象）、配置模拟依赖等。
    *   对于地球物理数据，可以使用ObsPy创建小型的、可控的 `Trace` 或 `Stream` 对象，或者准备非常小的、确定的示例数据文件。
2.  **执行 (Act)**: 调用被测试的代码（函数、方法）。
3.  **断言 (Assert)**: 验证执行结果是否与预期相符。使用测试框架提供的断言方法（如 `assert result == expected`, `pytest.raises(ValueError)`）。
    *   对于数值结果（如计算出的PSD值），注意浮点数比较的精度问题，可以使用 `np.testing.assert_almost_equal` 或 `pytest.approx`。
    *   验证生成的文件内容、图像特征（如果可能，但图像比较困难，通常验证元数据或日志更实际）。

### 2.4 测试用例设计
*   **覆盖正常路径**: 测试代码在典型输入和条件下的行为。
*   **覆盖边界条件**: 测试输入数据的最小值、最大值、空值、特殊值等。
    *   例如，测试 `period_limits` 为空或无效，`ppsd_length` 为0或负数。
*   **覆盖错误路径**: 测试代码在接收到无效输入或遇到预期错误情况时的行为（例如，文件未找到、仪器响应不匹配）。确保抛出正确的异常。
*   **保持测试独立**: 每个测试用例应独立于其他测试用例，不应依赖于其他测试的执行顺序或副作用。
*   **测试应快速**: 尤其是单元测试，应尽可能快地运行，以便频繁执行。
*   **可读性**: 测试代码也应易于阅读和理解。使用清晰的变量名和测试描述。

### 2.5 使用 Fixtures (`pytest`)
*   利用 `pytest`的 [fixtures](https://docs.pytest.org/en/stable/fixture.html) 来管理测试的准备阶段，创建可重用的测试设置和数据。
    *   例如，可以创建一个fixture来生成一个临时的 `output_dir`，或加载一个标准的测试用PPSD对象。
    ```python
    # tests/conftest.py (或者直接在测试文件中)
    import pytest
    import tempfile
    import shutil
    from pathlib import Path

    @pytest.fixture
    def temp_output_dir():
        """创建一个临时输出目录，测试结束后自动清理。"""
        path = Path(tempfile.mkdtemp(prefix="ppsd_test_"))
        yield path
        shutil.rmtree(path)
    ```

### 2.6 模拟 (Mocking)
*   使用 `unittest.mock` 模块 (或 `pytest-mock` 插件) 来模拟外部依赖或难以控制的部分。
    *   例如，模拟 `obspy.read()` 以避免实际文件读取，或模拟 `PPSD.plot()` 以避免实际生成图像，仅检查其是否被正确调用。

## 3. 运行测试

### 3.1 命令行执行
*   **`pytest`**:
    *   在项目根目录下运行 `pytest` 命令，它会自动发现并执行 `tests/` 目录下的所有测试。
    *   常用选项:
        *   `pytest -v`: (Verbose) 显示更详细的输出。
        *   `pytest -k "expression"`: 运行名称匹配表达式的测试。
        *   `pytest tests/specific_file.py`: 运行特定文件中的测试。
        *   `pytest tests/specific_file.py::test_specific_function`: 运行特定测试函数。
        *   `pytest --cov=src_directory`: (需要 `pytest-cov` 插件) 同时计算代码覆盖率。

### 3.2 IDE 集成
*   主流 Python IDE (如 VS Code, PyCharm) 都提供了对 `pytest` 和 `unittest` 的良好集成，可以直接在 IDE 中运行测试、查看结果和调试失败的测试。
*   通常，IDE会自动检测项目中的测试配置。

## 4. 测试覆盖率

### 4.1 目标
*   力求较高的测试覆盖率，以增加对代码正确性的信心。
*   **目标覆盖率**: 建议至少达到 **80%** 的语句覆盖率，关键核心模块应追求更高覆盖率 (如 >90%)。
*   覆盖率是衡量测试完整性的一个指标，但不是唯一指标。100%的覆盖率并不意味着代码没有bug，还需要高质量的测试用例。

### 4.2 工具
*   **`Coverage.py`**: 是 Python 中标准的测试覆盖率工具。
*   **`pytest-cov`**: `pytest` 的一个插件，可以方便地与 `pytest` 集成使用 `Coverage.py`。

### 4.3 生成覆盖率报告
1.  安装 `pytest-cov`: `pip install pytest-cov`
2.  运行测试并生成覆盖率数据:
    ```bash
    pytest --cov=cp_ppsd --cov-report=html --cov-report=term
    ```
    (假设您的主代码在 `cp_ppsd` 目录或模块下，请相应调整 `--cov` 参数)
    *   `--cov-report=term`: 在终端显示覆盖率摘要。
    *   `--cov-report=html`: 生成一个 HTML 格式的详细覆盖率报告 (通常在 `htmlcov/` 目录下)，可以逐行查看哪些代码被覆盖，哪些没有。

### 4.4 持续集成 (CI)
*   在 CI/CD 流程中集成测试运行和覆盖率检查，确保每次代码提交或合并请求都通过所有测试，并达到预期的覆盖率标准。

---

编写和维护良好的测试是确保 `cp_ppsd` 项目质量的关键。鼓励所有贡献者在添加新功能或修复bug时编写相应的测试。 