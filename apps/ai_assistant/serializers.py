"""
AI助手序列化器
"""
from rest_framework import serializers
from .models import ChatHistory, KnowledgeBase


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


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    """知识库文档序列化器"""
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text='标签名称列表'
    )
    
    class Meta:
        model = KnowledgeBase
        fields = [
            'id', 'title', 'content', 'doc_type', 'tags', 'tag_names',
            'problem', 'error_type', 'source', 'vector_id', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'vector_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """创建知识库文档"""
        tag_names = validated_data.pop('tag_names', [])
        
        # 生成 vector_id（简单使用时间戳）
        import time
        validated_data['vector_id'] = f'kb_{int(time.time() * 1000)}'
        
        # 创建知识库文档
        knowledge_doc = KnowledgeBase.objects.create(**validated_data)
        
        # 设置标签
        if tag_names:
            from apps.problem.models import Tag
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                knowledge_doc.tags.add(tag)
        
        return knowledge_doc
    
    def update(self, instance, validated_data):
        """更新知识库文档"""
        tag_names = validated_data.pop('tag_names', None)
        
        # 更新字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新标签
        if tag_names is not None:
            from apps.problem.models import Tag
            instance.tags.clear()
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        
        return instance
