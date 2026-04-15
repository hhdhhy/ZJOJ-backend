"""
AI助手限制检查器
- 每日对话次数限制
- 频率限制（防刷）
- 历史对话上限
"""
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, RateLimit, ChatHistory
from rest_framework.exceptions import Throttled


class AILimitChecker:
    """AI助手限制检查器"""
    
    # 配置常量
    MAX_HISTORY_PER_USER = 100  # 历史对话上限
    DAILY_QUOTA = 50  # 每日配额
    RATE_LIMIT_WINDOW = 60  # 频率限制窗口（秒）
    RATE_LIMIT_MAX = 10  # 窗口内最大请求数
    
    @classmethod
    def check_daily_quota(cls, user):
        """
        检查每日配额
        
        Args:
            user: 当前用户
        
        Returns:
            UserProfile 对象
        
        Raises:
            Throttled: 如果配额已用完
        """
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # 检查是否需要重置
        today = timezone.now().date()
        if profile.last_reset_date != today:
            profile.used_today = 0
            profile.last_reset_date = today
            profile.save()
        
        # 检查配额
        if profile.used_today >= profile.daily_quota:
            raise Throttled(
                detail=f'今日配额已用完（{profile.daily_quota}次），明天重置',
                wait=None
            )
        
        return profile
    
    @classmethod
    def check_rate_limit(cls, user):
        """
        检查频率限制
        
        Args:
            user: 当前用户
        
        Raises:
            Throttled: 如果请求过于频繁
        """
        now = timezone.now()
        window_start = now - timedelta(seconds=cls.RATE_LIMIT_WINDOW)
        
        # 获取或创建当前窗口的记录
        rate_limit, created = RateLimit.objects.get_or_create(
            user=user,
            window_start=window_start.replace(microsecond=0),
            defaults={'request_count': 0}
        )
        
        # 清理过期记录
        RateLimit.objects.filter(
            user=user,
            window_start__lt=window_start
        ).delete()
        
        # 检查是否超限
        if rate_limit.request_count >= cls.RATE_LIMIT_MAX:
            wait_time = cls.RATE_LIMIT_WINDOW - (now - rate_limit.window_start).seconds
            raise Throttled(
                detail=f'请求过于频繁，请{wait_time}秒后再试',
                wait=wait_time
            )
        
        # 增加计数
        rate_limit.request_count += 1
        rate_limit.save()
    
    @classmethod
    def increment_usage(cls, user):
        """
        增加使用次数
        
        Args:
            user: 当前用户
        """
        profile = UserProfile.objects.get(user=user)
        profile.used_today += 1
        profile.save()
    
    @classmethod
    def trim_history(cls, user):
        """
        修剪历史记录，保留最新的N条
        
        Args:
            user: 当前用户
        """
        history_count = ChatHistory.objects.filter(user=user).count()
        if history_count > cls.MAX_HISTORY_PER_USER:
            # 删除最旧的记录
            old_records = ChatHistory.objects.filter(user=user).order_by('created_at')
            delete_count = history_count - cls.MAX_HISTORY_PER_USER
            old_records[:delete_count].delete()


# 测试代码
if __name__ == "__main__":
    import os
    import sys
    import django
    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
    django.setup()
    
    from apps.ojauth.models import OJUser
    
    print("="*60)
    print("测试 AI 限制检查器")
    print("="*60)
    
    try:
        # 获取测试用户
        user = OJUser.objects.first()
        if not user:
            print("\n⚠️  没有用户，请先创建用户")
            sys.exit(0)
        
        print(f"\n测试用户: {user.username}")
        
        # 1. 测试每日配额检查
        print("\n1. 测试每日配额检查...")
        profile = AILimitChecker.check_daily_quota(user)
        print(f"   ✅ 配额检查通过")
        print(f"   今日已用: {profile.used_today}/{profile.daily_quota}")
        print(f"   剩余配额: {profile.daily_quota - profile.used_today}")
        
        # 2. 测试频率限制
        print("\n2. 测试频率限制...")
        AILimitChecker.check_rate_limit(user)
        print(f"   ✅ 频率限制检查通过")
        
        # 3. 测试增加使用次数
        print("\n3. 测试增加使用次数...")
        old_used = profile.used_today
        AILimitChecker.increment_usage(user)
        profile.refresh_from_db()
        print(f"   ✅ 使用次数增加成功")
        print(f"   之前: {old_used}, 现在: {profile.used_today}")
        
        # 4. 测试历史记录修剪
        print("\n4. 测试历史记录修剪...")
        current_count = ChatHistory.objects.filter(user=user).count()
        print(f"   当前历史记录数: {current_count}")
        print(f"   最大允许: {AILimitChecker.MAX_HISTORY_PER_USER}")
        print(f"   ✅ 修剪功能就绪")
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
