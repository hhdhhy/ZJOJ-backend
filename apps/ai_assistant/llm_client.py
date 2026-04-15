"""
云端 LLM 客户端
支持智谱AI、通义千问等云端大语言模型
"""
from zhipuai import ZhipuAI
from django.conf import settings


class LLMClient:
    """云端 LLM 客户端（智谱AI）"""
    
    def __init__(self, api_key=None, model=None):
        """
        初始化 LLM 客户端
        
        Args:
            api_key: API密钥（默认从settings读取）
            model: 模型名称（默认glm-4）
        """
        self.api_key = api_key or getattr(settings, 'ZHIPU_API_KEY', '')
        self.model = model or getattr(settings, 'ZHIPU_MODEL', 'glm-4')
        
        if not self.api_key:
            raise ValueError("请配置 ZHIPU_API_KEY")
        
        self.client = ZhipuAI(api_key=self.api_key)
    
    def chat(self, messages: list, temperature=0.7, max_tokens=2000) -> dict:
        """
        调用 LLM API
        
        Args:
            messages: 消息列表 [{'role': 'user', 'content': '...'}, ...]
            temperature: 温度参数 (0-1)，越高越随机
            max_tokens: 最大生成token数
        
        Returns:
            {
                'answer': '生成的答案',
                'tokens_used': 消耗的token数,
                'model': '使用的模型'
            }
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                'answer': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'model': self.model
            }
        
        except Exception as e:
            raise Exception(f"LLM API调用失败: {str(e)}")
    
    def chat_simple(self, question: str, system_prompt: str = None) -> dict:
        """
        简化版对话接口
        
        Args:
            question: 用户问题
            system_prompt: 系统提示词（可选）
        
        Returns:
            同 chat() 方法
        """
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        
        # 添加用户问题
        messages.append({'role': 'user', 'content': question})
        
        return self.chat(messages)


# 测试代码
if __name__ == "__main__":
    import os
    import sys
    import django
    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ZJOJ.settings')
    django.setup()
    
    print("="*60)
    print("测试 LLM 客户端")
    print("="*60)
    
    try:
        # 检查是否配置了API Key
        from django.conf import settings
        api_key = getattr(settings, 'ZHIPU_API_KEY', '')
        
        if not api_key or api_key == 'your-api-key-here':
            print("\n⚠️  未配置 ZHIPU_API_KEY，跳过实际API调用测试")
            print("\n请在 settings.py 中配置：")
            print("  ZHIPU_API_KEY = '你的API密钥'")
            print("  ZHIPU_MODEL = 'glm-4'")
            print("\n获取API密钥：https://open.bigmodel.cn/")
        else:
            print("\n1. 测试简单对话...")
            client = LLMClient()
            result = client.chat_simple("什么是二分查找？")
            
            print(f"   ✅ API调用成功")
            print(f"   模型: {result['model']}")
            print(f"   Token消耗: {result['tokens_used']}")
            print(f"   答案预览: {result['answer'][:100]}...")
            
            print("\n2. 测试带系统提示词的对话...")
            result2 = client.chat_simple(
                question="快速排序的时间复杂度是多少？",
                system_prompt="你是一个算法竞赛助手，回答要简洁准确。"
            )
            
            print(f"   ✅ 带提示词调用成功")
            print(f"   Token消耗: {result2['tokens_used']}")
            print(f"   答案预览: {result2['answer'][:100]}...")
            
            print("\n" + "="*60)
            print("✅ 所有测试通过！")
            print("="*60)
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
