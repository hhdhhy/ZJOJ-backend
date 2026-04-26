# Scripts 目录

本目录包含项目的各种脚本文件。

## 目录结构

```
scripts/
├── auto_deploy.py          # 自动部署脚本
├── deploy.ps1              # Windows PowerShell 部署脚本
└── README.md               # 本文件
```

## 测试脚本

测试相关的脚本位于 `tests/scripts/` 目录：

```
tests/scripts/
├── test_*.py               # Python 测试脚本
└── test_*.sh               # Shell 测试脚本
```

## 使用说明

### 自动部署

```bash
# Linux/Mac
python scripts/auto_deploy.py

# Windows
.\scripts\deploy.ps1
```

### 运行测试

```bash
# 运行 Python 测试
python tests/scripts/test_judge.py

# 运行 Shell 测试（需要 Git Bash 或 WSL）
bash tests/scripts/test_compile.sh
```

## 注意事项

- 测试脚本不会被提交到 Git 仓库（已在 .gitignore 中配置）
- 部署脚本需要根据实际环境修改配置
- 所有脚本都应该有执行权限（Linux/Mac）
