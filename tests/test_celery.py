"""
Celery 和提交功能测试脚本
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
django.setup()

from apps.problem.models import Problem, Submission
from apps.ojauth.models import OJUser
from apps.judge.tasks import judge_submission_task


def test_celery_import():
    """测试 Celery 导入"""
    print("="*60)
    print("测试1: Celery 导入")
    print("="*60)
    
    try:
        from ZJOJ.celery import app
        print(f"✅ Celery 应用导入成功")
        print(f"   应用名称: {app.main}")
        print(f"   Broker URL: {app.conf.broker_url}")
        return True
    except Exception as e:
        print(f"❌ Celery 导入失败: {e}")
        return False


def test_task_import():
    """测试任务导入"""
    print("\n" + "="*60)
    print("测试2: 评测任务导入")
    print("="*60)
    
    try:
        from apps.judge.tasks import judge_submission_task
        print(f"✅ 评测任务导入成功")
        print(f"   任务名称: {judge_submission_task.name}")
        return True
    except Exception as e:
        print(f"❌ 任务导入失败: {e}")
        return False


def test_database_models():
    """测试数据库模型"""
    print("\n" + "="*60)
    print("测试3: 数据库模型")
    print("="*60)
    
    try:
        # 检查 Submission 模型
        submission_count = Submission.objects.count()
        print(f"✅ Submission 模型正常")
        print(f"   当前提交数: {submission_count}")
        
        # 检查 TestCaseResult 模型
        from apps.problem.models import TestCaseResult
        testcase_count = TestCaseResult.objects.count()
        print(f"✅ TestCaseResult 模型正常")
        print(f"   当前测试点结果数: {testcase_count}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_submission():
    """测试创建提交记录"""
    print("\n" + "="*60)
    print("测试4: 创建提交记录")
    print("="*60)
    
    try:
        # 获取一个用户
        user = OJUser.objects.first()
        if not user:
            print("⚠️  没有找到用户，请先创建用户")
            return False
        
        # 获取一个题目
        problem = Problem.objects.first()
        if not problem:
            print("⚠️  没有找到题目，请先创建题目")
            return False
        
        print(f"   用户: {user.username}")
        print(f"   题目: {problem.problem_id} - {problem.title}")
        
        # 创建提交记录
        submission = Submission.objects.create(
            problem=problem,
            user=user,
            language='cpp',
            code='#include <iostream>\nusing namespace std;\nint main() {\n    cout << "Hello World" << endl;\n    return 0;\n}',
            status=0  # 等待评测
        )
        
        print(f"✅ 提交记录创建成功")
        print(f"   提交ID: {submission.id}")
        print(f"   状态: {submission.get_status_display()}")
        print(f"   代码长度: {submission.code_length} bytes")
        
        # 清理测试数据
        submission.delete()
        print(f"   测试数据已清理")
        
        return True
    except Exception as e:
        print(f"❌ 创建提交记录失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_serializer():
    """测试序列化器"""
    print("\n" + "="*60)
    print("测试5: 序列化器")
    print("="*60)
    
    try:
        from apps.problem.serializers import (
            SubmitCodeSerializer,
            SubmissionListSerializer,
            SubmissionDetailSerializer
        )
        
        print(f"✅ SubmitCodeSerializer 导入成功")
        print(f"✅ SubmissionListSerializer 导入成功")
        print(f"✅ SubmissionDetailSerializer 导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 序列化器导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_views():
    """测试视图"""
    print("\n" + "="*60)
    print("测试6: API 视图")
    print("="*60)
    
    try:
        from apps.problem.submission_views import (
            SubmitCodeView,
            SubmissionListView,
            SubmissionDetailView
        )
        
        print(f"✅ SubmitCodeView 导入成功")
        print(f"✅ SubmissionListView 导入成功")
        print(f"✅ SubmissionDetailView 导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 视图导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n🚀 开始测试 Celery 和提交功能\n")
    
    results = []
    
    # 运行所有测试
    results.append(("Celery 导入", test_celery_import()))
    results.append(("任务导入", test_task_import()))
    results.append(("数据库模型", test_database_models()))
    results.append(("创建提交", test_create_submission()))
    results.append(("序列化器", test_serializer()))
    results.append(("API 视图", test_views()))
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s} {status}")
    
    print("-"*60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
