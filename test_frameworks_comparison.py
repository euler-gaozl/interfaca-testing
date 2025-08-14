#!/usr/bin/env python3
"""
智能体框架对比测试
分别测试DeepSeek、LangChain、AutoGen的效果
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

from src.agents.test_generator import TestCaseGeneratorAgent
from src.agents.autogen_agent import AutoGenMultiAgent
from src.agents.langchain_agent import LangChainTestAgent
from src.utils.logger import log


def print_banner():
    """打印横幅"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔬 智能体框架对比测试                                      ║
║                DeepSeek vs LangChain vs AutoGen                             ║
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


async def test_deepseek_framework():
    """测试DeepSeek基础框架"""
    print_section("DeepSeek基础智能体测试", "🧠")
    
    print_step("初始化DeepSeek智能体")
    agent = TestCaseGeneratorAgent("ollama")
    print("   ✅ DeepSeek-R1:14b 智能体初始化完成")
    print("   🎯 特性: 思考推理、中文优化、本地部署")
    
    # 测试API规范
    api_spec = {
        "openapi": "3.0.0",
        "info": {"title": "电商API", "version": "1.0.0"},
        "paths": {
            "/products": {
                "get": {
                    "summary": "获取商品列表",
                    "parameters": [
                        {"name": "category", "in": "query", "schema": {"type": "string"}},
                        {"name": "limit", "in": "query", "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": {"description": "成功"}}
                },
                "post": {
                    "summary": "创建商品",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "price": {"type": "number"},
                                        "category": {"type": "string"}
                                    },
                                    "required": ["name", "price"]
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "创建成功"}}
                }
            },
            "/orders": {
                "post": {
                    "summary": "创建订单",
                    "security": [{"bearerAuth": []}],
                    "responses": {"201": {"description": "订单创建成功"}}
                }
            }
        }
    }
    
    print_step("DeepSeek生成测试用例")
    start_time = time.time()
    
    try:
        result = await agent.process({
            "project_id": 1,
            "api_spec": api_spec,
            "test_types": ["functional", "security"],
            "max_cases_per_endpoint": 3
        })
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   ⏱️  生成耗时: {duration:.2f} 秒")
        print(f"   📊 生成测试用例: {len(result.get('test_cases', []))} 个")
        print(f"   ✅ 生成成功: {result.get('success', False)}")
        
        # 分析测试用例质量
        test_cases = result.get('test_cases', [])
        if test_cases:
            print_step("DeepSeek测试用例质量分析")
            analyze_test_cases(test_cases, "DeepSeek")
        
        return {
            "framework": "DeepSeek",
            "success": result.get('success', False),
            "test_cases_count": len(test_cases),
            "duration": duration,
            "test_cases": test_cases,
            "ai_response_length": len(result.get('ai_response', '')),
            "features": ["思考推理", "中文优化", "本地部署", "快速响应"]
        }
        
    except Exception as e:
        print(f"   ❌ DeepSeek测试失败: {e}")
        return {
            "framework": "DeepSeek",
            "success": False,
            "error": str(e),
            "test_cases_count": 0,
            "duration": 0
        }


async def test_langchain_framework():
    """测试LangChain框架"""
    print_section("LangChain工具链智能体测试", "🔗")
    
    print_step("初始化LangChain智能体")
    agent = LangChainTestAgent("ollama")
    print("   ✅ LangChain工具链智能体初始化完成")
    print("   🔧 工具: api_analyzer, security_scanner, performance_analyzer, test_case_generator")
    print("   🎯 特性: 工具链集成、模块化分析、可扩展架构")
    
    # 使用相同的API规范进行对比
    api_spec = {
        "openapi": "3.0.0",
        "info": {"title": "电商API", "version": "1.0.0"},
        "paths": {
            "/products": {
                "get": {
                    "summary": "获取商品列表",
                    "parameters": [
                        {"name": "category", "in": "query", "schema": {"type": "string"}},
                        {"name": "limit", "in": "query", "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": {"description": "成功"}}
                },
                "post": {
                    "summary": "创建商品",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "price": {"type": "number"},
                                        "category": {"type": "string"}
                                    },
                                    "required": ["name", "price"]
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "创建成功"}}
                }
            },
            "/orders": {
                "post": {
                    "summary": "创建订单",
                    "security": [{"bearerAuth": []}],
                    "responses": {"201": {"description": "订单创建成功"}}
                }
            }
        }
    }
    
    print_step("LangChain工具链分析")
    start_time = time.time()
    
    try:
        result = await agent.process({
            "project_id": 1,
            "api_spec": api_spec,
            "test_types": ["functional", "security"],
            "max_cases_per_endpoint": 3
        })
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   ⏱️  分析耗时: {duration:.2f} 秒")
        print(f"   📊 生成测试用例: {len(result.get('test_cases', []))} 个")
        print(f"   🔧 使用工具: {', '.join(result.get('tools_used', []))}")
        print(f"   ✅ 分析成功: {result.get('success', False)}")
        
        # 分析测试用例质量
        test_cases = result.get('test_cases', [])
        if test_cases:
            print_step("LangChain测试用例质量分析")
            analyze_test_cases(test_cases, "LangChain")
        
        return {
            "framework": "LangChain",
            "success": result.get('success', False),
            "test_cases_count": len(test_cases),
            "duration": duration,
            "test_cases": test_cases,
            "tools_used": result.get('tools_used', []),
            "features": ["工具链集成", "模块化分析", "可扩展架构", "专业工具"]
        }
        
    except Exception as e:
        print(f"   ❌ LangChain测试失败: {e}")
        return {
            "framework": "LangChain",
            "success": False,
            "error": str(e),
            "test_cases_count": 0,
            "duration": 0
        }


async def test_autogen_framework():
    """测试AutoGen框架"""
    print_section("AutoGen多智能体协作测试", "👥")
    
    print_step("初始化AutoGen多智能体")
    agent = AutoGenMultiAgent("ollama")
    print("   ✅ AutoGen多智能体系统初始化完成")
    print("   👨‍💼 TestArchitect: 测试架构师")
    print("   🔧 FunctionalTester: 功能测试专家")
    print("   🔒 SecurityTester: 安全测试专家")
    print("   ⚡ PerformanceTester: 性能测试专家")
    print("   🎯 特性: 多智能体协作、专业分工、群体智能")
    
    # 使用相同的API规范进行对比
    api_spec = {
        "openapi": "3.0.0",
        "info": {"title": "电商API", "version": "1.0.0"},
        "paths": {
            "/products": {
                "get": {
                    "summary": "获取商品列表",
                    "parameters": [
                        {"name": "category", "in": "query", "schema": {"type": "string"}},
                        {"name": "limit", "in": "query", "schema": {"type": "integer"}}
                    ],
                    "responses": {"200": {"description": "成功"}}
                },
                "post": {
                    "summary": "创建商品",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "price": {"type": "number"},
                                        "category": {"type": "string"}
                                    },
                                    "required": ["name", "price"]
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "创建成功"}}
                }
            },
            "/orders": {
                "post": {
                    "summary": "创建订单",
                    "security": [{"bearerAuth": []}],
                    "responses": {"201": {"description": "订单创建成功"}}
                }
            }
        }
    }
    
    print_step("AutoGen多智能体协作")
    start_time = time.time()
    
    try:
        result = await agent.process({
            "project_id": 1,
            "api_spec": api_spec,
            "test_types": ["functional", "security"],
            "max_cases_per_endpoint": 3
        })
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   ⏱️  协作耗时: {duration:.2f} 秒")
        print(f"   📊 生成测试用例: {len(result.get('test_cases', []))} 个")
        print(f"   👥 参与智能体: {', '.join(result.get('agents_involved', []))}")
        print(f"   ✅ 协作成功: {result.get('success', False)}")
        
        # 分析测试用例质量
        test_cases = result.get('test_cases', [])
        if test_cases:
            print_step("AutoGen测试用例质量分析")
            analyze_test_cases(test_cases, "AutoGen")
        
        return {
            "framework": "AutoGen",
            "success": result.get('success', False),
            "test_cases_count": len(test_cases),
            "duration": duration,
            "test_cases": test_cases,
            "agents_involved": result.get('agents_involved', []),
            "features": ["多智能体协作", "专业分工", "群体智能", "协同决策"]
        }
        
    except Exception as e:
        print(f"   ❌ AutoGen测试失败: {e}")
        return {
            "framework": "AutoGen",
            "success": False,
            "error": str(e),
            "test_cases_count": 0,
            "duration": 0
        }


def analyze_test_cases(test_cases: list, framework_name: str):
    """分析测试用例质量"""
    if not test_cases:
        print("   ❌ 无测试用例可分析")
        return
    
    # 统计分析
    methods = {}
    test_types = {}
    priorities = {}
    endpoints = set()
    
    for case in test_cases:
        # HTTP方法统计
        method = case.get('method', 'GET')
        methods[method] = methods.get(method, 0) + 1
        
        # 测试类型统计
        test_type = case.get('test_type', 'functional')
        test_types[test_type] = test_types.get(test_type, 0) + 1
        
        # 优先级统计
        priority = case.get('priority', 'medium')
        priorities[priority] = priorities.get(priority, 0) + 1
        
        # 端点统计
        endpoint = case.get('endpoint', '/')
        endpoints.add(endpoint)
    
    print(f"   📊 测试用例总数: {len(test_cases)}")
    print(f"   🎯 覆盖端点: {len(endpoints)} 个")
    print(f"   🔧 HTTP方法分布: {dict(methods)}")
    print(f"   📋 测试类型分布: {dict(test_types)}")
    print(f"   ⭐ 优先级分布: {dict(priorities)}")
    
    # 质量评分
    quality_score = calculate_quality_score(test_cases)
    print(f"   🏆 质量评分: {quality_score:.1f}/10.0")
    
    # 显示前3个测试用例示例
    print(f"   📝 测试用例示例:")
    for i, case in enumerate(test_cases[:3], 1):
        name = case.get('name', '未命名')[:40]
        method = case.get('method', 'GET')
        endpoint = case.get('endpoint', '/')
        print(f"      {i}. {name} - {method} {endpoint}")


def calculate_quality_score(test_cases: list) -> float:
    """计算测试用例质量评分"""
    if not test_cases:
        return 0.0
    
    score = 0.0
    total_points = 10.0
    
    # 1. 数量评分 (2分)
    count_score = min(len(test_cases) / 10.0 * 2, 2.0)
    score += count_score
    
    # 2. 多样性评分 (2分)
    methods = set(case.get('method', 'GET') for case in test_cases)
    diversity_score = min(len(methods) / 4.0 * 2, 2.0)
    score += diversity_score
    
    # 3. 完整性评分 (2分)
    complete_cases = sum(1 for case in test_cases 
                        if case.get('name') and case.get('endpoint') and case.get('expected_status'))
    completeness_score = complete_cases / len(test_cases) * 2
    score += completeness_score
    
    # 4. 安全性测试评分 (2分)
    security_cases = sum(1 for case in test_cases if case.get('test_type') == 'security')
    security_score = min(security_cases / len(test_cases) * 4, 2.0)
    score += security_score
    
    # 5. 描述质量评分 (2分)
    described_cases = sum(1 for case in test_cases 
                         if case.get('description') and len(case.get('description', '')) > 10)
    description_score = described_cases / len(test_cases) * 2
    score += description_score
    
    return min(score, total_points)


def compare_frameworks(results: list):
    """对比框架结果"""
    print_section("框架对比分析", "⚖️")
    
    successful_frameworks = [r for r in results if r.get('success', False)]
    
    if not successful_frameworks:
        print("❌ 所有框架测试都失败了")
        return
    
    print_step("成功率统计")
    print(f"   总测试框架: {len(results)}")
    print(f"   成功框架: {len(successful_frameworks)}")
    print(f"   成功率: {len(successful_frameworks)/len(results)*100:.1f}%")
    
    print_step("性能对比")
    for result in successful_frameworks:
        framework = result['framework']
        duration = result.get('duration', 0)
        test_count = result.get('test_cases_count', 0)
        print(f"   🚀 {framework}: {duration:.2f}秒, {test_count}个测试用例")
    
    print_step("特性对比")
    for result in successful_frameworks:
        framework = result['framework']
        features = result.get('features', [])
        print(f"   🎯 {framework}: {', '.join(features)}")
    
    print_step("质量对比")
    for result in successful_frameworks:
        framework = result['framework']
        test_cases = result.get('test_cases', [])
        if test_cases:
            quality_score = calculate_quality_score(test_cases)
            print(f"   🏆 {framework}: 质量评分 {quality_score:.1f}/10.0")
    
    # 推荐最佳框架
    print_step("框架推荐")
    if len(successful_frameworks) == 1:
        best_framework = successful_frameworks[0]['framework']
        print(f"   🎯 推荐使用: {best_framework}")
    else:
        # 综合评分
        best_score = 0
        best_framework = None
        
        for result in successful_frameworks:
            framework = result['framework']
            test_cases = result.get('test_cases', [])
            quality_score = calculate_quality_score(test_cases) if test_cases else 0
            speed_score = max(0, 10 - result.get('duration', 10))  # 速度评分
            count_score = min(result.get('test_cases_count', 0) / 5, 10)  # 数量评分
            
            total_score = quality_score + speed_score * 0.3 + count_score * 0.2
            
            print(f"   📊 {framework}: 综合评分 {total_score:.1f}")
            
            if total_score > best_score:
                best_score = total_score
                best_framework = framework
        
        if best_framework:
            print(f"   🏆 最佳框架: {best_framework} (评分: {best_score:.1f})")


async def save_comparison_results(results: list):
    """保存对比结果"""
    print_step("保存对比结果")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    comparison_data = {
        "timestamp": timestamp,
        "test_type": "framework_comparison",
        "frameworks": ["DeepSeek", "LangChain", "AutoGen"],
        "model_used": "deepseek-r1:14b",
        "results": results,
        "summary": {
            "total_frameworks": len(results),
            "successful_frameworks": len([r for r in results if r.get('success', False)]),
            "total_test_cases": sum(r.get('test_cases_count', 0) for r in results),
            "average_duration": sum(r.get('duration', 0) for r in results) / len(results) if results else 0
        }
    }
    
    filename = f"framework_comparison_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"   ✅ 对比结果已保存: {filename}")
    return filename


async def main():
    """主测试流程"""
    print_banner()
    
    results = []
    
    # 1. 测试DeepSeek框架
    deepseek_result = await test_deepseek_framework()
    results.append(deepseek_result)
    
    # 2. 测试LangChain框架
    langchain_result = await test_langchain_framework()
    results.append(langchain_result)
    
    # 3. 测试AutoGen框架
    autogen_result = await test_autogen_framework()
    results.append(autogen_result)
    
    # 4. 对比分析
    compare_frameworks(results)
    
    # 5. 保存结果
    filename = await save_comparison_results(results)
    
    # 6. 总结
    print_section("测试完成总结", "🎉")
    print("✨ 智能体框架对比测试完成！")
    
    successful_count = len([r for r in results if r.get('success', False)])
    total_test_cases = sum(r.get('test_cases_count', 0) for r in results)
    
    print(f"\n📊 测试统计:")
    print(f"   • 测试框架: {len(results)} 个")
    print(f"   • 成功框架: {successful_count} 个")
    print(f"   • 总测试用例: {total_test_cases} 个")
    print(f"   • 结果文件: {filename}")
    
    print(f"\n🎯 框架特点:")
    print("   • DeepSeek: 思考推理强、中文优化、本地部署")
    print("   • LangChain: 工具链丰富、模块化、可扩展")
    print("   • AutoGen: 多智能体协作、专业分工、群体智能")
    
    print(f"\n💡 使用建议:")
    print("   • 快速原型: 选择DeepSeek基础框架")
    print("   • 复杂分析: 选择LangChain工具链")
    print("   • 团队协作: 选择AutoGen多智能体")


if __name__ == "__main__":
    asyncio.run(main())
