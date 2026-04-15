"""
AI助手序列化器
"""
from rest_framework import serializers
from .models import ChatHistory


class ChatRequestSerializer(serializers.Serializer):
    """聊天请求序列化器"""
    question = serializers.CharField(
        max_length=2000,
        required=True,
        help_text='用户问题'
    )
    top_k = serializers.IntegerField(
        default=5,
        min_value=1,
        max_value=10,
        help_text='检索文档数量'
    )
    use_rag = serializers.BooleanField(
        default=True,
        help_text='是否使用RAG检索增强'
    )


class SourceSerializer(serializers.Serializer):
    """引用来源序列化器"""
    id = serializers.CharField()
    title = serializers.CharField()
    type = serializers.CharField()
    similarity = serializers.FloatField()


class ChatResponseSerializer(serializers.Serializer):
    """聊天响应序列化器"""
    answer = serializers.CharField()
    sources = SourceSerializer(many=True, required=False)
    tokens_used = serializers.IntegerField()
    remaining_quota = serializers.IntegerField(required=False)
    chat_id = serializers.IntegerField(required=False)


class ChatHistorySerializer(serializers.ModelSerializer):
    """对话历史序列化器"""
    class Meta:
        model = ChatHistory
        fields = ['id', 'question', 'answer', 'sources', 'created_at', 'tokens_used']
        read_only_fields = fields


class UsageStatsSerializer(serializers.Serializer):
    """使用情况统计序列化器"""
    daily_quota = serializers.IntegerField()
    used_today = serializers.IntegerField()
    remaining = serializers.IntegerField()
    max_history = serializers.IntegerField()
    history_count = serializers.IntegerField()
    reset_time = serializers.CharField()
