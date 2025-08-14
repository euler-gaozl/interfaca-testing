"""
AI接口测试框架演示脚本
"""
import asyncio
import json
from src.agents.test_generator import TestCaseGeneratorAgent
from src.utils.logger import setup_logger, log

async def demo_test_generation():
    """演示测试用例生成功能"""
    print("🚀 AI接口测试框架演示")
    print("=" * 50)
    
    # 设置日志
    setup_logger()
    
    # 模拟API规范
    api_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "用户管理API",
            "version": "1.0.0",
            "description": "用户管理系统的RESTful API"
        },
        "servers": [
            {"url": "https://api.example.com/v1"}
        ],
        "paths": {
            "/users": {
                "get": {
                    "summary": "获取用户列表",
                    "description": "分页获取用户列表",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "schema": {"type": "integer", "default": 1}
                        },
                        {
                            "name": "limit",
                            "in": "query", 
                            "schema": {"type": "integer", "default": 10}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "成功返回用户列表",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "users": {"type": "array"},
                                            "total": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "summary": "创建新用户",
                    "description": "创建一个新的用户账户",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["username", "email"],
                                    "properties": {
                                        "username": {"type": "string"},
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string", "minLength": 8}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "用户创建成功"},
                        "400": {"description": "请求参数错误"},
                        "409": {"description": "用户已存在"}
                    }
                }
            },
            "/users/{id}": {
                "get": {
                    "summary": "获取用户详情",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "成功返回用户详情"},
                        "404": {"description": "用户不存在"}
                    }
                },
                "put": {
                    "summary": "更新用户信息",
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
                                        "username": {"type": "string"},
                                        "email": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "更新成功"},
                        "404": {"description": "用户不存在"}
                    }
                },
                "delete": {
                    "summary": "删除用户",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "204": {"description": "删除成功"},
                        "404": {"description": "用户不存在"}
                    }
                }
            }
        }
    }
    
    print("📋 API规范信息:")
    print(f"  - 标题: {api_spec['info']['title']}")
    print(f"  - 版本: {api_spec['info']['version']}")
    print(f"  - 端点数量: {len(api_spec['paths'])}")
    print()
    
    # 初始化测试用例生成智能体
    print("🤖 初始化AI测试用例生成智能体...")
    generator = TestCaseGeneratorAgent()
    
    # 准备输入数据
    input_data = {
        "project_id": 1,
        "api_spec": api_spec,
        "test_types": ["functional", "security"],
        "max_cases_per_endpoint": 3
    }
    
    print("⚡ 开始生成测试用例...")
    print("   (使用模拟AI客户端，实际部署时会调用真实AI模型)")
    print()
    
    # 生成测试用例
    result = await generator.process(input_data)
    
    if result["success"]:
        print("✅ 测试用例生成成功!")
        print(f"📊 生成统计:")
        print(f"  - 生成数量: {result['generated_count']} 个测试用例")
        print()
        
        print("📝 生成的测试用例:")
        print("-" * 50)
        
        for i, test_case in enumerate(result["test_cases"], 1):
            print(f"{i}. {test_case['name']}")
            print(f"   方法: {test_case['method']}")
            print(f"   端点: {test_case['endpoint']}")
            print(f"   类型: {test_case['test_type']}")
            print(f"   优先级: {test_case['priority']}")
            print(f"   描述: {test_case['description']}")
            if test_case.get('tags'):
                print(f"   标签: {', '.join(test_case['tags'])}")
            print()
        
        print("🤖 AI响应摘要:")
        print(f"   {result.get('ai_response', '模拟AI响应')[:100]}...")
        print()
        
    else:
        print("❌ 测试用例生成失败!")
        print(f"错误信息: {result.get('error', '未知错误')}")
    
    print("=" * 50)
    print("🎉 演示完成!")
    print()
    print("💡 下一步可以:")
    print("  1. 启动Web服务: python main.py")
    print("  2. 访问API文档: http://localhost:8000/docs")
    print("  3. 配置真实的AI模型API密钥")
    print("  4. 上传真实的API规范文档")

def main():
    """主函数"""
    try:
        asyncio.run(demo_test_generation())
    except KeyboardInterrupt:
        print("\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")

if __name__ == "__main__":
    main()
