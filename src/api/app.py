"""
FastAPI应用主文件
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback

from src.config.settings import settings
from src.utils.logger import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    log.info("🚀 AI接口测试框架启动中...")
    log.info(f"📊 服务运行在: http://{settings.server.host}:{settings.server.port}")
    
    yield
    
    # 关闭时执行
    log.info("🛑 AI接口测试框架关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    
    app = FastAPI(
        title="AI驱动的接口自动化测试框架",
        description="基于AI大模型和智能体的接口自动化测试系统",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        log.error(f"全局异常: {str(exc)}")
        log.error(f"异常详情: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "内部服务器错误",
                "message": str(exc) if settings.server.debug else "服务器内部错误",
                "type": type(exc).__name__
            }
        )
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "service": "AI接口测试框架"
        }
    
    # 根路径
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "欢迎使用AI驱动的接口自动化测试框架",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    # 注册路由
    register_routes(app)
    
    return app


def register_routes(app: FastAPI):
    """注册所有路由"""
    from src.api.routes import projects, test_cases, executions, reports, ai_analysis
    
    # 项目管理
    app.include_router(
        projects.router,
        prefix="/api/v1/projects",
        tags=["项目管理"]
    )
    
    # 测试用例管理
    app.include_router(
        test_cases.router,
        prefix="/api/v1/test-cases",
        tags=["测试用例"]
    )
    
    # 测试执行
    app.include_router(
        executions.router,
        prefix="/api/v1/executions",
        tags=["测试执行"]
    )
    
    # 报告管理
    app.include_router(
        reports.router,
        prefix="/api/v1/reports",
        tags=["测试报告"]
    )
    
    # AI分析
    app.include_router(
        ai_analysis.router,
        prefix="/api/v1/ai",
        tags=["AI分析"]
    )


# 创建应用实例供uvicorn使用
app = create_app()
