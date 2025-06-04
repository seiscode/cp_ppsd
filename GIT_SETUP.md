# Git 仓库设置说明

## 仓库初始化完成

✅ **Git仓库已成功创建并配置**

### 仓库信息
- **分支**: `master`
- **提交数**: 2
- **最新提交**: `f83f313` - Add run_cp_ppsd_broken.py for debugging purposes

### 已配置的 .gitignore 规则

#### Python 标准忽略项
- `__pycache__/` - Python字节码缓存
- `*.py[cod]` - 编译的Python文件
- `*.egg-info/` - 包信息目录
- `.mypy_cache/` - MyPy类型检查缓存

#### 项目特定忽略项
- `logs/*.log` - 日志文件（保留目录结构）
- `output/plots/*.png` - 生成的图像文件
- `output/waveforms/*.png` - 波形图像
- `output/npz/*.npz` - NPZ数据文件
- `data/*.mseed` - 大型地震数据文件
- `.cursor/` - IDE配置文件

#### 保留的目录结构
通过 `.gitkeep` 文件保留以下空目录：
- `data/.gitkeep`
- `logs/.gitkeep`
- `output/plots/.gitkeep`
- `output/waveforms/.gitkeep`
- `output/npz/.gitkeep`

### 提交历史

1. **初始提交** (`c9e8705`)
   - 完整的PPSD项目代码库
   - 核心功能模块和配置系统
   - 文档和测试套件
   - 203个文件，92,952行代码

2. **调试文件** (`f83f313`)
   - 添加调试用的运行脚本

### 使用建议

#### 日常开发工作流
```bash
# 查看状态
git status

# 添加修改的文件
git add <file>

# 提交更改
git commit -m "描述性提交信息"

# 查看提交历史
git log --oneline
```

#### 分支管理
```bash
# 创建新功能分支
git checkout -b feature/new-feature

# 切换分支
git checkout master

# 合并分支
git merge feature/new-feature
```

#### 远程仓库（如需要）
```bash
# 添加远程仓库
git remote add origin <repository-url>

# 推送到远程
git push -u origin master
```

### 注意事项

1. **大文件处理**: 地震数据文件(.mseed)已被忽略，避免仓库过大
2. **生成文件**: 输出图像和NPZ文件不会被跟踪，保持仓库整洁
3. **日志管理**: 日志文件被忽略，但保留目录结构
4. **IDE配置**: .cursor目录被忽略，避免IDE特定配置冲突

### 项目结构概览

```
cp_ppsd/
├── .git/                    # Git仓库数据
├── .gitignore              # Git忽略规则
├── cp_ppsd/                # 核心Python包
├── cursor_project_rules/   # 项目规则和文档
├── Docs/                   # 技术文档
├── data/                   # 地震数据（.gitkeep保留）
├── input/                  # 配置文件
├── logs/                   # 日志目录（.gitkeep保留）
├── output/                 # 输出目录（.gitkeep保留）
├── tests/                  # 测试套件
├── README.md              # 项目说明
├── requirements.txt       # Python依赖
└── setup.py              # 安装脚本
```

仓库已准备就绪，可以开始正常的版本控制工作流程！ 