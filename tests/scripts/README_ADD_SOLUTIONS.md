# 在服务器上添加错误解决方案文档

## 📋 说明

本文档包含5个详细的错误解决方案文档，需要在**云服务器**上执行导入。

## 📦 包含的文档

### 算法特定的错误分析
1. ✅ **动态规划 WA 常见原因** - DP状态定义、边界条件、转移方程等
2. ✅ **图论 TLE 优化技巧** - 算法选择、堆优化、剪枝等
3. ✅ **字符串 RE 常见问题** - 越界、空字符串、递归深度等

### 通用错误类型指南
4. ✅ **WA 常见原因及调试方法** - 边界条件、逻辑错误、对拍等
5. ✅ **TLE 时间复杂度优化** - 复杂度分析、前缀和、二分查找等

## 🚀 部署步骤

### 方法1：使用 Shell 脚本（推荐）

```bash
# 1. SSH 登录服务器
ssh zjoj@your-server-ip

# 2. 进入项目目录
cd /home/zjoj/ZJOJ

# 3. 拉取最新代码
git pull

# 4. 执行导入脚本
bash tests/scripts/add_error_solutions_server.sh
```

### 方法2：手动执行

```bash
# 1. SSH 登录服务器
ssh zjoj@your-server-ip

# 2. 进入项目目录
cd /home/zjoj/ZJOJ

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 执行 Python 脚本
python tests/scripts/add_error_solutions_detailed.py
```

## 📊 预期输出

```
============================================================
开始添加错误解决方案到知识库
============================================================
✅ 已创建文档: 动态规划 WA 常见原因
   📚 已同步到向量数据库
✅ 已创建文档: 图论 TLE 优化技巧
   📚 已同步到向量数据库
✅ 已创建文档: 字符串 RE 常见问题
   📚 已同步到向量数据库
✅ 已创建文档: WA 常见原因及调试方法
   📚 已同步到向量数据库
✅ 已创建文档: TLE 时间复杂度优化
   📚 已同步到向量数据库

============================================================
添加完成！
  ✅ 新增: 5 个文档
  ⚠️  跳过: 0 个文档
  📊 总计: 5 个文档
============================================================
```

## ⚠️ 注意事项

1. **必须在服务器上执行**：需要访问 MySQL 数据库和 ChromaDB
2. **确保服务正常运行**：Django、MySQL、Redis 都需要运行
3. **重复执行安全**：脚本会检测已存在的文档，不会重复添加
4. **首次执行较慢**：需要加载 Embedding 模型（约30秒）

## 🔍 验证结果

执行完成后，可以通过 API 验证：

```bash
# 获取 Token
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# 查询知识库
curl -X GET "http://localhost:8000/api/ai/knowledge/?doc_type=error_solution" \
  -H "Authorization: jwt YOUR_TOKEN"
```

应该能看到新添加的5个文档。

## 🎯 效果测试

添加完成后，可以测试错误解决方案推送：

1. 提交一个会 WA 的代码
2. 调用错误解决方案接口
3. 查看是否返回相关的解决方案

```bash
curl -X GET http://localhost:8000/api/ai/error-solution/{submission_id}/ \
  -H "Authorization: jwt YOUR_TOKEN"
```

---

**文档位置**：`tests/scripts/add_error_solutions_detailed.py`  
**创建时间**：2026-04-27
