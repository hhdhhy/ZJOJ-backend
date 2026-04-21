# 快速开始

> ⏱️ 预计阅读时间：5分钟

本文档帮助你快速了解 ZJOJ 项目并运行起来。

---

## 🎯 学习目标

完成本文档后，你将能够：
- ✅ 理解 ZJOJ 的核心功能
- ✅ 在本地运行开发环境
- ✅ 提交第一道题目
- ✅ 调用 API 接口

---

## 📋 前置要求

### 必需软件

| 软件 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | Django 运行环境 |
| MySQL | 5.7+ | 数据库 |
| Node.js | 16+ | go-judge 依赖 |
| Git | Latest | 代码管理 |

### 推荐工具

- VS Code / PyCharm - 代码编辑器
- Postman / Insomnia - API 测试
- DBeaver / Navicat - 数据库管理

---

## 🚀 5分钟快速启动

### 步骤 1: 克隆项目

```bash
git clone https://github.com/your-repo/ZJOJ.git
cd ZJOJ
```

### 步骤 2: 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装 Python 依赖
pip install -r requirements.txt
```

### 步骤 3: 配置数据库

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE zjoj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;

# 修改 ZJOJ/settings.py 中的数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zjoj',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 步骤 4: 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # 创建管理员账号
```

### 步骤 5: 启动服务

```bash
# 终端 1: 启动 Django
python manage.py runserver 8000

# 访问 http://localhost:8000/admin
```

🎉 **恭喜！ZJOJ 已经运行起来了！**

---

## 🧪 第一次评测

### 1. 创建题目

登录 Admin 后台 (`http://localhost:8000/admin`)：
- 进入 "Problems" → "Add Problem"
- 填写题目信息（标题、描述、时间限制、内存限制）
- 上传测试用例 ZIP 文件

### 2. 提交代码

使用 API 提交代码：

```bash
curl -X POST http://localhost:8000/api/submissions/submit/ \
  -H "Authorization: jwt YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_id": "A001",
    "language": "cpp",
    "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}"
  }'
```

### 3. 查看结果

```bash
curl http://localhost:8000/api/submissions/SUBMISSION_ID/ \
  -H "Authorization: jwt YOUR_TOKEN"
```

预期返回：
```json
{
  "status": "ACCEPTED",
  "score": 100,
  "time_used": 12,
  "memory_used": 3200
}
```

---

## 📚 下一步学习

根据你的角色选择学习路径：

### 👨‍💻 开发者
- [系统架构](02-ARCHITECTURE.md) - 了解技术设计
- [开发指南](05-DEVELOPMENT.md) - 代码规范和最佳实践
- [模块详解](06-MODULES/) - 深入各个功能模块

### 🔧 运维工程师
- [部署指南](03-DEPLOYMENT.md) - 生产环境部署
- [监控和日志](03-DEPLOYMENT.md#监控) - 系统监控配置

### 🎓 API 使用者
- [API 参考](04-API_REFERENCE.md) - 完整的接口文档
- [认证说明](06-MODULES/auth.md) - JWT Token 使用

---

## ❓ 常见问题

### Q1: 如何获取 JWT Token？

```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

返回的 `token` 字段即为 JWT Token。

### Q2: 评测服务未运行？

确保 go-judge 正在运行：

```bash
# 检查状态
sudo pm2 status | grep hydro-sandbox

# 启动服务
sudo pm2 start hydro-sandbox
```

### Q3: 数据库连接失败？

检查：
1. MySQL 服务是否启动
2. 数据库配置是否正确
3. 用户权限是否足够

```bash
# 测试连接
mysql -u root -p -h localhost zjoj
```

### Q4: 导入依赖时出错？

确保使用正确的 Python 版本：

```bash
python --version  # 应该 >= 3.8
pip --version     # 应该对应 Python 3.8+
```

---

## 🆘 获取帮助

遇到问题？

1. 📖 查看[完整文档](README.md)
2. 🔍 搜索已有 Issue
3. 💬 加入社区讨论群
4. 📝 提交新 Issue

---

<div align="center">

**继续学习 →** [系统架构](02-ARCHITECTURE.md)

</div>
