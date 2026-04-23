from rest_framework import serializers

from apps.ojauth.models import OJUser, UserStatusChoices, UserRoleChoices


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

class UerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OJUser
        # fields = "__all__"
        exclude = ['password',"groups","user_permissions"]


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = OJUser
        fields = ['username', 'email', 'telephone', 'realname', 'password', 
                  'password_confirm', 'role', 'school', 'grade']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'default': UserRoleChoices.STUDENT},
            'school': {'required': False, 'allow_blank': True},
            'grade': {'required': False, 'allow_blank': True},
        }
    
    def validate_username(self, value):
        if OJUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('用户名已存在')
        return value
    
    def validate_email(self, value):
        if OJUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('邮箱已被注册')
        return value
    
    def validate_telephone(self, value):
        if OJUser.objects.filter(telephone=value).exists():
            raise serializers.ValidationError('手机号已被注册')
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '两次密码不一致'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = OJUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    role_name = serializers.CharField(source='get_role_display', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = OJUser
        fields = ['uid', 'username', 'email', 'telephone', 'realname', 
                  'role', 'role_name', 'status', 'status_name',
                  'school', 'grade', 'avatar', 'bio', 'date_joined']
        read_only_fields = ['uid', 'username', 'email', 'date_joined']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    class Meta:
        model = OJUser
        fields = ['realname', 'telephone', 'school', 'grade', 'avatar', 'bio']