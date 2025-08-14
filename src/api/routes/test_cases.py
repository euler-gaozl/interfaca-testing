"""
测试用例管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

from src.models.schemas import (
    APIResponse, TestCase, TestCaseCreate, TestCaseBase
)
from src.utils.logger import log

router = APIRouter()

# 模拟数据存储
test_cases_db = {}
test_case_id_counter = 1


@router.get("/", response_model=APIResponse)
async def list_test_cases(project_id: Optional[int] = None):
    """获取测试用例列表"""
    try:
        test_cases = list(test_cases_db.values())
        
        if project_id:
            test_cases = [tc for tc in test_cases if tc.get("project_id") == project_id]
        
        return APIResponse(
            success=True,
            message="获取测试用例列表成功",
            data=test_cases
        )
    except Exception as e:
        log.error(f"获取测试用例列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{test_case_id}", response_model=APIResponse)
async def get_test_case(test_case_id: int):
    """获取测试用例详情"""
    try:
        if test_case_id not in test_cases_db:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        
        test_case = test_cases_db[test_case_id]
        return APIResponse(
            success=True,
            message="获取测试用例详情成功",
            data=test_case
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"获取测试用例详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=APIResponse)
async def create_test_case(test_case: TestCaseCreate):
    """创建测试用例"""
    try:
        global test_case_id_counter
        
        # 创建新测试用例
        new_test_case = {
            "id": test_case_id_counter,
            "project_id": test_case.project_id,
            "name": test_case.name,
            "description": test_case.description,
            "method": test_case.method,
            "endpoint": test_case.endpoint,
            "headers": test_case.headers or {},
            "query_params": test_case.query_params or {},
            "body": test_case.body or {},
            "expected_status": test_case.expected_status,
            "expected_response": test_case.expected_response or {},
            "test_type": test_case.test_type,
            "priority": test_case.priority,
            "tags": test_case.tags or [],
            "ai_generated": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        }
        
        test_cases_db[test_case_id_counter] = new_test_case
        test_case_id_counter += 1
        
        log.info(f"创建测试用例成功: {test_case.name}")
        
        return APIResponse(
            success=True,
            message="测试用例创建成功",
            data=new_test_case
        )
        
    except Exception as e:
        log.error(f"创建测试用例失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{test_case_id}", response_model=APIResponse)
async def update_test_case(test_case_id: int, test_case_update: TestCaseBase):
    """更新测试用例"""
    try:
        if test_case_id not in test_cases_db:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        
        test_case = test_cases_db[test_case_id]
        
        # 更新测试用例信息
        if test_case_update.name:
            test_case["name"] = test_case_update.name
        if test_case_update.description is not None:
            test_case["description"] = test_case_update.description
        if test_case_update.method:
            test_case["method"] = test_case_update.method
        if test_case_update.endpoint:
            test_case["endpoint"] = test_case_update.endpoint
        if test_case_update.headers is not None:
            test_case["headers"] = test_case_update.headers
        if test_case_update.query_params is not None:
            test_case["query_params"] = test_case_update.query_params
        if test_case_update.body is not None:
            test_case["body"] = test_case_update.body
        if test_case_update.expected_status:
            test_case["expected_status"] = test_case_update.expected_status
        if test_case_update.expected_response is not None:
            test_case["expected_response"] = test_case_update.expected_response
        if test_case_update.test_type:
            test_case["test_type"] = test_case_update.test_type
        if test_case_update.priority:
            test_case["priority"] = test_case_update.priority
        if test_case_update.tags is not None:
            test_case["tags"] = test_case_update.tags
        
        test_case["updated_at"] = datetime.now()
        
        log.info(f"更新测试用例成功: {test_case['name']}")
        
        return APIResponse(
            success=True,
            message="测试用例更新成功",
            data=test_case
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"更新测试用例失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{test_case_id}", response_model=APIResponse)
async def delete_test_case(test_case_id: int):
    """删除测试用例"""
    try:
        if test_case_id not in test_cases_db:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        
        test_case = test_cases_db[test_case_id]
        test_case["is_active"] = False
        test_case["updated_at"] = datetime.now()
        
        log.info(f"删除测试用例成功: {test_case['name']}")
        
        return APIResponse(
            success=True,
            message="测试用例删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"删除测试用例失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=APIResponse)
async def create_batch_test_cases(test_cases: List[TestCaseCreate]):
    """批量创建测试用例"""
    try:
        global test_case_id_counter
        created_cases = []
        
        for test_case in test_cases:
            new_test_case = {
                "id": test_case_id_counter,
                "project_id": test_case.project_id,
                "name": test_case.name,
                "description": test_case.description,
                "method": test_case.method,
                "endpoint": test_case.endpoint,
                "headers": test_case.headers or {},
                "query_params": test_case.query_params or {},
                "body": test_case.body or {},
                "expected_status": test_case.expected_status,
                "expected_response": test_case.expected_response or {},
                "test_type": test_case.test_type,
                "priority": test_case.priority,
                "tags": test_case.tags or [],
                "ai_generated": getattr(test_case, 'ai_generated', True),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_active": True
            }
            
            test_cases_db[test_case_id_counter] = new_test_case
            created_cases.append(new_test_case)
            test_case_id_counter += 1
        
        log.info(f"批量创建测试用例成功: {len(created_cases)} 个")
        
        return APIResponse(
            success=True,
            message=f"成功创建 {len(created_cases)} 个测试用例",
            data=created_cases
        )
        
    except Exception as e:
        log.error(f"批量创建测试用例失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
