"""
日志配置
"""
import sys
from pathlib import Path
from loguru import logger
from src.config.settings import settings

def setup_logger():
    """设置日志配置"""
    # 移除默认处理器
    logger.remove()
    
    # 确保日志目录存在
    log_file = Path(settings.logging.file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 控制台输出
    logger.add(
        sys.stdout,
        level=settings.logging.level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 文件输出
    logger.add(
        settings.logging.file,
        level=settings.logging.level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
        compression="zip"
    )
    
    return logger

# 导出logger实例
log = logger
