# AI接口测试框架使用文档

![版本](https://img.shields.io/badge/版本-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0%2B-orange)

## 目录

- [简介](#简介)
- [功能特点](#功能特点)
- [安装指南](#安装指南)
- [快速开始](#快速开始)
- [基本用法](#基本用法)
  - [创建测试项目](#创建测试项目)
  - [创建测试用例](#创建测试用例)
  - [执行测试](#执行测试)
  - [查看测试结果](#查看测试结果)
  - [生成AI测试报告](#生成ai测试报告)
- [高级功能](#高级功能)
  - [批量测试](#批量测试)
  - [执行策略](#执行策略)
  - [自定义验证](#自定义验证)
  - [导出报告](#导出报告)
- [API参考](#api参考)
- [演示脚本](#演示脚本)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 简介

AI接口测试框架是一个强大的自动化测试工具，专为API接口测试设计。它结合了传统测试方法和人工智能技术，提供全面的测试解决方案。框架支持批量测试、多种执行策略、自动化验证和AI驱动的测试报告生成。

本框架特别适合：
- RESTful API测试
- 微服务接口测试
- 回归测试
- 性能和负载测试
- 自动化CI/CD流程

## 功能特点

- **多种HTTP方法支持**：GET, POST, PUT, DELETE, PATCH等
- **批量测试**：同时执行多个测试用例
- **灵活的执行策略**：并行、串行或混合执行
- **自动重试**：失败测试自动重试
- **模拟模式**：无需真实HTTP请求的快速测试
- **AI测试报告**：使用大模型分析测试结果
- **多格式报告导出**：JSON, TXT等
- **RESTful API**：完整的API接口
- **异步处理**：高性能异步执行
- **详细日志**：完整的测试执行日志

## 安装指南

### 前提条件

- Python 3.8+
- pip (Python包管理器)

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/ai-interface-testing.git
cd ai-interface-testing
```

2. 创建虚拟环境（推荐）：

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 配置环境变量：

创建`.env`文件并设置必要的环境变量：

```
API_KEY=your_api_key_here
LOG_LEVEL=INFO
```

## 快速开始

1. 启动服务器：

```bash
python main.py
```

2. 运行演示脚本：

```bash
python framework_integration_demo.py
```

3. 访问API文档：

打开浏览器访问 `http://localhost:8000/docs`

## 基本用法

### 创建测试项目

测试项目是测试用例的集合，通常对应一个API服务或一组相关接口。

#### 通过API创建

```bash
curl -X POST "http://localhost:8000/api/v1/projects/" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "我的API测试项目",
           "description": "测试项目描述",
           "base_url": "https://api.example.com"
         }'
```

#### 通过Python代码创建

```python
import httpx

async def create_project():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/projects/",
            json={
                "name": "我的API测试项目",
                "description": "测试项目描述",
                "base_url": "https://api.example.com"
            }
        )
        return response.json()
```

### 创建测试用例

测试用例定义了要测试的API接口、请求参数和预期结果。

#### 单个测试用例

```bash
curl -X POST "http://localhost:8000/api/v1/test-cases/" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "获取用户信息",
           "description": "测试获取用户信息API",
           "method": "GET",
           "endpoint": "/users/1",
           "headers": {"Authorization": "Bearer token"},
           "expected_status": 200,
           "project_id": 1
         }'
```

#### 批量创建测试用例

```bash
curl -X POST "http://localhost:8000/api/v1/test-cases/batch" \
     -H "Content-Type: application/json" \
     -d '[
           {
             "name": "获取用户列表",
             "method": "GET",
             "endpoint": "/users",
             "expected_status": 200,
             "project_id": 1
           },
           {
             "name": "创建新用户",
             "method": "POST",
             "endpoint": "/users",
             "body": {"name": "张三", "email": "zhangsan@example.com"},
             "expected_status": 201,
             "project_id": 1
           }
         ]'
```

### 执行测试

#### 执行单个测试

```bash
curl -X POST "http://localhost:8000/api/v1/executions/" \
     -H "Content-Type: application/json" \
     -d '{
           "test_case_id": 1,
           "project_id": 1
         }'
```

#### 执行批量测试

```bash
curl -X POST "http://localhost:8000/api/v1/executions/batch" \
     -H "Content-Type: application/json" \
     -d '{
           "project_id": 1,
           "test_case_ids": [1, 2, 3],
           "concurrent_limit": 3,
           "timeout": 30,
           "retry_count": 1,
           "execution_strategy": "mixed"
         }'
```

### 查看测试结果

#### 获取执行状态

```bash
curl -X GET "http://localhost:8000/api/v1/executions/{execution_id}"
```

#### 获取详细结果

```bash
curl -X GET "http://localhost:8000/api/v1/executions/{execution_id}/results"
```

### 生成AI测试报告

AI测试报告提供了测试结果的智能分析和改进建议。

```bash
curl -X POST "http://localhost:8000/api/v1/ai/test-report/{execution_id}"
```

获取生成的报告：

```bash
curl -X GET "http://localhost:8000/api/v1/ai/test-report/{execution_id}"
```

## 高级功能

### 批量测试

批量测试允许同时执行多个测试用例，提高测试效率。

```python
async def execute_batch_test(project_id, test_case_ids):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/executions/batch",
            json={
                "project_id": project_id,
                "test_case_ids": test_case_ids,
                "concurrent_limit": 5,  # 最大并发数
                "timeout": 30,          # 超时时间(秒)
                "retry_count": 2,       # 失败重试次数
                "execution_strategy": "parallel"  # 执行策略
            }
        )
        return response.json()
```

### 执行策略

框架支持三种执行策略：

1. **并行(parallel)**：同时执行所有测试用例，适合独立的测试
2. **串行(serial)**：按顺序执行测试用例，适合有依赖关系的测试
3. **混合(mixed)**：结合并行和串行策略，平衡效率和可靠性

```json
{
  "execution_strategy": "parallel",  // 或 "serial", "mixed"
  "concurrent_limit": 3  // 并行策略的最大并发数
}
```

### 自定义验证

除了状态码验证外，还可以添加自定义验证规则：

```json
{
  "name": "验证响应内容",
  "method": "GET",
  "endpoint": "/users/1",
  "expected_status": 200,
  "validations": [
    {
      "type": "json_path",
      "path": "$.name",
      "expected_value": "张三"
    },
    {
      "type": "response_time",
      "max_time": 500
    }
  ],
  "project_id": 1
}
```

### 导出报告

可以将测试报告导出为不同格式：

```python
async def export_report(execution_id, format_type="json"):
    # 创建报告目录
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # 生成报告文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{reports_dir}/test_report_{timestamp}.{format_type}"
    
    # 获取AI报告
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/v1/ai/test-report/{execution_id}"
        )
        report = response.json()["data"]
    
    # 导出报告
    if format_type == "json":
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    elif format_type == "txt":
        # 文本格式导出逻辑
        with open(filename, "w", encoding="utf-8") as f:
            f.write("AI接口测试报告\n")
            # 写入报告内容...
    
    return filename
```

## API参考

完整的API文档可通过访问 `http://localhost:8000/docs` 获取。

### 主要端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/projects/` | POST | 创建测试项目 |
| `/api/v1/projects/{project_id}` | GET | 获取项目详情 |
| `/api/v1/test-cases/` | POST | 创建测试用例 |
| `/api/v1/test-cases/batch` | POST | 批量创建测试用例 |
| `/api/v1/executions/` | POST | 执行单个测试 |
| `/api/v1/executions/batch` | POST | 执行批量测试 |
| `/api/v1/executions/{execution_id}` | GET | 获取执行状态 |
| `/api/v1/executions/{execution_id}/results` | GET | 获取测试结果 |
| `/api/v1/ai/test-report/{execution_id}` | POST | 生成AI测试报告 |
| `/api/v1/ai/test-report/{execution_id}` | GET | 获取AI测试报告 |

## 演示脚本

框架提供了多个演示脚本，帮助用户快速上手：

### 批量测试演示

```bash
python batch_test_demo.py
```

这个脚本演示了如何创建项目、测试用例，执行批量测试并获取结果。

### 完整工作流程演示

```bash
python framework_integration_demo.py
```

这个脚本展示了从项目创建到报告生成的完整工作流程。

### 自定义集成

可以基于`AITestingFramework`类开发自定义测试流程：

```python
from framework_integration_demo import AITestingFramework

async def custom_workflow():
    framework = AITestingFramework()
    
    # 创建项目
    await framework.create_project("自定义项目")
    
    # 自定义测试用例
    test_cases = [
        {
            "name": "自定义测试1",
            "method": "GET",
            "endpoint": "/custom/endpoint",
            "expected_status": 200
        }
    ]
    await framework.create_test_cases(test_cases)
    
    # 执行测试
    await framework.execute_batch_test(strategy="serial")
    
    # 其他自定义逻辑...

if __name__ == "__main__":
    import asyncio
    asyncio.run(custom_workflow())
```

## 常见问题

### Q: 如何关闭服务器？

A: 在运行服务器的终端中按 `Ctrl+C`（Windows/Linux）或 `Cmd+C`（Mac）。

### Q: 如何修改服务器端口？

A: 编辑 `src/config/settings.py` 文件中的 `PORT` 设置。

### Q: 测试执行卡在"running"状态怎么办？

A: 可能是网络问题或目标API不可用。检查日志文件 `logs/app.log` 获取详细错误信息。

### Q: 如何在CI/CD环境中使用？

A: 可以使用命令行参数运行测试：

```bash
python -m src.api.app --headless --port 8080
python batch_test_demo.py --ci
```

### Q: 如何处理需要认证的API？

A: 在测试用例中添加认证信息：

```json
{
  "headers": {
    "Authorization": "Bearer your_token_here"
  },
  "auth": {
    "type": "basic",
    "username": "user",
    "password": "pass"
  }
}
```

## 贡献指南

我们欢迎社区贡献！如果你想参与项目开发，请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。
