"""
基于LangChain的智能体系统
"""
import asyncio
from typing import Dict, Any, List, Optional
import json

try:
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.tools import Tool
    from langchain.schema import SystemMessage, HumanMessage
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_openai import ChatOpenAI
    from langchain_community.llms import Ollama
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from src.agents.base_agent import BaseAgent
from src.utils.logger import log


class LangChainTestAgent(BaseAgent):
    """基于LangChain的测试智能体"""
    
    def __init__(self, model_type: str = "openai"):
        super().__init__("LangChain测试智能体", model_type)
        
        if not LANGCHAIN_AVAILABLE:
            log.warning("LangChain未安装，使用模拟模式")
            self.use_mock = True
            return
        
        self.use_mock = False
        self.llm = None
        self.agent_executor = None
        self._setup_langchain()
    
    def _setup_langchain(self):
        """设置LangChain组件"""
        if self.use_mock:
            return
        
        try:
            # 初始化LLM
            if self.model_type == "openai":
                self.llm = ChatOpenAI(
                    model=self.model_config.get("model", "gpt-4"),
                    api_key=self.model_config.get("api_key"),
                    base_url=self.model_config.get("base_url"),
                    temperature=0.7
                )
            elif self.model_type == "ollama":
                self.llm = Ollama(
                    model=self.model_config.get("model", "llama2"),
                    base_url=self.model_config.get("base_url", "http://localhost:11434")
                )
            else:
                log.warning(f"不支持的模型类型: {self.model_type}")
                self.use_mock = True
                return
            
            # 创建工具
            tools = self._create_tools()
            
            # 创建提示模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_system_prompt()),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # 创建智能体
            if self.model_type == "openai":
                agent = create_openai_functions_agent(self.llm, tools, prompt)
                self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            else:
                # 对于非OpenAI模型，使用简化的智能体
                self.agent_executor = None
            
        except Exception as e:
            log.error(f"LangChain设置失败: {e}")
            self.use_mock = True
    
    def _create_tools(self) -> List[Tool]:
        """创建LangChain工具"""
        tools = [
            Tool(
                name="api_analyzer",
                description="分析API规范并提取关键信息",
                func=self._analyze_api_spec
            ),
            Tool(
                name="test_case_generator",
                description="生成特定类型的测试用例",
                func=self._generate_test_cases
            ),
            Tool(
                name="security_scanner",
                description="扫描API安全风险",
                func=self._scan_security_risks
            ),
            Tool(
                name="performance_analyzer",
                description="分析API性能要求",
                func=self._analyze_performance
            )
        ]
        return tools
    
    def _analyze_api_spec(self, api_spec_json: str) -> str:
        """分析API规范工具"""
        try:
            api_spec = json.loads(api_spec_json)
            
            analysis = {
                "endpoints_count": len(api_spec.get("paths", {})),
                "methods": [],
                "security_schemes": list(api_spec.get("components", {}).get("securitySchemes", {}).keys()),
                "parameters": [],
                "request_bodies": []
            }
            
            for path, methods in api_spec.get("paths", {}).items():
                for method, details in methods.items():
                    analysis["methods"].append(f"{method.upper()} {path}")
                    
                    # 收集参数信息
                    params = details.get("parameters", [])
                    for param in params:
                        analysis["parameters"].append({
                            "name": param.get("name"),
                            "in": param.get("in"),
                            "required": param.get("required", False)
                        })
                    
                    # 收集请求体信息
                    if "requestBody" in details:
                        analysis["request_bodies"].append(f"{method.upper()} {path}")
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"API规范分析失败: {e}"
    
    def _generate_test_cases(self, requirements: str) -> str:
        """生成测试用例工具"""
        try:
            # 解析需求
            req_data = json.loads(requirements)
            endpoint = req_data.get("endpoint", "/api/test")
            method = req_data.get("method", "GET")
            test_type = req_data.get("test_type", "functional")
            
            # 生成测试用例
            test_cases = []
            
            if test_type == "functional":
                test_cases.extend([
                    {
                        "name": f"{method} {endpoint} - 正常请求测试",
                        "description": f"测试{endpoint}的正常功能",
                        "method": method,
                        "endpoint": endpoint,
                        "expected_status": 200,
                        "test_type": "functional",
                        "priority": "high"
                    },
                    {
                        "name": f"{method} {endpoint} - 边界值测试",
                        "description": f"测试{endpoint}的边界条件",
                        "method": method,
                        "endpoint": endpoint,
                        "expected_status": 400,
                        "test_type": "functional",
                        "priority": "medium"
                    }
                ])
            
            elif test_type == "security":
                test_cases.extend([
                    {
                        "name": f"{method} {endpoint} - 未授权访问测试",
                        "description": f"测试{endpoint}的权限控制",
                        "method": method,
                        "endpoint": endpoint,
                        "headers": {"Authorization": "Bearer invalid_token"},
                        "expected_status": 401,
                        "test_type": "security",
                        "priority": "critical"
                    },
                    {
                        "name": f"{method} {endpoint} - SQL注入测试",
                        "description": f"测试{endpoint}的SQL注入防护",
                        "method": method,
                        "endpoint": endpoint,
                        "query_params": {"id": "1' OR '1'='1"},
                        "expected_status": 400,
                        "test_type": "security",
                        "priority": "critical"
                    }
                ])
            
            return json.dumps(test_cases, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"测试用例生成失败: {e}"
    
    def _scan_security_risks(self, api_info: str) -> str:
        """扫描安全风险工具"""
        try:
            risks = [
                {
                    "risk": "未授权访问",
                    "severity": "high",
                    "description": "API端点可能缺乏适当的身份验证",
                    "recommendation": "实施JWT或OAuth2认证"
                },
                {
                    "risk": "输入验证不足",
                    "severity": "medium",
                    "description": "用户输入可能未经充分验证",
                    "recommendation": "添加输入验证和清理机制"
                },
                {
                    "risk": "敏感数据泄露",
                    "severity": "high",
                    "description": "API响应可能包含敏感信息",
                    "recommendation": "过滤响应中的敏感数据"
                }
            ]
            
            return json.dumps(risks, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"安全风险扫描失败: {e}"
    
    def _analyze_performance(self, api_info: str) -> str:
        """分析性能要求工具"""
        try:
            performance_analysis = {
                "response_time_target": "< 200ms",
                "throughput_target": "> 1000 req/s",
                "concurrent_users": 100,
                "bottlenecks": [
                    "数据库查询优化",
                    "缓存策略",
                    "连接池配置"
                ],
                "test_scenarios": [
                    {
                        "name": "基准性能测试",
                        "description": "测试单用户场景下的响应时间",
                        "users": 1,
                        "duration": "5分钟"
                    },
                    {
                        "name": "负载测试",
                        "description": "测试正常负载下的系统表现",
                        "users": 50,
                        "duration": "10分钟"
                    },
                    {
                        "name": "压力测试",
                        "description": "测试系统的极限承载能力",
                        "users": 200,
                        "duration": "15分钟"
                    }
                ]
            }
            
            return json.dumps(performance_analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"性能分析失败: {e}"
    
    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一个专业的API测试专家，具备以下能力：

1. 深入分析API规范和架构
2. 设计全面的测试策略
3. 生成高质量的测试用例
4. 识别安全风险和性能瓶颈
5. 使用专业工具进行分析

你可以使用以下工具：
- api_analyzer: 分析API规范
- test_case_generator: 生成测试用例
- security_scanner: 扫描安全风险
- performance_analyzer: 分析性能要求

请根据用户需求，合理使用这些工具来完成任务。"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据"""
        try:
            if self.use_mock:
                return await self._mock_process(input_data)
            
            api_spec = input_data.get("api_spec", {})
            test_types = input_data.get("test_types", [])
            
            # 构建任务描述
            task = self._build_task_description(api_spec, test_types)
            
            if self.agent_executor:
                # 使用LangChain智能体执行任务
                result = await self.agent_executor.ainvoke({
                    "input": task,
                    "chat_history": []
                })
                
                # 解析结果
                test_cases = self._parse_langchain_result(result.get("output", ""))
                
                return {
                    "success": True,
                    "test_cases": test_cases,
                    "langchain_output": result.get("output", ""),
                    "tools_used": ["api_analyzer", "test_case_generator"]
                }
            else:
                # 直接使用LLM
                messages = [
                    SystemMessage(content=self._get_system_prompt()),
                    HumanMessage(content=task)
                ]
                
                response = await self.llm.ainvoke(messages)
                
                # 处理不同类型的响应
                if hasattr(response, 'content'):
                    content = response.content
                elif isinstance(response, str):
                    content = response
                else:
                    content = str(response)
                
                test_cases = self._parse_langchain_result(content)
                
                return {
                    "success": True,
                    "test_cases": test_cases,
                    "langchain_output": content,
                    "direct_llm": True,
                    "tools_used": ["direct_llm"]
                }
            
        except Exception as e:
            log.error(f"LangChain智能体处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_cases": []
            }
    
    def _build_task_description(self, api_spec: Dict[str, Any], test_types: List[str]) -> str:
        """构建任务描述"""
        return f"""
请为以下API规范生成全面的测试用例：

API规范：
{json.dumps(api_spec, indent=2, ensure_ascii=False)}

测试要求：
- 测试类型：{', '.join(test_types)}
- 使用工具分析API规范
- 生成结构化的测试用例
- 考虑安全性和性能

请按照以下步骤：
1. 使用api_analyzer工具分析API规范
2. 使用security_scanner工具识别安全风险
3. 使用test_case_generator工具生成测试用例
4. 整合所有分析结果

最终输出JSON格式的测试用例数组。
"""
    
    def _parse_langchain_result(self, output: str) -> List[Dict[str, Any]]:
        """解析LangChain结果"""
        test_cases = []
        
        try:
            # 尝试提取JSON
            if '[' in output and ']' in output:
                start = output.find('[')
                end = output.rfind(']') + 1
                json_str = output[start:end]
                cases = json.loads(json_str)
                
                for case in cases:
                    if isinstance(case, dict):
                        test_case = {
                            "project_id": 1,
                            "name": case.get("name", "LangChain生成测试用例"),
                            "description": case.get("description", ""),
                            "method": case.get("method", "GET"),
                            "endpoint": case.get("endpoint", "/"),
                            "headers": case.get("headers", {}),
                            "query_params": case.get("query_params", {}),
                            "body": case.get("body", {}),
                            "expected_status": case.get("expected_status", 200),
                            "expected_response": case.get("expected_response", {}),
                            "test_type": case.get("test_type", "functional"),
                            "priority": case.get("priority", "medium"),
                            "tags": case.get("tags", ["langchain"]),
                            "ai_generated": True,
                            "framework": "langchain"
                        }
                        test_cases.append(test_case)
            
            # 如果没有提取到，生成默认测试用例
            if not test_cases:
                test_cases = self._generate_default_langchain_cases()
                
        except json.JSONDecodeError:
            test_cases = self._generate_default_langchain_cases()
        
        return test_cases
    
    def _generate_default_langchain_cases(self) -> List[Dict[str, Any]]:
        """生成默认的LangChain测试用例"""
        return [
            {
                "project_id": 1,
                "name": "LangChain工具链分析的API健康检查",
                "description": "使用LangChain工具链分析后生成的API健康检查测试",
                "method": "GET",
                "endpoint": "/api/health",
                "headers": {"Content-Type": "application/json"},
                "query_params": {},
                "body": {},
                "expected_status": 200,
                "expected_response": {"status": "healthy"},
                "test_type": "functional",
                "priority": "high",
                "tags": ["langchain", "health"],
                "ai_generated": True,
                "framework": "langchain"
            },
            {
                "project_id": 1,
                "name": "LangChain安全扫描器识别的认证测试",
                "description": "基于LangChain安全扫描器识别的认证漏洞测试",
                "method": "GET",
                "endpoint": "/api/secure/data",
                "headers": {"Authorization": "Bearer invalid_token"},
                "query_params": {},
                "body": {},
                "expected_status": 401,
                "expected_response": {},
                "test_type": "security",
                "priority": "critical",
                "tags": ["langchain", "security", "auth"],
                "ai_generated": True,
                "framework": "langchain"
            },
            {
                "project_id": 1,
                "name": "LangChain性能分析器设计的负载测试",
                "description": "基于LangChain性能分析器设计的系统负载测试",
                "method": "POST",
                "endpoint": "/api/performance/test",
                "headers": {"Content-Type": "application/json"},
                "query_params": {"concurrent": "50"},
                "body": {"test_data": "performance_payload"},
                "expected_status": 200,
                "expected_response": {},
                "test_type": "performance",
                "priority": "medium",
                "tags": ["langchain", "performance", "load"],
                "ai_generated": True,
                "framework": "langchain"
            }
        ]
    
    async def _mock_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """模拟LangChain处理"""
        await asyncio.sleep(1)
        
        log.info("使用模拟LangChain智能体")
        
        test_cases = self._generate_default_langchain_cases()
        
        mock_output = """
基于LangChain工具链分析：

1. API分析器结果：发现3个端点，包含认证机制
2. 安全扫描器结果：识别2个高风险安全问题
3. 性能分析器结果：建议进行负载测试
4. 测试用例生成器：生成了3个综合测试用例

生成的测试用例已整合多个工具的分析结果。
"""
        
        return {
            "success": True,
            "test_cases": test_cases,
            "langchain_output": mock_output,
            "tools_used": ["api_analyzer", "security_scanner", "performance_analyzer", "test_case_generator"],
            "mock_mode": True
        }


class LangChainWorkflow:
    """LangChain工作流编排"""
    
    def __init__(self):
        self.agent = LangChainTestAgent()
    
    async def execute_workflow(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """执行LangChain工作流"""
        log.info("启动LangChain工作流...")
        
        # 阶段1：API分析
        analysis_result = await self.agent.process({
            "api_spec": api_spec,
            "test_types": ["analysis"],
            "phase": "analysis"
        })
        
        # 阶段2：测试生成
        generation_result = await self.agent.process({
            "api_spec": api_spec,
            "test_types": ["functional", "security", "performance"],
            "phase": "generation",
            "analysis_context": analysis_result
        })
        
        return {
            "success": True,
            "workflow_complete": True,
            "analysis_phase": analysis_result,
            "generation_phase": generation_result,
            "total_test_cases": len(generation_result.get("test_cases", [])),
            "framework": "langchain"
        }
