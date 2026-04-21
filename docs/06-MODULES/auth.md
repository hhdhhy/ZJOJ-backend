# JWT 认证系统文档

## 概述
本系统使用JWT（JSON Web Token）实现用户认证，包含令牌生成和验证功能。

## 核心组件

### 1. get_token 函数

**功能**：为指定用户生成JWT令牌

**参数**：
- `user`：用户对象（OJUser实例）

**返回值**：
- JWT令牌字符串

**实现细节**：
- 令牌有效期：14天（60 * 24 * 14秒）
- Payload结构：`{"userid": user.uid, "exp": 过期时间}`
- 签名算法：HS256
- 使用Django的SECRET_KEY进行签名

### 2. JWTAuthentication 类

**功能**：Django REST framework的认证后端，用于验证JWT令牌

#### authenticate 方法

**流程**：
1. 从请求头获取Authorization字段
2. 验证格式是否为 `jwt <token>`
3. 解码并验证JWT令牌
4. 提取userid并验证用户状态

**异常处理**：
- `Token has expired`：令牌已过期
- `Invalid token signature`：签名无效
- `Invalid token format`：格式错误
- `No credentials provided`：缺少凭证
- `Credentials string should not contain spaces`：凭证包含空格
- `Invalid token payload`：载荷无效
- `User not found`：用户不存在
- `User inactive or deleted`：用户非活跃或已删除

#### authenticate_credentials 方法

**功能**：根据userid验证用户

**流程**：
1. 接收userid（字符串类型，ShortUUID）
2. 查询OJUser模型（使用uid字段）
3. 验证用户是否活跃
4. 返回用户对象

## 用户模型注意事项

### OJUser 模型特点

- 主键字段：`uid`（ShortUUIDField）
- 不是传统的自增id
- 字符串类型主键
- 在JWT认证中必须使用uid而非id

## 使用示例

```python
# 生成令牌
token = get_token(user)

# 设置请求头
headers = {"Authorization": f"jwt {token}"}
```

## 安全配置

- 建议使用至少32字节长度的SECRET_KEY以满足HMAC安全要求
- 当前使用默认Django开发密钥，生产环境需更换

## 测试说明

- 所有单元测试位于 `tests/` 目录
- 测试覆盖了正常情况和各种异常场景
- 测试使用独立的数据库，不影响生产数据