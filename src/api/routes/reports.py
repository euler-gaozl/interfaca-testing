"""
测试报告路由
"""
from fastapi import APIRouter, HTTPException
from src.models.schemas import APIResponse
from src.utils.logger import log

router = APIRouter()


@router.get("/", response_model=APIResponse)
async def list_reports():
    """获取测试报告列表"""
    try:
        return APIResponse(
            success=True,
            message="获取测试报告列表成功",
            data=[]
        )
    except Exception as e:
        log.error(f"获取测试报告列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
