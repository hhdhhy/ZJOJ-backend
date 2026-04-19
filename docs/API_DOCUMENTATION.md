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

### 1. 用户登录 ✅

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
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "uid": "abc123",
    "username": "john_doe",
    "realname": "John Doe",
    "email": "john@example.com",
    "telephone": "13800138000",
    "is_staff": false,
    "status": 1
  }
}
```

**失败 (400)：**
```json
{
  "messages": "参数错误",
  "errors": {
    "username": ["用户名不存在"]
  }
}
```

**错误类型：**
- `用户名不存在` - 用户不存在
- `密码错误` - 密码不正确
- `用户已锁定` - 账户被锁定
- `必填字段缺失` - 缺少用户名或密码

**实现代码：**
```python
from rest_framework.views import APIView
from MYJWT.myjwt import get_token
from apps.ojauth.seriallizers import LoginSerializer

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            token = get_token(user)
            return Response({"token": token, "user": UerSerializer(user).data})
        else:
            print(serializer.errors)
            return Response({"messages":"参数错误","errors":serializer.errors}, 
                          status=status.HTTP_400_BAD_REQUEST)
```

---

### 2. 获取用户信息 ✅

**接口地址：** `GET /api/user/profile/`

**认证要求：** 需要登录（JWT Token）

**请求示例：**
```bash
curl -H "Authorization: jwt YOUR_TOKEN" \
     http://localhost:8000/api/user/profile/
```

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "uid": "abc123",
    "username": "john_doe",
    "realname": "John Doe",
    "email": "john@example.com",
    "telephone": "13800138000",
    "is_staff": false,
    "status": 1,
    "date_joined": "2026-04-16T10:00:00",
    "last_login": "2026-04-20T01:20:00"
  }
}
```

**失败 (401)：**
```json
{
  "detail": "未提供身份验证凭据"
}
```

**实现代码：**
```python
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UerSerializer(user)
        return Response({
            "code": 200,
            "message": "获取成功",
            "data": serializer.data
        })
```

---

### 3. 更新用户信息 ✅

**接口地址：** `PUT /api/user/profile/`

**认证要求：** 需要登录（JWT Token）

**请求参数：**
```json
{
  "realname": "string (可选，真实姓名)",
  "telephone": "string (可选，电话号码)"
}
```

**请求示例：**
```bash
curl -X PUT http://localhost:8000/api/user/profile/ \
  -H "Authorization: jwt YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "realname": "张三",
    "telephone": "13900139000"
  }'
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
    "realname": "张三",
    "email": "john@example.com",
    "telephone": "13900139000",
    "is_staff": false,
    "status": 1
  }
}
```

**失败 (400)：**
```json
{
  "code": 400,
  "message": "该手机号已被注册"
}
```

**注意事项：**
- 只能更新 `realname` 和 `telephone` 字段
- 电话号码必须唯一，不能与其他用户重复
- username、email 等字段不可修改

**实现代码：**
```python
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        user = request.user
        
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
```

---

## 题目管理接口

### 4. 获取题目列表 ✅

**接口地址：** `GET /api/problems/`

**认证要求：** 需要登录（JWT Token）

**查询参数：**
- `title` (可选) - 按标题搜索
- `tag_id` (可选) - 按标签过滤
- `creator` (可选) - 按创建者用户名过滤

**请求示例：**
```bash
# 获取所有题目
curl -H "Authorization: jwt YOUR_TOKEN" \
     http://localhost:8000/api/problems/

# 按标题搜索
curl -H "Authorization: jwt YOUR_TOKEN" \
     "http://localhost:8000/api/problems/?title=二分"

# 按标签过滤
curl -H "Authorization: jwt YOUR_TOKEN" \
     "http://localhost:8000/api/problems/?tag_id=1"
```

**响应格式：**

**成功 (200)：**
```json
[
  {
    "problem_id": "P1001",
    "title": "A+B Problem",
    "description": "计算两个整数的和...",
    "time_limit": 1000,
    "memory_limit": 256,
    "upload_time": "2026-04-16T10:00:00",
    "update_time": "2026-04-16T12:00:00",
    "creator": {
      "uid": "abc123",
      "username": "admin"
    },
    "tags": [
      {"id": 1, "name": "入门"},
      {"id": 2, "name": "数学"}
    ]
  }
]
```

**实现代码：**
```python
class ProblemListView(generics.ListAPIView):
    serializer_class = ProblemListSerializer
    
    def get_queryset(self):
        queryset = Problem.objects.all().order_by('-upload_time')
        
        # 按标题搜索
        title = self.request.query_params.get('title', None)
        if title:
            queryset = queryset.filter(title__icontains=title)
        
        # 按标签过滤
        tag_id = self.request.query_params.get('tag_id', None)
        if tag_id:
            queryset = queryset.filter(tag__id=tag_id)
        
        return queryset
```

---

### 5. 创建题目 ✅

**接口地址：** `POST /api/problems/create/`

**认证要求：** 需要登录（JWT Token）

**请求参数：**
```json
{
  "problem_id": "string (题目编号，如 P1001)",
  "title": "string (题目标题)",
  "description": "string (题目描述，支持Markdown)",
  "time_limit": "int (时间限制，毫秒)",
  "memory_limit": "int (内存限制，MB)",
  "tags": ["int (标签ID列表，可选)"]
}
```

**请求示例：**
```bash
curl -X POST http://localhost:8000/api/problems/create/ \
  -H "Authorization: jwt YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_id": "P1001",
    "title": "A+B Problem",
    "description": "## 题目描述\n\n计算两个整数的和。",
    "time_limit": 1000,
    "memory_limit": 256,
    "tags": [1, 2]
  }'
```

**响应格式：**

**成功 (201)：**
```json
{
  "message": "题目创建成功",
  "data": {
    "problem_id": "P1001",
    "title": "A+B Problem",
    "description": "## 题目描述\n\n计算两个整数的和。",
    "time_limit": 1000,
    "memory_limit": 256,
    "upload_time": "2026-04-16T10:00:00",
    "update_time": "2026-04-16T10:00:00",
    "creator": {
      "uid": "abc123",
      "username": "admin"
    },
    "tags": [
      {"id": 1, "name": "入门"},
      {"id": 2, "name": "数学"}
    ]
  }
}
```

**失败 (400)：**
```json
{
  "message": "创建失败",
  "errors": {
    "problem_id": ["该题目编号已存在"]
  }
}
```

---

### 6. 获取题目详情 ✅

**接口地址：** `GET /api/problems/<problem_id>/`

**认证要求：** 需要登录（JWT Token）

**路径参数：**
- `problem_id` - 题目编号（如 P1001）

**请求示例：**
```bash
curl -H "Authorization: jwt YOUR_TOKEN" \
     http://localhost:8000/api/problems/P1001/
```

**响应格式：**

**成功 (200) ：**
```json
{
  "problem_id": "P1001",
  "title": "A+B Problem",
  "description": "## 题目描述\n\n计算两个整数的和。\n\n## 输入格式\n\n...",
  "time_limit": 1000,
  "memory_limit": 256,
  "upload_time": "2026-04-16T10:00:00",
  "update_time": "2026-04-16T12:00:00",
  "creator_name": "admin",
  "tags": [
    {"id": 1, "name": "入门", "create_time": "2026-04-16T09:00:00"},
    {"id": 2, "name": "数学", "create_time": "2026-04-16T09:00:00"}
  ]
}
```

**失败 (404)：**
```json
{
  "detail": "未找到"
}
```

---

### 7. 更新题目 ✅

**接口地址：** 
- `PUT /api/problems/<problem_id>/` - 完整更新
- `PATCH /api/problems/<problem_id>/` - 部分更新

**认证要求：** 需要登录 + 仅创建者可操作

**路径参数：**
- `problem_id` - 题目编号

**请求参数（PUT - 完整更新）：**
```json
{
  "title": "string",
  "description": "string",
  "time_limit": "int",
  "memory_limit": "int",
  "tags": ["int"]
}
```

**请求参数（PATCH - 部分更新）：**
```json
{
  "title": "新的标题"  // 只更新标题
}
```

**请求示例：**
```bash
# 部分更新标题
curl -X PATCH http://localhost:8000/api/problems/P1001/ \
  -H "Authorization: jwt YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "A+B Problem (Updated)"}'
```

**响应格式：**

**成功 (200)：**
```json
{
  "message": "题目更新成功",
  "data": {
    "problem_id": "P1001",
    "title": "A+B Problem (Updated)",
    ...
  }
}
```

**失败 (403)：**
```json
{
  "message": "无权限修改此题目"
}
```

**权限说明：**
- 只有题目的创建者可以修改
- 其他用户尝试修改会返回 403 Forbidden

---

### 8. 删除题目 ✅

**接口地址：** `DELETE /api/problems/<problem_id>/`

**认证要求：** 需要登录 + 仅创建者可操作

**路径参数：**
- `problem_id` - 题目编号

**请求示例：**
```bash
curl -X DELETE http://localhost:8000/api/problems/P1001/ \
  -H "Authorization: jwt YOUR_TOKEN"
```

**响应格式：**

**成功 (204)：**
```json
{
  "message": "题目删除成功"
}
```

**失败 (403)：**
```json
{
  "message": "无权限删除此题目"
}
```

**注意事项：**
- 删除题目会级联删除相关的提交记录
- 只有创建者可以删除

---

### 9. 获取标签列表 ✅

**接口地址：** `GET /api/problems/tags/`

**认证要求：** 需要登录（JWT Token）

**请求示例：**
```bash
curl -H "Authorization: jwt YOUR_TOKEN" \
     http://localhost:8000/api/problems/tags/
```

**响应格式：**

**成功 (200)：**
```json
[
  {
    "id": 1,
    "name": "入门",
    "create_time": "2026-04-16T09:00:00"
  },
  {
    "id": 2,
    "name": "动态规划",
    "create_time": "2026-04-16T09:30:00"
  },
  {
    "id": 3,
    "name": "图论",
    "create_time": "2026-04-16T10:00:00"
  }
]
```

---

### 10. 创建标签 ✅

**接口地址：** `POST /api/problems/tags/create/`

**认证要求：** 需要登录（JWT Token）

**请求参数：**
```json
{
  "name": "string (标签名称)"
}
```

**请求示例：**
```bash
curl -X POST http://localhost:8000/api/problems/tags/create/ \
  -H "Authorization: jwt YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "字符串"}'
```

**响应格式：**

**成功 (201)：**
```json
{
  "message": "标签创建成功",
  "data": {
    "id": 4,
    "name": "字符串",
    "create_time": "2026-04-16T11:00:00"
  }
}
```

**失败 (400)：**
```json
{
  "message": "该标签已存在"
}
```

或

```json
{
  "message": "标签名称不能为空"
}
```

---

## 测试用例管理接口

### 9. 上传测试用例 ✅

**接口地址：** `POST /api/problems/<problem_id>/testcases/upload/`

**认证要求：** 需要登录（JWT Token）+ 仅创建者可操作

**路径参数：**
- `problem_id` - 题目编号

**请求参数：**
- `file` - ZIP文件（表单数据）

**ZIP文件格式：**
- 包含 `.in` 和 `.out` 配对的测试数据文件
- 支持任意目录结构，系统会自动转换为Hydro标准格式（testdata/目录）
- 每个输入文件必须有对应的输出文件

**请求示例：**
```bash
curl -X POST http://localhost:8000/api/problems/P1001/testcases/upload/ \
  -H "Authorization: jwt YOUR_TOKEN" \
  -F "file=@testcases.zip"
```

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "测试用例上传成功",
  "data": {
    "problem_id": "P1001",
    "test_case_count": 10,
    "file_size": "125.50 KB",
    "filename": "testcases.zip"
  }
}
```

**失败 (400)：**
```json
{
  "code": 400,
  "message": "ZIP文件中没有找到.in输入文件"
}
```

**权限说明：** 只有题目的创建者可以上传测试用例

---

### 10. 获取测试用例列表 ✅

**接口地址：** `GET /api/problems/<problem_id>/testcases/`

**认证要求：** 需要登录（JWT Token）

**路径参数：**
- `problem_id` - 题目编号

**请求示例：**
```bash
curl -H "Authorization: jwt YOUR_TOKEN" \
     http://localhost:8000/api/problems/P1001/testcases/
```

**响应格式：**

**成功 (200) - 有测试用例：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "problem_id": "P1001",
    "has_testcases": true,
    "test_case_count": 10,
    "file_size": "125.50 KB",
    "test_cases": [
      {
        "id": 1,
        "input": "1.in",
        "output": "1.out",
        "input_size": "1.20 KB",
        "output_size": "1.15 KB"
      }
    ]
  }
}
```

**成功 (200) - 无测试用例：**
```json
{
  "code": 200,
  "message": "暂无测试用例",
  "data": {
    "problem_id": "P1001",
    "has_testcases": false,
    "test_case_count": 0
  }
}
```

---

### 11. 删除测试用例 ✅

**接口地址：** `DELETE /api/problems/<problem_id>/testcases/delete/`

**认证要求：** 需要登录（JWT Token）+ 仅创建者可操作

**路径参数：**
- `problem_id` - 题目编号

**请求示例：**
```bash
curl -X DELETE http://localhost:8000/api/problems/P1001/testcases/delete/ \
  -H "Authorization: jwt YOUR_TOKEN"
```

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "测试用例已删除"
}
```

**失败 (403)：**
```json
{
  "code": 403,
  "message": "无权限操作此题目"
}
```

**权限说明：** 只有题目的创建者可以删除测试用例

---

## 代码评测接口

### 12. 提交代码 ✅

**接口地址：** `POST /api/submissions/submit/`

**认证要求：** 需要登录（JWT Token）

**请求参数：**
```json
{
  "problem_id": "string (题目编号)",
  "language": "string (编程语言: cpp/c/java/python3)",
  "code": "string (源代码)"
}
```

**请求示例：**
```bash
curl -X POST http://localhost:8000/api/submissions/submit/ \
  -H "Authorization: jwt YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_id": "P1001",
    "language": "cpp",
    "code": "#include <iostream>\nusing namespace std;\n\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}"
  }'
```

**响应格式：**

**成功 (201)：**
```json
{
  "message": "代码提交成功",
  "data": {
    "id": 123,
    "problem": {
      "problem_id": "P1001",
      "title": "A+B Problem"
    },
    "user": {
      "uid": "abc123",
      "username": "john_doe"
    },
    "language": "cpp",
    "code_length": 123,
    "status": 0,
    "status_display": "等待评测",
    "submit_time": "2026-04-16T12:00:00"
  }
}
```

**评测状态说明：**
- 0: 等待评测 (Pending)
- 1: 评测中 (Judging)
- 2: 已完成 (Completed)
- 3: 编译错误 (Compilation Error)
- 4: 系统错误 (System Error)

**评测结果（完成后）：**
- AC: Accepted
- WA: Wrong Answer
- TLE: Time Limit Exceeded
- MLE: Memory Limit Exceeded
- RE: Runtime Error
- CE: Compilation Error
- SE: System Error

---

### 13. 获取提交列表 ✅

**接口地址：** `GET /api/submissions/`

**认证要求：** 需要登录（JWT Token）

**查询参数：**
- `problem_id` (可选) - 按题目过滤
- `user_id` (可选) - 按用户过滤
- `status` (可选) - 按状态过滤
- `result` (可选) - 按结果过滤

**请求示例：**
```bash
# 获取我的所有提交
curl -H "Authorization: jwt YOUR_TOKEN" \
     http://localhost:8000/api/submissions/

# 获取某题目的提交
curl -H "Authorization: jwt YOUR_TOKEN" \
     "http://localhost:8000/api/submissions/?problem_id=P1001"
```

**响应格式：**

**成功 (200)：**
```json
[
  {
    "id": 123,
    "problem": {
      "problem_id": "P1001",
      "title": "A+B Problem"
    },
    "user": {
      "uid": "abc123",
      "username": "john_doe"
    },
    "language": "cpp",
    "code_length": 123,
    "status": 2,
    "status_display": "已完成",
    "result": "AC",
    "result_display": "Accepted",
    "score": 100,
    "execution_time": 45,
    "memory_usage": 1024,
    "submit_time": "2026-04-16T12:00:00",
    "judge_time": "2026-04-16T12:00:05"
  }
]
```

---

### 14. 获取提交详情 ✅

**接口地址：** `GET /api/submissions/<submission_id>/`

**认证要求：** 需要登录（JWT Token）

**路径参数：**
- `submission_id` - 提交ID

**请求示例：**
```bash
curl -H "Authorization: jwt YOUR_TOKEN" \
     http://localhost:8000/api/submissions/123/
```

**响应格式：**

**成功 (200)：**
```json
{
  "id": 123,
  "problem": {
    "problem_id": "P1001",
    "title": "A+B Problem"
  },
  "user": {
    "uid": "abc123",
    "username": "john_doe"
  },
  "language": "cpp",
  "code": "#include <iostream>\n...",
  "code_length": 123,
  "status": 2,
  "status_display": "已完成",
  "result": "AC",
  "result_display": "Accepted",
  "score": 100,
  "execution_time": 45,
  "memory_usage": 1024,
  "submit_time": "2026-04-16T12:00:00",
  "judge_time": "2026-04-16T12:00:05",
  "test_case_results": [
    {
      "test_case_id": 1,
      "status": "AC",
      "execution_time": 12,
      "memory_usage": 512,
      "score": 50,
      "message": ""
    },
    {
      "test_case_id": 2,
      "status": "AC",
      "execution_time": 15,
      "memory_usage": 512,
      "score": 50,
      "message": ""
    }
  ]
}
```

**失败 (404)：**
```json
{
  "detail": "未找到"
}
```

---

### 14. 用户注册 ✅

**接口地址：** `POST /api/register/`

**认证要求：** 不需要登录

**请求参数：**
```json
{
  "username": "string (必填，2-20字符)",
  "password": "string (必填，6-20字符)",
  "email": "string (必填，唯一)",
  "realname": "string (必填，真实姓名)",
  "telephone": "string (可选，唯一)"
}
```

**请求示例：**
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "password123",
    "email": "newuser@example.com",
    "realname": "新用户",
    "telephone": "13900139000"
  }'
```

**响应格式：**

**成功 (201)：**
```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "uid": "xyz789",
    "username": "newuser",
    "realname": "新用户",
    "email": "newuser@example.com"
  }
}
```

**失败 (400)：**
```json
{
  "code": 400,
  "message": "用户名已存在"
}
```

或其他错误：
- `请填写必填字段` - 缺少必要参数
- `用户名长度必须在2-20字符之间` - 用户名长度不符合要求
- `密码长度必须在6-20字符之间` - 密码长度不符合要求
- `用户名已存在` - 用户名已被注册
- `邮箱已被注册` - 邮箱已被使用
- `该手机号已被注册` - 电话已被使用

**实现代码：**
```python
class RegisterView(APIView):
    permission_classes = [AllowAny]
    
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
                "message": "请填写必填字段"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证长度
        if len(username) < 2 or len(username) > 20:
            return Response({
                "code": 400,
                "message": "用户名长度必须在2-20字符之间"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 6 or len(password) > 20:
            return Response({
                "code": 400,
                "message": "密码长度必须在6-20字符之间"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查唯一性
        if OJUser.objects.filter(username=username).exists():
            return Response({"code": 400, "message": "用户名已存在"}, status=400)
        
        if OJUser.objects.filter(email=email).exists():
            return Response({"code": 400, "message": "邮箱已被注册"}, status=400)
        
        if telephone and OJUser.objects.filter(telephone=telephone).exists():
            return Response({"code": 400, "message": "该手机号已被注册"}, status=400)
        
        # 创建用户
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
```

---

### 15. 修改密码 ✅

**接口地址：** `POST /api/password/change/`

**认证要求：** 需要登录（JWT Token）

**请求参数：**
```json
{
  "old_password": "string (原密码)",
  "new_password": "string (新密码，6-20字符)"
}
```

**请求示例：**
```bash
curl -X POST http://localhost:8000/api/password/change/ \
  -H "Authorization: jwt YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "oldpass123",
    "new_password": "newpass456"
  }'
```

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "密码修改成功"
}
```

**失败 (400)：**
```json
{
  "code": 400,
  "message": "原密码错误"
}
```

或其他错误：
- `请提供原密码和新密码` - 缺少参数
- `原密码错误` - 原密码不正确
- `新密码长度必须在6-20字符之间` - 新密码长度不符合要求

**实现代码：**
```python
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({
                "code": 400,
                "message": "请提供原密码和新密码"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            return Response({
                "code": 400,
                "message": "原密码错误"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6 or len(new_password) > 20:
            return Response({
                "code": 400,
                "message": "新密码长度必须在6-20字符之间"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            "code": 200,
            "message": "密码修改成功"
        })
```

---

### 16. 重置密码（邮件）✅

**接口地址：** `POST /api/password/reset/`

**认证要求：** 不需要登录

**请求参数：**
```json
{
  "email": "string (注册邮箱)"
}
```

**请求示例：**
```bash
curl -X POST http://localhost:8000/api/password/reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

**响应格式：**

**成功 (200)：**
```json
{
  "code": 200,
  "message": "如果该邮箱已注册，重置链接将发送到您的邮箱"
}
```

**说明：**
- 为防止邮箱枚举攻击，无论邮箱是否存在都返回相同消息
- 实际项目中需要配置邮件服务并生成安全的reset token
- TODO: 实现邮件发送功能

**实现代码：**
```python
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                "code": 400,
                "message": "请提供邮箱地址"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = OJUser.objects.get(email=email)
        except OJUser.DoesNotExist:
            # 为防止邮箱枚举，即使不存在也返回成功
            return Response({
                "code": 200,
                "message": "如果该邮箱已注册，重置链接将发送到您的邮箱"
            })
        
        # TODO: 生成重置token并发送邮件
        # reset_token = generate_reset_token(user)
        # send_reset_email(email, reset_token)
        
        return Response({
            "code": 200,
            "message": "如果该邮箱已注册，重置链接将发送到您的邮箱"
        })
```

---

## 通用响应格式

### 成功响应
```json
{
  "token": "...",
  "user": {...}
}
```

### 错误响应
```json
{
  "messages": "错误描述",
  "errors": {...}
}
```

### HTTP 状态码
- `200` - 成功
- `400` - 请求参数错误
- `401` - 未授权（Token 无效或过期）
- `403` - 禁止访问
- `404` - 资源不存在
- `500` - 服务器错误

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

## AI助手接口 🤖

以下接口提供基于RAG技术的智能问答服务。

### 9. AI智能问答 ✅

**接口地址：** `POST /api/ai/chat/`

**认证方式：** JWT Token

**请求参数：**
```json
{
  "question": "string (必填)",
  "use_rag": true,  // 可选，是否使用RAG模式，默认true
  "top_k": 3        // 可选，检索文档数量，默认5
}
```

**响应格式：**

**成功 (200)：**
```json
{
  "answer": "二分查找是一种在有序数组中查找特定元素的算法...",
  "tokens_used": 270,
  "remaining_quota": 47,
  "chat_id": 3,
  "sources": [
    {
      "id": "kb_abc123",
      "content": "二分查找（Binary Search）是一种...",
      "metadata": {
        "doc_id": 1,
        "title": "二分查找算法",
        "doc_type": "algorithm"
      },
      "similarity": 0.9822
    }
  ]
}
```

**字段说明：**
- `answer`: AI生成的回答
- `tokens_used`: 消耗的Token数量
- `remaining_quota`: 剩余每日配额
- `chat_id`: 对话记录ID
- `sources`: 引用来源列表（仅RAG模式）
  - `id`: 文档向量ID
  - `content`: 文档内容片段
  - `metadata`: 文档元数据（标题、类型等）
  - `similarity`: 相似度（0-1之间）

**错误响应：**

**未认证 (401)：**
```json
{
  "detail": "身份认证信息未提供。"
}
```

**配额超限 (429)：**
```json
{
  "detail": "今日配额已用完，请明天再试"
}
```

**频率限制 (429)：**
```json
{
  "detail": "请求过于频繁，请稍后再试"
}
```

**服务器错误 (500)：**
```json
{
  "error": "处理失败: Error executing plan..."
}
```

**使用示例：**

```python
import requests

# 登录获取token
login_response = requests.post("http://127.0.0.1:8000/auth/login/", json={
    "username": "test_ai",
    "password": "TestPass123"
})
token = login_response.json()["token"]

headers = {
    "Authorization": f"jwt {token}",
    "Content-Type": "application/json"
}

# RAG模式问答（推荐用于技术问题）
rag_response = requests.post("http://127.0.0.1:8000/api/ai/chat/", headers=headers, json={
    "question": "什么是二分查找算法？",
    "use_rag": True,
    "top_k": 3
})
print(rag_response.json())

# 简单对话模式（适用于闲聊）
chat_response = requests.post("http://127.0.0.1:8000/api/ai/chat/", headers=headers, json={
    "question": "你好，请介绍一下自己",
    "use_rag": False
})
print(chat_response.json())
```

---

### 10. 获取对话历史 ✅

**接口地址：** `GET /api/ai/history/?limit=50&offset=0`

**认证方式：** JWT Token

**查询参数：**
- `limit`: 每页数量，默认50
- `offset`: 偏移量，默认0

**响应格式：**

**成功 (200)：**
```json
{
  "count": 10,
  "results": [
    {
      "id": 5,
      "question": "什么是二分查找算法？",
      "answer": "二分查找是一种...",
      "sources": [...],
      "tokens_used": 270,
      "created_at": "2026-04-16T00:05:58.123456"
    }
  ]
}
```

**使用示例：**

```python
# 获取最近10条对话
response = requests.get(
    "http://127.0.0.1:8000/api/ai/history/?limit=10&offset=0",
    headers=headers
)
print(response.json())
```

---

### 11. 使用情况统计 ✅

**接口地址：** `GET /api/ai/usage/`

**认证方式：** JWT Token

**响应格式：**

**成功 (200)：**
```json
{
  "daily_quota": 50,
  "used_today": 3,
  "remaining": 47,
  "max_history": 100,
  "history_count": 10,
  "reset_time": "明天 00:00"
}
```

**字段说明：**
- `daily_quota`: 每日配额上限
- `used_today`: 今日已使用次数
- `remaining`: 剩余可用次数
- `max_history`: 历史记录上限
- `history_count`: 当前历史记录数
- `reset_time`: 配额重置时间

**使用示例：**

```python
response = requests.get("http://127.0.0.1:8000/api/ai/usage/", headers=headers)
stats = response.json()
print(f"今日使用: {stats['used_today']}/{stats['daily_quota']}")
print(f"剩余配额: {stats['remaining']}")
```

---

### 12. 清空对话历史 ✅

**接口地址：** `DELETE /api/ai/history/clear/`

**认证方式：** JWT Token

**响应格式：**

**成功 (200)：**
```json
{
  "message": "已清空 10 条对话记录"
}
```

**使用示例：**

```python
response = requests.delete(
    "http://127.0.0.1:8000/api/ai/history/clear/",
    headers=headers
)
print(response.json())
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
- `400` - 请求参数错误
- `401` - 未授权（Token 无效或过期）
- `403` - 禁止访问
- `404` - 资源不存在
- `500` - 服务器错误

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
token = response.json()['token']
print(f"Token: {token}")
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
  localStorage.setItem('token', data.token);
  return data;
};
```

---

*最后更新：2026 年 4 月 16 日*

**新增内容：**
- ✅ AI助手接口（RAG智能问答系统）
  - AI智能问答（支持RAG模式和简单对话）
  - 对话历史管理
  - 使用情况统计
  - 配额和频率限制

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

*最后更新：2026 年 4 月 20 日*

**新增内容：**
- ✅ 测试用例管理接口（3个）
  - POST /api/problems/<id>/testcases/upload/ - 上传测试用例ZIP
  - GET /api/problems/<id>/testcases/ - 获取测试用例列表
  - DELETE /api/problems/<id>/testcases/delete/ - 删除测试用例
  - 自动转换任意格式为Hydro标准格式（testdata/目录）
- ✅ 用户认证接口（3个）
  - POST /api/register/ - 用户注册
  - POST /api/password/change/ - 修改密码
  - POST /api/password/reset/ - 重置密码（邮件）
- ✅ 用户信息接口（2个）
  - GET /api/user/profile/ - 获取当前用户信息
  - PUT /api/user/profile/ - 更新用户信息（realname、telephone）
- ✅ 题目管理接口（7个）
  - 获取题目列表（支持搜索和过滤）
  - 创建题目
  - 获取题目详情
  - 更新题目（PUT/PATCH）
  - 删除题目
  - 获取标签列表
  - 创建标签
- ✅ 代码评测接口（3个）
  - 提交代码
  - 获取提交列表
  - 获取提交详情（含测试点结果）
- ✅ AI助手接口（4个）
  - AI智能问答（支持RAG模式和简单对话）
  - 对话历史管理
  - 使用情况统计
  - 配额和频率限制
