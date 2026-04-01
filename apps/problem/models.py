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
    tag=models.ManyToManyField(Tag,verbose_name='标签',blank=True,related_name='problems')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    creator = models.ForeignKey(OJUser, on_delete=models.SET_NULL, null=True, related_name='created_problems', verbose_name='创建者')
