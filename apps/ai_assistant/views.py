"""
AI助手 API 视图
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .rag_engine import get_rag_engine
from .models import ChatHistory, UserProfile, LearningReport, KnowledgeBase
from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ChatHistorySerializer,
    UsageStatsSerializer,
    KnowledgeBaseSerializer
)
from .limits import AILimitChecker
from .learning_analytics import LearningAnalyticsService
from .error_pusher import ErrorSolutionPusher


class AIChatView(APIView):
    """AI 智能问答"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 1. 检查每日配额
        profile = AILimitChecker.check_daily_quota(request.user)
        
        # 2. 检查频率限制
        AILimitChecker.check_rate_limit(request.user)
        
        # 3. 验证请求
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        question = serializer.validated_data['question']
        top_k = serializer.validated_data.get('top_k', 5)
        use_rag = serializer.validated_data.get('use_rag', True)
        
        try:
            # 4. 调用 RAG 引擎或简单对话（使用全局单例）
            engine = get_rag_engine()
            
            if use_rag:
                result = engine.ask(question, top_k=top_k)
            else:
                result = engine.chat(question)
            
            # 5. 保存对话历史
            chat = ChatHistory.objects.create(
                user=request.user,
                question=question,
                answer=result['answer'],
                sources=result.get('sources', []),
                tokens_used=result['tokens_used']
            )
            
            # 6. 增加使用次数
            AILimitChecker.increment_usage(request.user)
            
            # 7. 修剪历史记录
            AILimitChecker.trim_history(request.user)
            
            # 8. 返回结果
            response_data = {
                'answer': result['answer'],
                'tokens_used': result['tokens_used'],
                'remaining_quota': profile.daily_quota - profile.used_today - 1,
                'chat_id': chat.id
            }
            
            if use_rag and 'sources' in result:
                response_data['sources'] = result['sources']
            
            return Response(response_data)
        
        except Exception as e:
            return Response({
                'error': f'处理失败: {str(e)}'
            }, status=500)


class ChatHistoryView(APIView):
    """获取对话历史"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, chat_id=None):
        """
        获取对话历史
        - 如果提供 chat_id，返回单条记录详情
        - 否则返回历史记录列表
        """
        # 如果提供了 chat_id，返回单条记录
        if chat_id is not None:
            return self._get_chat_detail(request, chat_id)
        
        # 否则返回列表
        return self._get_chat_list(request)
    
    def _get_chat_detail(self, request, chat_id):
        """获取单条聊天记录详情"""
        try:
            chat = ChatHistory.objects.get(id=chat_id, user=request.user)
            serializer = ChatHistorySerializer(chat)
            return Response(serializer.data)
        except ChatHistory.DoesNotExist:
            return Response({
                'error': '聊天记录不存在或无权访问'
            }, status=404)
    
    def _get_chat_list(self, request):
        """获取聊天记录列表"""
        # 获取查询参数
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        # 查询对话历史
        histories = ChatHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')[offset:offset + limit]
        
        serializer = ChatHistorySerializer(histories, many=True)
        
        # 获取总数
        total = ChatHistory.objects.filter(user=request.user).count()
        
        return Response({
            'count': total,
            'results': serializer.data
        })


class UsageStatsView(APIView):
    """获取使用情况统计"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # 重置今日计数
        today = timezone.now().date()
        if profile.last_reset_date != today:
            profile.used_today = 0
            profile.last_reset_date = today
            profile.save()
        
        # 获取历史记录数
        history_count = ChatHistory.objects.filter(user=request.user).count()
        
        return Response({
            'daily_quota': profile.daily_quota,
            'used_today': profile.used_today,
            'remaining': profile.daily_quota - profile.used_today,
            'max_history': profile.max_history,
            'history_count': history_count,
            'reset_time': '明天 00:00'
        })


class ClearHistoryView(APIView):
    """清空对话历史"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        # 删除所有对话历史
        deleted_count, _ = ChatHistory.objects.filter(user=request.user).delete()
        
        return Response({
            'message': f'已清空 {deleted_count} 条对话记录'
        })


class StudentLearningReportView(APIView):
    """学生个性化学情报告"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取学生学情报告"""
        days = int(request.query_params.get('days', 7))
        
        # 检查权限：只有学生可以查看自己的报告
        
        try:
            report = LearningAnalyticsService.get_or_generate_student_report(
                request.user, days
            )
            
            if not report:
                return Response({
                    'message': '暂无学习数据',
                    'data': None
                })
            
            return Response({
                'report_type': report.get_report_type_display(),
                'period': f"{report.period_start} 至 {report.period_end}",
                'summary': report.summary,
                'statistics': report.statistics,
                'recommendations': report.recommendations,
                'generated_at': report.generated_at,
            })
        except Exception as e:
            return Response({
                'error': f'生成报告失败: {str(e)}'
            }, status=500)


class ClassLearningReportView(APIView):
    """班级共性学情报告（教练）"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, class_id):
        """获取班级学情报告"""
        from apps.ojauth.models import Class, ClassMember
        
        days = int(request.query_params.get('days', 7))
        
        # 获取班级
        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({
                'error': '班级不存在'
            }, status=404)
        
        # 权限检查：只有教练或管理员可以查看
        user = request.user
        if not (user.is_coach() and class_obj.coach == user) and not user.is_admin_user():
            return Response({
                'error': '无权查看此班级的报告'
            }, status=403)
        
        try:
            report = LearningAnalyticsService.get_or_generate_class_report(
                class_obj, user, days
            )
            
            if not report:
                return Response({
                    'message': '暂无学习数据',
                    'data': None
                })
            
            return Response({
                'report_type': report.get_report_type_display(),
                'class_name': class_obj.name,
                'period': f"{report.period_start} 至 {report.period_end}",
                'summary': report.summary,
                'statistics': report.statistics,
                'recommendations': report.recommendations,
                'generated_at': report.generated_at,
            })
        except Exception as e:
            return Response({
                'error': f'生成报告失败: {str(e)}'
            }, status=500)


class ErrorSolutionView(APIView):
    """判题失败错误解决方案"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, submission_id):
        """获取提交记录的错误解决方案"""
        user = request.user
        
        # 检查配额（与 AI 问答共用）
        quota_check = AIUsageTracker.check_daily_quota(user)
        if not quota_check['allowed']:
            return Response({
                'error': f'今日配额已用完 ({quota_check["used"]}/{quota_check["daily_quota"]})',
                'remaining': 0,
                'reset_time': '明天 00:00'
            }, status=429)
        
        try:
            solutions = ErrorSolutionPusher.push_on_judge_failure(submission_id)
            
            # 记录使用情况
            AIUsageTracker.record_usage(
                user=user,
                tokens_used=0,  # 错误解决方案不消耗 token
                chat_id=None
            )
            
            # 获取剩余配额
            remaining = AIUsageTracker.get_remaining_quota(user)
            
            return Response({
                'submission_id': submission_id,
                'solutions': solutions,
                'count': len(solutions),
                'remaining_quota': remaining,
            })
        except Exception as e:
            return Response({
                'error': f'获取解决方案失败: {str(e)}'
            }, status=500)


class KnowledgeBaseView(APIView):
    """知识库管理"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, kb_id=None):
        """
        获取知识库文档
        - 如果提供 kb_id，返回单个文档详情
        - 否则返回文档列表（支持过滤）
        """
        if kb_id is not None:
            return self._get_knowledge_detail(request, kb_id)
        return self._get_knowledge_list(request)
    
    def _get_knowledge_detail(self, request, kb_id):
        """获取单个知识库文档详情"""
        try:
            doc = KnowledgeBase.objects.get(id=kb_id)
            serializer = KnowledgeBaseSerializer(doc)
            return Response(serializer.data)
        except KnowledgeBase.DoesNotExist:
            return Response({
                'error': '知识库文档不存在'
            }, status=404)
    
    def _get_knowledge_list(self, request):
        """获取知识库文档列表"""
        # 获取查询参数
        doc_type = request.query_params.get('doc_type', None)
        error_type = request.query_params.get('error_type', None)
        is_active = request.query_params.get('is_active', None)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # 构建查询
        queryset = KnowledgeBase.objects.all()
        
        if doc_type:
            queryset = queryset.filter(doc_type=doc_type)
        if error_type:
            queryset = queryset.filter(error_type=error_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        docs = queryset[start:end]
        
        serializer = KnowledgeBaseSerializer(docs, many=True)
        
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })
    
    def post(self, request):
        """创建知识库文档（仅教练或管理员）"""
        user = request.user
        if not (user.is_coach() or user.is_admin_user()):
            return Response({
                'error': '只有教练或管理员可以添加知识库文档'
            }, status=403)
        
        # 幂等性检查：检查是否已存在相同标题+类型+错误类型的文档
        title = request.data.get('title')
        doc_type = request.data.get('doc_type')
        error_type = request.data.get('error_type', '')
        
        if title and doc_type:
            existing_doc = KnowledgeBase.objects.filter(
                title=title,
                doc_type=doc_type,
                error_type=error_type
            ).first()
            
            if existing_doc:
                return Response({
                    'message': '该知识库文档已存在',
                    'data': KnowledgeBaseSerializer(existing_doc).data,
                    'is_duplicate': True
                }, status=200)
        
        serializer = KnowledgeBaseSerializer(data=request.data)
        if serializer.is_valid():
            doc = serializer.save()
            
            # 异步同步到向量数据库
            try:
                import threading
                def sync_to_vector():
                    try:
                        from .rag_engine import RAGEngine
                        engine = RAGEngine()
                        engine.vector_store.add_document(
                            doc_id=doc.vector_id,
                            text=doc.content,
                            metadata={
                                'title': doc.title,
                                'type': doc.doc_type,
                                'doc_id': doc.id,
                                'error_type': doc.error_type or '',
                                'source': doc.source or '',
                            }
                        )
                    except Exception as e:
                        print(f"⚠️ 向量数据库同步失败: {e}")
                
                thread = threading.Thread(target=sync_to_vector)
                thread.daemon = True
                thread.start()
            except Exception as e:
                print(f"⚠️ 启动向量同步线程失败: {e}")
            
            return Response({
                'message': '知识库文档创建成功',
                'data': KnowledgeBaseSerializer(doc).data
            }, status=201)
        
        return Response(serializer.errors, status=400)
    
    def put(self, request, kb_id):
        """更新知识库文档（仅教练或管理员）"""
        user = request.user
        if not (user.is_coach() or user.is_admin_user()):
            return Response({
                'error': '只有教练或管理员可以更新知识库文档'
            }, status=403)
        
        try:
            doc = KnowledgeBase.objects.get(id=kb_id)
        except KnowledgeBase.DoesNotExist:
            return Response({
                'error': '知识库文档不存在'
            }, status=404)
        
        serializer = KnowledgeBaseSerializer(doc, data=request.data, partial=True)
        if serializer.is_valid():
            doc = serializer.save()
            
            # 异步更新向量数据库
            try:
                import threading
                def update_vector():
                    try:
                        from .rag_engine import RAGEngine
                        engine = RAGEngine()
                        engine.vector_store.update_document(
                            doc_id=doc.vector_id,
                            text=doc.content,
                            metadata={
                                'title': doc.title,
                                'type': doc.doc_type,
                                'doc_id': doc.id,
                                'error_type': doc.error_type or '',
                                'source': doc.source or '',
                            }
                        )
                    except Exception as e:
                        print(f"⚠️ 向量数据库更新失败: {e}")
                
                thread = threading.Thread(target=update_vector)
                thread.daemon = True
                thread.start()
            except Exception as e:
                print(f"⚠️ 启动向量更新线程失败: {e}")
            
            return Response({
                'message': '知识库文档更新成功',
                'data': KnowledgeBaseSerializer(doc).data
            })
        
        return Response(serializer.errors, status=400)
    
    def delete(self, request, kb_id):
        """删除知识库文档（仅教练或管理员）"""
        user = request.user
        if not (user.is_coach() or user.is_admin_user()):
            return Response({
                'error': '只有教练或管理员可以删除知识库文档'
            }, status=403)
        
        try:
            doc = KnowledgeBase.objects.get(id=kb_id)
            vector_id = doc.vector_id
            doc.delete()
            
            # 异步从向量数据库删除
            try:
                import threading
                def delete_from_vector():
                    try:
                        from .rag_engine import RAGEngine
                        engine = RAGEngine()
                        engine.vector_store.delete_document(doc_id=vector_id)
                    except Exception as e:
                        print(f"⚠️ 向量数据库删除失败: {e}")
                
                thread = threading.Thread(target=delete_from_vector)
                thread.daemon = True
                thread.start()
            except Exception as e:
                print(f"⚠️ 启动向量删除线程失败: {e}")
            
            return Response({
                'message': '知识库文档删除成功'
            })
        except KnowledgeBase.DoesNotExist:
            return Response({
                'error': '知识库文档不存在'
            }, status=404)
