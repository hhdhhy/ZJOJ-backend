# -*- coding: utf-8 -*-
"""
优化 error_pusher.py 的查询关键词构建策略
"""

file_path = r'E:\learning file\ZJOJ\apps\ai_assistant\error_pusher.py'

new_code = '''        # 只对非AC的提交推送
        if submission.result == 'AC':
            return []
        
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
        
        # 从知识库检索相关解决方案
        engine = RAGEngine()
        solutions = []
        
        for query in query_keywords:
            try:
                result = engine.search_knowledge_base(
                    query=query,
                    doc_type='error_solution',
                    top_k=3
                )
                
                for doc in result:
                    solution = {
                        'title': doc['title'],
                        'content': doc['content'],  # 返回完整内容，前端通过滚动条展示
                        'doc_type': doc['doc_type'],
                        'relevance_score': doc.get('score', 0),
                    }
                    solutions.append(solution)
                
                # 如果找到足够的解决方案，提前退出
                if len(solutions) >= 3:
                    break
                    
            except Exception as e:
                continue
        
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
                pass'''

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 定位要替换的代码块
old_block_start = "        # 只对非AC的提交推送\n        if submission.result == 'AC':"
old_block_end = "        # 去重（基于标题）"

start_idx = content.find(old_block_start)
end_idx = content.find(old_block_end)

if start_idx != -1 and end_idx != -1:
    # 保留 "# 去重（基于标题）" 这一行
    new_content = content[:start_idx] + new_code + '\n        \n' + content[end_idx:]
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 查询关键词优化完成！")
    print("\n改进内容：")
    print("1. ✅ 增加题目标签作为查询关键词")
    print("2. ✅ 按优先级构建5种查询策略")
    print("3. ✅ 添加通用错误类型兜底方案")
    print("4. ✅ 保持内容完整性（已移除截断）")
else:
    print("❌ 未找到要替换的代码块")
    print(f"start_idx: {start_idx}, end_idx: {end_idx}")
