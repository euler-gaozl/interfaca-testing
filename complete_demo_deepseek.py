#!/usr/bin/env python3
"""
DeepSeek-R1 完整功能演示
展示真实AI模型的接口自动化测试能力
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from src.agents.test_generator import TestCaseGeneratorAgent
from src.agents.base_agent import test_ollama_connection
from src.models.schemas import TestType
from src.config.settings import settings


def print_banner():
    """打印横幅"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🤖 DeepSeek-R1 AI接口自动化测试工具                        ║
║                          真实AI模型完整功能演示                               ║
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


async def check_environment():
    """检查环境"""
    print_section("环境检查", "🔍")
    
    print_step("检查Ollama连接")
    base_url = settings.ai_models.ollama_base_url
    model = settings.ai_models.ollama_model
    
    print(f"   连接地址: {base_url}")
    print(f"   模型名称: {model}")
    
    is_connected = await test_ollama_connection(base_url, model)
    
    if is_connected:
        print("   ✅ Ollama连接成功，DeepSeek-R1模型可用")
        return True
    else:
        print("   ❌ Ollama连接失败或模型不可用")
        print("\n   请检查:")
        print("   1. Ollama服务是否运行: ollama serve")
        print("   2. 模型是否存在: ollama list")
        print("   3. 端口是否正确: 11434")
        return False


async def demo_test_generation():
    """演示测试用例生成"""
    print_section("AI测试用例生成演示", "🤖")
    
    print_step("初始化DeepSeek-R1智能体")
    generator = TestCaseGeneratorAgent("ollama")
    print("   ✅ DeepSeek-R1测试生成智能体已初始化")
    
    print_step("准备API规范")
    # 电商API规范
    api_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "电商平台API",
            "version": "2.0.0",
            "description": "包含商品管理、订单处理、用户认证的完整电商API"
        },
        "servers": [
            {"url": "https://api.ecommerce.com/v2", "description": "生产环境"}
        ],
        "paths": {
            "/products": {
                "get": {
                    "summary": "获取商品列表",
                    "description": "分页获取商品列表，支持搜索和筛选",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "schema": {"type": "integer", "minimum": 1, "default": 1}
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
                        },
                        {
                            "name": "category",
                            "in": "query",
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "search",
                            "in": "query",
                            "schema": {"type": "string", "minLength": 2}
                        },
                        {
                            "name": "min_price",
                            "in": "query",
                            "schema": {"type": "number", "minimum": 0}
                        },
                        {
                            "name": "max_price",
                            "in": "query",
                            "schema": {"type": "number", "minimum": 0}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "商品列表获取成功",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "products": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "integer"},
                                                        "name": {"type": "string"},
                                                        "price": {"type": "number"},
                                                        "category": {"type": "string"},
                                                        "stock": {"type": "integer"},
                                                        "image_url": {"type": "string"}
                                                    }
                                                }
                                            },
                                            "total": {"type": "integer"},
                                            "page": {"type": "integer"},
                                            "limit": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "请求参数错误"},
                        "500": {"description": "服务器内部错误"}
                    }
                },
                "post": {
                    "summary": "创建新商品",
                    "description": "管理员创建新商品",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name", "price", "category", "stock"],
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "minLength": 1,
                                            "maxLength": 200
                                        },
                                        "description": {"type": "string"},
                                        "price": {
                                            "type": "number",
                                            "minimum": 0.01,
                                            "maximum": 999999.99
                                        },
                                        "category": {"type": "string"},
                                        "stock": {
                                            "type": "integer",
                                            "minimum": 0
                                        },
                                        "image_url": {
                                            "type": "string",
                                            "format": "uri"
                                        },
                                        "tags": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "商品创建成功"},
                        "400": {"description": "请求数据无效"},
                        "401": {"description": "未授权"},
                        "403": {"description": "权限不足"},
                        "409": {"description": "商品名称已存在"}
                    }
                }
            },
            "/orders": {
                "post": {
                    "summary": "创建订单",
                    "description": "用户创建新订单",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["items", "shipping_address"],
                                    "properties": {
                                        "items": {
                                            "type": "array",
                                            "minItems": 1,
                                            "items": {
                                                "type": "object",
                                                "required": ["product_id", "quantity"],
                                                "properties": {
                                                    "product_id": {"type": "integer"},
                                                    "quantity": {"type": "integer", "minimum": 1}
                                                }
                                            }
                                        },
                                        "shipping_address": {
                                            "type": "object",
                                            "required": ["street", "city", "postal_code", "country"],
                                            "properties": {
                                                "street": {"type": "string"},
                                                "city": {"type": "string"},
                                                "postal_code": {"type": "string"},
                                                "country": {"type": "string"}
                                            }
                                        },
                                        "payment_method": {
                                            "type": "string",
                                            "enum": ["credit_card", "paypal", "bank_transfer"]
                                        },
                                        "coupon_code": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "订单创建成功"},
                        "400": {"description": "订单数据无效"},
                        "401": {"description": "用户未登录"},
                        "402": {"description": "支付失败"},
                        "409": {"description": "库存不足"}
                    }
                }
            },
            "/auth/login": {
                "post": {
                    "summary": "用户登录",
                    "description": "用户身份验证",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["email", "password"],
                                    "properties": {
                                        "email": {
                                            "type": "string",
                                            "format": "email"
                                        },
                                        "password": {
                                            "type": "string",
                                            "minLength": 8
                                        },
                                        "remember_me": {"type": "boolean"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "登录成功",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "access_token": {"type": "string"},
                                            "refresh_token": {"type": "string"},
                                            "expires_in": {"type": "integer"},
                                            "user": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "email": {"type": "string"},
                                                    "name": {"type": "string"},
                                                    "role": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {"description": "邮箱或密码错误"},
                        "423": {"description": "账户被锁定"},
                        "429": {"description": "登录尝试过于频繁"}
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }
    
    print(f"   📊 API规范统计:")
    print(f"      端点数量: {len(api_spec['paths'])} 个")
    print(f"      API版本: {api_spec['info']['version']}")
    print(f"      API描述: {api_spec['info']['description']}")
    
    print_step("调用DeepSeek-R1生成测试用例")
    generation_input = {
        "project_id": 1,
        "api_spec": api_spec,
        "test_types": [TestType.FUNCTIONAL, TestType.SECURITY],
        "max_cases_per_endpoint": 4
    }
    
    print("   ⚡ 正在调用DeepSeek-R1模型...")
    print("   💭 AI正在分析API规范并生成测试用例...")
    
    start_time = datetime.now()
    
    try:
        result = await generator.process(generation_input)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"   ⏱️  生成耗时: {duration:.2f} 秒")
        
        if result["success"]:
            test_cases = result["test_cases"]
            ai_response = result["ai_response"]
            
            print(f"   ✅ 生成成功! 共生成 {len(test_cases)} 个测试用例")
            
            return test_cases, ai_response
        else:
            print(f"   ❌ 生成失败: {result['error']}")
            return [], ""
            
    except Exception as e:
        print(f"   ❌ 生成过程出错: {e}")
        return [], ""


def analyze_test_cases(test_cases: list):
    """分析测试用例质量"""
    print_section("测试用例质量分析", "📊")
    
    if not test_cases:
        print("   ❌ 没有测试用例可分析")
        return
    
    print_step("基础统计")
    total_cases = len(test_cases)
    print(f"   总测试用例数: {total_cases}")
    
    # 按端点分组
    endpoints = {}
    for case in test_cases:
        endpoint = case.get('endpoint', 'unknown')
        if endpoint not in endpoints:
            endpoints[endpoint] = []
        endpoints[endpoint].append(case)
    
    print(f"   覆盖端点数: {len(endpoints)}")
    
    print_step("端点覆盖分析")
    for endpoint, cases in endpoints.items():
        print(f"   📍 {endpoint}")
        print(f"      测试用例数: {len(cases)}")
        
        methods = set(case.get('method', 'unknown') for case in cases)
        print(f"      HTTP方法: {', '.join(methods)}")
        
        test_types = set(case.get('test_type', 'unknown') for case in cases)
        print(f"      测试类型: {', '.join(test_types)}")
        print()
    
    print_step("测试类型分布")
    test_type_stats = {}
    priority_stats = {}
    method_stats = {}
    
    for case in test_cases:
        # 统计测试类型
        test_type = case.get('test_type', 'unknown')
        test_type_stats[test_type] = test_type_stats.get(test_type, 0) + 1
        
        # 统计优先级
        priority = case.get('priority', 'unknown')
        priority_stats[priority] = priority_stats.get(priority, 0) + 1
        
        # 统计HTTP方法
        method = case.get('method', 'unknown')
        method_stats[method] = method_stats.get(method, 0) + 1
    
    print("   📈 测试类型:")
    for test_type, count in test_type_stats.items():
        percentage = (count / total_cases) * 100
        print(f"      {test_type}: {count} 个 ({percentage:.1f}%)")
    
    print("\n   🎯 优先级分布:")
    for priority, count in priority_stats.items():
        percentage = (count / total_cases) * 100
        print(f"      {priority}: {count} 个 ({percentage:.1f}%)")
    
    print("\n   🔧 HTTP方法:")
    for method, count in method_stats.items():
        percentage = (count / total_cases) * 100
        print(f"      {method}: {count} 个 ({percentage:.1f}%)")


def display_test_cases(test_cases: list):
    """展示测试用例详情"""
    print_section("生成的测试用例详情", "📝")
    
    if not test_cases:
        print("   ❌ 没有测试用例可展示")
        return
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 测试用例 {i}: {case.get('name', '未命名')}")
        print(f"   🎯 描述: {case.get('description', '无描述')}")
        print(f"   🔧 方法: {case.get('method', 'GET')} {case.get('endpoint', '/')}")
        print(f"   📊 类型: {case.get('test_type', 'functional')} | 优先级: {case.get('priority', 'medium')}")
        
        # 显示请求体（如果有）
        body = case.get('body', {})
        if body:
            print(f"   📦 请求体: {json.dumps(body, ensure_ascii=False)}")
        
        # 显示查询参数（如果有）
        query_params = case.get('query_params', {})
        if query_params:
            print(f"   🔍 查询参数: {json.dumps(query_params, ensure_ascii=False)}")
        
        # 显示期望状态码
        expected_status = case.get('expected_status', 200)
        print(f"   ✅ 期望状态码: {expected_status}")
        
        # 显示标签（如果有）
        tags = case.get('tags', [])
        if tags:
            print(f"   🏷️  标签: {', '.join(tags)}")


def analyze_ai_response(ai_response: str):
    """分析AI响应质量"""
    print_section("AI响应质量分析", "🧠")
    
    if not ai_response:
        print("   ❌ 没有AI响应可分析")
        return
    
    print_step("响应统计")
    print(f"   响应长度: {len(ai_response)} 字符")
    print(f"   响应行数: {len(ai_response.splitlines())} 行")
    
    print_step("推理过程分析")
    if "<think>" in ai_response and "</think>" in ai_response:
        think_start = ai_response.find("<think>")
        think_end = ai_response.find("</think>") + 8
        thinking_content = ai_response[think_start:think_end]
        
        print("   ✅ 包含推理过程")
        print(f"   🧠 推理内容长度: {len(thinking_content)} 字符")
        
        # 显示推理过程的一部分
        print("\n   💭 推理过程片段:")
        lines = thinking_content.split('\n')[:10]  # 显示前10行
        for line in lines:
            if line.strip():
                print(f"      {line.strip()}")
        if len(thinking_content.split('\n')) > 10:
            print("      ...")
    else:
        print("   ❌ 未包含推理过程")
    
    print_step("JSON格式分析")
    if '[' in ai_response and ']' in ai_response:
        print("   ✅ 包含JSON数组格式")
    elif '{' in ai_response and '}' in ai_response:
        print("   ✅ 包含JSON对象格式")
    else:
        print("   ❌ 未检测到JSON格式")


async def save_results(test_cases: list, ai_response: str):
    """保存结果"""
    print_section("保存测试结果", "💾")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存测试用例
    test_cases_file = f"deepseek_demo_test_cases_{timestamp}.json"
    with open(test_cases_file, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2, default=str)
    print(f"   ✅ 测试用例已保存: {test_cases_file}")
    
    # 保存AI响应
    ai_response_file = f"deepseek_demo_ai_response_{timestamp}.txt"
    with open(ai_response_file, 'w', encoding='utf-8') as f:
        f.write(ai_response)
    print(f"   ✅ AI响应已保存: {ai_response_file}")
    
    # 生成测试报告
    report = {
        "timestamp": timestamp,
        "model": "deepseek-r1:14b",
        "test_cases_count": len(test_cases),
        "test_cases_file": test_cases_file,
        "ai_response_file": ai_response_file,
        "summary": {
            "total_cases": len(test_cases),
            "endpoints_covered": len(set(case.get('endpoint', '') for case in test_cases)),
            "test_types": list(set(case.get('test_type', '') for case in test_cases)),
            "priorities": list(set(case.get('priority', '') for case in test_cases))
        }
    }
    
    report_file = f"deepseek_demo_report_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print(f"   ✅ 测试报告已保存: {report_file}")
    
    return test_cases_file, ai_response_file, report_file


async def main():
    """主演示流程"""
    print_banner()
    
    # 1. 环境检查
    if not await check_environment():
        return
    
    # 2. 测试用例生成演示
    test_cases, ai_response = await demo_test_generation()
    
    if not test_cases:
        print("\n❌ 测试用例生成失败，演示终止")
        return
    
    # 3. 分析测试用例
    analyze_test_cases(test_cases)
    
    # 4. 展示测试用例详情
    display_test_cases(test_cases)
    
    # 5. 分析AI响应
    analyze_ai_response(ai_response)
    
    # 6. 保存结果
    test_cases_file, ai_response_file, report_file = await save_results(test_cases, ai_response)
    
    # 7. 总结
    print_section("演示完成总结", "🎉")
    print("✨ DeepSeek-R1 AI接口自动化测试工具演示成功完成！")
    
    print(f"\n📊 演示结果:")
    print(f"   • 生成测试用例: {len(test_cases)} 个")
    print(f"   • 覆盖API端点: {len(set(case.get('endpoint', '') for case in test_cases))} 个")
    print(f"   • AI推理质量: {'优秀' if '<think>' in ai_response else '良好'}")
    
    print(f"\n📁 生成文件:")
    print(f"   • 测试用例: {test_cases_file}")
    print(f"   • AI响应: {ai_response_file}")
    print(f"   • 测试报告: {report_file}")
    
    print(f"\n🚀 下一步建议:")
    print("   • 启动Web服务查看完整功能: python main.py")
    print("   • 运行模拟AI对比测试: python complete_demo.py")
    print("   • 集成到CI/CD流水线中进行自动化测试")
    
    print(f"\n💡 DeepSeek-R1模型特点:")
    print("   • 强大的推理能力，包含详细的思考过程")
    print("   • 深度理解API规范，生成高质量测试用例")
    print("   • 支持多种测试类型：功能、安全、性能")
    print("   • 本地部署，数据安全可控")


if __name__ == "__main__":
    asyncio.run(main())
