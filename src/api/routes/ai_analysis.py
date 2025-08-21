"""
AI分析路由 - 使用大模型分析测试结果并生成报告
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Path, Query, Depends

from src.models.schemas import APIResponse
from src.utils.logger import log
from src.config.settings import settings

router = APIRouter()

# 模拟AI分析报告存储
ai_reports_db = {}

@router.post("/test-report/{execution_id}", response_model=APIResponse)
async def generate_ai_test_report(
    execution_id: str = Path(..., description="执行ID"),
    background_tasks: BackgroundTasks = None
):
    """使用AI生成测试报告"""
    try:
        # 获取测试执行结果
        from src.api.routes.executions import executions_db
        if execution_id not in executions_db:
            raise HTTPException(status_code=404, detail="执行任务不存在")
        
        execution = executions_db[execution_id]
        
        # 在后台生成AI测试报告
        if background_tasks:
            background_tasks.add_task(
                analyze_test_results,
                execution_id=execution_id,
                execution=execution
            )
            
            return APIResponse(
                success=True,
                message="AI测试报告生成任务已创建，请稍后查询结果",
                data={"execution_id": execution_id}
            )
        else:
            # 同步生成报告
            report = await analyze_test_results(execution_id, execution)
            return APIResponse(
                success=True,
                message="AI测试报告生成成功",
                data=report
            )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"生成AI测试报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-report/{execution_id}", response_model=APIResponse)
async def get_ai_test_report(
    execution_id: str = Path(..., description="执行ID")
):
    """获取AI生成的测试报告"""
    try:
        if execution_id not in ai_reports_db:
            raise HTTPException(status_code=404, detail="AI测试报告不存在")
        
        report = ai_reports_db[execution_id]
        
        return APIResponse(
            success=True,
            message="获取AI测试报告成功",
            data=report
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"获取AI测试报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_test_results(execution_id: str, execution: Any) -> Dict[str, Any]:
    """使用AI分析测试结果并生成报告"""
    try:
        log.info(f"开始AI分析测试结果: {execution_id}")
        
        # 准备测试数据
        test_results = execution.results
        test_case_ids = execution.test_case_ids
        
        # 获取测试用例详情
        from src.api.routes.test_cases import test_cases_db
        test_cases = [test_cases_db.get(tc_id, {}) for tc_id in test_case_ids]
        
        # 计算结果统计
        total = len(test_case_ids)
        completed = len(test_results)
        
        # 处理状态，可能是字符串或枚举
        def get_status_str(status):
            if hasattr(status, 'value'):  # 如果是枚举
                return status.value
            return str(status).lower()  # 否则转为小写字符串
        
        passed = sum(1 for r in test_results if get_status_str(r.status) == "passed")
        failed = sum(1 for r in test_results if get_status_str(r.status) == "failed")
        error = sum(1 for r in test_results if get_status_str(r.status) == "error")
        skipped = sum(1 for r in test_results if get_status_str(r.status) == "skipped")
        
        # 计算平均响应时间
        response_times = [r.response_time for r in test_results if r.response_time is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # 生成AI分析
        ai_analysis = {
            "overall_assessment": generate_overall_assessment(passed, total),
            "performance_analysis": generate_performance_analysis(response_times),
            "test_coverage_analysis": generate_test_coverage_analysis(test_cases),
            "failure_analysis": generate_failure_analysis(test_results, test_cases),
            "recommendations": generate_recommendations(test_results, test_cases)
        }
        
        # 生成测试报告
        report = {
            "report_id": str(uuid.uuid4()),
            "execution_id": execution_id,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "completed": completed,
                "passed": passed,
                "failed": failed,
                "error": error,
                "skipped": skipped,
                "pass_rate": (passed / completed * 100) if completed > 0 else 0,
                "avg_response_time": avg_response_time
            },
            "ai_analysis": ai_analysis,
            "detailed_results": [
                {
                    "test_case_id": r.test_case_id,
                    "name": next((tc.get("name", f"测试用例 {r.test_case_id}") for tc in test_cases if tc.get("id") == r.test_case_id), f"测试用例 {r.test_case_id}"),
                    "status": get_status_str(r.status),
                    "response_time": r.response_time,
                    "actual_status": r.actual_status,
                    "error_message": r.error_message,
                    "ai_insights": generate_test_case_insights(r, test_cases)
                }
                for r in test_results
            ]
        }
        
        # 保存报告
        ai_reports_db[execution_id] = report
        
        log.info(f"AI测试报告生成完成: {execution_id}")
        
        return report
    except Exception as e:
        log.error(f"AI分析测试结果失败: {e}")
        raise

def generate_overall_assessment(passed: int, total: int) -> str:
    """生成整体评估"""
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    if pass_rate == 100:
        return "所有测试用例均通过，API接口表现良好，符合预期行为。"
    elif pass_rate >= 80:
        return f"大部分测试用例通过（{pass_rate:.2f}%），API接口基本功能正常，但存在少量问题需要关注。"
    elif pass_rate >= 50:
        return f"测试通过率较低（{pass_rate:.2f}%），API接口存在较多问题，建议进行修复后再次测试。"
    else:
        return f"测试通过率严重不足（{pass_rate:.2f}%），API接口可能存在严重问题，需要全面检查和修复。"

def generate_performance_analysis(response_times: List[float]) -> str:
    """生成性能分析"""
    if not response_times:
        return "无法进行性能分析，未收集到响应时间数据。"
    
    avg_time = sum(response_times) / len(response_times)
    max_time = max(response_times) if response_times else 0
    min_time = min(response_times) if response_times else 0
    
    if avg_time < 100:
        performance = "优秀"
    elif avg_time < 300:
        performance = "良好"
    elif avg_time < 1000:
        performance = "一般"
    else:
        performance = "较差"
    
    return f"API性能{performance}，平均响应时间为{avg_time:.2f}ms，最快响应{min_time:.2f}ms，最慢响应{max_time:.2f}ms。"

def generate_test_coverage_analysis(test_cases: List[Dict[str, Any]]) -> str:
    """生成测试覆盖率分析"""
    # 统计HTTP方法覆盖
    methods = [tc.get("method", "").upper() for tc in test_cases if tc.get("method")]
    unique_methods = set(methods)
    
    # 统计测试类型覆盖
    test_types = [tc.get("test_type", "") for tc in test_cases if tc.get("test_type")]
    unique_test_types = set(test_types)
    
    coverage_analysis = f"测试覆盖了{len(unique_methods)}种HTTP方法（{', '.join(unique_methods)}）"
    
    if unique_test_types:
        coverage_analysis += f"，包含{len(unique_test_types)}种测试类型（{', '.join(unique_test_types)}）"
    
    # 分析覆盖率是否全面
    common_methods = {"GET", "POST", "PUT", "DELETE", "PATCH"}
    missing_methods = common_methods - unique_methods
    
    if missing_methods:
        coverage_analysis += f"。建议增加对{', '.join(missing_methods)}方法的测试，以提高API覆盖率。"
    else:
        coverage_analysis += "。测试覆盖了所有常见HTTP方法，覆盖率较为全面。"
    
    return coverage_analysis

def generate_failure_analysis(test_results: List[Any], test_cases: List[Dict[str, Any]]) -> str:
    """生成失败分析"""
    # 处理状态，可能是字符串或枚举
    def get_status_str(status):
        if hasattr(status, 'value'):  # 如果是枚举
            return status.value
        return str(status).lower()  # 否则转为小写字符串
    
    failed_results = [r for r in test_results if get_status_str(r.status) in ["failed", "error"]]
    
    if not failed_results:
        return "所有测试用例均通过，未发现失败用例。"
    
    # 分析失败原因
    status_code_issues = [r for r in failed_results if r.error_message and "状态码不匹配" in r.error_message]
    timeout_issues = [r for r in failed_results if r.error_message and "timeout" in r.error_message.lower()]
    validation_issues = [r for r in failed_results if r.error_message and "验证失败" in r.error_message]
    other_issues = [r for r in failed_results if r not in status_code_issues + timeout_issues + validation_issues]
    
    analysis = f"共有{len(failed_results)}个测试用例失败，"
    
    if status_code_issues:
        analysis += f"其中{len(status_code_issues)}个是状态码不匹配问题，"
    
    if timeout_issues:
        analysis += f"{len(timeout_issues)}个是超时问题，"
    
    if validation_issues:
        analysis += f"{len(validation_issues)}个是响应内容验证失败，"
    
    if other_issues:
        analysis += f"{len(other_issues)}个是其他类型问题，"
    
    # 移除最后的逗号
    analysis = analysis.rstrip("，") + "。"
    
    # 添加具体失败用例信息
    if failed_results:
        analysis += " 失败的测试用例包括："
        for i, r in enumerate(failed_results[:3], 1):  # 只显示前3个
            test_case = next((tc for tc in test_cases if tc.get("id") == r.test_case_id), {})
            test_name = test_case.get("name", f"测试用例 {r.test_case_id}")
            analysis += f"\n{i}. {test_name}：{r.error_message or '未知错误'}"
        
        if len(failed_results) > 3:
            analysis += f"\n...以及其他{len(failed_results) - 3}个失败用例。"
    
    return analysis

def generate_recommendations(test_results: List[Any], test_cases: List[Dict[str, Any]]) -> List[str]:
    """生成建议"""
    recommendations = []
    
    # 处理状态，可能是字符串或枚举
    def get_status_str(status):
        if hasattr(status, 'value'):  # 如果是枚举
            return status.value
        return str(status).lower()  # 否则转为小写字符串
    
    # 基于测试结果生成建议
    failed_results = [r for r in test_results if get_status_str(r.status) in ["failed", "error"]]
    
    if failed_results:
        recommendations.append("修复失败的测试用例，特别关注状态码不匹配和响应验证失败的问题。")
    
    # 检查测试覆盖率
    methods = [tc.get("method", "").upper() for tc in test_cases if tc.get("method")]
    unique_methods = set(methods)
    common_methods = {"GET", "POST", "PUT", "DELETE", "PATCH"}
    missing_methods = common_methods - unique_methods
    
    if missing_methods:
        recommendations.append(f"增加对{', '.join(missing_methods)}方法的测试，提高API覆盖率。")
    
    # 检查性能问题
    response_times = [r.response_time for r in test_results if r.response_time is not None]
    if response_times and max(response_times) > 1000:
        recommendations.append("优化API性能，部分接口响应时间超过1秒，影响用户体验。")
    
    # 通用建议
    recommendations.append("考虑添加更多边界条件和异常情况的测试用例，提高测试的健壮性。")
    recommendations.append("定期执行回归测试，确保新功能不会影响现有功能。")
    
    return recommendations

def generate_test_case_insights(test_result: Any, test_cases: List[Dict[str, Any]]) -> str:
    """生成测试用例洞察"""
    test_case = next((tc for tc in test_cases if tc.get("id") == test_result.test_case_id), {})
    
    # 处理状态，可能是字符串或枚举
    def get_status_str(status):
        if hasattr(status, 'value'):  # 如果是枚举
            return status.value
        return str(status).lower()  # 否则转为小写字符串
    
    status = get_status_str(test_result.status)
    
    if status == "passed":
        return "测试通过，接口行为符合预期。"
    elif status == "failed":
        if test_result.error_message and "状态码不匹配" in test_result.error_message:
            expected = test_case.get("expected_status", "未知")
            actual = test_result.actual_status or "未知"
            return f"接口返回了非预期的状态码。期望：{expected}，实际：{actual}。可能是接口行为发生变化或测试预期需要更新。"
        else:
            return f"测试失败：{test_result.error_message or '未知原因'}。建议检查接口实现或测试用例设置。"
    elif status == "error":
        return f"测试执行出错：{test_result.error_message or '未知错误'}。可能是网络问题、超时或接口不可用。"
    else:  # skipped
        return "测试被跳过，未执行。"
