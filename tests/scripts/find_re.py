from apps.problem.models import Submission

# 查找所有 RE 状态的提交
re_subs = Submission.objects.filter(result='RE')[:5]
print(f'找到 {re_subs.count()} 个 RE 提交')
for sub in re_subs:
    print(f'ID: {sub.id}, Status: {sub.get_status_display()}, Error: {sub.error_message[:50] if sub.error_message else "None"}')
