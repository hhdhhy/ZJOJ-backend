"""
学情分析服务
- 班级共性问题总结（教练）
- 学生个性化学情报告（学生）
"""
from django.utils import timezone
from datetime import timedelta, date
from apps.problem.models import Submission
from apps.ai_assistant.llm_client import LLMClient
from apps.ai_assistant.models import LearningReport
from apps.ai_assistant.api_optimizer import APICallOptimizer
from apps.ai_assistant.prompts import REPORT_SYSTEM_PROMPT


class LearningAnalyticsService:
    """学情分析服务"""
    
    @staticmethod
    def generate_student_report(user, days=7):
        """
        生成学生个性化学情报告
        :param user: 学生用户
        :param days: 统计天数
        :return: 学情报告对象
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 获取提交记录
        submissions = Submission.objects.filter(
            user=user,
            submit_time__date__gte=start_date,
            submit_time__date__lte=end_date
        )
        
        if not submissions.exists():
            return None
        
        # 统计数据
        total_submissions = submissions.count()
        ac_count = submissions.filter(result='AC').count()
        wa_count = submissions.filter(result='WA').count()
        tle_count = submissions.filter(result='TLE').count()
        mle_count = submissions.filter(result='MLE').count()
        re_count = submissions.filter(result='RE').count()
        ce_count = submissions.filter(result='CE').count()
        
        ac_rate = (ac_count / total_submissions * 100) if total_submissions > 0 else 0
        
        # 按题目统计
        problem_stats = {}
        for sub in submissions:
            pid = sub.problem_id
            if pid not in problem_stats:
                problem_stats[pid] = {
                    'total': 0,
                    'ac': False,
                    'best_result': sub.result,
                    'attempts': []
                }
            problem_stats[pid]['total'] += 1
            problem_stats[pid]['attempts'].append(sub.result)
            if sub.result == 'AC':
                problem_stats[pid]['ac'] = True
            elif problem_stats[pid]['best_result'] != 'AC':
                problem_stats[pid]['best_result'] = sub.result
        
        # 未AC的题目
        unsolved_problems = [
            pid for pid, stats in problem_stats.items()
            if not stats['ac']
        ]
        
        # 常见错误类型
        error_types = {
            'WA': wa_count,
            'TLE': tle_count,
            'MLE': mle_count,
            'RE': re_count,
            'CE': ce_count,
        }
        common_errors = sorted(
            [(k, v) for k, v in error_types.items() if v > 0],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        statistics = {
            'total_submissions': total_submissions,
            'ac_count': ac_count,
            'ac_rate': round(ac_rate, 2),
            'unsolved_count': len(unsolved_problems),
            'common_errors': dict(common_errors),
            'problem_stats': problem_stats,
        }
        
        # 生成AI总结
        error_detail = '；'.join([
            f"{err}: {cnt}次（占比{cnt/total_submissions*100:.1f}%）"
            for err, cnt in common_errors
        ]) if common_errors else '无错误记录'

        # 构造已解决/未解决题目信息
        solved_count = sum(1 for pid, stats in problem_stats.items() if stats['ac'])
        attempted_pids = sorted(problem_stats.keys())
        unsolved_detail = '、'.join(unsolved_problems) if unsolved_problems else '无'

        summary_prompt = f"""
## 学生编程练习数据（近{days}天）

### 整体统计
- 总提交次数：{total_submissions}
- 通过次数：{ac_count}
- 通过率：{ac_rate}%
- 尝试题目数：{len(attempted_pids)} 道（{attempted_pids}）
- 已解决：{solved_count} 道
- 未解决：{len(unsolved_problems)} 道（{unsolved_detail}）

### 错误分布
{error_detail}

### 各题表现
"""
        for pid, stats in problem_stats.items():
            status = '已通过' if stats['ac'] else '未通过'
            attempts_str = ' → '.join(stats['attempts'])
            summary_prompt += f"- {pid}：提交{stats['total']}次，{status}（{attempts_str}）\n"

        summary_prompt += f"""
请基于以上数据生成一份学情分析报告。要求：
1. 先肯定学生的积极表现（如提交频率、尝试难度、坚持程度等）
2. 诊断学习中的系统性问题（透过错误类型看本质，如「WA高发→逻辑严密性不足」）
3. 针对每种高频错误类型给出1条具体的改进建议
4. 如果尝试了多道题但均未通过，建议降低难度梯度
5. 如果同一道题反复提交但未通过，建议暂停并重新理解题意
"""

        try:
            llm = LLMClient()
            messages = [
                {'role': 'system', 'content': REPORT_SYSTEM_PROMPT},
                {'role': 'user', 'content': summary_prompt}
            ]
            result = llm.chat(messages, temperature=0.7)
            summary = result['answer']
        except Exception as e:
            summary = f"学生在过去{days}天内提交了{total_submissions}次代码，通过率为{ac_rate}%。"
        
        # 生成建议
        recommendations = []
        if ac_rate < 50:
            recommendations.append("建议先巩固基础算法，提高代码正确率")
        if wa_count > total_submissions * 0.3:
            recommendations.append("答案错误较多，注意边界条件和特殊情况处理")
        if tle_count > total_submissions * 0.2:
            recommendations.append("超时较多，优化算法复杂度，减少不必要的循环")
        if len(unsolved_problems) > 5:
            recommendations.append(f"有{len(unsolved_problems)}道题目未通过，建议逐个击破")
        
        # 保存报告
        report = LearningReport.objects.create(
            user=user,
            report_type='student',
            period_start=start_date,
            period_end=end_date,
            summary=summary,
            statistics=statistics,
            recommendations=recommendations,
        )
        
        return report
    
    @staticmethod
    def generate_class_report(class_obj, coach, days=7):
        """
        生成班级共性学情报告
        :param class_obj: 班级对象
        :param coach: 教练用户
        :param days: 统计天数
        :return: 学情报告对象
        """
        from apps.ojauth.models import ClassMember
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 获取班级所有学生
        members = ClassMember.objects.filter(class_obj=class_obj).select_related('user')
        student_ids = [m.user.uid for m in members]
        
        if not student_ids:
            return None
        
        # 获取班级所有提交
        submissions = Submission.objects.filter(
            user_id__in=student_ids,
            submit_time__date__gte=start_date,
            submit_time__date__lte=end_date
        )
        
        if not submissions.exists():
            return None
        
        # 整体统计
        total_submissions = submissions.count()
        ac_count = submissions.filter(result='AC').count()
        ac_rate = (ac_count / total_submissions * 100) if total_submissions > 0 else 0
        
        # 按学生统计
        student_performance = {}
        for member in members:
            user = member.user
            user_subs = submissions.filter(user=user)
            user_total = user_subs.count()
            user_ac = user_subs.filter(result='AC').count()
            user_ac_rate = (user_ac / user_total * 100) if user_total > 0 else 0
            
            student_performance[user.username] = {
                'realname': user.realname,
                'submissions': user_total,
                'ac_count': user_ac,
                'ac_rate': round(user_ac_rate, 2),
            }
        
        # 按题目统计（共性难题）
        problem_difficulty = {}
        for sub in submissions:
            pid = sub.problem_id
            if pid not in problem_difficulty:
                problem_difficulty[pid] = {'total': 0, 'ac': 0}
            problem_difficulty[pid]['total'] += 1
            if sub.result == 'AC':
                problem_difficulty[pid]['ac'] += 1
        
        # 计算每题通过率，找出难题
        hard_problems = []
        for pid, stats in problem_difficulty.items():
            if stats['total'] >= 3:  # 至少3人提交
                rate = stats['ac'] / stats['total'] * 100
                if rate < 50:  # 通过率低于50%
                    hard_problems.append({
                        'problem_id': pid,
                        'submissions': stats['total'],
                        'ac_rate': round(rate, 2),
                    })
        
        hard_problems.sort(key=lambda x: x['ac_rate'])
        
        # 常见错误分布
        error_distribution = {
            'WA': submissions.filter(result='WA').count(),
            'TLE': submissions.filter(result='TLE').count(),
            'MLE': submissions.filter(result='MLE').count(),
            'RE': submissions.filter(result='RE').count(),
            'CE': submissions.filter(result='CE').count(),
        }
        
        statistics = {
            'total_students': len(student_ids),
            'active_students': len([s for s in student_performance.values() if s['submissions'] > 0]),
            'total_submissions': total_submissions,
            'ac_rate': round(ac_rate, 2),
            'hard_problems': hard_problems[:10],  # 前10个难题
            'error_distribution': error_distribution,
            'student_performance': student_performance,
        }
        
        # 生成AI总结
        summary_prompt = f"""
请基于以下班级编程练习数据，生成一份班级学情分析报告。

## 数据概览
- 班级总人数：{len(student_ids)}，活跃：{statistics['active_students']}人（活跃率{statistics['active_students']/len(student_ids)*100:.1f}%）
- 总提交：{total_submissions}次，整体通过率：{ac_rate}%
- 共性难题（通过率<50%且≥3人提交）：{len(hard_problems)}道
- 错误分布：{', '.join([f'{k}:{v}次({v/total_submissions*100:.1f}%)' for k,v in sorted(error_distribution.items(),key=lambda x:x[1],reverse=True) if v>0])}

## 学生分层
"""
        for u, s in student_performance.items():
            if s['submissions'] > 0:
                summary_prompt += f"- {s.get('realname', u)}：提交{s['submissions']}次，通过率{s['ac_rate']}%\n"
        summary_prompt += """
## 共性难题详情
"""
        for p in hard_problems[:5]:
            summary_prompt += f"- {p['problem_id']}：{p['submissions']}次提交，通过率{p['ac_rate']}%\n"
        if not hard_problems:
            summary_prompt += "无\n"

        summary_prompt += """
## 分析要求
1. 评估班级整体学习阶段（入门/基础/进阶）
2. 诊断最突出的1-2个共性问题，分析其深层原因
3. 针对学生分层给出差异化教学策略
4. 对共性难题给出课堂教学形式建议（专题讲解/分组讨论/代码走读）
5. 给出可量化的改进目标（如\"未来2周内WA占比降至30%以下\"）
6. 指出班级中需要个别辅导的学生及其问题
"""
        
        try:
            llm = LLMClient()
            messages = [
                {'role': 'system', 'content': REPORT_SYSTEM_PROMPT},
                {'role': 'user', 'content': summary_prompt}
            ]
            result = llm.chat(messages, temperature=0.7)
            summary = result['answer']
        except Exception as e:
            summary = f"班级在过去{days}天内共有{total_submissions}次提交，整体通过率为{ac_rate}%。"
        
        # 生成教学建议
        recommendations = []
        if ac_rate < 40:
            recommendations.append("班级整体通过率偏低，建议加强基础知识讲解")
        if len(hard_problems) > 5:
            recommendations.append(f"有{len(hard_problems)}道共性难题，建议集中讲解")
        if error_distribution.get('TLE', 0) > total_submissions * 0.2:
            recommendations.append("超时问题普遍，建议开展算法复杂度专题训练")
        if statistics['active_students'] < len(student_ids) * 0.5:
            recommendations.append("活跃度不足，建议设置激励机制提高学生参与度")
        
        # 保存报告
        report = LearningReport.objects.create(
            user=coach,
            class_obj=class_obj,
            report_type='class',
            period_start=start_date,
            period_end=end_date,
            summary=summary,
            statistics=statistics,
            recommendations=recommendations,
        )
        
        return report
    
    @staticmethod
    def get_or_generate_student_report(user, days=7):
        """
        获取或生成学生报告（带缓存）
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 查找已有报告
        existing = LearningReport.objects.filter(
            user=user,
            report_type='student',
            period_start=start_date,
            period_end=end_date,
        ).first()
        
        if existing:
            return existing
        
        # 生成新报告
        return LearningAnalyticsService.generate_student_report(user, days)
    
    @staticmethod
    def get_or_generate_class_report(class_obj, coach, days=7):
        """
        获取或生成班级报告（带缓存）
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 查找已有报告
        existing = LearningReport.objects.filter(
            user=coach,
            class_obj=class_obj,
            report_type='class',
            period_start=start_date,
            period_end=end_date,
        ).first()
        
        if existing:
            return existing
        
        # 生成新报告
        return LearningAnalyticsService.generate_class_report(class_obj, coach, days)
