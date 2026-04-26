# 项目文件整理总结

## 📅 整理时间
2026年4月27日

## ✅ 完成的整理工作

### 1. 测试脚本整理

**问题**：根目录有16个测试文件（9个 .py + 7个 .sh），导致项目结构混乱。

**解决方案**：
- 创建 `tests/scripts/` 目录专门存放测试脚本
- 移动所有 `test_*.py` 和 `test_*.sh` 文件到该目录
- 更新 `.gitignore` 排除测试脚本（但保留 tests/scripts 下的）
- 创建 `tests/scripts/README.md` 说明文档

**结果**：
```
tests/scripts/
├── README.md
├── test_absolute_path.py
├── test_adapter_compile.py
├── test_ai_chat.sh
├── test_ai_local.py
├── test_compile.py
├── test_compile.sh
├── test_compile_direct.sh
├── test_compile_in_celery.py
├── test_cpp.sh
├── test_cpp_cached.sh
├── test_cpp_multi_cmd.sh
├── test_gojudge.sh
├── test_gojudge_compile.py
├── test_judge.py
├── test_simple.py
└── test_submission.py
```

### 2. 文档整理

**问题**：docs 目录有重复和过时的文档。

**删除的文件**：
- `API_DOCUMENTATION.md` - 只包含示例代码，不是真正的 API 文档
- `PROJECT_DOCUMENTATION.md` - 旧的主文档，已被编号文档替代
- `REFACTORING_COMPLETE.md` - 重构完成临时文档
- `REFACTORING_GUIDE.md` - 重构指南临时文档

**保留的核心文档**：
```
docs/
├── README.md                          # 文档索引
├── 01-GETTING_STARTED.md              # 快速开始
├── 02-ARCHITECTURE.md                 # 架构设计
├── 03-DEPLOYMENT.md                   # 部署指南
├── 04-API_REFERENCE.md                # API 参考
├── 05-DEVELOPMENT.md                  # 开发指南
├── 06-MODULES/                        # 模块文档
├── 07-DATABASE.md                     # 数据库设计
├── DOCKER_DEPLOYMENT.md               # Docker 部署详解
├── GOJUDGE_DOCUMENTATION.md           # go-judge 文档总结
└── JUDGE_SYSTEM.md                    # 评测系统文档
```

### 3. 脚本目录整理

**问题**：部署脚本散落在根目录。

**解决方案**：
- 创建 `scripts/` 目录存放部署和维护脚本
- 移动 `auto_deploy.py` 和 `deploy.ps1` 到 scripts 目录
- 创建 `scripts/README.md` 说明文档

**结果**：
```
scripts/
├── README.md
├── auto_deploy.py
└── deploy.ps1
```

### 4. Git 配置更新

更新 `.gitignore` 文件：
```gitignore
# Test scripts (keep only essential tests in tests/ directory)
test_*.py
test_*.sh
!tests/test_*.py
!tests/scripts/test_*.py
!tests/scripts/test_*.sh
create_*.py
upload_*.py
```

## 📊 整理效果对比

### 整理前
```
ZJOJ/
├── test_*.py (9 files) ❌ 混乱
├── test_*.sh (7 files) ❌ 混乱
├── auto_deploy.py     ❌ 位置不当
├── deploy.ps1         ❌ 位置不当
├── docs/ (15 files)   ❌ 有重复
└── ...
```

### 整理后
```
ZJOJ/
├── scripts/           ✅ 集中管理
│   ├── README.md
│   ├── auto_deploy.py
│   └── deploy.ps1
├── tests/
│   └── scripts/       ✅ 分类清晰
│       ├── README.md
│       ├── test_*.py (9 files)
│       └── test_*.sh (7 files)
├── docs/ (11 files)   ✅ 无重复
└── ...
```

## 🎯 整理原则

1. **职责分离**：不同类型的文件放在不同的目录
2. **命名规范**：测试文件统一以 `test_` 开头
3. **文档化**：每个目录都有 README 说明
4. **版本控制**：测试脚本不提交到 Git
5. **易于维护**：清晰的目录结构便于查找和管理

## 📝 后续建议

1. **定期清理**：每季度检查一次项目结构
2. **文档更新**：保持文档与代码同步
3. **脚本规范**：所有脚本添加注释说明用途
4. **自动化**：考虑使用 pre-commit hooks 自动检查文件位置

## 🔗 相关文档

- [项目主文档](../README.md)
- [部署指南](../DEPLOY.md)
- [开发指南](../docs/05-DEVELOPMENT.md)
