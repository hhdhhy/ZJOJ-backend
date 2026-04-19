from django.db import models

# Create your models here.

from apps.ojauth.models import OJUser


class Tag(models.Model):
    name = models.CharField(max_length=50,unique=True, verbose_name='标签名')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name


class Problem(models.Model):

    problem_id = models.CharField(primary_key=True,max_length=20, unique=True, verbose_name='题目编号')
    title = models.CharField(max_length=100)
    description = models.TextField()
    time_limit = models.PositiveIntegerField()
    memory_limit = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True, related_name='problems')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    creator = models.ForeignKey(OJUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_problems', verbose_name='创建者')


class Submission(models.Model):
    """
    代码提交模型
    存储用户提交的代码及评测结果
    """
    
    STATUS_CHOICES = [
        (0, '等待评测'),
        (1, '评测中'),
        (2, '已完成'),
        (3, '编译错误'),
        (4, '系统错误'),
    ]
    
    RESULT_CHOICES = [
        ('AC', 'Accepted'),
        ('WA', 'Wrong Answer'),
        ('TLE', 'Time Limit Exceeded'),
        ('MLE', 'Memory Limit Exceeded'),
        ('RE', 'Runtime Error'),
        ('CE', 'Compilation Error'),
        ('SE', 'System Error'),
    ]
    
    LANGUAGE_CHOICES = [
        ('cpp', 'C++'),
        ('c', 'C'),
        ('java', 'Java'),
        ('python3', 'Python 3'),
        ('python2', 'Python 2'),
    ]
    
    # 基本信息
    id = models.AutoField(primary_key=True, verbose_name='提交ID')
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='所属题目'
    )
    user = models.ForeignKey(
        OJUser,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='提交用户'
    )
    
    # 代码信息
    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        verbose_name='编程语言'
    )
    code = models.TextField(verbose_name='源代码')
    code_length = models.PositiveIntegerField(default=0, verbose_name='代码长度')
    
    # 评测状态
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=0,
        verbose_name='评测状态'
    )
    result = models.CharField(
        max_length=10,
        choices=RESULT_CHOICES,
        blank=True,
        null=True,
        verbose_name='评测结果'
    )
    
    # 评测结果
    score = models.PositiveIntegerField(default=0, verbose_name='得分')
    execution_time = models.PositiveIntegerField(default=0, verbose_name='运行时间(ms)')
    memory_usage = models.PositiveIntegerField(default=0, verbose_name='内存使用(KB)')
    
    # 时间戳
    submit_time = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    judge_time = models.DateTimeField(blank=True, null=True, verbose_name='评测时间')
    
    class Meta:
        db_table = 'submission'
        ordering = ['-submit_time']
        indexes = [
            models.Index(fields=['-submit_time']),
            models.Index(fields=['user', '-submit_time']),
            models.Index(fields=['problem', '-submit_time']),
        ]
        verbose_name = '提交记录'
        verbose_name_plural = '提交记录'
    
    def __str__(self):
        return f'Submission #{self.id} by {self.user.username}'
    
    def save(self, *args, **kwargs):
        # 自动计算代码长度
        if self.code:
            self.code_length = len(self.code.encode('utf-8'))
        super().save(*args, **kwargs)


class TestCaseResult(models.Model):
    """
    测试点结果模型
    存储每个测试点的详细评测结果
    """
    
    STATUS_CHOICES = [
        ('AC', 'Accepted'),
        ('WA', 'Wrong Answer'),
        ('TLE', 'Time Limit Exceeded'),
        ('MLE', 'Memory Limit Exceeded'),
        ('RE', 'Runtime Error'),
    ]
    
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='test_case_results',
        verbose_name='所属提交'
    )
    test_case_id = models.PositiveIntegerField(verbose_name='测试点ID')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name='测试点状态'
    )
    execution_time = models.PositiveIntegerField(default=0, verbose_name='运行时间(ms)')
    memory_usage = models.PositiveIntegerField(default=0, verbose_name='内存使用(KB)')
    score = models.PositiveIntegerField(default=0, verbose_name='该测试点得分')
    message = models.TextField(blank=True, default='', verbose_name='详细信息')
    
    class Meta:
        db_table = 'test_case_result'
        ordering = ['test_case_id']
        unique_together = ['submission', 'test_case_id']
        verbose_name = '测试点结果'
        verbose_name_plural = '测试点结果'
    
    def __str__(self):
        return f'Test Case {self.test_case_id}: {self.status}'
