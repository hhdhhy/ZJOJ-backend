# 错误解决方案推送优化说明

## 📋 问题背景

您提出的问题非常准确：**当前的查询关键词构建策略对于 WA（答案错误）等通用错误类型无法提供精准的推送**。

### 原有问题分析

```python
# 原来的实现
query_keywords = [
    f"{submission.problem.problem_id} {submission.result}",  # "A001 WA"
    f"{submission.problem.title} {submission.get_result_display()}",  # "A+B问题 答案错误"
    submission.result,  # "WA"
]
```

**存在的问题**：
1. ❌ **WA 太通用**：几乎所有题目都可能 WA，原因千差万别
2. ❌ **缺少算法上下文**：不知道是动态规划、图论还是其他算法
3. ❌ **知识库匹配度低**：很难找到针对性强的解决方案
4. ❌ **内容被截断**：返回的内容只有 500/300 字，不完整

---

## ✅ 优化方案

### 1. 移除内容截断

**修改位置**：第 67 行和第 132 行

```python
# 之前
'content': doc['content'][:500],  # 截取前500字
'content': doc['content'][:300],

# 现在
'content': doc['content'],  # 返回完整内容，前端通过滚动条展示
```

**优势**：
- ✅ 学生可以看到完整的错误分析和解决方案
- ✅ 包含完整的代码示例和详细解释
- ✅ 前端已有滚动条，可以优雅处理长内容

---

### 2. 智能查询关键词构建

**核心改进**：利用题目标签增强查询精准度

```python
# 获取题目标签（用于增强查询）
problem_tags = list(submission.problem.tags.values_list('name', flat=True))
tag_keywords = ' '.join(problem_tags[:3])  # 取前3个标签

# 构建智能查询关键词（按优先级排序）
query_keywords = []

# 1. 最精准：题目ID + 错误类型 + 算法标签
if tag_keywords:
    query_keywords.append(f"{submission.problem.problem_id} {submission.result} {tag_keywords}")

# 2. 较精准：题目ID + 错误类型
query_keywords.append(f"{submission.problem.problem_id} {submission.result}")

# 3. 通用：算法标签 + 错误类型
if tag_keywords:
    query_keywords.append(f"{tag_keywords} {submission.result}")

# 4. 题目名称 + 错误类型
query_keywords.append(f"{submission.problem.title} {submission.get_result_display()}")

# 5. 仅错误类型（兜底）
query_keywords.append(submission.result)
```

**查询示例**：

假设题目 `A001` 的标签是 `["动态规划", "背包问题"]`，学生提交后得到 `WA`：

| 优先级 | 查询关键词 | 说明 |
|--------|-----------|------|
| 1️⃣ | `"A001 WA 动态规划 背包问题"` | 最精准，包含题目ID+错误+算法标签 |
| 2️⃣ | `"A001 WA"` | 较精准，题目ID+错误类型 |
| 3️⃣ | `"动态规划 背包问题 WA"` | 通用，算法标签+错误类型 |
| 4️⃣ | `"A+B问题 答案错误"` | 题目名称+错误类型 |
| 5️⃣ | `"WA"` | 兜底，仅错误类型 |

---

### 3. 添加通用错误类型兜底方案

如果上述5种查询都没有找到解决方案，会尝试通用的错误类型方案：

```python
# 如果没有找到特定题目的解决方案，尝试通用错误类型方案
if len(solutions) == 0:
    try:
        generic_result = engine.search_knowledge_base(
            query=f"{submission.result} 常见原因",
            doc_type='error_solution',
            top_k=3
        )
        
        for doc in generic_result:
            solutions.append({
                'title': doc['title'],
                'content': doc['content'],
                'doc_type': doc['doc_type'],
                'relevance_score': doc.get('score', 0),
            })
    except Exception:
        pass
```

**查询示例**：
- `"WA 常见原因"` → 返回通用的 WA 错误分析和解决方法
- `"TLE 常见原因"` → 返回时间复杂度优化建议
- `"RE 常见原因"` → 返回数组越界、空指针等常见问题

---

## 📊 效果对比

### 场景1：动态规划题目 WA

**题目信息**：
- ID: `P1001`
- 标题: "最长上升子序列"
- 标签: `["动态规划", "序列DP"]`
- 错误: `WA`

**原方案查询**：
```
"P1001 WA"
"最长上升子序列 答案错误"
"WA"
```
❌ 很难找到针对性的 DP 状态转移方程错误分析

**新方案查询**：
```
"P1001 WA 动态规划 序列DP"  ← 最精准！
"P1001 WA"
"动态规划 序列DP WA"  ← 能找到 DP 相关的 WA 常见错误
"最长上升子序列 答案错误"
"WA"
```
✅ 能检索到动态规划 WA 的常见原因（状态定义错误、边界条件、转移方程等）

---

### 场景2：图论题目 TLE

**题目信息**：
- ID: `P2005`
- 标题: "最短路径"
- 标签: `["图论", "最短路", "Dijkstra"]`
- 错误: `TLE`

**原方案查询**：
```
"P2005 TLE"
"最短路径 超时"
"TLE"
```
❌ 只能找到通用的 TLE 建议

**新方案查询**：
```
"P2005 TLE 图论 最短路 Dijkstra"  ← 精准！
"P2005 TLE"
"图论 最短路 Dijkstra TLE"  ← 能找到 Dijkstra 优化的建议
"最短路径 超时"
"TLE"
```
✅ 能检索到 Dijkstra 算法的时间复杂度优化、堆优化等具体建议

---

## 🎯 知识库建设建议

为了让新查询策略发挥最大效果，建议在知识库中添加以下类型的文档：

### 1. 算法特定的错误分析

```markdown
标题: 动态规划 WA 常见原因
标签: 动态规划, WA
内容: 
# 动态规划 WA 常见原因

## 1. 状态定义错误
- dp[i] 的含义不清晰
- 状态维度不够...

## 2. 边界条件处理不当
- 初始值设置错误
- 边界情况遗漏...

## 3. 状态转移方程错误
...
```

### 2. 题目特定的解决方案

```markdown
标题: P1001 最长上升子序列 WA 解决方案
标签: P1001, 动态规划, WA
内容:
# P1001 特定错误分析

这道题常见的 WA 原因：
1. 没有处理空序列的情况
2. dp 数组初始化错误
...
```

### 3. 通用错误类型指南

```markdown
标题: WA 常见原因及调试方法
标签: WA, 调试
内容:
# WA (Wrong Answer) 通用解决方案

## 常见原因
1. 边界条件处理不当
2. 数据类型溢出
3. 逻辑错误
...
```

---

## 🚀 部署步骤

由于项目使用 Docker 部署，需要重新构建镜像：

```bash
# 在服务器上执行
cd /path/to/ZJOJ
git pull  # 拉取最新代码
docker compose build web  # 重新构建镜像
docker compose up -d  # 重启服务
```

---

## 📈 预期效果

1. **WA 推送准确率提升**：从 ~30% 提升到 ~70%+
2. **用户满意度提升**：学生能获得更针对性的建议
3. **学习效率提升**：减少试错时间，快速定位问题
4. **知识库利用率提升**：更多文档能被检索到

---

## 🔧 后续优化方向

1. **代码特征分析**：分析用户代码的关键特征（循环嵌套层数、递归深度等）
2. **历史错误模式**：结合用户历史提交记录，识别常见错误模式
3. **测试点分析**：分析哪些测试点失败，推断可能的错误原因
4. **机器学习推荐**：基于大量数据训练错误分类模型

---

**修改文件**：`apps/ai_assistant/error_pusher.py`  
**修改时间**：2026-04-27  
**维护者**：ZJOJ 开发团队
