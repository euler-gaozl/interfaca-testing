"""
测试用例生成智能体
"""
import json
from typing import Dict, Any, List
from datetime import datetime

from src.agents.base_agent import BaseAgent, get_ai_client
from src.models.schemas import TestType, HTTPMethod, Priority
from src.utils.logger import log


class TestCaseGeneratorAgent(BaseAgent):
    """测试用例生成智能体"""
    
    def __init__(self, model_type: str = "openai"):
        super().__init__("测试用例生成专家", model_type)
        self.ai_client = get_ai_client(model_type)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试用例"""
        try:
            api_spec = input_data.get("api_spec", {})
            test_types = input_data.get("test_types", [TestType.FUNCTIONAL])
            max_cases_per_endpoint = input_data.get("max_cases_per_endpoint", 5)
            
            log.info(f"开始生成测试用例，API规范: {len(str(api_spec))} 字符")
            
            # 构建提示词
            prompt = self._build_generation_prompt(api_spec, test_types, max_cases_per_endpoint)
            
            # 调用AI生成测试用例
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.ai_client.chat_completion(messages)
            
            # 解析AI响应
            project_id = input_data.get("project_id")
            if project_id is None:
                raise ValueError("project_id is required but not provided")
            if not isinstance(project_id, int):
                try:
                    project_id = int(project_id)
                except (ValueError, TypeError):
                    raise ValueError(f"project_id must be an integer, got {type(project_id)}")
            
            test_cases = self._parse_ai_response(response, project_id)
            
            log.info(f"成功生成 {len(test_cases)} 个测试用例")
            
            return {
                "success": True,
                "test_cases": test_cases,
                "generated_count": len(test_cases),
                "ai_response": response
            }
            
        except Exception as e:
            log.error(f"生成测试用例失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_cases": []
            }
    
    def _build_generation_prompt(self, api_spec: Dict[str, Any], test_types: List[TestType], max_cases: int) -> str:
        """构建生成提示词"""
        # 针对DeepSeek-R1优化的提示词
        if self.model_type == "ollama" and "deepseek" in self.model_config.get("model", "").lower():
            return self._build_deepseek_prompt(api_spec, test_types, max_cases)
        else:
            return self._build_standard_prompt(api_spec, test_types, max_cases)
    
    def _build_deepseek_prompt(self, api_spec: Dict[str, Any], test_types: List[TestType], max_cases: int) -> str:
        """构建针对DeepSeek-R1优化的提示词"""
        prompt = f"""<think>
我需要分析这个API规范并生成全面的测试用例。让我仔细分析：

1. 首先理解API的整体结构和业务逻辑
2. 识别每个端点的功能和参数要求
3. 考虑各种测试场景：正常、边界、异常、安全
4. 为每个端点设计合适的测试用例
5. 确保测试覆盖率和质量

API规范分析：
{json.dumps(api_spec, indent=2, ensure_ascii=False)}

测试类型要求：{', '.join(test_types)}
每个端点最多生成：{max_cases} 个测试用例

我需要为每个端点生成以下类型的测试用例：
- 正常功能测试：验证基本功能
- 参数验证测试：测试必需参数、可选参数、参数类型
- 边界值测试：测试参数的边界情况
- 错误处理测试：测试各种错误场景
- 安全测试：测试注入攻击、认证绕过等
- 性能测试：测试响应时间和并发处理

让我开始生成测试用例...
</think>

作为专业的API测试专家，我将基于提供的API规范生成全面的测试用例。

我需要分析API规范的结构，理解每个端点的功能，然后设计覆盖各种场景的测试用例。

请为以下API规范生成测试用例：

API规范：
{json.dumps(api_spec, indent=2, ensure_ascii=False)}

测试要求：
- 测试类型：{', '.join(test_types)}
- 每个端点最多生成：{max_cases} 个测试用例
- 必须包含：正常场景、边界场景、异常场景、安全测试

请严格按照以下JSON格式返回测试用例数组：

[
  {{
    "name": "具体的测试用例名称",
    "description": "详细的测试用例描述",
    "method": "GET|POST|PUT|DELETE|PATCH",
    "endpoint": "/api/具体端点路径",
    "headers": {{"Content-Type": "application/json"}},
    "query_params": {{}},
    "body": {{}},
    "expected_status": 200,
    "expected_response": {{}},
    "test_type": "functional|security|performance",
    "priority": "low|medium|high|critical",
    "tags": ["相关标签"]
  }}
]

重要要求：
1. 必须返回有效的JSON数组格式
2. 每个测试用例都要有明确的测试目标
3. 考虑真实的业务场景和数据
4. 包含安全性测试用例
5. 测试用例名称要具有描述性和唯一性"""
        return prompt
    
    def _build_standard_prompt(self, api_spec: Dict[str, Any], test_types: List[TestType], max_cases: int) -> str:
        """构建标准提示词"""
        prompt = f"""
作为专业的API测试专家，请基于以下API规范生成全面的测试用例。

API规范:
{json.dumps(api_spec, indent=2, ensure_ascii=False)}

测试要求:
- 测试类型: {', '.join(test_types)}
- 每个端点最多生成: {max_cases} 个测试用例
- 包含正常场景、边界场景、异常场景
- 考虑安全性测试（如SQL注入、XSS等）
- 考虑性能测试场景

请为每个API端点生成测试用例，格式如下JSON数组：
[
  {{
    "name": "测试用例名称",
    "description": "测试用例描述",
    "method": "HTTP方法",
    "endpoint": "API端点",
    "headers": {{"Content-Type": "application/json"}},
    "query_params": {{}},
    "body": {{}},
    "expected_status": 200,
    "expected_response": {{}},
    "test_type": "functional|security|performance",
    "priority": "low|medium|high|critical",
    "tags": ["tag1", "tag2"]
  }}
]

注意事项:
1. 确保测试用例覆盖所有重要场景
2. 包含数据验证测试
3. 考虑认证和授权测试
4. 生成的JSON必须格式正确
5. 测试用例名称要具有描述性
"""
        return prompt
    
    def _parse_ai_response(self, response: str, project_id: int) -> List[Dict[str, Any]]:
        """解析AI响应并转换为测试用例"""
        test_cases = []
        
        try:
            # 记录原始响应用于调试
            log.info(f"AI响应长度: {len(response)} 字符")
            
            # 多种JSON提取策略
            json_extracted = False
            
            # 策略1: 提取完整的JSON数组
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                try:
                    json_str = response[json_start:json_end]
                    log.info(f"尝试解析JSON数组: {json_str[:200]}...")
                    parsed_cases = json.loads(json_str)
                    
                    if isinstance(parsed_cases, list):
                        for case in parsed_cases:
                            if isinstance(case, dict):
                                test_case = self._create_test_case_from_dict(case, project_id)
                                test_cases.append(test_case)
                        json_extracted = True
                        log.info(f"成功解析JSON数组，提取到 {len(test_cases)} 个测试用例")
                except json.JSONDecodeError as e:
                    log.warning(f"JSON数组解析失败: {e}")
            
            # 策略2: 如果数组解析失败，尝试提取单个JSON对象
            if not json_extracted:
                obj_start = response.find('{')
                obj_end = response.rfind('}') + 1
                
                if obj_start != -1 and obj_end > obj_start:
                    try:
                        json_str = response[obj_start:obj_end]
                        log.info(f"尝试解析JSON对象: {json_str[:200]}...")
                        case = json.loads(json_str)
                        
                        if isinstance(case, dict):
                            test_case = self._create_test_case_from_dict(case, project_id)
                            test_cases.append(test_case)
                            json_extracted = True
                            log.info("成功解析单个JSON对象")
                    except json.JSONDecodeError as e:
                        log.warning(f"JSON对象解析失败: {e}")
            
            # 策略3: 尝试逐行查找JSON片段
            if not json_extracted:
                log.info("尝试逐行解析JSON片段")
                lines = response.split('\n')
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            case = json.loads(line)
                            if isinstance(case, dict) and 'name' in case:
                                test_case = self._create_test_case_from_dict(case, project_id)
                                test_cases.append(test_case)
                                json_extracted = True
                                log.info(f"从第{i+1}行解析到测试用例")
                        except json.JSONDecodeError:
                            continue
            
            # 策略4: 使用正则表达式提取JSON片段
            if not json_extracted:
                import re
                log.info("使用正则表达式提取JSON")
                
                # 查找类似测试用例的结构
                json_pattern = r'\{[^{}]*"name"[^{}]*\}'
                matches = re.findall(json_pattern, response, re.DOTALL)
                
                for match in matches:
                    try:
                        case = json.loads(match)
                        if isinstance(case, dict):
                            test_case = self._create_test_case_from_dict(case, project_id)
                            test_cases.append(test_case)
                            json_extracted = True
                    except json.JSONDecodeError:
                        continue
                
                if json_extracted:
                    log.info(f"正则表达式提取到 {len(test_cases)} 个测试用例")
            
            # 策略5: 智能文本解析（从AI响应中提取关键信息）
            if not json_extracted:
                log.info("尝试智能文本解析")
                test_cases = self._parse_text_response(response, project_id)
                if test_cases:
                    json_extracted = True
                    log.info(f"智能文本解析提取到 {len(test_cases)} 个测试用例")
            
            # 如果所有策略都失败，生成默认测试用例
            if not json_extracted or not test_cases:
                log.warning("所有解析策略都失败，生成默认测试用例")
                test_cases = self._generate_default_test_cases(project_id)
        
        except Exception as e:
            log.error(f"解析AI响应时发生未预期错误: {e}")
            test_cases = self._generate_default_test_cases(project_id)
        
        log.info(f"最终返回 {len(test_cases)} 个测试用例")
        return test_cases
    
    def _create_test_case_from_dict(self, case: Dict[str, Any], project_id: int) -> Dict[str, Any]:
        """从字典创建测试用例"""
        return {
            "project_id": project_id,
            "name": case.get("name", "AI生成测试用例"),
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
            "tags": case.get("tags", []),
            "ai_generated": True
        }
    
    def _parse_text_response(self, response: str, project_id: int) -> List[Dict[str, Any]]:
        """智能文本解析，从自然语言响应中提取测试用例信息"""
        test_cases = []
        
        try:
            # 查找测试用例相关的关键词
            lines = response.split('\n')
            current_case = {}
            
            for line in lines:
                line = line.strip()
                
                # 检测测试用例名称
                if any(keyword in line.lower() for keyword in ['测试', 'test', '用例', 'case']):
                    if current_case and 'name' in current_case:
                        # 保存当前测试用例
                        test_case = self._create_test_case_from_dict(current_case, project_id)
                        test_cases.append(test_case)
                    
                    # 开始新的测试用例
                    current_case = {"name": line}
                
                # 检测HTTP方法
                elif any(method in line.upper() for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']):
                    for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        if method in line.upper():
                            current_case["method"] = method
                            break
                
                # 检测端点
                elif line.startswith('/') or '/api/' in line:
                    # 提取端点路径
                    import re
                    endpoint_match = re.search(r'(/[^\s]*)', line)
                    if endpoint_match:
                        current_case["endpoint"] = endpoint_match.group(1)
                
                # 检测状态码
                elif any(code in line for code in ['200', '201', '400', '401', '404', '500']):
                    import re
                    status_match = re.search(r'\b(\d{3})\b', line)
                    if status_match:
                        current_case["expected_status"] = int(status_match.group(1))
            
            # 保存最后一个测试用例
            if current_case and 'name' in current_case:
                test_case = self._create_test_case_from_dict(current_case, project_id)
                test_cases.append(test_case)
        
        except Exception as e:
            log.error(f"智能文本解析失败: {e}")
        
        return test_cases
    
    def _generate_default_test_cases(self, project_id: int) -> List[Dict[str, Any]]:
        """生成默认测试用例"""
        return [
            {
                "project_id": project_id,
                "name": "基础GET请求测试",
                "description": "测试基础GET请求功能",
                "method": "GET",
                "endpoint": "/api/test",
                "headers": {"Content-Type": "application/json"},
                "query_params": {},
                "body": {},
                "expected_status": 200,
                "expected_response": {},
                "test_type": "functional",
                "priority": "medium",
                "tags": ["basic", "get"],
                "ai_generated": True
            },
            {
                "project_id": project_id,
                "name": "POST请求数据验证测试",
                "description": "测试POST请求的数据验证",
                "method": "POST",
                "endpoint": "/api/test",
                "headers": {"Content-Type": "application/json"},
                "query_params": {},
                "body": {"test": "data"},
                "expected_status": 201,
                "expected_response": {},
                "test_type": "functional",
                "priority": "high",
                "tags": ["validation", "post"],
                "ai_generated": True
            },
            {
                "project_id": project_id,
                "name": "无效参数错误处理测试",
                "description": "测试无效参数的错误处理",
                "method": "POST",
                "endpoint": "/api/test",
                "headers": {"Content-Type": "application/json"},
                "query_params": {},
                "body": {"invalid": "data"},
                "expected_status": 400,
                "expected_response": {},
                "test_type": "functional",
                "priority": "medium",
                "tags": ["error", "validation"],
                "ai_generated": True
            }
        ]
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的API测试用例生成专家，具有以下能力：

1. 深入理解API规范（OpenAPI/Swagger）
2. 设计全面的测试场景覆盖
3. 识别潜在的安全风险点
4. 生成高质量的测试数据
5. 遵循测试最佳实践

你的任务是基于API规范生成全面、准确、实用的测试用例，确保：
- 功能完整性测试
- 边界条件测试
- 错误处理测试
- 安全性测试
- 性能相关测试

请始终以JSON格式返回结构化的测试用例数据。"""


class APISpecParser:
    """API规范解析器"""
    
    @staticmethod
    def parse_openapi(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析OpenAPI规范"""
        endpoints = []
        
        paths = spec.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    endpoint = {
                        "path": path,
                        "method": method.upper(),
                        "summary": details.get("summary", ""),
                        "description": details.get("description", ""),
                        "parameters": details.get("parameters", []),
                        "requestBody": details.get("requestBody", {}),
                        "responses": details.get("responses", {}),
                        "security": details.get("security", [])
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    @staticmethod
    def parse_postman(collection: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析Postman集合"""
        endpoints = []
        
        def extract_requests(items):
            for item in items:
                if "request" in item:
                    request = item["request"]
                    endpoint = {
                        "path": request.get("url", {}).get("raw", ""),
                        "method": request.get("method", "GET"),
                        "summary": item.get("name", ""),
                        "description": item.get("description", ""),
                        "headers": request.get("header", []),
                        "body": request.get("body", {}),
                    }
                    endpoints.append(endpoint)
                elif "item" in item:
                    extract_requests(item["item"])
        
        if "item" in collection:
            extract_requests(collection["item"])
        
        return endpoints
