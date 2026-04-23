"""
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
        
        # 构建查询关键词
        query_keywords = [
            f"{submission.problem.problem_id} {submission.result}",
            f"{submission.problem.title} {submission.get_result_display()}",
            submission.result,
        ]
        
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
                        'content': doc['content'][:500],  # 截取前500字
                        'doc_type': doc['doc_type'],
                        'relevance_score': doc.get('score', 0),
                    }
                    solutions.append(solution)
                
                # 如果找到足够的解决方案，提前退出
                if len(solutions) >= 3:
                    break
                    
            except Exception as e:
                continue
        
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
                    'content': doc['content'][:300],
                    'relevance_score': doc.get('score', 0),
                })
            
            return suggestions
        except Exception as e:
            return []
