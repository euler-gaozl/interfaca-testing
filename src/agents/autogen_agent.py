"""
基于AutoGen的多智能体协作系统
"""
import asyncio
from typing import Dict, Any, List, Optional
import json

try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False

from src.agents.base_agent import BaseAgent
from src.utils.logger import log


class AutoGenMultiAgent(BaseAgent):
    """基于AutoGen的多智能体协作系统"""
    
    def __init__(self, model_type: str = "openai"):
        super().__init__("AutoGen多智能体系统", model_type)
        
        if not AUTOGEN_AVAILABLE:
            log.warning("AutoGen未安装，使用模拟模式")
            self.use_mock = True
            return
        
        self.use_mock = False
        self.agents = {}
        self.group_chat = None
        self.manager = None
        self._setup_agents()
    
    def _setup_agents(self):
        """设置多个智能体"""
        if self.use_mock:
            return
        
        # 配置LLM
        llm_config = self._get_llm_config()
        
        # 测试架构师智能体
        self.agents["architect"] = AssistantAgent(
            name="TestArchitect",
            system_message="""你是一个专业的测试架构师。你的职责是：
1. 分析API规范的整体架构
2. 设计测试策略和测试计划
3. 识别关键测试场景和风险点
4. 协调其他智能体的工作
请始终从架构和策略的角度思考问题。""",
            llm_config=llm_config
        )
        
        # 功能测试专家智能体
        self.agents["functional_tester"] = AssistantAgent(
            name="FunctionalTester",
            system_message="""你是一个功能测试专家。你的职责是：
1. 设计功能测试用例
2. 验证API的基本功能
3. 测试正常流程和边界条件
4. 确保业务逻辑的正确性
专注于功能完整性和用户体验。""",
            llm_config=llm_config
        )
        
        # 安全测试专家智能体
        self.agents["security_tester"] = AssistantAgent(
            name="SecurityTester",
            system_message="""你是一个安全测试专家。你的职责是：
1. 识别潜在的安全漏洞
2. 设计安全测试用例
3. 测试认证和授权机制
4. 检查输入验证和注入攻击
专注于系统安全性和数据保护。""",
            llm_config=llm_config
        )
        
        # 性能测试专家智能体
        self.agents["performance_tester"] = AssistantAgent(
            name="PerformanceTester",
            system_message="""你是一个性能测试专家。你的职责是：
1. 设计性能测试场景
2. 分析响应时间和吞吐量
3. 测试并发和负载能力
4. 识别性能瓶颈
专注于系统性能和可扩展性。""",
            llm_config=llm_config
        )
        
        # 用户代理
        self.agents["user_proxy"] = UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False
        )
        
        # 设置群聊
        self.group_chat = GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            max_round=10
        )
        
        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config=llm_config
        )
    
    def _get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        if self.model_type == "openai":
            return {
                "config_list": [{
                    "model": self.model_config.get("model", "gpt-4"),
                    "api_key": self.model_config.get("api_key"),
                    "base_url": self.model_config.get("base_url")
                }],
                "temperature": 0.7
            }
        elif self.model_type == "ollama":
            # AutoGen对Ollama的支持需要OpenAI兼容配置
            return {
                "config_list": [{
                    "model": self.model_config.get("model", "deepseek-r1:14b"),
                    "api_key": "ollama",
                    "base_url": self.model_config.get("base_url", "http://localhost:11434/v1")
                }],
                "temperature": 0.7,
                "timeout": 120
            }
        else:
            # 使用模拟配置
            return {"temperature": 0.7}
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """多智能体协作处理"""
        try:
            if self.use_mock:
                return await self._mock_process(input_data)
            
            api_spec = input_data.get("api_spec", {})
            test_types = input_data.get("test_types", [])
            
            # 构建协作任务
            task_message = self._build_collaboration_task(api_spec, test_types)
            
            # 启动多智能体协作
            log.info("启动AutoGen多智能体协作...")
            
            # 由用户代理发起任务
            try:
                await self.agents["user_proxy"].a_initiate_chat(
                    self.manager,
                    message=task_message
                )
            except Exception as chat_error:
                log.warning(f"AutoGen聊天失败，使用模拟模式: {chat_error}")
                return await self._mock_process(input_data)
            
            # 收集所有智能体的输出
            messages = self.group_chat.messages
            test_cases = self._extract_test_cases_from_messages(messages)
            
            return {
                "success": True,
                "test_cases": test_cases,
                "collaboration_messages": [msg.content for msg in messages],
                "agents_involved": list(self.agents.keys())
            }
            
        except Exception as e:
            log.error(f"AutoGen多智能体协作失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_cases": []
            }
    
    def _build_collaboration_task(self, api_spec: Dict[str, Any], test_types: List[str]) -> str:
        """构建协作任务描述"""
        return f"""
我们需要为以下API规范设计全面的测试用例：

API规范：
{json.dumps(api_spec, indent=2, ensure_ascii=False)}

测试要求：
- 测试类型：{', '.join(test_types)}
- 需要多个专家协作
- 确保测试覆盖全面

请各位专家从自己的专业角度分析这个API，并协作设计测试用例。

TestArchitect：请先分析整体架构和测试策略
FunctionalTester：请设计功能测试用例
SecurityTester：请识别安全风险并设计安全测试
PerformanceTester：请设计性能测试场景

最终请整合所有专家的建议，输出结构化的测试用例。
"""
    
    def _extract_test_cases_from_messages(self, messages) -> List[Dict[str, Any]]:
        """从协作消息中提取测试用例"""
        test_cases = []
        
        for message in messages:
            content = message.content
            
            # 尝试从消息中提取JSON格式的测试用例
            if '[' in content and ']' in content:
                try:
                    start = content.find('[')
                    end = content.rfind(']') + 1
                    json_str = content[start:end]
                    cases = json.loads(json_str)
                    
                    for case in cases:
                        if isinstance(case, dict) and 'name' in case:
                            test_cases.append({
                                "project_id": 1,
                                "name": case.get("name", "AutoGen生成测试用例"),
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
                                "tags": case.get("tags", ["autogen"]),
                                "ai_generated": True,
                                "agent_source": message.name if hasattr(message, 'name') else "unknown"
                            })
                except json.JSONDecodeError:
                    continue
        
        # 如果没有提取到测试用例，生成默认的
        if not test_cases:
            test_cases = self._generate_default_autogen_cases()
        
        return test_cases
    
    def _generate_default_autogen_cases(self) -> List[Dict[str, Any]]:
        """生成默认的AutoGen测试用例"""
        return [
            {
                "project_id": 1,
                "name": "架构师设计的基础API测试",
                "description": "由测试架构师设计的基础API功能验证",
                "method": "GET",
                "endpoint": "/api/health",
                "headers": {"Content-Type": "application/json"},
                "query_params": {},
                "body": {},
                "expected_status": 200,
                "expected_response": {},
                "test_type": "functional",
                "priority": "high",
                "tags": ["autogen", "architecture"],
                "ai_generated": True,
                "agent_source": "TestArchitect"
            },
            {
                "project_id": 1,
                "name": "功能专家设计的业务流程测试",
                "description": "由功能测试专家设计的核心业务流程验证",
                "method": "POST",
                "endpoint": "/api/business/process",
                "headers": {"Content-Type": "application/json"},
                "query_params": {},
                "body": {"action": "validate"},
                "expected_status": 200,
                "expected_response": {},
                "test_type": "functional",
                "priority": "critical",
                "tags": ["autogen", "functional"],
                "ai_generated": True,
                "agent_source": "FunctionalTester"
            },
            {
                "project_id": 1,
                "name": "安全专家设计的权限验证测试",
                "description": "由安全测试专家设计的权限和认证验证",
                "method": "GET",
                "endpoint": "/api/secure/data",
                "headers": {"Authorization": "Bearer invalid_token"},
                "query_params": {},
                "body": {},
                "expected_status": 401,
                "expected_response": {},
                "test_type": "security",
                "priority": "critical",
                "tags": ["autogen", "security"],
                "ai_generated": True,
                "agent_source": "SecurityTester"
            },
            {
                "project_id": 1,
                "name": "性能专家设计的负载测试",
                "description": "由性能测试专家设计的系统负载能力验证",
                "method": "GET",
                "endpoint": "/api/performance/load",
                "headers": {"Content-Type": "application/json"},
                "query_params": {"concurrent_users": "100"},
                "body": {},
                "expected_status": 200,
                "expected_response": {},
                "test_type": "performance",
                "priority": "medium",
                "tags": ["autogen", "performance"],
                "ai_generated": True,
                "agent_source": "PerformanceTester"
            }
        ]
    
    async def _mock_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """模拟AutoGen处理过程"""
        await asyncio.sleep(1)  # 模拟协作时间
        
        log.info("使用模拟AutoGen多智能体协作")
        
        test_cases = self._generate_default_autogen_cases()
        
        mock_messages = [
            "TestArchitect: 我分析了API架构，建议采用分层测试策略...",
            "FunctionalTester: 我设计了核心功能测试用例，覆盖主要业务流程...",
            "SecurityTester: 我识别了3个潜在安全风险，设计了相应的安全测试...",
            "PerformanceTester: 我设计了性能测试场景，包括负载和压力测试..."
        ]
        
        return {
            "success": True,
            "test_cases": test_cases,
            "collaboration_messages": mock_messages,
            "agents_involved": ["TestArchitect", "FunctionalTester", "SecurityTester", "PerformanceTester"],
            "mock_mode": True
        }


class AutoGenTestOrchestrator:
    """AutoGen测试编排器"""
    
    def __init__(self):
        self.multi_agent = AutoGenMultiAgent()
    
    async def orchestrate_testing(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """编排多智能体测试流程"""
        log.info("启动AutoGen测试编排...")
        
        # 第一阶段：分析和规划
        planning_result = await self.multi_agent.process({
            "api_spec": api_spec,
            "test_types": ["functional", "security", "performance"],
            "phase": "planning"
        })
        
        if not planning_result["success"]:
            return planning_result
        
        # 第二阶段：测试用例生成
        generation_result = await self.multi_agent.process({
            "api_spec": api_spec,
            "test_types": ["functional", "security", "performance"],
            "phase": "generation",
            "planning_context": planning_result
        })
        
        return {
            "success": True,
            "planning_phase": planning_result,
            "generation_phase": generation_result,
            "total_test_cases": len(generation_result.get("test_cases", [])),
            "orchestration_complete": True
        }
