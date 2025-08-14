#!/usr/bin/env python3
"""
简化的DeepSeek-R1测试脚本
"""
import asyncio
import json
from src.agents.base_agent import OllamaClient

async def simple_test():
    """简单测试DeepSeek-R1"""
    print("🤖 测试DeepSeek-R1简单对话...")
    
    client = OllamaClient("http://localhost:11434", "deepseek-r1:14b")
    
    # 简单的测试提示
    messages = [
        {
            "role": "user", 
            "content": """请为以下API生成一个简单的测试用例，返回JSON格式：

API: POST /users/register
功能: 用户注册
参数: username, email, password

请返回格式：
{
  "name": "测试名称",
  "method": "POST",
  "endpoint": "/users/register",
  "body": {"username": "test", "email": "test@example.com", "password": "password123"}
}"""
        }
    ]
    
    try:
        response = await client.chat_completion(messages, temperature=0.3, max_tokens=500)
        print(f"✅ 响应成功，长度: {len(response)}")
        print(f"📝 响应内容:\n{response}")
        
        # 尝试提取JSON
        if '{' in response and '}' in response:
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            try:
                parsed = json.loads(json_str)
                print(f"✅ JSON解析成功: {parsed}")
            except:
                print(f"❌ JSON解析失败")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    await client.client.aclose()

if __name__ == "__main__":
    asyncio.run(simple_test())
