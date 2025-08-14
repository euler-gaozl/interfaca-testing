#!/usr/bin/env python3
"""
完整的AI接口自动化测试演示
展示：项目创建 -> 测试用例生成 -> 测试执行 -> 报告生成
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List

from src.agents.test_generator import TestCaseGeneratorAgent
from src.models.schemas import TestStatus, TestType, HTTPMethod, Priority

def print_header(title: str):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_step(step: str):
    """打印步骤"""
    print(f"\n📋 {step}")
    print("-" * 50)

async def simulate_test_execution(test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """模拟测试执行"""
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"   执行测试 {i}/{len(test_cases)}: {test_case['name']}")
        
        # 模拟网络请求延迟
        await asyncio.sleep(0.5)
        
        # 模拟不同的测试结果
        if "错误处理" in test_case['name']:
            status = TestStatus.PASSED
            actual_status = 400
            response_time = 0.15
        elif "安全" in test_case['name']:
            status = TestStatus.FAILED
            actual_status = 200
            response_time = 0.25
            error_msg = "检测到潜在的安全漏洞"
        else:
            status = TestStatus.PASSED
            actual_status = test_case.get('expected_status', 200)
            response_time = 0.12
        
        result = {
            "test_case_id": i,
            "test_case_name": test_case['name'],
            "status": status,
            "response_time": response_time,
            "actual_status": actual_status,
            "expected_status": test_case.get('expected_status', 200),
            "actual_response": {"message": "success", "data": {}},
            "error_message": error_msg if status == TestStatus.FAILED else None,
            "started_at": datetime.now(),
            "completed_at": datetime.now()
        }
        results.append(result)
        
        # 显示结果
        status_icon = "✅" if status == TestStatus.PASSED else "❌"
        print(f"      {status_icon} {status.value} ({response_time*1000:.0f}ms)")
    
    return results

def generate_test_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成测试报告"""
    total_tests = len(results)
    passed_tests = len([r for r in results if r['status'] == TestStatus.PASSED])
    failed_tests = len([r for r in results if r['status'] == TestStatus.FAILED])
    
    avg_response_time = sum(r['response_time'] for r in results) / total_tests if total_tests > 0 else 0
    
    report = {
        "execution_summary": {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            "avg_response_time": f"{avg_response_time*1000:.0f}ms"
        },
        "detailed_results": results,
        "ai_analysis": {
            "summary": "测试执行完成，发现1个安全相关问题需要关注",
            "insights": [
                "API响应时间整体表现良好，平均响应时间在可接受范围内",
                "功能性测试全部通过，基础功能运行正常",
                "安全测试发现潜在漏洞，建议加强输入验证"
            ],
            "recommendations": [
                "对用户输入进行更严格的验证和过滤",
                "添加更多的边界值测试用例",
                "考虑添加性能压力测试",
                "建议实施API访问频率限制"
            ],
            "risk_assessment": {
                "security_risk": "中等",
                "performance_risk": "低",
                "reliability_risk": "低"
            }
        },
        "generated_at": datetime.now().isoformat()
    }
    
    return report

async def main():
    """主演示流程"""
    print_header("AI接口自动化测试完整演示")
    
    # 1. 项目信息
    print_step("步骤1: 项目初始化")
    project_info = {
        "name": "电商API完整测试",
        "description": "演示完整的AI自动化测试流程",
        "base_url": "https://api.ecommerce-demo.com"
    }
    print(f"   项目名称: {project_info['name']}")
    print(f"   项目描述: {project_info['description']}")
    print(f"   基础URL: {project_info['base_url']}")
    
    # 2. API规范
    api_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "电商API",
            "version": "1.0.0",
            "description": "完整的电商系统API"
        },
        "paths": {
            "/products": {
                "get": {
                    "summary": "获取商品列表",
                    "parameters": [
                        {"name": "page", "in": "query", "schema": {"type": "integer"}},
                        {"name": "limit", "in": "query", "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {"description": "成功返回商品列表"},
                        "400": {"description": "请求参数错误"}
                    }
                },
                "post": {
                    "summary": "创建新商品",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name", "price"],
                                    "properties": {
                                        "name": {"type": "string", "minLength": 1},
                                        "price": {"type": "number", "minimum": 0},
                                        "description": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "商品创建成功"},
                        "400": {"description": "请求数据无效"}
                    }
                }
            },
            "/users/{id}": {
                "get": {
                    "summary": "获取用户信息",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {"description": "成功返回用户信息"},
                        "404": {"description": "用户不存在"}
                    }
                }
            },
            "/auth/login": {
                "post": {
                    "summary": "用户登录",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["username", "password"],
                                    "properties": {
                                        "username": {"type": "string"},
                                        "password": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "登录成功"},
                        "401": {"description": "认证失败"}
                    }
                }
            }
        }
    }
    
    print(f"   API端点数量: {len(api_spec['paths'])}")
    print(f"   API版本: {api_spec['info']['version']}")
    
    # 3. AI测试用例生成
    print_step("步骤2: AI智能生成测试用例")
    print("   🤖 初始化AI测试生成智能体...")
    
    generator = TestCaseGeneratorAgent("openai")
    
    generation_input = {
        "project_id": 1,
        "api_spec": api_spec,
        "test_types": [TestType.FUNCTIONAL, TestType.SECURITY],
        "max_cases_per_endpoint": 2
    }
    
    print("   ⚡ 开始生成测试用例...")
    result = await generator.process(generation_input)
    
    if result["success"]:
        test_cases = result["test_cases"]
        print(f"   ✅ 成功生成 {len(test_cases)} 个测试用例")
        
        print("\n   📝 生成的测试用例:")
        for i, case in enumerate(test_cases, 1):
            print(f"      {i}. {case['name']}")
            print(f"         方法: {case['method']} {case['endpoint']}")
            print(f"         类型: {case['test_type']} | 优先级: {case['priority']}")
            print(f"         描述: {case['description']}")
    else:
        print(f"   ❌ 生成失败: {result['error']}")
        return
    
    # 4. 测试执行
    print_step("步骤3: 自动化测试执行")
    print("   🚀 开始执行测试用例...")
    
    execution_results = await simulate_test_execution(test_cases)
    
    print(f"\n   📊 执行完成，共执行 {len(execution_results)} 个测试")
    
    # 5. 测试报告生成
    print_step("步骤4: AI智能分析与报告生成")
    print("   📈 生成测试报告...")
    
    report = generate_test_report(execution_results)
    
    print(f"\n   📋 测试执行摘要:")
    summary = report["execution_summary"]
    print(f"      总测试数: {summary['total_tests']}")
    print(f"      通过: {summary['passed']} | 失败: {summary['failed']}")
    print(f"      通过率: {summary['pass_rate']}")
    print(f"      平均响应时间: {summary['avg_response_time']}")
    
    print(f"\n   🤖 AI分析结果:")
    analysis = report["ai_analysis"]
    print(f"      摘要: {analysis['summary']}")
    
    print(f"\n   💡 关键洞察:")
    for insight in analysis["insights"]:
        print(f"      • {insight}")
    
    print(f"\n   🔧 改进建议:")
    for recommendation in analysis["recommendations"]:
        print(f"      • {recommendation}")
    
    print(f"\n   ⚠️  风险评估:")
    risks = analysis["risk_assessment"]
    print(f"      安全风险: {risks['security_risk']}")
    print(f"      性能风险: {risks['performance_risk']}")
    print(f"      可靠性风险: {risks['reliability_risk']}")
    
    # 6. 保存报告
    print_step("步骤5: 保存测试报告")
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"   💾 测试报告已保存: {report_file}")
    
    # 总结
    print_header("演示完成总结")
    print("🎉 AI接口自动化测试完整流程演示成功！")
    print("\n✨ 展示的核心功能:")
    print("   1. ✅ 项目管理 - 支持API规范导入")
    print("   2. ✅ AI测试用例生成 - 基于API规范智能生成")
    print("   3. ✅ 自动化测试执行 - 并发执行，实时监控")
    print("   4. ✅ AI智能分析 - 深度分析测试结果")
    print("   5. ✅ 测试报告生成 - 详细报告，支持多种格式")
    
    print("\n🚀 生产环境部署建议:")
    print("   • 配置真实的AI模型API密钥")
    print("   • 集成数据库存储测试数据")
    print("   • 添加CI/CD集成")
    print("   • 配置告警和通知机制")
    print("   • 扩展更多测试类型（性能、负载等）")
    
    print(f"\n📊 本次演示统计:")
    print(f"   • 生成测试用例: {len(test_cases)} 个")
    print(f"   • 执行测试: {len(execution_results)} 个")
    print(f"   • 通过率: {summary['pass_rate']}")
    print(f"   • 报告文件: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())
