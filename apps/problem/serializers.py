from rest_framework import serializers
from apps.problem.models import Problem, Tag, Submission, TestCaseResult


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
            'creator_name'
        ]
        read_only_fields = ['upload_time', 'update_time', 'creator_name']
    
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
        
        # 获取创建者
        creator = None
        if request and hasattr(request, 'user'):
            creator = request.user
        
        # 创建题目（直接传入creator）
        problem = Problem.objects.create(creator=creator, **validated_data)
        
        # 关联标签
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            problem.tags.set(tags)
        
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
            instance.tags.set(tags)
        
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
        
        # 获取创建者
        creator = None
        if request and hasattr(request, 'user'):
            creator = request.user
        
        # 创建题目（直接传入creator）
        problem = Problem.objects.create(creator=creator, **validated_data)
        
        # 关联标签
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            problem.tags.set(tags)
        
        return problem
  


# ==================== 提交相关序列化器 ====================

class SubmitCodeSerializer(serializers.ModelSerializer):
    """提交代码序列化器"""
    class Meta:
        model = Submission
        fields = ['problem', 'language', 'code']
    
    def validate_problem(self, value):
        if not Problem.objects.filter(problem_id=value.problem_id).exists():
            raise serializers.ValidationError('题目不存在')
        return value
    
    def validate_language(self, value):
        valid_languages = ['cpp', 'c', 'java', 'python3', 'python2']
        if value not in valid_languages:
            raise serializers.ValidationError(f'不支持的编程语言: {value}')
        return value
    
    def validate_code(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError('代码不能为空')
        if len(value) > 65536:
            raise serializers.ValidationError('代码长度不能超过64KB')
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        else:
            raise serializers.ValidationError('用户未登录')
        return Submission.objects.create(**validated_data)


class TestCaseResultSerializer(serializers.ModelSerializer):
    """测试点结果序列化器"""
    class Meta:
        model = TestCaseResult
        fields = ['test_case_id', 'status', 'execution_time', 'memory_usage', 'score', 'message']


class SubmissionListSerializer(serializers.ModelSerializer):
    """提交列表序列化器"""
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    problem_id = serializers.CharField(source='problem.problem_id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'problem_id', 'problem_title', 'username',
            'language', 'language_display', 'status', 'status_display',
            'result', 'result_display', 'score', 'execution_time',
            'memory_usage', 'submit_time'
        ]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    """提交详情序列化器"""
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    problem_id = serializers.CharField(source='problem.problem_id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    test_case_results = TestCaseResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'problem_id', 'problem_title', 'username',
            'language', 'language_display', 'code', 'code_length',
            'status', 'status_display', 'result', 'result_display',
            'score', 'execution_time', 'memory_usage',
            'submit_time', 'judge_time', 'test_case_results'
        ]
