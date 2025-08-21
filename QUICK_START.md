# AI接口测试框架快速入门指南

这个快速入门指南将帮助你在几分钟内开始使用AI接口测试框架。

## 1. 安装

确保你已安装Python 3.8+，然后安装依赖：

```bash
# 克隆仓库（如果尚未克隆）
git clone https://github.com/yourusername/ai-interface-testing.git
cd ai-interface-testing

# 安装依赖
pip install -r requirements.txt
```

## 2. 启动服务

```bash
# 启动API服务器
python main.py
```

服务器将在 http://localhost:8000 上运行。

## 3. 运行演示

我们提供了两个演示脚本，帮助你快速了解框架功能：

```bash
# 批量测试演示
python batch_test_demo.py

# 或者运行完整工作流程演示
python framework_integration_demo.py
```

## 4. 基本工作流程

AI接口测试框架的基本工作流程包括：

1. **创建测试项目** → 2. **创建测试用例** → 3. **执行测试** → 4. **查看结果** → 5. **生成AI报告**

## 5. 使用Python代码

以下是使用Python代码进行测试的简单示例：

```python
import asyncio
import httpx

async def simple_test():
    # 1. 创建项目
    async with httpx.AsyncClient() as client:
        project_response = await client.post(
            "http://localhost:8000/api/v1/projects/",
            json={
                "name": "快速入门项目",
                "description": "示例项目",
                "base_url": "https://httpbin.org"
            }
        )
        project_data = project_response.json()
        project_id = project_data["data"]["id"]
        print(f"项目创建成功，ID: {project_id}")
    
    # 2. 创建测试用例
    async with httpx.AsyncClient() as client:
        test_cases = [
            {
                "name": "GET请求测试",
                "method": "GET",
                "endpoint": "/get",
                "expected_status": 200,
                "project_id": project_id
            },
            {
                "name": "POST请求测试",
                "method": "POST",
                "endpoint": "/post",
                "body": {"name": "测试数据"},
                "expected_status": 200,
                "project_id": project_id
            }
        ]
        
        test_case_response = await client.post(
            "http://localhost:8000/api/v1/test-cases/batch",
            json=test_cases
        )
        test_case_data = test_case_response.json()
        test_case_ids = [tc["id"] for tc in test_case_data["data"]]
        print(f"测试用例创建成功: {test_case_ids}")
    
    # 3. 执行批量测试
    async with httpx.AsyncClient() as client:
        execution_response = await client.post(
            "http://localhost:8000/api/v1/executions/batch",
            json={
                "project_id": project_id,
                "test_case_ids": test_case_ids,
                "execution_strategy": "parallel"
            }
        )
        execution_data = execution_response.json()
        execution_id = execution_data["data"]["execution_id"]
        print(f"测试执行任务已创建，ID: {execution_id}")
    
    # 4. 监控执行状态
    while True:
        async with httpx.AsyncClient() as client:
            status_response = await client.get(
                f"http://localhost:8000/api/v1/executions/{execution_id}"
            )
            status_data = status_response.json()
            status = status_data["data"]["status"]
            print(f"当前状态: {status}")
            
            if status in ["completed", "failed", "stopped"]:
                break
            
            await asyncio.sleep(1)
    
    # 5. 获取测试结果
    async with httpx.AsyncClient() as client:
        results_response = await client.get(
            f"http://localhost:8000/api/v1/executions/{execution_id}/results"
        )
        results_data = results_response.json()
        print("测试结果摘要:")
        print(f"通过率: {results_data['data']['summary']['pass_rate']}%")
    
    # 6. 生成AI测试报告
    async with httpx.AsyncClient() as client:
        report_response = await client.post(
            f"http://localhost:8000/api/v1/ai/test-report/{execution_id}"
        )
        report_data = report_response.json()
        print("AI测试报告已生成")

if __name__ == "__main__":
    asyncio.run(simple_test())
```

将上面的代码保存为 `quick_test.py` 并运行：

```bash
python quick_test.py
```

## 6. 使用REST API

如果你想直接使用REST API，这里是基本流程：

```bash
# 1. 创建项目
curl -X POST "http://localhost:8000/api/v1/projects/" \
     -H "Content-Type: application/json" \
     -d '{"name": "API测试", "base_url": "https://httpbin.org"}'

# 2. 创建测试用例
curl -X POST "http://localhost:8000/api/v1/test-cases/batch" \
     -H "Content-Type: application/json" \
     -d '[{"name": "GET测试", "method": "GET", "endpoint": "/get", "expected_status": 200, "project_id": 1}]'

# 3. 执行测试
curl -X POST "http://localhost:8000/api/v1/executions/batch" \
     -H "Content-Type: application/json" \
     -d '{"project_id": 1, "test_case_ids": [1], "execution_strategy": "parallel"}'

# 4. 查看结果 (替换 {execution_id} 为实际ID)
curl -X GET "http://localhost:8000/api/v1/executions/{execution_id}/results"

# 5. 生成AI报告
curl -X POST "http://localhost:8000/api/v1/ai/test-report/{execution_id}"
```

## 7. 下一步

- 查看完整的 [README.md](README.md) 获取详细文档
- 访问 API 文档: http://localhost:8000/docs
- 探索 `framework_integration_demo.py` 了解更多高级功能

## 8. 常见问题

- **Q: 如何关闭服务器?**  
  A: 在运行服务器的终端中按 `Ctrl+C`

- **Q: 如何查看日志?**  
  A: 查看 `logs/app.log` 文件

- **Q: 测试执行失败怎么办?**  
  A: 检查目标API是否可访问，查看日志获取详细错误信息
