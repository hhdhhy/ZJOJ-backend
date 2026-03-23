# ZJOJ API 接口文档

## 认证机制

### JWT 认证方式
所有需要认证的接口使用 JWT Token 进行身份验证。

**请求头格式：**
```
Authorization: jwt <token>
```

**Token 获取：**
通过登录接口获取 JWT Token。

---

## 用户认证接口

### 1. 用户登录

**接口地址：** `POST /api/login/`

**请求参数：**
```json
{
  "username": "string (2-20 字符)",
  "password": "string (6-20 字符)"
}
```

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "uid": "abc123",
      "username": "john_doe",
      "realname": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

**失败 (400)：**
```json
{
  "code": 400,
  "message": "用户名不存在",
  "data": null
}
```

**错误类型：**
- `用户名不存在` - 用户不存在
- `密码错误` - 密码不正确
- `用户已锁定` - 账户被锁定
- `请传入用户名以及密码` - 缺少必填字段

**实现代码：**
```python
from rest_framework.views import APIView
from MYJWT.myjwt import get_token
from apps.ojauth.seriallizers import LoginSerializer

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = get_token(user)
            
            # 更新最后登录时间
            user.last_login = timezone.now()
            user.save()
            
            return Response({
                'token': token,
                'user': {
                    'uid': user.uid,
                    'username': user.username,
                    'realname': user.realname,
                    'email': user.email
                }
            })
        return Response(serializer.errors, status=400)
```

---

### 2. 用户注册

**接口地址：** `POST /api/register/`

**请求参数：**
```json
{
  "username": "string (唯一)",
  "password": "string",
  "email": "string (唯一)",
  "realname": "string",
  "telephone": "string (可选)"
}
```

**响应格式：**

**成功 (201)：**
```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "uid": "abc123",
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

**失败 (400)：**
```json
{
  "code": 400,
  "message": "用户名已存在",
  "data": null
}
```

**实现代码：**
```python
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        realname = request.data.get('realname')
        telephone = request.data.get('telephone', '')
        
        # 验证必填字段
        if not all([username, password, email, realname]):
            return Response({'message': '请填写必填字段'}, status=400)
        
        # 检查用户名是否已存在
        if OJUser.objects.filter(username=username).exists():
            return Response({'message': '用户名已存在'}, status=400)
        
        # 检查邮箱是否已存在
        if OJUser.objects.filter(email=email).exists():
            return Response({'message': '邮箱已被注册'}, status=400)
        
        # 创建用户
        user = OJUser.objects.create_user(
            username=username,
            realname=realname,
            email=email,
            password=password,
            telephone=telephone
        )
        
        return Response({
            'uid': user.uid,
            'username': user.username,
            'email': user.email
        }, status=201)
```

---

### 3. 用户登出

**接口地址：** `POST /api/logout/`

**认证方式：** JWT Token

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

**实现代码：**
```python
class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        # JWT 为无状态认证，登出只需客户端删除 token
        # 如需实现黑名单机制，可将 token 加入黑名单
        return Response({'message': '登出成功'})
```

---

### 4. 获取当前用户信息

**接口地址：** `GET /api/user/profile/`

**认证方式：** JWT Token

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "data": {
    "uid": "abc123",
    "username": "john_doe",
    "realname": "John Doe",
    "email": "john@example.com",
    "telephone": "13800138000",
    "is_staff": false,
    "is_active": true,
    "status": 1,
    "date_joined": "2026-03-24T10:30:00Z",
    "last_login": "2026-03-24T12:00:00Z"
  }
}
```

**实现代码：**
```python
class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        user = request.user
        return Response({
            'uid': user.uid,
            'username': user.username,
            'realname': user.realname,
            'email': user.email,
            'telephone': user.telephone,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'status': user.status,
            'date_joined': user.date_joined,
            'last_login': user.last_login
        })
```

---

### 5. 更新用户信息

**接口地址：** `PUT /api/user/profile/`

**认证方式：** JWT Token

**请求参数：**
```json
{
  "realname": "string (可选)",
  "telephone": "string (可选)"
}
```

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "uid": "abc123",
    "username": "john_doe",
    "realname": "John Updated",
    "email": "john@example.com"
  }
}
```

**实现代码：**
```python
class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def put(self, request):
        user = request.user
        
        # 可更新的字段
        realname = request.data.get('realname')
        telephone = request.data.get('telephone')
        
        if realname:
            user.realname = realname
        if telephone:
            user.telephone = telephone
        
        user.save()
        
        return Response({
            'uid': user.uid,
            'username': user.username,
            'realname': user.realname,
            'email': user.email
        })
```

---

### 6. 修改密码

**接口地址：** `POST /api/password/change/`

**认证方式：** JWT Token

**请求参数：**
```json
{
  "old_password": "string",
  "new_password": "string (6-20 字符)"
}
```

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

**错误类型：**
- `原密码错误` - 原密码不正确
- `新密码长度不符合要求` - 新密码长度不在 6-20 字符范围

**实现代码：**
```python
class PasswordChangeView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        # 验证原密码
        if not user.check_password(old_password):
            return Response({'message': '原密码错误'}, status=400)
        
        # 验证新密码长度
        if len(new_password) < 6 or len(new_password) > 20:
            return Response({'message': '新密码长度不符合要求'}, status=400)
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        return Response({'message': '密码修改成功'})
```

---

### 7. 重置密码（邮件）

**接口地址：** `POST /api/password/reset/`

**请求参数：**
```json
{
  "email": "string"
}
```

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "重置邮件已发送，请查收",
  "data": null
}
```

**实现代码：**
```python
class PasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')
        
        # 查找用户
        try:
            user = OJUser.objects.get(email=email)
        except OJUser.DoesNotExist:
            # 为防止邮箱枚举，即使不存在也返回成功
            return Response({'message': '重置邮件已发送，请查收'})
        
        # 生成重置 token（6 小时有效期）
        reset_token = generate_reset_token(user)
        
        # 发送重置邮件
        reset_link = f"https://your-domain.com/reset-password?token={reset_token}"
        send_mail(
            subject='密码重置',
            message=f'点击链接重置密码：{reset_link}',
            from_email='noreply@zjoj.com',
            recipient_list=[email],
            fail_silently=False,
        )
        
        return Response({'message': '重置邮件已发送，请查收'})
```

---

### 8. 确认重置密码

**接口地址：** `POST /api/password/reset/confirm/`

**请求参数：**
```json
{
  "token": "string",
  "new_password": "string (6-20 字符)"
}
```

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "密码重置成功",
  "data": null
}
```

**实现代码：**
```python
class PasswordResetConfirmView(APIView):
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        # 验证 token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = OJUser.objects.get(uid=user_id)
        except (jwt.InvalidTokenError, OJUser.DoesNotExist):
            return Response({'message': '无效的重置令牌'}, status=400)
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        return Response({'message': '密码重置成功'})
```

---

## 通用响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

### HTTP 状态码
- `200` - 成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未授权（Token 无效或过期）
- `403` - 禁止访问
- `404` - 资源不存在
- `500` - 服务器错误

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400001 | 用户名不存在 |
| 400002 | 密码错误 |
| 400003 | 用户已锁定 |
| 400004 | 必填字段缺失 |
| 400005 | 用户名已存在 |
| 400006 | 邮箱已被注册 |
| 400007 | 原密码错误 |
| 400008 | 新密码长度不符合要求 |
| 400009 | 无效的重置令牌 |
| 401001 | Token 已过期 |
| 401002 | Token 无效 |
| 401003 | 用户不存在 |
| 401004 | 用户非活跃 |

---

## 使用示例

### Python 示例
```python
import requests

# 登录
login_url = "http://localhost:8000/api/login/"
login_data = {
    "username": "john_doe",
    "password": "password123"
}
response = requests.post(login_url, json=login_data)
token = response.json()['data']['token']

# 访问受保护的接口
headers = {"Authorization": f"jwt {token}"}
profile_url = "http://localhost:8000/api/user/profile/"
response = requests.get(profile_url, headers=headers)
print(response.json())
```

### JavaScript 示例
```javascript
// 登录
const login = async (username, password) => {
  const response = await fetch('/api/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.data.token);
  return data;
};

// 访问受保护的接口
const getUserProfile = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch('/api/user/profile/', {
    headers: {
      'Authorization': `jwt ${token}`
    }
  });
  
  return await response.json();
};
```

---

*最后更新：2026 年 3 月 24 日*
