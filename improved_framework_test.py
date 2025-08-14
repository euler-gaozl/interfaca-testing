#!/usr/bin/env python3
"""
改进的智能体框架测试脚本
增强错误处理和诊断功能
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, Any, List
import traceback

from src.agents.test_generator import TestCaseGeneratorAgent
from src.agents.langchain_agent import LangChainTestAgent
from src.agents.autogen_agent import AutoGenMultiAgent
from src.utils.logger import log


class ImprovedFrameworkTester:
    """改进的框架测试器"""
    
    def __init__(self):
        self.test_api_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "电商API",
                "version": "1.0.0"
            },
            "paths": {
                "/products": {
                    "get": {
                        "summary": "获取商品列表",
                        "parameters": [
                            {
                                "name": "category",
                                "in": "query",
                                "schema": {"type": "string"}
                            },
                            {
                                "name": "limit",
                                "in": "query",
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "200": {"description": "成功"}
                        }
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
                        "responses": {
                            "201": {"description": "创建成功"}
                        }
                    }
                },
                "/orders": {
                    "post": {
                        "summary": "创建订单",
                        "security": [{"bearerAuth": []}],
                        "responses": {
                            "201": {"description": "订单创建成功"}
                        }
                    }
                }
            }
        }
        
        self.test_requirements = {
            "test_types": ["functional", "security"],
            "coverage": "comprehensive",
            "priority": "high"
        }
    
    async def test_framework(self, framework_name: str, agent_class, timeout: int = 180) -> Dict[str, Any]:
        """测试单个框架"""
        print(f"\n🧪 测试 {framework_name}")
        print("=" * 60)
        
        start_time = time.time()
        result = {
            "framework": framework_name,
            "success": False,
            "test_cases": [],
            "duration": 0,
            "error": None,
            "details": {}
        }
        
        try:
            # 创建智能体实例
            print(f"   📋 初始化{framework_name}智能体...")
            agent = agent_class()
            
            # 检查智能体状态
            if hasattr(agent, 'use_mock') and agent.use_mock:
                print(f"   ⚠️  {framework_name}使用模拟模式")
                result["details"]["mock_mode"] = True
            
            # 准备输入数据
            input_data = {
                "api_spec": self.test_api_spec,
                "test_types": self.test_requirements["test_types"],
                "requirements": self.test_requirements,
                "project_id": 1  # 添加必需的project_id参数
            }
            
            print(f"   🚀 启动{framework_name}处理...")
            
            # 使用超时控制
            try:
                response = await asyncio.wait_for(
                    agent.process(input_data),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                raise Exception(f"处理超时（{timeout}秒）")
            
            # 处理结果
            if response and response.get("success", False):
                test_cases = response.get("test_cases", [])
                result.update({
                    "success": True,
                    "test_cases": test_cases,
                    "test_case_count": len(test_cases),
                    "response": response
                })
                
                # 提取框架特定信息
                if framework_name == "LangChain":
                    result["details"]["tools_used"] = response.get("tools_used", [])
                    result["details"]["langchain_output"] = response.get("langchain_output", "")
                elif framework_name == "AutoGen":
                    result["details"]["agents_involved"] = response.get("agents_involved", [])
                    result["details"]["collaboration_messages"] = response.get("collaboration_messages", [])
                
                print(f"   ✅ {framework_name}: 成功生成 {len(test_cases)} 个测试用例")
                
            else:
                error_msg = response.get("error", "未知错误") if response else "无响应"
                result["error"] = error_msg
                print(f"   ❌ {framework_name}: 处理失败 - {error_msg}")
            
        except Exception as e:
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
            print(f"   💥 {framework_name}: 异常 - {e}")
            log.error(f"{framework_name}测试异常: {e}")
            log.debug(f"{framework_name}异常详情: {traceback.format_exc()}")
        
        finally:
            result["duration"] = time.time() - start_time
            print(f"   ⏱️  耗时: {result['duration']:.2f} 秒")
        
        return result
    
    def calculate_quality_score(self, result: Dict[str, Any]) -> float:
        """计算质量评分"""
        if not result["success"]:
            return 0.0
        
        score = 0.0
        test_cases = result.get("test_cases", [])
        
        # 基础分数
        if test_cases:
            score += 3.0
        
        # 测试用例数量分数
        case_count = len(test_cases)
        if case_count >= 3:
            score += 2.0
        elif case_count >= 2:
            score += 1.5
        elif case_count >= 1:
            score += 1.0
        
        # 测试类型覆盖分数
        test_types = set()
        for case in test_cases:
            test_types.add(case.get("test_type", "unknown"))
        
        if "functional" in test_types:
            score += 1.0
        if "security" in test_types:
            score += 1.5
        if "performance" in test_types:
            score += 1.0
        
        # 框架特定加分
        framework = result["framework"]
        if framework == "LangChain":
            tools_used = result.get("details", {}).get("tools_used", [])
            if len(tools_used) > 1:
                score += 0.5
        elif framework == "AutoGen":
            agents = result.get("details", {}).get("agents_involved", [])
            if len(agents) > 2:
                score += 0.5
        
        # 性能加分
        duration = result.get("duration", 0)
        if duration < 30:
            score += 0.5
        elif duration < 60:
            score += 0.3
        
        return min(score, 10.0)
    
    def get_framework_features(self, framework: str) -> List[str]:
        """获取框架特性"""
        features = {
            "DeepSeek": ["思考推理", "中文优化", "本地部署", "快速响应"],
            "LangChain": ["工具链丰富", "模块化设计", "可扩展性", "生态完善"],
            "AutoGen": ["多智能体协作", "专业分工", "群体智能", "角色扮演"]
        }
        return features.get(framework, ["未知特性"])
    
    async def run_comprehensive_test(self):
        """运行全面测试"""
        print("🎯 改进的智能体框架对比测试")
        print("=" * 80)
        
        # 测试框架配置
        frameworks = [
            ("DeepSeek", TestCaseGeneratorAgent),
            ("LangChain", LangChainTestAgent),
            ("AutoGen", AutoGenMultiAgent)
        ]
        
        results = []
        
        # 逐个测试框架
        for framework_name, agent_class in frameworks:
            result = await self.test_framework(framework_name, agent_class)
            result["quality_score"] = self.calculate_quality_score(result)
            result["features"] = self.get_framework_features(framework_name)
            results.append(result)
        
        # 生成对比报告
        self.generate_comparison_report(results)
        
        return results
    
    def generate_comparison_report(self, results: List[Dict[str, Any]]):
        """生成对比报告"""
        print("\n📊 测试结果对比分析")
        print("=" * 80)
        
        # 成功率统计
        successful = [r for r in results if r["success"]]
        success_rate = len(successful) / len(results) * 100
        
        print(f"\n📋 成功率统计")
        print("-" * 60)
        print(f"   总测试框架: {len(results)}")
        print(f"   成功框架: {len(successful)}")
        print(f"   成功率: {success_rate:.1f}%")
        
        # 性能对比
        print(f"\n📋 性能对比")
        print("-" * 60)
        for result in successful:
            duration = result["duration"]
            case_count = len(result["test_cases"])
            print(f"   🚀 {result['framework']}: {duration:.2f}秒, {case_count}个测试用例")
        
        # 特性对比
        print(f"\n📋 特性对比")
        print("-" * 60)
        for result in results:
            features = ", ".join(result["features"])
            print(f"   🎯 {result['framework']}: {features}")
        
        # 质量对比
        print(f"\n📋 质量对比")
        print("-" * 60)
        for result in successful:
            score = result["quality_score"]
            print(f"   🏆 {result['framework']}: 质量评分 {score:.1f}/10.0")
        
        # 错误分析
        failed = [r for r in results if not r["success"]]
        if failed:
            print(f"\n📋 错误分析")
            print("-" * 60)
            for result in failed:
                print(f"   ❌ {result['framework']}: {result['error']}")
        
        # 推荐建议
        if successful:
            best = max(successful, key=lambda x: x["quality_score"])
            print(f"\n📋 框架推荐")
            print("-" * 60)
            print(f"   🎯 推荐使用: {best['framework']}")
            print(f"   📊 质量评分: {best['quality_score']:.1f}/10.0")
            print(f"   ⚡ 性能表现: {best['duration']:.2f}秒")
            print(f"   🧪 测试用例: {len(best['test_cases'])}个")
        
        # 保存详细结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"improved_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📋 保存测试结果")
        print("-" * 60)
        print(f"   ✅ 详细结果已保存: {filename}")


async def main():
    """主函数"""
    tester = ImprovedFrameworkTester()
    
    try:
        results = await tester.run_comprehensive_test()
        
        print("\n🎉 改进测试完成总结")
        print("=" * 80)
        
        successful_count = sum(1 for r in results if r["success"])
        total_cases = sum(len(r["test_cases"]) for r in results)
        
        print(f"✨ 智能体框架改进测试完成！")
        print(f"\n📊 测试统计:")
        print(f"   • 测试框架: {len(results)} 个")
        print(f"   • 成功框架: {successful_count} 个")
        print(f"   • 总测试用例: {total_cases} 个")
        
        if successful_count > 0:
            best = max([r for r in results if r["success"]], key=lambda x: x["quality_score"])
            print(f"\n🏆 最佳框架: {best['framework']}")
            print(f"   • 质量评分: {best['quality_score']:.1f}/10.0")
            print(f"   • 执行时间: {best['duration']:.2f}秒")
            print(f"   • 测试用例: {len(best['test_cases'])}个")
        
        print(f"\n💡 使用建议:")
        print(f"   • 快速原型: 选择DeepSeek基础框架")
        print(f"   • 复杂分析: 选择LangChain工具链")
        print(f"   • 团队协作: 选择AutoGen多智能体")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        log.error(f"主测试流程错误: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
