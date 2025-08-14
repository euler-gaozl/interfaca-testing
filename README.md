这是一个测试题。
实现：接口自动化测试（测试用例自动生成、接口自动测试、测试报告自动生成） 
要求：利用AI大模型（一个，或多个大模型）和智能体开发框架（Autogen/langchain/fastAPI等）开发一套接口自动化测试程序。
过程：在开发过程中我想到了llm的巨大的先验知识和弱逻辑，经过对任务逐步拆解，此项目完全由claude生成。
思考：也许每个项目都可以被工程师拆解到非常细，然后让ai自动完成。

# AI驱动的接口自动化测试框架

基于AI大模型和智能体的接口自动化测试系统，支持测试用例自动生成、接口自动测试、测试报告自动生成。

## 🚀 项目特色

- **AI智能体协作**: 使用AutoGen、LangChain等多种框架构建多智能体协作系统。
- **测试用例自动生成**: 基于API规范智能生成全面的测试用例。
- **多协议支持**: 支持REST API、GraphQL、WebSocket等多种协议。
- **智能分析**: AI驱动的测试结果分析和优化建议。
- **本地部署**: 支持完全本地化部署，数据安全可控。
- **可扩展架构**: 模块化设计，易于扩展和定制。

## 📋 系统要求

- Python 3.10+
- 8GB+ RAM (推荐)
- 2GB+ 磁盘空间

## 🛠️ 安装部署

### 1. 克隆项目
```bash
git clone <repository-url>
cd interface-testing
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
编辑 `.env` 文件，配置AI模型API密钥：
```bash
# AI模型API密钥
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here

# 安全密钥
SECRET_KEY=your_secret_key_here
```

### 4. 启动服务
```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## 📖 使用指南

### 1. 健康检查
启动服务后，首先可以检查服务的健康状况：
```bash
curl http://localhost:8000/health
```

### 2. 访问API文档
访问以下地址查看可交互的API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 创建测试项目
```bash
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Content-Type: application/json" \
  -d ".{
    \"name\": \"示例API项目\",
    \"description\": \"这是一个示例API测试项目\",
    \"base_url\": \"https://api.example.com\"
  }"
```

### 4. AI生成测试用例
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate-test-cases" \
  -H "Content-Type: application/json" \
  -d ".{
    \"project_id\": 1,
    \"spec_content\": {
      \"openapi\": \"3.0.0\",
      \"info\": {\"title\": \"示例API\", \"version\": \"1.0.0\"},
      \"paths\": {
        \"/users\": {
          \"get\": {
            \"summary\": \"获取用户列表\",
            \"responses\": {\"200\": {\"description\": \"成功\"}}
          }
        }
      }
    }
  }"
```

## 🏗️ 项目架构

```
interface-testing/
├── src/
│   ├── agents/              # AI智能体 (AutoGen, LangChain等)
│   ├── api/                 # FastAPI接口
│   │   ├── app.py           # 应用主文件
│   │   └── routes/          # API路由模块 (projects, test_cases, etc.)
│   ├── config/              # 配置管理 (Pydantic)
│   ├── models/              # 数据模型 (Pydantic Schemas)
│   └── utils/               # 工具函数 (logger)
├── data/                    # 数据文件 (SQLite数据库)
├── logs/                    # 日志文件
├── reports/                 # 测试报告
├── .env                     # 环境变量
├── config.yaml              # 主配置文件
├── requirements.txt         # Python依赖
└── main.py                  # 程序入口
```

## 🤖 AI智能体说明

### 测试用例生成智能体
- **功能**: 基于API规范自动生成测试用例。
- **支持格式**: OpenAPI/Swagger, Postman Collection。
- **生成类型**: 功能测试、安全测试、性能测试、边界测试。

### 测试结果分析智能体
- **功能**: 智能分析测试结果，识别问题模式。
- **输出**: 问题总结、根因分析、优化建议。

## 🔧 配置说明

### AI模型配置
在 `config.yaml` 中配置AI模型。框架支持本地和云端多种模型。
```yaml
ai_models:
  primary: "ollama"  # 主要模型
  fallback: "openai"  # 备用模型
  openai:
    model: "gpt-4"
    api_key: "${OPENAI_API_KEY}"
  ollama:
    base_url: "http://localhost:11434"
    model: "deepseek-r1:14b" # 可替换为其他本地模型
```

### 测试配置
```yaml
testing:
  protocols: ["rest", "graphql", "websocket"]
  concurrent_limit: 10
  timeout: 30
  retry_count: 3
```

## 🧪 开发测试

### 运行单元测试
```bash
pytest tests/
```

### 代码格式化与检查
```bash
# 格式化
black src/ tests/
# 检查
ruff check .
```

## 📊 功能特性

### ✅ 已实现功能
- [x] **核心服务**: 基于FastAPI的健壮API服务。
- [x] **项目管理**: 创建和管理测试项目。
- [x] **测试用例管理**: 存储和检索测试用例。
- [x] **测试执行**: 异步执行测试流程。
- [x] **AI分析**: 集成AI大模型进行分析任务。
- [x] **报告管理**: 生成和管理测试报告。
- [x] **配置系统**: 基于Pydantic和YAML的灵活配置。
- [x] **日志系统**: 集成日志记录。

### 🚧 开发中功能
- [ ] 完整的测试执行引擎
- [ ] AI结果分析智能体
- [ ] 报告生成系统
- [ ] Web界面
- [ ] 性能测试支持

### 🔮 计划功能
- [ ] CI/CD集成
- [ ] 分布式测试
- [ ] 实时监控
- [ ] 插件系统

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证 

本项目采用 MIT 许可证。

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/)
- [AutoGen](https://github.com/microsoft/autogen)
- [LangChain](https://github.com/langchain-ai/langchain)
- [Pydantic](https://pydantic-docs.helpmanual.io/)