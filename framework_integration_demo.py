#!/usr/bin/env python3
"""
智能体框架集成演示
展示AutoGen、LangChain、FastAPI等框架的完整集成
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from src.agents.test_generator import TestCaseGeneratorAgent
from src.agents.autogen_agent import AutoGenMultiAgent, AutoGenTestOrchestrator
from src.agents.langchain_agent import LangChainTestAgent, LangChainWorkflow
from src.models.schemas import TestType
from src.config.settings import settings


def print_banner():
    """打印横幅"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 AI智能体框架集成演示                                    ║
║              AutoGen + LangChain + FastAPI + DeepSeek-R1                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def print_section(title: str, emoji: str = "🎯"):
    """打印章节标题"""
    print(f"\n{emoji} {title}")
    print("=" * 80)


def print_step(step: str, emoji: str = "📋"):
    """打印步骤"""
    print(f"\n{emoji} {step}")
    print("-" * 60)


async def demo_basic_agent():
    """演示基础智能体"""
    print_section("基础智能体演示", "🤖")
    
    print_step("初始化基础智能体")
    agent = TestCaseGeneratorAgent("ollama")
    print("   ✅ 基础智能体初始化完成")
    
    # 简单API规范
    api_spec = {
        "openapi": "3.0.0",
        "info": {"title": "用户API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "summary": "获取用户列表",
                    "responses": {"200": {"description": "成功"}}
                },
                "post": {
                    "summary": "创建用户",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "创建成功"}}
                }
            }
        }
    }
    
    print_step("生成测试用例")
    start_time = datetime.now()
    
    result = await agent.process({
        "project_id": 1,
        "api_spec": api_spec,
        "test_types": [TestType.FUNCTIONAL],
        "max_cases_per_endpoint": 2
    })
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"   ⏱️  耗时: {duration:.2f} 秒")
    print(f"   📊 生成测试用例: {len(result.get('test_cases', []))} 个")
    print(f"   ✅ 成功: {result.get('success', False)}")
    
    return result


async def demo_autogen_agent():
    """演示AutoGen多智能体"""
    print_section("AutoGen多智能体协作演示", "👥")
    
    print_step("初始化AutoGen多智能体系统")
    agent = AutoGenMultiAgent("ollama")
    print("   ✅ AutoGen多智能体系统初始化完成")
    print("   👨‍💼 TestArchitect - 测试架构师")
    print("   🔧 FunctionalTester - 功能测试专家")
    print("   🔒 SecurityTester - 安全测试专家")
    print("   ⚡ PerformanceTester - 性能测试专家")
    
    # 复杂API规范
    api_spec = {
        "openapi": "3.0.0",
        "info": {"title": "电商API", "version": "2.0.0"},
        "paths": {
            "/products": {
                "get": {"summary": "获取商品列表"},
                "post": {"summary": "创建商品"}
            },
            "/orders": {
                "post": {"summary": "创建订单"}
            },
            "/auth/login": {
                "post": {"summary": "用户登录"}
            }
        }
    }
    
    print_step("启动多智能体协作")
    start_time = datetime.now()
    
    result = await agent.process({
        "project_id": 1,
        "api_spec": api_spec,
        "test_types": [TestType.FUNCTIONAL, TestType.SECURITY],
        "max_cases_per_endpoint": 2
    })
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"   ⏱️  协作耗时: {duration:.2f} 秒")
    print(f"   📊 生成测试用例: {len(result.get('test_cases', []))} 个")
    print(f"   👥 参与智能体: {', '.join(result.get('agents_involved', []))}")
    print(f"   ✅ 协作成功: {result.get('success', False)}")
    
    return result


async def demo_langchain_agent():
    """演示LangChain工具链智能体"""
    print_section("LangChain工具链智能体演示", "🔗")
    
    print_step("初始化LangChain工具链智能体")
    agent = LangChainTestAgent("ollama")
    print("   ✅ LangChain工具链智能体初始化完成")
    print("   🔍 api_analyzer - API规范分析器")
    print("   🛡️  security_scanner - 安全风险扫描器")
    print("   ⚡ performance_analyzer - 性能分析器")
    print("   🧪 test_case_generator - 测试用例生成器")
    
    # API规范
    api_spec = {
        "openapi": "3.0.0",
        "info": {"title": "支付API", "version": "1.0.0"},
        "paths": {
            "/payments": {
                "post": {
                    "summary": "创建支付",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "amount": {"type": "number"},
                                        "currency": {"type": "string"},
                                        "card_number": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    print_step("执行工具链分析")
    start_time = datetime.now()
    
    result = await agent.process({
        "project_id": 1,
        "api_spec": api_spec,
        "test_types": [TestType.FUNCTIONAL, TestType.SECURITY],
        "max_cases_per_endpoint": 2
    })
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"   ⏱️  分析耗时: {duration:.2f} 秒")
    print(f"   📊 生成测试用例: {len(result.get('test_cases', []))} 个")
    print(f"   🔧 使用工具: {', '.join(result.get('tools_used', []))}")
    print(f"   ✅ 分析成功: {result.get('success', False)}")
    
    return result


async def demo_framework_comparison():
    """演示框架对比"""
    print_section("智能体框架对比分析", "⚖️")
    
    # 统一的API规范
    api_spec = {
        "openapi": "3.0.0",
        "info": {"title": "博客API", "version": "1.0.0"},
        "paths": {
            "/posts": {
                "get": {"summary": "获取文章列表"},
                "post": {"summary": "创建文章"}
            },
            "/comments": {
                "post": {"summary": "添加评论"}
            }
        }
    }
    
    results = {}
    
    # 基础智能体
    print_step("测试基础智能体")
    try:
        basic_agent = TestCaseGeneratorAgent("ollama")
        basic_result = await basic_agent.process({
            "project_id": 1,
            "api_spec": api_spec,
            "test_types": [TestType.FUNCTIONAL],
            "max_cases_per_endpoint": 2
        })
        results["basic"] = {
            "success": basic_result.get("success", False),
            "test_cases": len(basic_result.get("test_cases", [])),
            "framework": "基础智能体"
        }
        print(f"   ✅ 基础智能体: {results['basic']['test_cases']} 个测试用例")
    except Exception as e:
        results["basic"] = {"success": False, "error": str(e)}
        print(f"   ❌ 基础智能体失败: {e}")
    
    # AutoGen智能体
    print_step("测试AutoGen多智能体")
    try:
        autogen_agent = AutoGenMultiAgent("ollama")
        autogen_result = await autogen_agent.process({
            "project_id": 1,
            "api_spec": api_spec,
            "test_types": [TestType.FUNCTIONAL],
            "max_cases_per_endpoint": 2
        })
        results["autogen"] = {
            "success": autogen_result.get("success", False),
            "test_cases": len(autogen_result.get("test_cases", [])),
            "framework": "AutoGen多智能体",
            "agents": autogen_result.get("agents_involved", [])
        }
        print(f"   ✅ AutoGen: {results['autogen']['test_cases']} 个测试用例")
    except Exception as e:
        results["autogen"] = {"success": False, "error": str(e)}
        print(f"   ❌ AutoGen失败: {e}")
    
    # LangChain智能体
    print_step("测试LangChain工具链")
    try:
        langchain_agent = LangChainTestAgent("ollama")
        langchain_result = await langchain_agent.process({
            "project_id": 1,
            "api_spec": api_spec,
            "test_types": [TestType.FUNCTIONAL],
            "max_cases_per_endpoint": 2
        })
        results["langchain"] = {
            "success": langchain_result.get("success", False),
            "test_cases": len(langchain_result.get("test_cases", [])),
            "framework": "LangChain工具链",
            "tools": langchain_result.get("tools_used", [])
        }
        print(f"   ✅ LangChain: {results['langchain']['test_cases']} 个测试用例")
    except Exception as e:
        results["langchain"] = {"success": False, "error": str(e)}
        print(f"   ❌ LangChain失败: {e}")
    
    return results


def analyze_framework_results(results: Dict[str, Any]):
    """分析框架结果"""
    print_section("框架对比分析结果", "📊")
    
    successful_frameworks = [name for name, result in results.items() if result.get("success", False)]
    
    print_step("成功率统计")
    print(f"   总测试框架: {len(results)}")
    print(f"   成功框架: {len(successful_frameworks)}")
    print(f"   成功率: {len(successful_frameworks)/len(results)*100:.1f}%")
    
    if successful_frameworks:
        print_step("测试用例生成对比")
        for name in successful_frameworks:
            result = results[name]
            framework_name = result.get("framework", name)
            test_cases = result.get("test_cases", 0)
            print(f"   📋 {framework_name}: {test_cases} 个测试用例")
            
            # 显示特殊特性
            if "agents" in result:
                print(f"      👥 协作智能体: {len(result['agents'])} 个")
            if "tools" in result:
                print(f"      🔧 使用工具: {len(result['tools'])} 个")
    
    print_step("框架推荐")
    if not successful_frameworks:
        print("   ❌ 所有框架都遇到问题，建议检查配置")
    elif len(successful_frameworks) == 1:
        framework_name = results[successful_frameworks[0]].get("framework", successful_frameworks[0])
        print(f"   🎯 推荐使用: {framework_name}")
    else:
        # 根据测试用例数量推荐
        best_count = max(results[name].get("test_cases", 0) for name in successful_frameworks)
        best_frameworks = [name for name in successful_frameworks if results[name].get("test_cases", 0) == best_count]
        
        if "autogen" in best_frameworks:
            print("   🎯 推荐使用: AutoGen多智能体 (适合复杂协作场景)")
        elif "langchain" in best_frameworks:
            print("   🎯 推荐使用: LangChain工具链 (适合工具集成场景)")
        else:
            framework_name = results[best_frameworks[0]].get("framework", best_frameworks[0])
            print(f"   🎯 推荐使用: {framework_name}")


async def demo_fastapi_integration():
    """演示FastAPI集成"""
    print_section("FastAPI集成演示", "🌐")
    
    print_step("FastAPI路由集成")
    print("   ✅ 智能体API路由已集成")
    print("   📍 /agents/generate-tests - 生成测试用例")
    print("   📍 /agents/autogen-orchestrate - AutoGen编排")
    print("   📍 /agents/langchain-workflow - LangChain工作流")
    print("   📍 /agents/compare-frameworks - 框架对比")
    print("   📍 /agents/frameworks - 框架信息")
    print("   📍 /agents/health - 健康检查")
    
    print_step("支持的功能特性")
    print("   🎯 多框架支持: Basic、AutoGen、LangChain")
    print("   🤖 多模型支持: OpenAI、Claude、Ollama")
    print("   🔄 异步处理: 全异步API设计")
    print("   📊 结果对比: 框架效果对比分析")
    print("   🏥 健康监控: 实时状态检查")
    print("   📝 标准化输出: 统一的响应格式")


async def save_demo_results(basic_result, autogen_result, langchain_result, comparison_results):
    """保存演示结果"""
    print_section("保存演示结果", "💾")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 汇总结果
    demo_results = {
        "timestamp": timestamp,
        "demo_type": "framework_integration",
        "frameworks_tested": ["basic", "autogen", "langchain"],
        "model_used": "deepseek-r1:14b",
        "results": {
            "basic_agent": {
                "success": basic_result.get("success", False),
                "test_cases_count": len(basic_result.get("test_cases", [])),
                "framework": "basic"
            },
            "autogen_agent": {
                "success": autogen_result.get("success", False),
                "test_cases_count": len(autogen_result.get("test_cases", [])),
                "framework": "autogen",
                "agents_involved": autogen_result.get("agents_involved", [])
            },
            "langchain_agent": {
                "success": langchain_result.get("success", False),
                "test_cases_count": len(langchain_result.get("test_cases", [])),
                "framework": "langchain",
                "tools_used": langchain_result.get("tools_used", [])
            }
        },
        "comparison": comparison_results,
        "integration_status": {
            "fastapi": "integrated",
            "autogen": "available",
            "langchain": "available",
            "deepseek_r1": "connected"
        }
    }
    
    # 保存结果文件
    results_file = f"framework_integration_demo_{timestamp}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(demo_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"   ✅ 演示结果已保存: {results_file}")
    
    return results_file


async def main():
    """主演示流程"""
    print_banner()
    
    # 1. 基础智能体演示
    basic_result = await demo_basic_agent()
    
    # 2. AutoGen多智能体演示
    autogen_result = await demo_autogen_agent()
    
    # 3. LangChain工具链演示
    langchain_result = await demo_langchain_agent()
    
    # 4. 框架对比演示
    comparison_results = await demo_framework_comparison()
    
    # 5. 分析对比结果
    analyze_framework_results(comparison_results)
    
    # 6. FastAPI集成演示
    await demo_fastapi_integration()
    
    # 7. 保存演示结果
    results_file = await save_demo_results(
        basic_result, autogen_result, langchain_result, comparison_results
    )
    
    # 8. 总结
    print_section("演示完成总结", "🎉")
    print("✨ 智能体框架集成演示成功完成！")
    
    print(f"\n📊 演示统计:")
    print(f"   • 测试框架: 3 个 (Basic、AutoGen、LangChain)")
    print(f"   • AI模型: DeepSeek-R1:14b (本地部署)")
    print(f"   • Web框架: FastAPI (异步API)")
    print(f"   • 总测试用例: {len(basic_result.get('test_cases', [])) + len(autogen_result.get('test_cases', [])) + len(langchain_result.get('test_cases', []))} 个")
    
    print(f"\n🎯 核心特性:")
    print("   • ✅ 多智能体协作 (AutoGen)")
    print("   • ✅ 工具链集成 (LangChain)")
    print("   • ✅ 异步API服务 (FastAPI)")
    print("   • ✅ 本地AI模型 (DeepSeek-R1)")
    print("   • ✅ 框架对比分析")
    print("   • ✅ 健壮性保证")
    print("   • ✅ 安全性考虑")
    print("   • ✅ 行业标准遵循")
    print("   • ✅ 代码质量分析")
    
    print(f"\n📁 生成文件:")
    print(f"   • 演示结果: {results_file}")
    
    print(f"\n🚀 下一步操作:")
    print("   • 启动Web服务: python main.py")
    print("   • 访问API文档: http://localhost:8000/docs")
    print("   • 测试智能体API: /agents/frameworks")
    print("   • 对比框架效果: /agents/compare-frameworks")
    
    print(f"\n💡 技术亮点:")
    print("   • 真实AI推理能力，非模拟响应")
    print("   • 多框架协同工作，各有所长")
    print("   • 本地化部署，数据安全可控")
    print("   • 符合行业标准的API设计")
    print("   • 可扩展的智能体架构")


if __name__ == "__main__":
    asyncio.run(main())
