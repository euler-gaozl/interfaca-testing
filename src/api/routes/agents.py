"""
智能体相关API路由
集成AutoGen、LangChain、FastAPI等智能体开发框架
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from enum import Enum

from src.agents.test_generator import TestCaseGeneratorAgent
from src.agents.test_analyzer import TestAnalyzerAgent
from src.agents.report_generator import ReportGeneratorAgent
from src.agents.autogen_agent import AutoGenMultiAgent, AutoGenTestOrchestrator
from src.agents.langchain_agent import LangChainTestAgent, LangChainWorkflow
from src.models.schemas import TestType
from src.utils.logger import log

router = APIRouter(prefix="/agents", tags=["智能体"])


class AgentFramework(str, Enum):
    """智能体框架类型"""
    BASIC = "basic"
    AUTOGEN = "autogen"
    LANGCHAIN = "langchain"


class ModelType(str, Enum):
    """AI模型类型"""
    OPENAI = "openai"
    CLAUDE = "claude"
    OLLAMA = "ollama"


@router.post("/generate-tests")
async def generate_test_cases(
    api_spec: Dict[str, Any],
    test_types: List[TestType] = [TestType.FUNCTIONAL],
    max_cases_per_endpoint: int = 5,
    model_type: ModelType = ModelType.OLLAMA,
    framework: AgentFramework = AgentFramework.BASIC
) -> Dict[str, Any]:
    """
    生成测试用例
    
    支持多种智能体框架：
    - basic: 基础单智能体
    - autogen: AutoGen多智能体协作
    - langchain: LangChain工具链智能体
    """
    try:
        log.info(f"使用{framework}框架和{model_type}模型生成测试用例")
        
        if framework == AgentFramework.BASIC:
            # 基础智能体
            generator = TestCaseGeneratorAgent(model_type.value)
            result = await generator.process({
                "project_id": 1,
                "api_spec": api_spec,
                "test_types": test_types,
                "max_cases_per_endpoint": max_cases_per_endpoint
            })
            
        elif framework == AgentFramework.AUTOGEN:
            # AutoGen多智能体协作
            autogen_agent = AutoGenMultiAgent(model_type.value)
            result = await autogen_agent.process({
                "project_id": 1,
                "api_spec": api_spec,
                "test_types": test_types,
                "max_cases_per_endpoint": max_cases_per_endpoint
            })
            
        elif framework == AgentFramework.LANGCHAIN:
            # LangChain工具链智能体
            langchain_agent = LangChainTestAgent(model_type.value)
            result = await langchain_agent.process({
                "project_id": 1,
                "api_spec": api_spec,
                "test_types": test_types,
                "max_cases_per_endpoint": max_cases_per_endpoint
            })
            
        else:
            raise HTTPException(status_code=400, detail=f"不支持的框架: {framework}")
        
        # 添加框架信息到结果中
        result["framework"] = framework.value
        result["model_type"] = model_type.value
        
        return result
        
    except Exception as e:
        log.error(f"生成测试用例失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autogen-orchestrate")
async def autogen_orchestrate_testing(
    api_spec: Dict[str, Any],
    model_type: ModelType = ModelType.OLLAMA
) -> Dict[str, Any]:
    """
    AutoGen多智能体编排测试
    
    使用多个专业智能体协作：
    - TestArchitect: 测试架构师
    - FunctionalTester: 功能测试专家
    - SecurityTester: 安全测试专家
    - PerformanceTester: 性能测试专家
    """
    try:
        log.info("启动AutoGen多智能体编排测试")
        
        orchestrator = AutoGenTestOrchestrator()
        result = await orchestrator.orchestrate_testing(api_spec)
        
        result["framework"] = "autogen"
        result["model_type"] = model_type.value
        
        return result
        
    except Exception as e:
        log.error(f"AutoGen编排测试失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/langchain-workflow")
async def langchain_workflow_execution(
    api_spec: Dict[str, Any],
    model_type: ModelType = ModelType.OLLAMA
) -> Dict[str, Any]:
    """
    LangChain工作流执行
    
    使用LangChain工具链：
    - api_analyzer: API规范分析器
    - security_scanner: 安全风险扫描器
    - performance_analyzer: 性能分析器
    - test_case_generator: 测试用例生成器
    """
    try:
        log.info("启动LangChain工作流执行")
        
        workflow = LangChainWorkflow()
        result = await workflow.execute_workflow(api_spec)
        
        result["framework"] = "langchain"
        result["model_type"] = model_type.value
        
        return result
        
    except Exception as e:
        log.error(f"LangChain工作流执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-results")
async def analyze_test_results(
    test_results: List[Dict[str, Any]],
    model_type: ModelType = ModelType.OLLAMA,
    framework: AgentFramework = AgentFramework.BASIC
) -> Dict[str, Any]:
    """分析测试结果"""
    try:
        log.info(f"使用{framework}框架分析测试结果")
        
        if framework == AgentFramework.BASIC:
            analyzer = TestAnalyzerAgent(model_type.value)
            result = await analyzer.process({
                "test_results": test_results,
                "analysis_type": "comprehensive"
            })
            
        elif framework == AgentFramework.AUTOGEN:
            # 可以扩展为AutoGen分析智能体
            analyzer = TestAnalyzerAgent(model_type.value)
            result = await analyzer.process({
                "test_results": test_results,
                "analysis_type": "autogen_collaborative"
            })
            
        elif framework == AgentFramework.LANGCHAIN:
            # 可以扩展为LangChain分析工具链
            analyzer = TestAnalyzerAgent(model_type.value)
            result = await analyzer.process({
                "test_results": test_results,
                "analysis_type": "langchain_tools"
            })
        
        result["framework"] = framework.value
        result["model_type"] = model_type.value
        
        return result
        
    except Exception as e:
        log.error(f"分析测试结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report")
async def generate_test_report(
    test_data: Dict[str, Any],
    report_type: str = "comprehensive",
    model_type: ModelType = ModelType.OLLAMA,
    framework: AgentFramework = AgentFramework.BASIC
) -> Dict[str, Any]:
    """生成测试报告"""
    try:
        log.info(f"使用{framework}框架生成测试报告")
        
        generator = ReportGeneratorAgent(model_type.value)
        
        result = await generator.process({
            "test_data": test_data,
            "report_type": report_type,
            "include_recommendations": True,
            "framework": framework.value
        })
        
        result["framework"] = framework.value
        result["model_type"] = model_type.value
        
        return result
        
    except Exception as e:
        log.error(f"生成测试报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/frameworks")
async def get_available_frameworks() -> Dict[str, Any]:
    """获取可用的智能体框架信息"""
    return {
        "frameworks": [
            {
                "name": "basic",
                "description": "基础单智能体，适合简单测试用例生成",
                "features": ["单智能体", "快速响应", "基础功能"],
                "use_cases": ["快速原型", "简单API测试", "基础功能验证"]
            },
            {
                "name": "autogen",
                "description": "AutoGen多智能体协作系统",
                "features": ["多智能体协作", "专业分工", "群体智能"],
                "use_cases": ["复杂系统测试", "全面质量保证", "专业测试策略"],
                "agents": [
                    "TestArchitect - 测试架构师",
                    "FunctionalTester - 功能测试专家", 
                    "SecurityTester - 安全测试专家",
                    "PerformanceTester - 性能测试专家"
                ]
            },
            {
                "name": "langchain",
                "description": "LangChain工具链智能体系统",
                "features": ["工具链集成", "模块化分析", "可扩展架构"],
                "use_cases": ["深度分析", "工具集成", "自定义工作流"],
                "tools": [
                    "api_analyzer - API规范分析器",
                    "security_scanner - 安全风险扫描器",
                    "performance_analyzer - 性能分析器",
                    "test_case_generator - 测试用例生成器"
                ]
            }
        ],
        "models": [
            {
                "name": "openai",
                "description": "OpenAI GPT模型",
                "status": "需要API密钥"
            },
            {
                "name": "claude",
                "description": "Anthropic Claude模型",
                "status": "需要API密钥"
            },
            {
                "name": "ollama",
                "description": "本地Ollama模型",
                "status": "本地部署，数据安全"
            }
        ]
    }


@router.get("/health")
async def agent_health_check() -> Dict[str, Any]:
    """智能体系统健康检查"""
    try:
        # 检查各个框架的可用性
        health_status = {
            "basic_agent": "healthy",
            "autogen_available": False,
            "langchain_available": False,
            "models": {
                "ollama": "unknown",
                "openai": "unknown",
                "claude": "unknown"
            }
        }
        
        # 检查AutoGen
        try:
            from src.agents.autogen_agent import AUTOGEN_AVAILABLE
            health_status["autogen_available"] = AUTOGEN_AVAILABLE
        except:
            health_status["autogen_available"] = False
        
        # 检查LangChain
        try:
            from src.agents.langchain_agent import LANGCHAIN_AVAILABLE
            health_status["langchain_available"] = LANGCHAIN_AVAILABLE
        except:
            health_status["langchain_available"] = False
        
        # 检查Ollama连接
        try:
            from src.agents.base_agent import test_ollama_connection
            from src.config.settings import settings
            
            ollama_status = await test_ollama_connection(
                settings.ai_models.ollama_base_url,
                settings.ai_models.ollama_model
            )
            health_status["models"]["ollama"] = "healthy" if ollama_status else "unavailable"
        except:
            health_status["models"]["ollama"] = "error"
        
        return {
            "status": "healthy",
            "timestamp": "2025-01-15T00:10:00Z",
            "details": health_status
        }
        
    except Exception as e:
        log.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/compare-frameworks")
async def compare_frameworks(
    api_spec: Dict[str, Any],
    test_types: List[TestType] = [TestType.FUNCTIONAL],
    model_type: ModelType = ModelType.OLLAMA
) -> Dict[str, Any]:
    """
    对比不同智能体框架的效果
    
    同时使用多个框架生成测试用例，便于对比分析
    """
    try:
        log.info("开始对比不同智能体框架")
        
        results = {}
        
        # 基础智能体
        try:
            basic_agent = TestCaseGeneratorAgent(model_type.value)
            basic_result = await basic_agent.process({
                "project_id": 1,
                "api_spec": api_spec,
                "test_types": test_types,
                "max_cases_per_endpoint": 3
            })
            results["basic"] = {
                "success": basic_result.get("success", False),
                "test_cases_count": len(basic_result.get("test_cases", [])),
                "framework": "basic"
            }
        except Exception as e:
            results["basic"] = {"success": False, "error": str(e)}
        
        # AutoGen智能体
        try:
            autogen_agent = AutoGenMultiAgent(model_type.value)
            autogen_result = await autogen_agent.process({
                "project_id": 1,
                "api_spec": api_spec,
                "test_types": test_types,
                "max_cases_per_endpoint": 3
            })
            results["autogen"] = {
                "success": autogen_result.get("success", False),
                "test_cases_count": len(autogen_result.get("test_cases", [])),
                "framework": "autogen",
                "agents_involved": autogen_result.get("agents_involved", [])
            }
        except Exception as e:
            results["autogen"] = {"success": False, "error": str(e)}
        
        # LangChain智能体
        try:
            langchain_agent = LangChainTestAgent(model_type.value)
            langchain_result = await langchain_agent.process({
                "project_id": 1,
                "api_spec": api_spec,
                "test_types": test_types,
                "max_cases_per_endpoint": 3
            })
            results["langchain"] = {
                "success": langchain_result.get("success", False),
                "test_cases_count": len(langchain_result.get("test_cases", [])),
                "framework": "langchain",
                "tools_used": langchain_result.get("tools_used", [])
            }
        except Exception as e:
            results["langchain"] = {"success": False, "error": str(e)}
        
        # 生成对比分析
        comparison = {
            "total_frameworks_tested": len(results),
            "successful_frameworks": len([r for r in results.values() if r.get("success", False)]),
            "model_type": model_type.value,
            "results": results,
            "recommendation": _generate_framework_recommendation(results)
        }
        
        return comparison
        
    except Exception as e:
        log.error(f"框架对比失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_framework_recommendation(results: Dict[str, Any]) -> str:
    """生成框架推荐"""
    successful = [name for name, result in results.items() if result.get("success", False)]
    
    if not successful:
        return "所有框架都遇到问题，建议检查配置和依赖"
    
    if len(successful) == 1:
        return f"推荐使用 {successful[0]} 框架"
    
    # 根据测试用例数量和特性推荐
    best_count = max(results[name].get("test_cases_count", 0) for name in successful)
    best_frameworks = [name for name in successful if results[name].get("test_cases_count", 0) == best_count]
    
    if "autogen" in best_frameworks:
        return "推荐使用 AutoGen 框架，适合复杂协作场景"
    elif "langchain" in best_frameworks:
        return "推荐使用 LangChain 框架，适合工具链集成"
    else:
        return f"推荐使用 {best_frameworks[0]} 框架"
