from apps.problem.models import Submission

sub = Submission.objects.get(id=40)
print('ID:', sub.id)
print('Status:', sub.get_status_display())
print('Result:', sub.result)
print('Error:', sub.error_message[:100] if sub.error_message else 'None')
