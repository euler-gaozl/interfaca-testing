#!/usr/bin/env python3
"""
DeepSeek-R1 集成测试脚本
测试真实AI模型的测试用例生成能力
"""
import asyncio
import json
from datetime import datetime

from src.agents.test_generator import TestCaseGeneratorAgent
from src.agents.base_agent import test_ollama_connection
from src.models.schemas import TestType
from src.config.settings import settings


def print_header(title: str):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")


def print_step(step: str):
    """打印步骤"""
    print(f"\n📋 {step}")
    print("-" * 50)


async def test_ollama_connectivity():
    """测试Ollama连接"""
    print_step("步骤1: 测试Ollama连接")
    
    base_url = settings.ai_models.ollama_base_url
    model = settings.ai_models.ollama_model
    
    print(f"   连接地址: {base_url}")
    print(f"   模型名称: {model}")
    
    is_connected = await test_ollama_connection(base_url, model)
    
    if is_connected:
        print("   ✅ Ollama连接成功，模型可用")
        return True
    else:
        print("   ❌ Ollama连接失败或模型不可用")
        return False


async def test_deepseek_generation():
    """测试DeepSeek-R1测试用例生成"""
    print_step("步骤2: 测试DeepSeek-R1测试用例生成")
    
    # 创建测试用例生成智能体
    print("   🤖 初始化DeepSeek-R1测试生成智能体...")
    generator = TestCaseGeneratorAgent("ollama")
    
    # 准备测试API规范
    api_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "用户管理API",
            "version": "1.0.0",
            "description": "用户注册、登录、信息管理API"
        },
        "paths": {
            "/users/register": {
                "post": {
                    "summary": "用户注册",
                    "description": "创建新用户账户",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["username", "email", "password"],
                                    "properties": {
                                        "username": {
                                            "type": "string",
                                            "minLength": 3,
                                            "maxLength": 20,
                                            "pattern": "^[a-zA-Z0-9_]+$"
                                        },
                                        "email": {
                                            "type": "string",
                                            "format": "email"
                                        },
                                        "password": {
                                            "type": "string",
                                            "minLength": 8,
                                            "maxLength": 128
                                        },
                                        "phone": {
                                            "type": "string",
                                            "pattern": "^\\+?[1-9]\\d{1,14}$"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "注册成功",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "username": {"type": "string"},
                                            "email": {"type": "string"},
                                            "created_at": {"type": "string", "format": "date-time"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "请求参数错误"},
                        "409": {"description": "用户名或邮箱已存在"}
                    }
                }
            },
            "/users/login": {
                "post": {
                    "summary": "用户登录",
                    "description": "用户身份验证",
                    "requestBody": {
                        "required": True,
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
                        "200": {
                            "description": "登录成功",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "token": {"type": "string"},
                                            "user": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "username": {"type": "string"},
                                                    "email": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {"description": "用户名或密码错误"},
                        "429": {"description": "登录尝试过于频繁"}
                    }
                }
            },
            "/users/{id}": {
                "get": {
                    "summary": "获取用户信息",
                    "description": "根据用户ID获取用户详细信息",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer", "minimum": 1}
                        }
                    ],
                    "responses": {
                        "200": {"description": "获取成功"},
                        "404": {"description": "用户不存在"},
                        "403": {"description": "无权限访问"}
                    },
                    "security": [{"bearerAuth": []}]
                },
                "put": {
                    "summary": "更新用户信息",
                    "description": "更新用户的个人信息",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                        "phone": {"type": "string"},
                                        "profile": {
                                            "type": "object",
                                            "properties": {
                                                "nickname": {"type": "string"},
                                                "avatar": {"type": "string", "format": "uri"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "更新成功"},
                        "400": {"description": "请求参数错误"},
                        "403": {"description": "无权限操作"},
                        "404": {"description": "用户不存在"}
                    },
                    "security": [{"bearerAuth": []}]
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
    
    print(f"   📊 API规范: {len(api_spec['paths'])} 个端点")
    
    # 生成测试用例
    generation_input = {
        "project_id": 1,
        "api_spec": api_spec,
        "test_types": [TestType.FUNCTIONAL, TestType.SECURITY],
        "max_cases_per_endpoint": 3
    }
    
    print("   ⚡ 开始调用DeepSeek-R1生成测试用例...")
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
            
            # 显示生成的测试用例
            print("\n   📝 生成的测试用例:")
            for i, case in enumerate(test_cases, 1):
                print(f"      {i}. {case['name']}")
                print(f"         方法: {case['method']} {case['endpoint']}")
                print(f"         类型: {case['test_type']} | 优先级: {case['priority']}")
                print(f"         描述: {case['description']}")
                if case.get('tags'):
                    print(f"         标签: {', '.join(case['tags'])}")
                print()
            
            # 显示AI原始响应的一部分
            print(f"\n   🤖 AI原始响应 (前500字符):")
            print(f"      {ai_response[:500]}...")
            
            return True, test_cases, ai_response
        else:
            print(f"   ❌ 生成失败: {result['error']}")
            return False, [], ""
            
    except Exception as e:
        print(f"   ❌ 生成过程出错: {e}")
        return False, [], ""


async def analyze_generation_quality(test_cases: list, ai_response: str):
    """分析生成质量"""
    print_step("步骤3: 分析生成质量")
    
    if not test_cases:
        print("   ❌ 没有测试用例可分析")
        return
    
    # 统计分析
    total_cases = len(test_cases)
    test_types = {}
    priorities = {}
    methods = {}
    endpoints = set()
    
    for case in test_cases:
        # 统计测试类型
        test_type = case.get('test_type', 'unknown')
        test_types[test_type] = test_types.get(test_type, 0) + 1
        
        # 统计优先级
        priority = case.get('priority', 'unknown')
        priorities[priority] = priorities.get(priority, 0) + 1
        
        # 统计HTTP方法
        method = case.get('method', 'unknown')
        methods[method] = methods.get(method, 0) + 1
        
        # 统计端点
        endpoints.add(case.get('endpoint', 'unknown'))
    
    print(f"   📊 测试用例统计:")
    print(f"      总数量: {total_cases}")
    print(f"      覆盖端点: {len(endpoints)} 个")
    
    print(f"\n   📈 测试类型分布:")
    for test_type, count in test_types.items():
        percentage = (count / total_cases) * 100
        print(f"      {test_type}: {count} 个 ({percentage:.1f}%)")
    
    print(f"\n   🎯 优先级分布:")
    for priority, count in priorities.items():
        percentage = (count / total_cases) * 100
        print(f"      {priority}: {count} 个 ({percentage:.1f}%)")
    
    print(f"\n   🔧 HTTP方法分布:")
    for method, count in methods.items():
        percentage = (count / total_cases) * 100
        print(f"      {method}: {count} 个 ({percentage:.1f}%)")
    
    # 质量评估
    print(f"\n   ✨ 质量评估:")
    
    # 检查是否包含安全测试
    security_tests = [case for case in test_cases if case.get('test_type') == 'security']
    if security_tests:
        print(f"      ✅ 包含安全测试: {len(security_tests)} 个")
    else:
        print(f"      ⚠️  缺少安全测试用例")
    
    # 检查测试用例名称质量
    unique_names = set(case.get('name', '') for case in test_cases)
    if len(unique_names) == total_cases:
        print(f"      ✅ 测试用例名称唯一性: 100%")
    else:
        print(f"      ⚠️  测试用例名称重复: {total_cases - len(unique_names)} 个")
    
    # 检查描述完整性
    with_description = [case for case in test_cases if case.get('description', '').strip()]
    desc_percentage = (len(with_description) / total_cases) * 100
    print(f"      📝 描述完整性: {desc_percentage:.1f}%")
    
    # 检查AI响应中是否包含推理过程
    if "<think>" in ai_response and "</think>" in ai_response:
        print(f"      🧠 包含推理过程: ✅")
    else:
        print(f"      🧠 包含推理过程: ❌")


async def save_test_results(test_cases: list, ai_response: str):
    """保存测试结果"""
    print_step("步骤4: 保存测试结果")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存测试用例
    test_cases_file = f"deepseek_test_cases_{timestamp}.json"
    with open(test_cases_file, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2, default=str)
    print(f"   💾 测试用例已保存: {test_cases_file}")
    
    # 保存AI原始响应
    ai_response_file = f"deepseek_ai_response_{timestamp}.txt"
    with open(ai_response_file, 'w', encoding='utf-8') as f:
        f.write(ai_response)
    print(f"   💾 AI响应已保存: {ai_response_file}")
    
    return test_cases_file, ai_response_file


async def main():
    """主测试流程"""
    print_header("DeepSeek-R1 集成测试")
    
    # 1. 测试连接
    is_connected = await test_ollama_connectivity()
    if not is_connected:
        print("\n❌ Ollama连接失败，请检查:")
        print("   1. Ollama服务是否运行: ollama serve")
        print("   2. 模型是否存在: ollama list")
        print("   3. 端口是否正确: 11434")
        return
    
    # 2. 测试生成
    success, test_cases, ai_response = await test_deepseek_generation()
    if not success:
        print("\n❌ 测试用例生成失败")
        return
    
    # 3. 分析质量
    await analyze_generation_quality(test_cases, ai_response)
    
    # 4. 保存结果
    test_cases_file, ai_response_file = await save_test_results(test_cases, ai_response)
    
    # 总结
    print_header("测试完成总结")
    print("🎉 DeepSeek-R1 集成测试成功完成！")
    print("\n✨ 测试结果:")
    print(f"   • 生成测试用例: {len(test_cases)} 个")
    print(f"   • 测试用例文件: {test_cases_file}")
    print(f"   • AI响应文件: {ai_response_file}")
    
    print("\n🚀 下一步建议:")
    print("   • 运行完整演示: python complete_demo.py")
    print("   • 启动Web服务: python main.py")
    print("   • 对比模拟AI和真实AI的效果差异")


if __name__ == "__main__":
    asyncio.run(main())
