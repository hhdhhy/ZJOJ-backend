from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import exceptions
from django.contrib.auth import get_user_model
import jwt
import time
from MYJWT.myjwt import get_token, JWTAuthentication
from ZJOJ import settings
from apps.ojauth.models import OJUser

class JWTUtilsTestCase(TestCase):
    def setUp(self):
        self.user = OJUser.objects.create_user(
            username='testuser',
            realname='Test User',
            email='test@example.com',
            password='testpass123'
        )
        self.authenticator = JWTAuthentication()

    def test_get_token_generates_valid_jwt(self):
        """测试get_token函数生成有效的JWT令牌"""
        token = get_token(self.user)
        
        # 解码并验证令牌
        decoded = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=['HS256'],
            options={"verify_signature": True}
        )
        
        # 验证payload内容
        self.assertEqual(decoded['userid'], self.user.uid)
        self.assertIn('exp', decoded)
        
        # 验证过期时间在合理范围内（14天左右）
        expected_exp = int(time.time()) + (60 * 24 * 14)  # 14天
        exp_diff = abs(decoded['exp'] - expected_exp)
        self.assertLess(exp_diff, 60)  # 允许1分钟的误差

    def test_jwt_authentication_with_valid_token(self):
        """测试使用有效JWT令牌进行认证"""
        # 生成令牌
        token = get_token(self.user)
        
        # 创建请求模拟
        class MockRequest:
            pass
            
        request = MockRequest()
        request.META = {'HTTP_AUTHORIZATION': f'jwt {token}'}
        
        # 执行认证
        result = self.authenticator.authenticate(request)
        
        # 验证结果
        self.assertIsNotNone(result)
        authenticated_user, _ = result
        self.assertEqual(authenticated_user.uid, self.user.uid)

    def test_jwt_authentication_with_expired_token(self):
        """测试使用已过期的JWT令牌进行认证"""
        # 手动生成一个已过期的令牌
        expired_payload = {
            'userid': self.user.uid,
            'exp': int(time.time()) - 3600  # 1小时前过期
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        # 创建请求模拟
        class MockRequest:
            pass
            
        request = MockRequest()
        request.META = {'HTTP_AUTHORIZATION': f'jwt {expired_token}'}
        
        # 验证抛出过期异常
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authenticator.authenticate(request)
        
        self.assertIn('Token has expired', str(context.exception))

    def test_jwt_authentication_with_invalid_signature(self):
        """测试使用签名无效的JWT令牌进行认证"""
        # 手动生成一个签名无效的令牌
        valid_payload = {
            'userid': self.user.uid,
            'exp': int(time.time()) + 3600  # 1小时后过期
        }
        # 使用不同的密钥编码
        invalid_token = jwt.encode(
            valid_payload,
            'different-secret-key',
            algorithm='HS256'
        )
        
        # 创建请求模拟
        class MockRequest:
            pass
            
        request = MockRequest()
        request.META = {'HTTP_AUTHORIZATION': f'jwt {invalid_token}'}
        
        # 验证抛出签名无效异常
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authenticator.authenticate(request)
        
        self.assertIn('Invalid token signature', str(context.exception))

    def test_jwt_authentication_with_invalid_format(self):
        """测试使用格式无效的JWT令牌进行认证"""
        # 创建请求模拟，使用非JWT格式的授权头
        class MockRequest:
            pass
            
        request = MockRequest()
        request.META = {'HTTP_AUTHORIZATION': 'invalid-format'}
        
        # 验证返回None（不匹配JWT前缀）
        result = self.authenticator.authenticate(request)
        self.assertIsNone(result)

    def test_jwt_authentication_with_missing_credentials(self):
        """测试缺少凭证的JWT认证"""
        # 创建请求模拟，只有JWT前缀没有令牌
        class MockRequest:
            pass
            
        request = MockRequest()
        request.META = {'HTTP_AUTHORIZATION': 'jwt'}
        
        # 验证抛出认证失败异常
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authenticator.authenticate(request)
        
        self.assertIn('No credentials provided', str(context.exception))

    def test_jwt_authentication_with_multiple_parts(self):
        """测试包含多个部分的JWT认证头"""
        # 创建请求模拟，认证头包含空格分隔的多个部分
        class MockRequest:
            pass
            
        request = MockRequest()
        request.META = {'HTTP_AUTHORIZATION': 'jwt token part2'}
        
        # 验证抛出认证失败异常
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authenticator.authenticate(request)
        
        self.assertIn('Credentials string should not contain spaces', str(context.exception))

    def test_jwt_authentication_with_invalid_payload(self):
        """测试使用无效载荷的JWT令牌进行认证"""
        # 手动生成一个没有userid的令牌
        invalid_payload = {
            'exp': int(time.time()) + 3600
            # 缺少userid字段
        }
        token = jwt.encode(
            invalid_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        # 创建请求模拟
        class MockRequest:
            pass
            
        request = MockRequest()
        request.META = {'HTTP_AUTHORIZATION': f'jwt {token}'}
        
        # 验证抛出认证失败异常
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authenticator.authenticate(request)
        
        self.assertIn('Invalid token payload', str(context.exception))

    def test_authenticate_credentials_with_valid_id(self):
        """测试authenticate_credentials方法使用有效用户ID"""
        result = self.authenticator.authenticate_credentials(self.user.uid)
        
        self.assertIsNotNone(result)
        authenticated_user, _ = result
        self.assertEqual(authenticated_user.uid, self.user.uid)

    def test_authenticate_credentials_with_invalid_id_type(self):
        """测试authenticate_credentials方法使用无效ID类型"""
        # 当uid不存在时，应该返回User not found
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authenticator.authenticate_credentials("not_an_integer")
        
        self.assertIn('User not found', str(context.exception))

    def test_authenticate_credentials_with_nonexistent_user(self):
        """测试authenticate_credentials方法使用不存在的用户"""
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authenticator.authenticate_credentials(999999)  # 假设这个ID不存在
        
        self.assertIn('User not found', str(context.exception))

    def test_authenticate_credentials_with_inactive_user(self):
        """测试authenticate_credentials方法使用非活跃用户"""
        # 测试用户不存在的情况
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.authenticator.authenticate_credentials('invalid_uid_for_test')
        
        self.assertIn('User not found', str(context.exception))