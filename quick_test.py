#!/usr/bin/env python3
"""
AI接口测试框架快速示例脚本

这个脚本展示了如何使用AI接口测试框架进行基本的API测试。
它包含了完整的工作流程：创建项目、创建测试用例、执行测试、查看结果和生成AI报告。
"""
import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, List, Any

# 服务器配置
API_BASE_URL = "http://localhost:8000/api/v1"

async def quick_test():
    """运行快速测试示例"""
    print("🚀 AI接口测试框架快速示例")
    print("=" * 50)
    
    # 1. 创建项目
    print("\n📁 创建测试项目...")
    async with httpx.AsyncClient() as client:
        project_response = await client.post(
            f"{API_BASE_URL}/projects/",
            json={
                "name": f"快速示例项目-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "description": "用于演示AI接口测试框架的基本功能",
                "base_url": "https://httpbin.org"
            }
        )
        
        if project_response.status_code != 200:
            print(f"❌ 创建项目失败: {project_response.text}")
            return
        
        project_data = project_response.json()
        project_id = project_data["data"]["id"]
        print(f"✅ 项目创建成功，ID: {project_id}")
    
    # 2. 创建测试用例
    print("\n📝 创建测试用例...")
    test_cases = [
        {
            "name": "GET请求测试",
            "description": "测试基本GET请求",
            "method": "GET",
            "endpoint": "/get",
            "query_params": {"param1": "value1", "param2": "value2"},
            "expected_status": 200,
            "test_type": "functional",
            "priority": "high",
            "project_id": project_id
        },
        {
            "name": "POST请求测试",
            "description": "测试基本POST请求",
            "method": "POST",
            "endpoint": "/post",
            "body": {
                "name": "测试用户",
                "email": "test@example.com"
            },
            "expected_status": 200,
            "test_type": "functional",
            "priority": "medium",
            "project_id": project_id
        },
        {
            "name": "状态码测试",
            "description": "测试特定状态码",
            "method": "GET",
            "endpoint": "/status/418",
            "expected_status": 418,
            "test_type": "functional",
            "priority": "low",
            "project_id": project_id
        }
    ]
    
    async with httpx.AsyncClient() as client:
        test_case_response = await client.post(
            f"{API_BASE_URL}/test-cases/batch",
            json=test_cases
        )
        
        if test_case_response.status_code != 200:
            print(f"❌ 创建测试用例失败: {test_case_response.text}")
            return
        
        test_case_data = test_case_response.json()
        test_case_ids = [tc["id"] for tc in test_case_data["data"]]
        print(f"✅ 成功创建 {len(test_case_ids)} 个测试用例: {test_case_ids}")
    
    # 3. 执行批量测试
    print("\n🚀 执行批量测试...")
    async with httpx.AsyncClient() as client:
        execution_response = await client.post(
            f"{API_BASE_URL}/executions/batch",
            json={
                "project_id": project_id,
                "test_case_ids": test_case_ids,
                "concurrent_limit": 2,
                "timeout": 30,
                "retry_count": 1,
                "execution_strategy": "mixed"  # mixed, parallel, serial
            }
        )
        
        if execution_response.status_code != 200:
            print(f"❌ 创建批量测试执行失败: {execution_response.text}")
            return
        
        execution_data = execution_response.json()
        execution_id = execution_data["data"]["execution_id"]
        print(f"✅ 批量测试执行任务已创建，ID: {execution_id}")
    
    # 4. 监控执行状态
    print("\n⏳ 监控测试执行状态...")
    while True:
        async with httpx.AsyncClient() as client:
            status_response = await client.get(f"{API_BASE_URL}/executions/{execution_id}")
            
            if status_response.status_code != 200:
                print(f"❌ 获取执行状态失败: {status_response.text}")
                return
            
            status_data = status_response.json()
            execution = status_data["data"]
            status = execution["status"]
            
            print(f"📊 当前状态: {status}, 已完成: {len(execution['results'])}/{len(execution['test_case_ids'])}")
            
            if status in ["completed", "failed", "stopped"]:
                break
            
            await asyncio.sleep(1)
    
    # 5. 获取测试结果
    print("\n📋 获取测试结果...")
    async with httpx.AsyncClient() as client:
        results_response = await client.get(f"{API_BASE_URL}/executions/{execution_id}/results")
        
        if results_response.status_code != 200:
            print(f"❌ 获取执行结果失败: {results_response.text}")
            return
        
        results_data = results_response.json()
        test_results = results_data["data"]
        
        # 显示结果摘要
        print("\n📊 测试结果摘要:")
        print(f"总测试用例数: {test_results['summary']['total']}")
        print(f"已完成: {test_results['summary']['completed']}")
        print(f"通过: {test_results['summary']['passed']}")
        print(f"失败: {test_results['summary']['failed']}")
        print(f"错误: {test_results['summary']['error']}")
        print(f"跳过: {test_results['summary']['skipped']}")
        print(f"通过率: {test_results['summary']['pass_rate']:.2f}%")
        print(f"平均响应时间: {test_results['summary']['avg_response_time']:.2f}ms")
        
        # 显示详细结果
        print("\n📝 详细测试结果:")
        for result in test_results["results"]:
            status_emoji = "✅" if result["status"] == "passed" else "❌"
            print(f"{status_emoji} 测试用例 {result['test_case_id']}: {result['status']}")
            if result["status"] != "passed":
                print(f"   错误信息: {result.get('error_message', '无')}")
            if result.get("response_time"):
                print(f"   响应时间: {result['response_time']:.2f}ms")
            print(f"   状态码: {result.get('actual_status', '无')}")
            print()
    
    # 6. 生成AI测试报告
    print("\n🤖 生成AI测试报告...")
    async with httpx.AsyncClient() as client:
        report_response = await client.post(f"{API_BASE_URL}/ai/test-report/{execution_id}")
        
        if report_response.status_code != 200:
            print(f"❌ 生成AI测试报告失败: {report_response.text}")
            return
        
        print("✅ AI测试报告生成成功")
        
        # 获取AI报告
        report_get_response = await client.get(f"{API_BASE_URL}/ai/test-report/{execution_id}")
        
        if report_get_response.status_code != 200:
            print(f"❌ 获取AI测试报告失败: {report_get_response.text}")
            return
        
        report_data = report_get_response.json()
        ai_report = report_data["data"]
        
        # 显示AI报告
        print("\n🧠 AI测试报告分析")
        print("=" * 50)
        
        # 检查AI报告是否完整
        if "ai_analysis" not in ai_report:
            print("⚠️ AI报告数据不完整，显示可用部分")
        else:
            # 显示整体评估
            print("\n📊 整体评估:")
            print(ai_report["ai_analysis"]["overall_assessment"])
            
            # 显示性能分析
            print("\n⚡ 性能分析:")
            print(ai_report["ai_analysis"]["performance_analysis"])
            
            # 显示测试覆盖率分析
            print("\n🔍 测试覆盖率分析:")
            print(ai_report["ai_analysis"]["test_coverage_analysis"])
            
            # 显示失败分析
            print("\n❌ 失败分析:")
            print(ai_report["ai_analysis"]["failure_analysis"])
            
            # 显示建议
            print("\n💡 AI建议:")
            for i, recommendation in enumerate(ai_report["ai_analysis"]["recommendations"], 1):
                print(f"{i}. {recommendation}")
    
    # 7. 导出报告
    print("\n📊 导出测试报告...")
    
    # 创建报告目录
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # 生成报告文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{reports_dir}/quick_test_report_{timestamp}.json"
    
    # 导出报告
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(ai_report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 报告已导出到: {filename}")
    
    print("\n✨ 快速测试示例完成")
    print("=" * 50)
    print("📚 查看 README.md 和 QUICK_START.md 获取更多信息")

if __name__ == "__main__":
    asyncio.run(quick_test())
