# 测试脚本目录

本目录包含各种测试和调试脚本，用于开发和测试阶段。

## Python 测试脚本

- `test_judge.py` - 评测系统测试
- `test_submission.py` - 提交功能测试
- `test_ai_local.py` - AI 助手本地测试
- `test_compile.py` - 编译功能测试
- `test_gojudge_compile.py` - go-judge 编译测试
- `test_adapter_compile.py` - adapter 编译测试
- `test_absolute_path.py` - 绝对路径测试
- `test_simple.py` - 简单功能测试

## Shell 测试脚本

- `test_compile.sh` - 编译流程测试
- `test_compile_direct.sh` - 直接编译测试
- `test_cpp.sh` - C++ 代码测试
- `test_cpp_cached.sh` - C++ 缓存测试
- `test_cpp_multi_cmd.sh` - C++ 多命令测试
- `test_gojudge.sh` - go-judge API 测试
- `test_ai_chat.sh` - AI 聊天测试

## 使用方法

### Python 脚本

```bash
# 在项目根目录运行
python tests/scripts/test_judge.py
```

### Shell 脚本

```bash
# 需要 Git Bash、WSL 或 Linux/Mac 环境
bash tests/scripts/test_compile.sh

# 或者先赋予执行权限
chmod +x tests/scripts/test_compile.sh
./tests/scripts/test_compile.sh
```

## 注意事项

⚠️ **这些脚本不会被提交到 Git 仓库**

这些脚本仅用于开发和调试，已在 `.gitignore` 中配置排除。请不要将临时的测试脚本放在项目根目录。

## 添加新测试

如果需要添加新的测试脚本：
1. Python 脚本命名为 `test_*.py`
2. Shell 脚本命名为 `test_*.sh`
3. 放在此目录下
4. 在脚本开头添加注释说明用途
