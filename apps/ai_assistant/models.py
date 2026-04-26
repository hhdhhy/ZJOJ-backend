"""
AI助手数据模型
"""
from django.db import models
from apps.ojauth.models import OJUser


class KnowledgeBase(models.Model):
    """知识库文档"""
    DOC_TYPE_CHOICES = [
        ('algorithm', '算法讲解'),
        ('solution', '题解'),
        ('template', '代码模板'),
        ('concept', '概念说明'),
        ('error_solution', '错误解决方案'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, verbose_name='类型')
    tags = models.ManyToManyField('problem.Tag', blank=True, verbose_name='标签')
    problem = models.ForeignKey(
        'problem.Problem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_docs',
        verbose_name='关联题目'
    )
    error_type = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='错误类型（WA/TLE/MLE/RE/CE）'
    )
    source = models.CharField(max_length=500, blank=True, verbose_name='来源')
    vector_id = models.CharField(max_length=100, unique=True, verbose_name='向量ID')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '知识库文档'
        verbose_name_plural = '知识库文档'
        ordering = ['-created_at']
        # 添加唯一性约束：同一标题+类型+错误类型的文档只能有一个
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'doc_type', 'error_type'],
                name='unique_knowledge_doc'
            )
        ]
    
    def __str__(self):
        return self.title


class UserProfile(models.Model):
    """用户AI助手配置"""
    user = models.OneToOneField(OJUser, on_delete=models.CASCADE, related_name='ai_profile')
    daily_quota = models.IntegerField(default=50, verbose_name='每日配额')
    used_today = models.IntegerField(default=0, verbose_name='今日已用')
    last_reset_date = models.DateField(auto_now_add=True, verbose_name='上次重置日期')
    max_history = models.IntegerField(default=100, verbose_name='最大历史记录数')
    
    class Meta:
        verbose_name = '用户AI配置'
        verbose_name_plural = '用户AI配置'
    
    def __str__(self):
        return f'{self.user.username}的AI配置'


class ChatHistory(models.Model):
    """对话历史"""
    user = models.ForeignKey(OJUser, on_delete=models.CASCADE, related_name='chat_histories', verbose_name='用户')
    question = models.TextField(verbose_name='问题')
    answer = models.TextField(verbose_name='答案')
    sources = models.JSONField(default=list, verbose_name='引用来源')
    model_used = models.CharField(max_length=50, default='glm-4', verbose_name='使用的模型')
    tokens_used = models.IntegerField(default=0, verbose_name='消耗Token数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '对话历史'
        verbose_name_plural = '对话历史'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.question[:50]}'


class RateLimit(models.Model):
    """频率限制记录"""
    user = models.ForeignKey(OJUser, on_delete=models.CASCADE, related_name='rate_limits')
    window_start = models.DateTimeField(verbose_name='时间窗口开始')
    request_count = models.IntegerField(default=0, verbose_name='请求次数')
    
    class Meta:
        unique_together = ['user', 'window_start']
        verbose_name = '频率限制'
        verbose_name_plural = '频率限制'
    
    def __str__(self):
        return f'{self.user.username} - {self.window_start}'


class APICache(models.Model):
    """API调用缓存"""
    cache_key = models.CharField(max_length=200, unique=True, verbose_name='缓存键')
    response_data = models.JSONField(verbose_name='响应数据')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = 'API缓存'
        verbose_name_plural = 'API缓存'
        indexes = [
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return self.cache_key
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at


class LearningReport(models.Model):
    """学情报告"""
    REPORT_TYPE_CHOICES = [
        ('student', '学生个性报告'),
        ('class', '班级共性报告'),
    ]
    
    user = models.ForeignKey(
        OJUser,
        on_delete=models.CASCADE,
        related_name='learning_reports',
        verbose_name='用户'
    )
    class_obj = models.ForeignKey(
        'ojauth.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='learning_reports',
        verbose_name='班级（仅班级报告）'
    )
    report_type = models.CharField(
        max_length=10,
        choices=REPORT_TYPE_CHOICES,
        verbose_name='报告类型'
    )
    period_start = models.DateField(verbose_name='统计开始日期')
    period_end = models.DateField(verbose_name='统计结束日期')
    summary = models.TextField(verbose_name='总结内容')
    statistics = models.JSONField(default=dict, verbose_name='统计数据')
    recommendations = models.JSONField(default=list, verbose_name='建议列表')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')
    
    class Meta:
        verbose_name = '学情报告'
        verbose_name_plural = '学情报告'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['user', '-generated_at']),
            models.Index(fields=['class_obj', '-generated_at']),
        ]
    
    def __str__(self):
        return f'{self.get_report_type_display()} - {self.user.username}'
