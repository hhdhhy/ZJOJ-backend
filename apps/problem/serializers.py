from rest_framework import serializers
from apps.problem.models import Problem, Tag


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ProblemListSerializer(serializers.ModelSerializer):
    """题目列表序列化器（简化版）"""
    tags = TagSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    
    class Meta:
        model = Problem
        fields = [
            'problem_id', 
            'title', 
            'time_limit', 
            'memory_limit',
            'tags',
            'upload_time',
            'update_time',
            'creator_name'
        ]


class ProblemDetailSerializer(serializers.ModelSerializer):
    """题目详情序列化器"""
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='标签ID列表'
    )
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    
    class Meta:
        model = Problem
        fields = [
            'problem_id',
            'title',
            'description',
            'time_limit',
            'memory_limit',
            'tags',
            'tag_ids',
            'upload_time',
            'update_time',
            'creator',
            'creator_name'
        ]
        read_only_fields = ['upload_time', 'update_time', 'creator', 'creator_name']
    
    def validate_problem_id(self, value):
        """验证题目编号唯一性"""
        if Problem.objects.filter(problem_id=value).exists():
            raise serializers.ValidationError('该题目编号已存在')
        return value
    
    def validate_tag_ids(self, value):
        """验证标签ID是否存在"""
        if value:
            existing_tags = Tag.objects.filter(id__in=value)
            if len(existing_tags) != len(value):
                raise serializers.ValidationError('部分标签不存在')
        return value
    
    def validate_time_limit(self, value):
        """验证时间限制"""
        if value <= 0:
            raise serializers.ValidationError('时间限制必须大于0')
        return value
    
    def validate_memory_limit(self, value):
        """验证内存限制"""
        if value <= 0:
            raise serializers.ValidationError('内存限制必须大于0')
        return value
    
    def create(self, validated_data):
        """创建题目并关联标签"""
        tag_ids = validated_data.pop('tag_ids', [])
        request = self.context.get('request')
        
        # 设置创建者
        if request and hasattr(request, 'user'):
            validated_data['creator'] = request.user
        
        problem = Problem.objects.create(**validated_data)
        
        # 关联标签
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            problem.tag.set(tags)
        
        return problem
    
    def update(self, instance, validated_data):
        """更新题目及标签"""
        tag_ids = validated_data.pop('tag_ids', None)
        
        # 更新题目基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新标签关联
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            instance.tag.set(tags)
        
        return instance


class CreateProblemSerializer(serializers.ModelSerializer):
    """创建题目专用序列化器"""
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='标签ID列表'
    )
    
    class Meta:
        model = Problem
        fields = [
            'problem_id',
            'title',
            'description',
            'time_limit',
            'memory_limit',
            'tag_ids'
        ]
    
    def validate_problem_id(self, value):
        """验证题目编号唯一性"""
        if Problem.objects.filter(problem_id=value).exists():
            raise serializers.ValidationError('该题目编号已存在')
        return value
    
    def validate_tag_ids(self, value):
        """验证标签ID是否存在"""
        if value:
            existing_tags = Tag.objects.filter(id__in=value)
            if len(existing_tags) != len(value):
                raise serializers.ValidationError(f'部分标签不存在，提供的ID: {value}')
        return value
    
    def validate_time_limit(self, value):
        """验证时间限制"""
        if value <= 0:
            raise serializers.ValidationError('时间限制必须大于0')
        return value
    
    def validate_memory_limit(self, value):
        """验证内存限制"""
        if value <= 0:
            raise serializers.ValidationError('内存限制必须大于0')
        return value
    
    def create(self, validated_data):
        """创建题目并关联标签"""
        tag_ids = validated_data.pop('tag_ids', [])
        request = self.context.get('request')
        
        # 设置创建者
        if request and hasattr(request, 'user'):
            validated_data['creator'] = request.user
        
        problem = Problem.objects.create(**validated_data)
        
        # 关联标签
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            problem.tag.set(tags)
        
        return problem
