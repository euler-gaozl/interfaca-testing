"""
AI驱动的接口自动化测试程序 - 主入口
"""
import uvicorn
from src.api.app import create_app
from src.config.settings import settings
from src.utils.logger import setup_logger

def main():
    """主函数"""
    # 设置日志
    setup_logger()
    
    # 创建应用
    app = create_app()
    
    # 启动服务
    uvicorn.run(
        "src.api.app:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload
    )

if __name__ == "__main__":
    main()
