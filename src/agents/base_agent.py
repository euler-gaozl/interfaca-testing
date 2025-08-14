"""
基础AI智能体
"""
import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

import httpx

from src.config.settings import settings
from src.utils.logger import log


class BaseAgent(ABC):
    """基础AI智能体抽象类"""
    
    def __init__(self, name: str, model_type: str = "openai"):
        self.name = name
        self.model_type = model_type
        self.model_config = self._get_model_config()
        self.conversation_history: List[Dict[str, str]] = []
    
    def _get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        if self.model_type == "openai":
            return {
                "api_key": settings.ai_models.openai_api_key,
                "model": settings.ai_models.openai_model,
                "base_url": settings.ai_models.openai_base_url
            }
        elif self.model_type == "claude":
            return {
                "api_key": settings.ai_models.claude_api_key,
                "model": settings.ai_models.claude_model
            }
        elif self.model_type == "ollama":
            return {
                "base_url": settings.ai_models.ollama_base_url,
                "model": settings.ai_models.ollama_model
            }
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据并返回结果"""
        pass
    
    def add_to_history(self, role: str, content: str):
        """添加对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return f"""你是一个专业的{self.name}，专门负责接口自动化测试相关任务。
请始终以专业、准确、有用的方式回应用户请求。
当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""


class OllamaClient:
    """真实的Ollama客户端"""
    
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)
        log.info(f"初始化Ollama客户端: {base_url}, 模型: {model}")
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """与Ollama API通信"""
        try:
            # 构建提示词（Ollama使用单一prompt而不是messages格式）
            prompt = self._build_prompt(messages)
            
            # 构建请求数据
            request_data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "max_tokens": kwargs.get("max_tokens", 2000)
                }
            }
            
            log.info(f"发送请求到Ollama: {self.base_url}/api/generate")
            
            # 发送请求
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API错误: {response.status_code} - {response.text}")
            
            result = response.json()
            ai_response = result.get("response", "")
            
            log.info(f"Ollama响应成功，长度: {len(ai_response)}")
            return ai_response
            
        except Exception as e:
            log.error(f"Ollama API调用失败: {e}")
            raise
    
    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """构建适合Ollama的提示词"""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


class MockAIClient:
    """模拟AI客户端，用于在没有真实API密钥时进行开发测试"""
    
    def __init__(self, model_type: str):
        self.model_type = model_type
        log.warning(f"使用模拟AI客户端: {model_type}")
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """模拟聊天完成"""
        await asyncio.sleep(0.5)  # 模拟网络延迟
        
        last_message = messages[-1]["content"] if messages else ""
        
        # 根据消息内容返回模拟响应
        if "测试用例" in last_message:
            return """基于API规范，我生成了以下测试用例：
1. 正常请求测试
2. 参数验证测试
3. 边界值测试
4. 错误处理测试
5. 安全性测试"""
        
        elif "分析" in last_message:
            return """测试结果分析：
- 总体通过率: 85%
- 发现问题: 3个
- 性能表现: 良好
- 安全风险: 低
建议优化接口响应时间和错误处理机制。"""
        
        elif "报告" in last_message:
            return """测试报告已生成，包含以下内容：
- 执行摘要
- 详细测试结果
- 性能指标
- 安全评估
- 改进建议"""
        
        else:
            return f"我是{self.model_type}模型的模拟响应。收到消息: {last_message[:50]}..."


async def test_ollama_connection(base_url: str, model: str) -> bool:
    """测试Ollama连接"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 测试服务可用性
            response = await client.get(f"{base_url}/api/tags")
            if response.status_code != 200:
                return False
            
            # 检查模型是否存在
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            return model in model_names
    except Exception as e:
        log.error(f"Ollama连接测试失败: {e}")
        return False


def get_ai_client(model_type: Optional[str] = None):
    """获取AI客户端"""
    if model_type is None:
        model_type = settings.ai_models.primary
    
    try:
        if model_type == "openai":
            if not settings.ai_models.openai_api_key or settings.ai_models.openai_api_key == "your_openai_api_key_here":
                return MockAIClient("openai")
            
            # 这里应该导入真实的OpenAI客户端
            # from openai import AsyncOpenAI
            # return AsyncOpenAI(api_key=settings.ai_models.openai_api_key)
            return MockAIClient("openai")
        
        elif model_type == "claude":
            if not settings.ai_models.claude_api_key or settings.ai_models.claude_api_key == "your_claude_api_key_here":
                return MockAIClient("claude")
            
            # 这里应该导入真实的Claude客户端
            return MockAIClient("claude")
        
        elif model_type == "ollama":
            # 返回真实的Ollama客户端
            return OllamaClient(
                base_url=settings.ai_models.ollama_base_url,
                model=settings.ai_models.ollama_model
            )
        
        else:
            log.warning(f"未知的模型类型: {model_type}，使用默认模拟客户端")
            return MockAIClient("unknown")
    
    except Exception as e:
        log.error(f"创建AI客户端失败: {e}")
        return MockAIClient("fallback")
