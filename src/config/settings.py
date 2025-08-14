"""
配置管理 - 适配Python 3.10
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AIModelConfig(BaseSettings):
    """AI模型配置"""
    model_config = {"extra": "allow"}
    
    primary: str = "openai"
    fallback: str = "ollama"
    openai_api_key: Optional[str] = Field(None)
    openai_model: str = "gpt-4"
    openai_base_url: str = "https://api.openai.com/v1"
    claude_api_key: Optional[str] = Field(None)
    claude_model: str = "claude-3-sonnet-20240229"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen:7b"

class DatabaseConfig(BaseSettings):
    """数据库配置"""
    type: str = "sqlite"
    path: str = "./data/test.db"
    echo: bool = False

class ServerConfig(BaseSettings):
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    reload: bool = True

class TestingConfig(BaseSettings):
    """测试配置"""
    protocols: List[str] = ["rest", "graphql", "websocket"]
    concurrent_limit: int = 10
    timeout: int = 30
    retry_count: int = 3

class ReportingConfig(BaseSettings):
    """报告配置"""
    output_dir: str = "./reports"
    formats: List[str] = ["html", "json", "pdf"]
    template_dir: str = "./templates"

class LoggingConfig(BaseSettings):
    """日志配置"""
    level: str = "INFO"
    file: str = "./logs/app.log"
    rotation: str = "1 day"
    retention: str = "7 days"

class SecurityConfig(BaseSettings):
    """安全配置"""
    secret_key: str = Field("default_secret_key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

class Settings:
    """全局配置管理"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self._config_data = self._load_config()
        
        # 初始化各模块配置
        self.ai_models = AIModelConfig(**self._config_data.get("ai_models", {}))
        self.database = DatabaseConfig(**self._config_data.get("database", {}))
        self.server = ServerConfig(**self._config_data.get("server", {}))
        self.testing = TestingConfig(**self._config_data.get("testing", {}))
        self.reporting = ReportingConfig(**self._config_data.get("reporting", {}))
        self.logging = LoggingConfig(**self._config_data.get("logging", {}))
        self.security = SecurityConfig(**self._config_data.get("security", {}))
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = Path(self.config_file)
        if not config_path.exists():
            # 如果配置文件不存在，返回默认配置
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # 环境变量替换
        config_data = self._replace_env_vars(config_data)
        return config_data
    
    def _replace_env_vars(self, data: Any) -> Any:
        """递归替换环境变量"""
        if isinstance(data, dict):
            return {k: self._replace_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            return os.getenv(env_var, data)
        return data

# 全局配置实例
settings = Settings()
