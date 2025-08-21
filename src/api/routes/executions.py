"""
测试执行路由
"""
import asyncio
import uuid
import httpx
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Path, Query, Depends

from src.models.schemas import (
    APIResponse, BatchExecutionRequest, TestBatchExecution, 
    TestExecutionResult, TestStatus, ExecutionStatus
)
from src.utils.logger import log
from src.config.settings import settings

# 模拟模式配置
MOCK_MODE = True  # 设置为True启用模拟模式，False使用真实HTTP请求

router = APIRouter()

# 模拟数据存储
executions_db: Dict[str, TestBatchExecution] = {}

# 获取测试用例数据
async def get_test_case(test_case_id: int) -> Optional[Dict[str, Any]]:
    """从测试用例API获取测试用例数据"""
    try:
        # 这里应该是从数据库或API获取测试用例数据
        # 为了演示，我们使用模拟数据
        from src.api.routes.test_cases import test_cases_db
        return test_cases_db.get(test_case_id)
    except Exception as e:
        log.error(f"获取测试用例失败: {e}")
        return None

@router.get("/", response_model=APIResponse)
async def list_executions(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """获取测试执行列表"""
    try:
        executions = list(executions_db.values())
        
        # 过滤条件
        if project_id:
            executions = [e for e in executions if e.project_id == project_id]
        if status:
            executions = [e for e in executions if e.status == status]
        
        # 分页
        total = len(executions)
        executions = executions[offset:offset+limit]
        
        return APIResponse(
            success=True,
            message="获取测试执行列表成功",
            data={
                "items": executions,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        log.error(f"获取测试执行列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=APIResponse)
async def create_batch_execution(
    request: BatchExecutionRequest,
    background_tasks: BackgroundTasks
):
    """创建批量测试执行任务"""
    try:
        # 生成唯一执行ID
        execution_id = str(uuid.uuid4())
        
        # 创建执行记录
        execution = TestBatchExecution(
            execution_id=execution_id,
            project_id=request.project_id,
            test_case_ids=request.test_case_ids,
            concurrent_limit=request.concurrent_limit,
            timeout=request.timeout,
            retry_count=request.retry_count,
            execution_strategy=request.execution_strategy,
            started_at=datetime.now(),
            status=ExecutionStatus.PENDING
        )
        
        # 保存到数据库
        executions_db[execution_id] = execution
        
        # 在后台执行测试
        background_tasks.add_task(
            execute_batch_tests,
            execution_id=execution_id,
            concurrent_limit=request.concurrent_limit,
            timeout=request.timeout,
            retry_count=request.retry_count,
            execution_strategy=request.execution_strategy
        )
        
        return APIResponse(
            success=True,
            message="批量测试执行任务已创建",
            data={"execution_id": execution_id}
        )
    except Exception as e:
        log.error(f"创建批量测试执行任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{execution_id}", response_model=APIResponse)
async def get_execution(
    execution_id: str = Path(..., description="执行ID")
):
    """获取测试执行详情"""
    try:
        if execution_id not in executions_db:
            raise HTTPException(status_code=404, detail="执行任务不存在")
        
        execution = executions_db[execution_id]
        
        return APIResponse(
            success=True,
            message="获取测试执行详情成功",
            data=execution
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"获取测试执行详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{execution_id}/results", response_model=APIResponse)
async def get_execution_results(
    execution_id: str = Path(..., description="执行ID")
):
    """获取测试执行结果"""
    try:
        if execution_id not in executions_db:
            raise HTTPException(status_code=404, detail="执行任务不存在")
        
        execution = executions_db[execution_id]
        
        # 计算结果统计
        total = len(execution.test_case_ids)
        completed = len(execution.results)
        passed = sum(1 for r in execution.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in execution.results if r.status == TestStatus.FAILED)
        error = sum(1 for r in execution.results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in execution.results if r.status == TestStatus.SKIPPED)
        
        # 计算平均响应时间
        response_times = [r.response_time for r in execution.results if r.response_time is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        summary = {
            "total": total,
            "completed": completed,
            "passed": passed,
            "failed": failed,
            "error": error,
            "skipped": skipped,
            "pass_rate": (passed / completed * 100) if completed > 0 else 0,
            "avg_response_time": avg_response_time
        }
        
        return APIResponse(
            success=True,
            message="获取测试执行结果成功",
            data={
                "execution_id": execution_id,
                "status": execution.status,
                "summary": summary,
                "results": execution.results
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"获取测试执行结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{execution_id}/stop", response_model=APIResponse)
async def stop_execution(
    execution_id: str = Path(..., description="执行ID")
):
    """停止测试执行"""
    try:
        if execution_id not in executions_db:
            raise HTTPException(status_code=404, detail="执行任务不存在")
        
        execution = executions_db[execution_id]
        
        if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
            return APIResponse(
                success=False,
                message=f"无法停止已{execution.status}的执行任务",
                error=f"当前状态: {execution.status}"
            )
        
        # 更新状态为停止
        execution.status = ExecutionStatus.STOPPED
        execution.completed_at = datetime.now()
        executions_db[execution_id] = execution
        
        return APIResponse(
            success=True,
            message="测试执行已停止"
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"停止测试执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 异步执行测试的后台任务
async def execute_batch_tests(
    execution_id: str,
    concurrent_limit: int,
    timeout: int,
    retry_count: int,
    execution_strategy: str
):
    """异步执行批量测试"""
    try:
        if execution_id not in executions_db:
            log.error(f"执行任务不存在: {execution_id}")
            return
        
        execution = executions_db[execution_id]
        
        # 更新状态为运行中
        execution.status = ExecutionStatus.RUNNING
        executions_db[execution_id] = execution
        
        log.info(f"开始执行批量测试: {execution_id}, 策略: {execution_strategy}")
        
        # 根据执行策略选择执行方式
        if execution_strategy == "parallel":
            await execute_parallel(execution_id, concurrent_limit, timeout, retry_count)
        elif execution_strategy == "serial":
            await execute_serial(execution_id, timeout, retry_count)
        else:  # mixed
            await execute_mixed(execution_id, concurrent_limit, timeout, retry_count)
        
        # 更新执行状态
        execution = executions_db[execution_id]
        
        # 如果已经被手动停止，不更新状态
        if execution.status != ExecutionStatus.STOPPED:
            # 检查是否有失败的测试
            has_failed = any(r.status in [TestStatus.FAILED, TestStatus.ERROR] for r in execution.results)
            
            execution.status = ExecutionStatus.FAILED if has_failed else ExecutionStatus.COMPLETED
            execution.completed_at = datetime.now()
            
            # 更新摘要
            total = len(execution.test_case_ids)
            completed = len(execution.results)
            passed = sum(1 for r in execution.results if r.status == TestStatus.PASSED)
            failed = sum(1 for r in execution.results if r.status == TestStatus.FAILED)
            error = sum(1 for r in execution.results if r.status == TestStatus.ERROR)
            skipped = sum(1 for r in execution.results if r.status == TestStatus.SKIPPED)
            
            # 计算平均响应时间
            response_times = [r.response_time for r in execution.results if r.response_time is not None]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            execution.summary = {
                "total": total,
                "completed": completed,
                "passed": passed,
                "failed": failed,
                "error": error,
                "skipped": skipped,
                "pass_rate": (passed / completed * 100) if completed > 0 else 0,
                "avg_response_time": avg_response_time
            }
            
            executions_db[execution_id] = execution
        
        log.info(f"批量测试执行完成: {execution_id}, 状态: {execution.status}")
        
    except Exception as e:
        log.error(f"执行批量测试失败: {e}")
        
        # 更新状态为失败
        if execution_id in executions_db:
            execution = executions_db[execution_id]
            execution.status = ExecutionStatus.FAILED
            execution.completed_at = datetime.now()
            executions_db[execution_id] = execution

# 并行执行测试
async def execute_parallel(execution_id: str, concurrent_limit: int, timeout: int, retry_count: int):
    """并行执行测试"""
    execution = executions_db[execution_id]
    
    # 创建任务列表
    tasks = []
    semaphore = asyncio.Semaphore(concurrent_limit)
    
    for test_case_id in execution.test_case_ids:
        # 检查是否已停止
        if executions_db[execution_id].status == ExecutionStatus.STOPPED:
            break
        
        # 创建执行任务
        task = execute_test_with_semaphore(
            semaphore, 
            execution_id, 
            test_case_id, 
            timeout, 
            retry_count
        )
        tasks.append(task)
    
    # 等待所有任务完成
    if tasks:
        await asyncio.gather(*tasks)

# 串行执行测试
async def execute_serial(execution_id: str, timeout: int, retry_count: int):
    """串行执行测试"""
    execution = executions_db[execution_id]
    
    for test_case_id in execution.test_case_ids:
        # 检查是否已停止
        if executions_db[execution_id].status == ExecutionStatus.STOPPED:
            break
        
        # 串行执行每个测试
        await execute_single_test(execution_id, test_case_id, timeout, retry_count)

# 混合执行测试（按优先级分组）
async def execute_mixed(execution_id: str, concurrent_limit: int, timeout: int, retry_count: int):
    """混合执行测试（先串行执行高优先级，再并行执行其他）"""
    execution = executions_db[execution_id]
    
    # 获取所有测试用例
    test_cases = []
    for test_case_id in execution.test_case_ids:
        test_case = await get_test_case(test_case_id)
        if test_case:
            test_cases.append(test_case)
    
    # 按优先级分组
    high_priority = [tc["id"] for tc in test_cases if tc.get("priority") in ["high", "critical"]]
    normal_priority = [tc["id"] for tc in test_cases if tc.get("priority") not in ["high", "critical"]]
    
    # 先串行执行高优先级测试
    for test_case_id in high_priority:
        # 检查是否已停止
        if executions_db[execution_id].status == ExecutionStatus.STOPPED:
            break
        
        await execute_single_test(execution_id, test_case_id, timeout, retry_count)
    
    # 再并行执行其他测试
    tasks = []
    semaphore = asyncio.Semaphore(concurrent_limit)
    
    for test_case_id in normal_priority:
        # 检查是否已停止
        if executions_db[execution_id].status == ExecutionStatus.STOPPED:
            break
        
        task = execute_test_with_semaphore(
            semaphore, 
            execution_id, 
            test_case_id, 
            timeout, 
            retry_count
        )
        tasks.append(task)
    
    # 等待所有任务完成
    if tasks:
        await asyncio.gather(*tasks)

# 使用信号量控制并发
async def execute_test_with_semaphore(semaphore, execution_id, test_case_id, timeout, retry_count):
    """使用信号量控制并发执行测试"""
    async with semaphore:
        await execute_single_test(execution_id, test_case_id, timeout, retry_count)

# 执行单个测试用例
async def execute_single_test(execution_id: str, test_case_id: int, timeout: int, retry_count: int):
    """执行单个测试用例"""
    # 获取测试用例
    test_case = await get_test_case(test_case_id)
    if not test_case:
        # 记录错误
        result = TestExecutionResult(
            test_case_id=test_case_id,
            status=TestStatus.ERROR,
            error_message="测试用例不存在",
            started_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        # 更新结果
        execution = executions_db[execution_id]
        execution.results.append(result)
        executions_db[execution_id] = execution
        return
    
    # 记录开始时间
    started_at = datetime.now()
    
    # 初始化结果
    result = TestExecutionResult(
        test_case_id=test_case_id,
        status=TestStatus.SKIPPED,
        started_at=started_at
    )
    
    # 获取项目信息
    project_id = test_case.get("project_id")
    
    # 这里应该从数据库获取项目信息
    # 为了演示，我们使用模拟数据
    base_url = "https://api.example.com"  # 应该从项目配置中获取
    
    # 构建请求URL
    endpoint = test_case.get("endpoint", "")
    url = f"{base_url}{endpoint}"
    
    # 获取请求参数
    method = test_case.get("method", "GET")
    headers = test_case.get("headers", {})
    query_params = test_case.get("query_params", {})
    body = test_case.get("body", {})
    expected_status = test_case.get("expected_status", 200)
    expected_response = test_case.get("expected_response", {})
    
    # 执行HTTP请求
    for attempt in range(retry_count + 1):
        try:
            log.info(f"执行测试: {test_case.get('name')}, 尝试 {attempt+1}/{retry_count+1}")
            
            # 获取项目信息 - 从项目API获取
            from src.api.routes.projects import projects_db
            project = projects_db.get(project_id, {})
            base_url = project.get("base_url", "https://httpbin.org")
            
            log.info(f"使用基础URL: {base_url}")
            
            # 构建完整URL
            endpoint = test_case.get("endpoint", "")
            url = f"{base_url}{endpoint}"
            log.info(f"请求URL: {url}")
            
            # 模拟模式 - 不发送真实HTTP请求
            if MOCK_MODE:
                log.info(f"模拟模式: 模拟请求 {method} {url}")
                # 模拟响应
                await asyncio.sleep(0.5)  # 模拟网络延迟
                
                # 根据测试用例类型生成模拟响应
                if "418" in url:  # 状态码测试
                    response_status = 418
                    response_json = {"message": "I'm a teapot"}
                else:
                    response_status = expected_status
                    response_json = {
                        "url": url,
                        "method": method,
                        "args": query_params,
                        "json": body,
                        "headers": headers,
                        "origin": "127.0.0.1",
                        "success": True
                    }
                
                # 计算响应时间
                response_time = 50.0  # 模拟50ms响应时间
                
                # 验证状态码
                if response_status == expected_status:
                    result.status = TestStatus.PASSED
                else:
                    result.status = TestStatus.FAILED
                    result.error_message = f"状态码不匹配: 期望 {expected_status}, 实际 {response_status}"
                
                # 记录响应信息
                result.response_time = response_time
                result.actual_status = response_status
                result.actual_response = response_json
                
                # 跳出重试循环
                break
            
            # 真实HTTP请求
            async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
                start_time = datetime.now()
                
                # 发送请求
                if method == "GET":
                    response = await client.get(url, headers=headers, params=query_params)
                elif method == "POST":
                    response = await client.post(url, headers=headers, params=query_params, json=body)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, params=query_params, json=body)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers, params=query_params)
                elif method == "PATCH":
                    response = await client.patch(url, headers=headers, params=query_params, json=body)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                # 计算响应时间
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000  # 毫秒
                
                # 解析响应
                try:
                    response_json = response.json()
                except:
                    response_json = {"text": response.text}
                
                # 验证状态码
                if response.status_code == expected_status:
                    # 验证响应内容（简单实现，实际应该更复杂）
                    validation_passed = True
                    
                    # 如果有期望的响应，进行验证
                    if expected_response:
                        # 这里应该实现更复杂的验证逻辑
                        # 简单起见，我们只检查响应中是否包含期望的键
                        for key in expected_response:
                            if key not in response_json:
                                validation_passed = False
                                break
                    
                    if validation_passed:
                        result.status = TestStatus.PASSED
                    else:
                        result.status = TestStatus.FAILED
                        result.error_message = "响应内容验证失败"
                else:
                    result.status = TestStatus.FAILED
                    result.error_message = f"状态码不匹配: 期望 {expected_status}, 实际 {response.status_code}"
                
                # 记录响应信息
                result.response_time = response_time
                result.actual_status = response.status_code
                result.actual_response = response_json
                
                # 如果成功，跳出重试循环
                if result.status == TestStatus.PASSED:
                    break
                
                # 如果失败但还有重试次数，继续重试
                if attempt < retry_count:
                    await asyncio.sleep(1)  # 重试前等待1秒
                
            # 如果执行到这里，说明请求成功发送（无论结果如何）
            # 不需要继续重试
            break
                
        except Exception as e:
            # 记录错误
            result.status = TestStatus.ERROR
            result.error_message = f"执行异常: {str(e)}"
            log.error(f"测试执行异常: {str(e)}")
            
            # 如果还有重试次数，继续重试
            if attempt < retry_count:
                await asyncio.sleep(1)  # 重试前等待1秒
            
    # 记录完成时间
    result.completed_at = datetime.now()
    
    # 更新结果
    execution = executions_db[execution_id]
    execution.results.append(result)
    executions_db[execution_id] = execution
    
    log.info(f"测试完成: {test_case.get('name')}, 状态: {result.status}")
