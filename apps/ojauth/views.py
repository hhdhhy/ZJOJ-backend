from datetime import datetime
from django.shortcuts import render
from pyexpat.errors import messages
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from MYJWT.myjwt import get_token
from .models import OJUser, Class, ClassMember
from .seriallizers import LoginSerializer, UerSerializer, RegisterSerializer, UserProfileSerializer, UserProfileUpdateSerializer
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
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "code": 201,
                "message": "注册成功",
                "data": {
                    "uid": user.uid,
                    "username": user.username,
                    "email": user.email,
                    "role": user.get_role_display()
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "code": 400,
                "message": "注册失败",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    获取用户信息接口
    GET /api/user/profile/
    """
    permission_classes = [IsAuthenticated]  # 需要登录
    
    def get(self, request):
        """获取当前用户信息"""
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response({
            "code": 200,
            "message": "获取成功",
            "data": serializer.data
        })
    
    def put(self, request):
        """更新用户信息"""
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "code": 200,
                "message": "更新成功",
                "data": UserProfileSerializer(user).data
            })
        else:
            return Response({
                "code": 400,
                "message": "更新失败",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


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


class ClassListView(APIView):
    """
    班级列表接口
    GET /api/classes/ - 获取班级列表
    POST /api/classes/ - 创建班级（教练）
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取班级列表"""
        user = request.user
        
        # 教练可以看到自己管理的班级
        if user.is_coach() or user.is_admin_user():
            classes = Class.objects.filter(coach=user)
        else:
            # 学生可以看到自己加入的班级
            class_members = ClassMember.objects.filter(user=user)
            classes = Class.objects.filter(id__in=[cm.class_obj_id for cm in class_members])
        
        class_list = []
        for cls in classes:
            member_count = ClassMember.objects.filter(class_obj=cls).count()
            class_list.append({
                'id': cls.id,
                'name': cls.name,
                'coach': cls.coach.username if cls.coach else None,
                'description': cls.description,
                'member_count': member_count,
                'create_time': cls.create_time
            })
        
        return Response({
            "code": 200,
            "message": "获取成功",
            "data": class_list
        })
    
    def post(self, request):
        """创建班级（仅教练）"""
        user = request.user
        
        if not (user.is_coach() or user.is_admin_user()):
            return Response({
                "code": 403,
                "message": "只有教练可以创建班级"
            }, status=status.HTTP_403_FORBIDDEN)
        
        name = request.data.get('name')
        description = request.data.get('description', '')
        
        if not name:
            return Response({
                "code": 400,
                "message": "班级名称不能为空"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已存在
        if Class.objects.filter(name=name).exists():
            return Response({
                "code": 400,
                "message": "该班级已存在"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cls = Class.objects.create(
            name=name,
            coach=user,
            description=description
        )
        
        return Response({
            "code": 201,
            "message": "班级创建成功",
            "data": {
                'id': cls.id,
                'name': cls.name
            }
        }, status=status.HTTP_201_CREATED)


class ClassDetailView(APIView):
    """
    班级详情接口
    GET /api/classes/{id}/ - 获取班级详情
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, class_id):
        """获取班级详情和成员列表"""
        try:
            cls = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({
                "code": 404,
                "message": "班级不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 权限检查：只有教练或班级成员可以查看
        user = request.user
        if not (user.is_coach() and cls.coach == user) and \
           not ClassMember.objects.filter(class_obj=cls, user=user).exists() and \
           not user.is_admin_user():
            return Response({
                "code": 403,
                "message": "无权查看此班级"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 获取成员列表
        members = ClassMember.objects.filter(class_obj=cls).select_related('user')
        member_list = [{
            'uid': m.user.uid,
            'username': m.user.username,
            'realname': m.user.realname,
            'join_time': m.join_time
        } for m in members]
        
        return Response({
            "code": 200,
            "message": "获取成功",
            "data": {
                'id': cls.id,
                'name': cls.name,
                'coach': cls.coach.username if cls.coach else None,
                'description': cls.description,
                'create_time': cls.create_time,
                'members': member_list
            }
        })


class ClassMemberView(APIView):
    """
    班级成员管理接口
    POST /api/classes/{id}/members/ - 添加成员（教练）
    DELETE /api/classes/{id}/members/ - 移除成员（教练）
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, class_id):
        """添加班级成员（仅教练）"""
        user = request.user
        
        try:
            cls = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({
                "code": 404,
                "message": "班级不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 权限检查
        if not (user.is_coach() and cls.coach == user) and not user.is_admin_user():
            return Response({
                "code": 403,
                "message": "只有班主任可以添加成员"
            }, status=status.HTTP_403_FORBIDDEN)
        
        username = request.data.get('username')
        if not username:
            return Response({
                "code": 400,
                "message": "请提供用户名"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = OJUser.objects.get(username=username)
        except OJUser.DoesNotExist:
            return Response({
                "code": 404,
                "message": "用户不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not student.is_student():
            return Response({
                "code": 400,
                "message": "只能添加学生"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已在班级中
        if ClassMember.objects.filter(class_obj=cls, user=student).exists():
            return Response({
                "code": 400,
                "message": "该学生已在班级中"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ClassMember.objects.create(class_obj=cls, user=student)
        
        return Response({
            "code": 200,
            "message": "添加成功"
        })
    
    def delete(self, request, class_id):
        """移除班级成员（仅教练）"""
        user = request.user
        
        try:
            cls = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({
                "code": 404,
                "message": "班级不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 权限检查
        if not (user.is_coach() and cls.coach == user) and not user.is_admin_user():
            return Response({
                "code": 403,
                "message": "只有班主任可以移除成员"
            }, status=status.HTTP_403_FORBIDDEN)
        
        username = request.data.get('username')
        if not username:
            return Response({
                "code": 400,
                "message": "请提供用户名"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = OJUser.objects.get(username=username)
        except OJUser.DoesNotExist:
            return Response({
                "code": 404,
                "message": "用户不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 删除成员关系
        deleted, _ = ClassMember.objects.filter(class_obj=cls, user=student).delete()
        
        if deleted == 0:
            return Response({
                "code": 404,
                "message": "该学生不在班级中"
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "code": 200,
            "message": "移除成功"
        })





