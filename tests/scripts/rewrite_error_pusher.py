# -*- coding: utf-8 -*-
"""
重写 error_pusher.py 文件，包含所有优化
"""

file_path = r'E:\learning file\ZJOJ\apps\ai_assistant\error_pusher.py'

content = '''"""
判题失败自动推送服务
当学生提交代码评测失败时，自动从知识库检索相关解决方案并推送
"""
from apps.problem.models import Submission
from apps.ai_assistant.rag_engine import RAGEngine
from apps.ai_assistant.api_optimizer import APICallOptimizer


class ErrorSolutionPusher:
    """错误解决方案推送器"""
    
    @staticmethod
    def push_on_judge_failure(submission_id):
        """
        在判题失败后推送解决方案
        :param submission_id: 提交记录ID
        :return: 解决方案列表
        """
        try:
            submission = Submission.objects.select_related('problem').get(id=submission_id)
        except Submission.DoesNotExist:
            return []
        
        # 只对非AC的提交推送
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
                pass
        
        # 去重（基于标题）
        seen_titles = set()
        unique_solutions = []
        for sol in solutions:
            if sol['title'] not in seen_titles:
                seen_titles.add(sol['title'])
                unique_solutions.append(sol)
        
        return unique_solutions[:3]  # 最多返回3个
    
    @staticmethod
    def get_error_suggestions(problem_id, error_type, top_k=3):
        """
        获取特定题目和错误类型的建议
        :param problem_id: 题目ID
        :param error_type: 错误类型（WA/TLE/MLE/RE/CE）
        :param top_k: 返回数量
        :return: 建议列表
        """
        query = f"{problem_id} {error_type}"
        
        engine = RAGEngine()
        try:
            results = engine.search_knowledge_base(
                query=query,
                doc_type='error_solution',
                top_k=top_k
            )
            
            suggestions = []
            for doc in results:
                suggestions.append({
                    'title': doc['title'],
                    'content': doc['content'],  # 返回完整内容，前端通过滚动条展示
                    'relevance_score': doc.get('score', 0),
                })
            
            return suggestions
        except Exception as e:
            return []
'''

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 文件重写完成！")
print("\n主要改进：")
print("1. ✅ 移除内容截断（返回完整内容）")
print("2. ✅ 增加题目标签作为查询关键词")
print("3. ✅ 按优先级构建5种查询策略")
print("4. ✅ 添加通用错误类型兜底方案")
