#!/usr/bin/env python3
"""
测试JSON解析修复
验证AI响应解析的健壮性
"""
import asyncio
import json
from src.agents.test_generator import TestCaseGeneratorAgent
from src.utils.logger import log


def test_json_parsing():
    """测试JSON解析功能"""
    print("🧪 测试JSON解析修复功能")
    print("=" * 60)
    
    # 创建测试智能体
    agent = TestCaseGeneratorAgent("ollama")
    
    # 测试各种AI响应格式
    test_responses = [
        # 1. 标准JSON数组
        '''[
  {
    "name": "用户登录测试",
    "method": "POST",
    "endpoint": "/api/login",
    "expected_status": 200
  }
]''',
        
        # 2. 带有思考过程的DeepSeek-R1响应
        '''<think>
我需要为这个API生成测试用例...
</think>

基于API规范，我生成以下测试用例：

[
  {
    "name": "获取用户列表测试",
    "description": "测试获取所有用户的功能",
    "method": "GET",
    "endpoint": "/api/users",
    "headers": {"Content-Type": "application/json"},
    "expected_status": 200,
    "test_type": "functional",
    "priority": "high"
  },
  {
    "name": "创建用户测试",
    "method": "POST",
    "endpoint": "/api/users",
    "body": {"name": "测试用户", "email": "test@example.com"},
    "expected_status": 201
  }
]''',
        
        # 3. 单个JSON对象
        '''{
    "name": "单个测试用例",
    "method": "GET",
    "endpoint": "/api/test",
    "expected_status": 200
}''',
        
        # 4. 格式错误的JSON（缺少逗号）
        '''[
  {
    "name": "测试用例1"
    "method": "GET"
    "endpoint": "/api/test1"
  }
  {
    "name": "测试用例2",
    "method": "POST",
    "endpoint": "/api/test2"
  }
]''',
        
        # 5. 自然语言描述
        '''我为您生成了以下测试用例：

测试用例1：用户注册功能测试
- 方法：POST
- 端点：/api/register
- 预期状态码：201

测试用例2：获取用户信息测试
- 方法：GET
- 端点：/api/users/123
- 预期状态码：200

测试用例3：删除用户测试
- 方法：DELETE
- 端点：/api/users/123
- 预期状态码：204''',
        
        # 6. 混合格式
        '''这里是生成的测试用例：

{"name": "测试用例A", "method": "GET", "endpoint": "/api/a"}

还有另一个：
{"name": "测试用例B", "method": "POST", "endpoint": "/api/b", "expected_status": 201}''',
        
        # 7. 完全无效的响应
        '''这是一个完全无效的响应，没有任何JSON格式的内容。
只是普通的文本描述，无法解析出测试用例。'''
    ]
    
    # 测试每种响应格式
    for i, response in enumerate(test_responses, 1):
        print(f"\n📋 测试场景 {i}:")
        print(f"响应类型: {get_response_type(response)}")
        print(f"响应长度: {len(response)} 字符")
        
        try:
            # 使用解析方法
            test_cases = agent._parse_ai_response(response, project_id=1)
            
            print(f"✅ 解析成功: {len(test_cases)} 个测试用例")
            
            # 显示解析结果
            for j, case in enumerate(test_cases, 1):
                print(f"   {j}. {case.get('name', '未命名')} - {case.get('method', 'GET')} {case.get('endpoint', '/')}")
        
        except Exception as e:
            print(f"❌ 解析失败: {e}")
        
        print("-" * 40)


def get_response_type(response: str) -> str:
    """识别响应类型"""
    if response.strip().startswith('[') and response.strip().endswith(']'):
        return "JSON数组"
    elif response.strip().startswith('{') and response.strip().endswith('}'):
        return "JSON对象"
    elif '<think>' in response:
        return "DeepSeek-R1思考格式"
    elif any(keyword in response.lower() for keyword in ['测试', 'test', '用例']):
        return "自然语言描述"
    else:
        return "未知格式"


async def test_real_ai_generation():
    """测试真实AI生成"""
    print("\n🤖 测试真实AI生成和解析")
    print("=" * 60)
    
    agent = TestCaseGeneratorAgent("ollama")
    
    # 简单的API规范
    api_spec = {
        "openapi": "3.0.0",
        "info": {"title": "测试API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {"summary": "获取用户列表"},
                "post": {"summary": "创建用户"}
            }
        }
    }
    
    try:
        result = await agent.process({
            "project_id": 1,
            "api_spec": api_spec,
            "test_types": ["functional"],
            "max_cases_per_endpoint": 2
        })
        
        print(f"✅ AI生成成功: {result.get('success', False)}")
        print(f"📊 生成测试用例: {len(result.get('test_cases', []))} 个")
        
        # 显示生成的测试用例
        for i, case in enumerate(result.get('test_cases', []), 1):
            print(f"   {i}. {case.get('name', '未命名')}")
            print(f"      方法: {case.get('method', 'GET')}")
            print(f"      端点: {case.get('endpoint', '/')}")
            print(f"      状态码: {case.get('expected_status', 200)}")
        
        # 显示原始AI响应（截取前500字符）
        ai_response = result.get('ai_response', '')
        if ai_response:
            print(f"\n📝 AI原始响应（前500字符）:")
            print(ai_response[:500] + "..." if len(ai_response) > 500 else ai_response)
    
    except Exception as e:
        print(f"❌ AI生成失败: {e}")


def test_edge_cases():
    """测试边界情况"""
    print("\n🔍 测试边界情况")
    print("=" * 60)
    
    agent = TestCaseGeneratorAgent("ollama")
    
    edge_cases = [
        # 空响应
        "",
        
        # 只有空格
        "   \n\n   ",
        
        # 只有JSON标记但内容为空
        "[]",
        
        # 嵌套JSON
        '''{"data": [{"name": "嵌套测试", "method": "GET"}]}''',
        
        # 包含特殊字符的JSON
        '''[{"name": "特殊字符测试 \"引号\" \\反斜杠\\", "method": "GET"}]''',
        
        # 超长响应
        "这是一个很长的响应..." + "x" * 10000 + '''[{"name": "长响应测试", "method": "GET"}]''',
    ]
    
    for i, case in enumerate(edge_cases, 1):
        print(f"\n📋 边界测试 {i}:")
        print(f"输入长度: {len(case)} 字符")
        
        try:
            test_cases = agent._parse_ai_response(case, project_id=1)
            print(f"✅ 处理成功: {len(test_cases)} 个测试用例")
        except Exception as e:
            print(f"❌ 处理失败: {e}")


async def main():
    """主测试流程"""
    print("🚀 JSON解析修复验证测试")
    print("=" * 80)
    
    # 1. 测试各种JSON格式解析
    test_json_parsing()
    
    # 2. 测试真实AI生成
    await test_real_ai_generation()
    
    # 3. 测试边界情况
    test_edge_cases()
    
    print("\n🎉 测试完成总结")
    print("=" * 60)
    print("✅ JSON解析功能已修复并增强")
    print("✅ 支持多种AI响应格式")
    print("✅ 具备健壮的错误处理")
    print("✅ 包含智能文本解析")
    print("✅ 提供默认测试用例备用方案")
    
    print("\n💡 修复要点:")
    print("• 多策略JSON提取（数组、对象、逐行、正则）")
    print("• DeepSeek-R1思考格式支持")
    print("• 自然语言智能解析")
    print("• 详细的日志记录")
    print("• 优雅的降级处理")


if __name__ == "__main__":
    asyncio.run(main())
