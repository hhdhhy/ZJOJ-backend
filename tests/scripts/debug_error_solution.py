import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings_production')

import django
django.setup()

from apps.problem.models import Submission
from apps.ai_assistant.error_pusher import ErrorSolutionPusher

# 获取提交记录
try:
    sub = Submission.objects.get(id=40)
    print(f'提交ID: {sub.id}')
    print(f'用户: {sub.user.username}')
    print(f'题目ID: {sub.problem.problem_id if sub.problem else "N/A"}')
    print(f'题目名称: {sub.problem.title if sub.problem else "N/A"}')
    print(f'结果: {sub.result}')
    print(f'错误信息: {sub.error_message[:50] if sub.error_message else "None"}')
    print()
    
    # 调用错误解决方案推送器
    print('调用 ErrorSolutionPusher...')
    solutions = ErrorSolutionPusher.push_on_judge_failure(40)
    
    print(f'找到 {len(solutions)} 个解决方案:')
    for sol in solutions:
        print(f'  - {sol["title"]}')
        print(f'    类型: {sol["doc_type"]}')
        print(f'    相关性: {sol["relevance_score"]}')
        print()
        
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
