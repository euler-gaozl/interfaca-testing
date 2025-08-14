"""
项目管理路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

from src.models.schemas import (
    TestProject, TestProjectCreate, APIResponse,
    GenerateTestCasesRequest, APISpecUpload
)
from src.agents.test_generator import TestCaseGeneratorAgent
from src.utils.logger import log

router = APIRouter()

# 模拟数据存储（实际应用中应使用数据库）
projects_db = {}
project_id_counter = 1


@router.get("/", response_model=APIResponse)
async def list_projects():
    """获取项目列表"""
    try:
        projects = list(projects_db.values())
        return APIResponse(
            success=True,
            message="获取项目列表成功",
            data=projects
        )
    except Exception as e:
        log.error(f"获取项目列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=APIResponse)
async def create_project(project: TestProjectCreate):
    """创建新项目"""
    try:
        global project_id_counter
        
        # 检查项目名称是否已存在
        for existing_project in projects_db.values():
            if existing_project["name"] == project.name:
                raise HTTPException(status_code=400, detail="项目名称已存在")
        
        # 创建新项目
        new_project = {
            "id": project_id_counter,
            "name": project.name,
            "description": project.description,
            "base_url": project.base_url,
            "headers": project.headers or {},
            "auth_config": project.auth_config or {},
            "api_spec": project.api_spec or {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        }
        
        projects_db[project_id_counter] = new_project
        project_id_counter += 1
        
        log.info(f"创建项目成功: {project.name}")
        
        return APIResponse(
            success=True,
            message="项目创建成功",
            data=new_project
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"创建项目失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=APIResponse)
async def get_project(project_id: int):
    """获取项目详情"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        project = projects_db[project_id]
        return APIResponse(
            success=True,
            message="获取项目详情成功",
            data=project
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"获取项目详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{project_id}", response_model=APIResponse)
async def update_project(project_id: int, project_update: TestProjectCreate):
    """更新项目"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        project = projects_db[project_id]
        
        # 更新项目信息
        if project_update.name:
            project["name"] = project_update.name
        if project_update.description is not None:
            project["description"] = project_update.description
        if project_update.base_url is not None:
            project["base_url"] = project_update.base_url
        if project_update.headers is not None:
            project["headers"] = project_update.headers
        if project_update.auth_config is not None:
            project["auth_config"] = project_update.auth_config
        if project_update.api_spec is not None:
            project["api_spec"] = project_update.api_spec
        
        project["updated_at"] = datetime.now()
        
        log.info(f"更新项目成功: {project['name']}")
        
        return APIResponse(
            success=True,
            message="项目更新成功",
            data=project
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"更新项目失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}", response_model=APIResponse)
async def delete_project(project_id: int):
    """删除项目"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        project = projects_db[project_id]
        project["is_active"] = False
        project["updated_at"] = datetime.now()
        
        log.info(f"删除项目成功: {project['name']}")
        
        return APIResponse(
            success=True,
            message="项目删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"删除项目失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/upload-spec", response_model=APIResponse)
async def upload_api_spec(project_id: int, spec_upload: APISpecUpload):
    """上传API规范"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        project = projects_db[project_id]
        project["api_spec"] = {
            "type": spec_upload.spec_type,
            "content": spec_upload.spec_content,
            "uploaded_at": datetime.now().isoformat()
        }
        project["updated_at"] = datetime.now()
        
        log.info(f"上传API规范成功: 项目 {project['name']}, 类型 {spec_upload.spec_type}")
        
        return APIResponse(
            success=True,
            message="API规范上传成功",
            data=project["api_spec"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"上传API规范失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/generate-tests", response_model=APIResponse)
async def generate_test_cases(project_id: int, request: GenerateTestCasesRequest):
    """AI生成测试用例"""
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        project = projects_db[project_id]
        
        if not project.get("api_spec"):
            raise HTTPException(status_code=400, detail="项目尚未上传API规范")
        
        # 初始化测试用例生成智能体
        generator = TestCaseGeneratorAgent()
        
        # 准备输入数据
        input_data = {
            "project_id": project_id,
            "api_spec": project["api_spec"].get("content", {}),
            "test_types": request.test_types,
            "max_cases_per_endpoint": request.max_cases_per_endpoint
        }
        
        # 生成测试用例
        result = await generator.process(input_data)
        
        if result["success"]:
            log.info(f"AI生成测试用例成功: 项目 {project['name']}, 生成 {result['generated_count']} 个用例")
            
            return APIResponse(
                success=True,
                message=f"成功生成 {result['generated_count']} 个测试用例",
                data={
                    "test_cases": result["test_cases"],
                    "generated_count": result["generated_count"],
                    "ai_response": result.get("ai_response", "")
                }
            )
        else:
            raise HTTPException(status_code=500, detail=f"生成测试用例失败: {result.get('error', '未知错误')}")
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"生成测试用例失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
