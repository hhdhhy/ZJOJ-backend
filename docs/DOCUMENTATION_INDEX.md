# ZJOJ 项目文档中心

## 📖 欢迎使用 ZJOJ 文档

本文档中心提供了 ZJOJ（铸剑在线评测系统）的完整技术文档，帮助开发者快速理解项目架构、进行二次开发或部署运维。

---

## 🚀 快速导航

### 📌 新手入门

- **[项目总览](TECHNICAL_OVERVIEW.md)** - 了解项目整体情况
- **[快速开始](01-GETTING_STARTED.md)** - 5分钟快速上手
- **[开发指南](05-DEVELOPMENT.md)** - 开发规范与最佳实践

### 🏗️ 系统架构

- **[架构设计](02-ARCHITECTURE.md)** - 系统整体架构与技术选型
- **[数据库设计](07-DATABASE.md)** - 数据模型概览
- **[数据库详细设计](DATABASE_DETAILED.md)** - 完整的表结构、索引、优化策略

### 🔧 核心模块

#### 评测系统
- **[评测系统概览](JUDGE_SYSTEM.md)** - go-judge 集成指南
- **[评测系统详解](JUDGE_SYSTEM_DETAILED.md)** - 编译、执行、结果判定全流程
- **[go-judge 文档](GOJUDGE_DOCUMENTATION.md)** - go-judge 官方文档总结

#### AI 助手
- **[AI 助手模块](06-MODULES/ai-assistant.md)** - RAG 架构概览
- **[AI 助手详解](AI_ASSISTANT_DETAILED.md)** - 向量检索、DeepSeek 集成详解

#### 其他模块
- **[用户认证](06-MODULES/auth.md)** - JWT 认证与权限管理
- **[题目管理](06-MODULES/problem.md)** - 题目的 CRUD 操作
- **[权限系统](06-MODULES/permission-system.md)** - 角色与权限控制

### 🚀 部署运维

- **[部署指南](03-DEPLOYMENT.md)** - Docker 部署基础
- **[Docker 部署详解](DOCKER_DEPLOYMENT.md)** - 容器化部署最佳实践
- **[部署与运维详解](DEPLOYMENT_DETAILED.md)** - 生产环境部署、监控、故障排查

### 📡 API 参考

- **[API 参考文档](04-API_REFERENCE.md)** - 完整的 REST API 文档

---

## 📚 文档分类

### 按角色分类

#### 👨‍💻 开发者
1. [快速开始](01-GETTING_STARTED.md)
2. [开发指南](05-DEVELOPMENT.md)
3. [API 参考](04-API_REFERENCE.md)
4. [架构设计](02-ARCHITECTURE.md)

#### 🔧 运维工程师
1. [部署指南](03-DEPLOYMENT.md)
2. [部署与运维详解](DEPLOYMENT_DETAILED.md)
3. [Docker 部署详解](DOCKER_DEPLOYMENT.md)

#### 🎓 学习者
1. [项目总览](TECHNICAL_OVERVIEW.md)
2. [评测系统概览](JUDGE_SYSTEM.md)
3. [AI 助手模块](06-MODULES/ai-assistant.md)

### 按主题分类

#### 基础概念
- [项目总览](TECHNICAL_OVERVIEW.md)
- [架构设计](02-ARCHITECTURE.md)
- [数据库设计](07-DATABASE.md)

#### 核心技术
- [评测系统详解](JUDGE_SYSTEM_DETAILED.md)
- [AI 助手详解](AI_ASSISTANT_DETAILED.md)
- [go-judge 文档](GOJUDGE_DOCUMENTATION.md)

#### 实战指南
- [快速开始](01-GETTING_STARTED.md)
- [部署与运维详解](DEPLOYMENT_DETAILED.md)
- [开发指南](05-DEVELOPMENT.md)

---

## 📊 文档统计

| 类别 | 文档数量 | 说明 |
|------|---------|------|
| 基础文档 | 5 | 快速开始、架构、部署、API、开发指南 |
| 模块文档 | 5 | 认证、题目、评测、AI、权限 |
| 详细实现 | 4 | 评测系统、AI 助手、数据库、部署运维 |
| 专项文档 | 2 | go-judge、Docker 部署 |
| **总计** | **16** | - |

---

## 🔍 常见问题

### Q1: 如何快速搭建开发环境？

查看 [快速开始](01-GETTING_STARTED.md)，按照步骤操作即可在 5 分钟内完成环境搭建。

### Q2: 如何理解评测系统的工作原理？

推荐阅读顺序：
1. [评测系统概览](JUDGE_SYSTEM.md) - 了解基本概念
2. [评测系统详解](JUDGE_SYSTEM_DETAILED.md) - 深入理解实现细节
3. [go-judge 文档](GOJUDGE_DOCUMENTATION.md) - 学习 go-judge 的使用

### Q3: 如何部署到生产环境？

查看 [部署与运维详解](DEPLOYMENT_DETAILED.md)，包含完整的生产环境部署流程、监控配置和故障排查指南。

### Q4: AI 助手是如何工作的？

阅读 [AI 助手详解](AI_ASSISTANT_DETAILED.md)，了解 RAG 架构、向量检索和 DeepSeek API 集成的完整流程。

### Q5: 数据库表结构是怎样的？

查看 [数据库详细设计](DATABASE_DETAILED.md)，包含所有表的字段说明、索引策略和常用查询示例。

---

## 📝 文档更新日志

### 2026-04-27
- ✅ 创建项目技术文档总览
- ✅ 新增评测系统详细实现文档
- ✅ 新增 AI 助手详细实现文档
- ✅ 新增数据库详细设计文档
- ✅ 新增部署与运维详细文档
- ✅ 完善文档导航和索引

---

## 💡 贡献指南

如果您发现文档错误或需要补充内容，欢迎：

1. 提交 Issue 描述问题
2. 提交 Pull Request 修复文档
3. 通过邮件联系维护者

---

## 📧 联系方式

- GitHub Issues: https://github.com/your-repo/ZJOJ/issues
- Email: your-email@example.com
- 文档维护者: ZJOJ Team

---

**最后更新**: 2026-04-27  
**文档版本**: v1.0.0
