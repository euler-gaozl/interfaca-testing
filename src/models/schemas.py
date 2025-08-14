"""
Pydantic数据模型 - Python 3.10兼容
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

class TestStatus(str, Enum):
    """测试状态枚举"""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"

class TestType(str, Enum):
    """测试类型枚举"""
    FUNCTIONAL = "functional"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"

class Priority(str, Enum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HTTPMethod(str, Enum):
    """HTTP方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

# 基础模型
class BaseSchema(BaseModel):
    """基础模型"""
    class Config:
        from_attributes = True

# 项目相关模型
class TestProjectBase(BaseSchema):
    """测试项目基础模型"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    base_url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    auth_config: Optional[Dict[str, Any]] = None

class TestProjectCreate(TestProjectBase):
    """创建测试项目模型"""
    api_spec: Optional[Dict[str, Any]] = None

class TestProject(TestProjectBase):
    """测试项目模型"""
    id: int
    api_spec: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

# 测试用例相关模型
class TestCaseBase(BaseSchema):
    """测试用例基础模型"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    method: HTTPMethod
    endpoint: str = Field(..., min_length=1, max_length=500)
    headers: Optional[Dict[str, str]] = None
    query_params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    expected_status: int = Field(200, ge=100, le=599)
    expected_response: Optional[Dict[str, Any]] = None
    test_type: TestType = TestType.FUNCTIONAL
    priority: Priority = Priority.MEDIUM
    tags: Optional[List[str]] = None

class TestCaseCreate(TestCaseBase):
    """创建测试用例模型"""
    project_id: int

class TestCase(TestCaseBase):
    """测试用例模型"""
    id: int
    project_id: int
    ai_generated: bool
    created_at: datetime
    updated_at: datetime
    is_active: bool

# 测试执行相关模型
class TestExecutionResult(BaseSchema):
    """测试执行结果"""
    test_case_id: int
    status: TestStatus
    response_time: Optional[float] = None
    actual_status: Optional[int] = None
    actual_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

class TestBatchExecution(BaseSchema):
    """批量测试执行"""
    execution_id: str
    project_id: int
    test_case_ids: List[int]
    results: List[TestExecutionResult] = []
    summary: Optional[Dict[str, Any]] = None

# API规范相关模型
class APISpecUpload(BaseSchema):
    """API规范上传"""
    project_id: int
    spec_type: str = Field(..., pattern="^(openapi|swagger|postman)$")
    spec_content: Dict[str, Any]

class GenerateTestCasesRequest(BaseSchema):
    """生成测试用例请求"""
    project_id: int
    test_types: List[TestType] = [TestType.FUNCTIONAL]
    include_security: bool = True
    include_performance: bool = False
    max_cases_per_endpoint: int = 5

class AIAnalysisRequest(BaseSchema):
    """AI分析请求"""
    execution_id: str
    analysis_type: str = Field(..., pattern="^(summary|detailed|security|performance)$")

class AIAnalysisResult(BaseSchema):
    """AI分析结果"""
    execution_id: str
    analysis_type: str
    summary: str
    insights: List[str]
    recommendations: List[str]
    risk_assessment: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None

# 报告相关模型
class ReportRequest(BaseSchema):
    """报告生成请求"""
    execution_id: str
    format: str = Field("html", pattern="^(html|json|pdf)$")
    include_ai_analysis: bool = True
    template: Optional[str] = None

class ReportResponse(BaseSchema):
    """报告响应"""
    report_id: int
    file_path: str
    download_url: str
    created_at: datetime

# 响应模型
class APIResponse(BaseSchema):
    """通用API响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    error: Optional[str] = None

class PaginatedResponse(BaseSchema):
    """分页响应"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
