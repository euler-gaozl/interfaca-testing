#!/usr/bin/env python3
"""
快速框架功能验证
简单测试每个框架的基本功能
"""
import asyncio
import time
from src.agents.test_generator import TestCaseGeneratorAgent
from src.agents.autogen_agent import AutoGenMultiAgent
from src.agents.langchain_agent import LangChainTestAgent


async def quick_test_deepseek():
    """快速测试DeepSeek"""
    print("🧠 测试DeepSeek基础智能体...")
    
    try:
        agent = TestCaseGeneratorAgent("ollama")
        
        # 简单API规范
        api_spec = {
            "openapi": "3.0.0",
            "info": {"title": "测试API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {"summary": "测试端点"}
                }
            }
        }
        
        start_time = time.time()
        result = await agent.process({
            "project_id": 1,
            "api_spec": api_spec,
            "test_types": ["functional"],
            "max_cases_per_endpoint": 2
        })
        duration = time.time() - start_time
        
        success = result.get('success', False)
        test_count = len(result.get('test_cases', []))
        
        print(f"   ✅ DeepSeek: {success}, {test_count}个测试用例, {duration:.2f}秒")
        return {"framework": "DeepSeek", "success": success, "count": test_count, "duration": duration}
        
    except Exception as e:
        print(f"   ❌ DeepSeek失败: {e}")
        return {"framework": "DeepSeek", "success": False, "error": str(e)}


async def quick_test_langchain():
    """快速测试LangChain"""
    print("🔗 测试LangChain工具链智能体...")
    
    try:
        agent = LangChainTestAgent("ollama")
        
        # 简单API规范
        api_spec = {
            "openapi": "3.0.0",
            "info": {"title": "测试API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {"summary": "测试端点"}
                }
            }
        }
        
        start_time = time.time()
        result = await agent.process({
            "project_id": 1,
            "api_spec": api_spec,
            "test_types": ["functional"],
            "max_cases_per_endpoint": 2
        })
        duration = time.time() - start_time
        
        success = result.get('success', False)
        test_count = len(result.get('test_cases', []))
        tools_used = result.get('tools_used', [])
        
        print(f"   ✅ LangChain: {success}, {test_count}个测试用例, {duration:.2f}秒, 工具: {tools_used}")
        return {"framework": "LangChain", "success": success, "count": test_count, "duration": duration, "tools": tools_used}
        
    except Exception as e:
        print(f"   ❌ LangChain失败: {e}")
        return {"framework": "LangChain", "success": False, "error": str(e)}


async def quick_test_autogen():
    """快速测试AutoGen"""
    print("👥 测试AutoGen多智能体...")
    
    try:
        agent = AutoGenMultiAgent("ollama")
        
        # 简单API规范
        api_spec = {
            "openapi": "3.0.0",
            "info": {"title": "测试API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {"summary": "测试端点"}
                }
            }
        }
        
        start_time = time.time()
        result = await agent.process({
            "project_id": 1,
            "api_spec": api_spec,
            "test_types": ["functional"],
            "max_cases_per_endpoint": 2
        })
        duration = time.time() - start_time
        
        success = result.get('success', False)
        test_count = len(result.get('test_cases', []))
        agents = result.get('agents_involved', [])
        
        print(f"   ✅ AutoGen: {success}, {test_count}个测试用例, {duration:.2f}秒, 智能体: {agents}")
        return {"framework": "AutoGen", "success": success, "count": test_count, "duration": duration, "agents": agents}
        
    except Exception as e:
        print(f"   ❌ AutoGen失败: {e}")
        return {"framework": "AutoGen", "success": False, "error": str(e)}


async def main():
    """主测试流程"""
    print("🚀 快速框架功能验证")
    print("=" * 50)
    
    results = []
    
    # 并发测试所有框架
    tasks = [
        quick_test_deepseek(),
        quick_test_langchain(),
        quick_test_autogen()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\n📊 测试结果汇总:")
    print("-" * 30)
    
    successful = 0
    for result in results:
        if isinstance(result, dict) and result.get('success', False):
            successful += 1
            framework = result['framework']
            count = result.get('count', 0)
            duration = result.get('duration', 0)
            print(f"✅ {framework}: {count}个测试用例, {duration:.2f}秒")
        elif isinstance(result, dict):
            framework = result.get('framework', 'Unknown')
            error = result.get('error', 'Unknown error')
            print(f"❌ {framework}: {error}")
        else:
            print(f"❌ 异常: {result}")
    
    print(f"\n🎯 成功率: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    
    if successful > 0:
        print("✨ 至少有一个框架工作正常！")
    else:
        print("⚠️ 所有框架都遇到问题，请检查配置")


if __name__ == "__main__":
    asyncio.run(main())
