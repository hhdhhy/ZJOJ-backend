from rest_framework import serializers

from apps.ojauth.models import OJUser, UserStatusChoices


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20,min_length=2)
    password = serializers.CharField(max_length=20,min_length=6)

    def validate(self,data):
        password = data.get('password')
        username = data.get('username')
        if username and password :
            user =OJUser.objects.filter(username=username).first()
            if not user:
                raise serializers.ValidationError('用户名不存在')
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')

            if user.status==UserStatusChoices.LOCKED:
                raise serializers.ValidationError('用户已锁定')
            data['user'] = user
        else:
            raise serializers.ValidationError('请传入用户名以及密码')

        return data