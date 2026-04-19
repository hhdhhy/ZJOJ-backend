from datetime import datetime
from django.shortcuts import render
from pyexpat.errors import messages
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from MYJWT.myjwt import get_token
from .models import OJUser
from .seriallizers import LoginSerializer, UerSerializer
import MYJWT.myjwt


class LoginView(APIView):
    permission_classes = [AllowAny]  # 登录不需要认证
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            token = get_token(user)
            return Response({"token": token, "user": UerSerializer(user).data})
        else:
            detail = list(serializer.errors.values())[0][0]
            print(detail)
            return Response(
                {"detail": detail, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(APIView):
    """
    用户注册接口
    POST /api/register/
    """
    permission_classes = [AllowAny]  # 注册不需要认证
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        realname = request.data.get('realname')
        telephone = request.data.get('telephone', '')
        
        # 验证必填字段
        if not all([username, password, email, realname]):
            return Response({
                "code": 400,
                "message": "请填写必填字段",
                "errors": {
                    "username": "用户名不能为空" if not username else None,
                    "password": "密码不能为空" if not password else None,
                    "email": "邮箱不能为空" if not email else None,
                    "realname": "真实姓名不能为空" if not realname else None,
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证用户名长度
        if len(username) < 2 or len(username) > 20:
            return Response({
                "code": 400,
                "message": "用户名长度必须在2-20字符之间"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证密码长度
        if len(password) < 6 or len(password) > 20:
            return Response({
                "code": 400,
                "message": "密码长度必须在6-20字符之间"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户名是否已存在
        if OJUser.objects.filter(username=username).exists():
            return Response({
                "code": 400,
                "message": "用户名已存在"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查邮箱是否已存在
        if OJUser.objects.filter(email=email).exists():
            return Response({
                "code": 400,
                "message": "邮箱已被注册"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查电话是否已存在（如果提供了电话）
        if telephone and OJUser.objects.filter(telephone=telephone).exists():
            return Response({
                "code": 400,
                "message": "该手机号已被注册"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建用户
        try:
            user = OJUser.objects.create_user(
                username=username,
                realname=realname,
                email=email,
                password=password,
                telephone=telephone
            )
            
            return Response({
                "code": 201,
                "message": "注册成功",
                "data": {
                    "uid": user.uid,
                    "username": user.username,
                    "realname": user.realname,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "code": 500,
                "message": f"注册失败：{str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    """
    获取用户信息接口
    GET /api/user/profile/
    """
    permission_classes = [IsAuthenticated]  # 需要登录
    
    def get(self, request):
        """获取当前用户信息"""
        user = request.user
        serializer = UerSerializer(user)
        return Response({
            "code": 200,
            "message": "获取成功",
            "data": serializer.data
        })
    
    def put(self, request):
        """更新用户信息（部分字段）"""
        user = request.user
        
        # 可更新的字段
        realname = request.data.get('realname')
        telephone = request.data.get('telephone')
        
        if realname:
            user.realname = realname
        if telephone:
            # 检查电话是否已被其他用户使用
            if OJUser.objects.filter(telephone=telephone).exclude(uid=user.uid).exists():
                return Response({
                    "code": 400,
                    "message": "该手机号已被注册"
                }, status=status.HTTP_400_BAD_REQUEST)
            user.telephone = telephone
        
        user.save()
        serializer = UerSerializer(user)
        
        return Response({
            "code": 200,
            "message": "更新成功",
            "data": serializer.data
        })


class ChangePasswordView(APIView):
    """
    修改密码接口
    POST /api/password/change/
    """
    permission_classes = [IsAuthenticated]  # 需要登录
    
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        # 验证参数
        if not old_password or not new_password:
            return Response({
                "code": 400,
                "message": "请提供原密码和新密码"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证原密码
        if not user.check_password(old_password):
            return Response({
                "code": 400,
                "message": "原密码错误"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证新密码长度
        if len(new_password) < 6 or len(new_password) > 20:
            return Response({
                "code": 400,
                "message": "新密码长度必须在6-20字符之间"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        return Response({
            "code": 200,
            "message": "密码修改成功"
        })


class ResetPasswordView(APIView):
    """
    重置密码接口（发送重置邮件）
    POST /api/password/reset/
    """
    permission_classes = [AllowAny]  # 不需要登录
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                "code": 400,
                "message": "请提供邮箱地址"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找用户
        try:
            user = OJUser.objects.get(email=email)
        except OJUser.DoesNotExist:
            # 为防止邮箱枚举，即使不存在也返回成功
            return Response({
                "code": 200,
                "message": "如果该邮箱已注册，重置链接将发送到您的邮箱"
            })
        
        # TODO: 生成重置token并发送邮件
        # 这里需要配置邮件服务和生成安全的reset token
        # reset_token = generate_reset_token(user)
        # send_reset_email(email, reset_token)
        
        return Response({
            "code": 200,
            "message": "如果该邮箱已注册，重置链接将发送到您的邮箱"
        })





