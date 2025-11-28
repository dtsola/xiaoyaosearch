"""
小遥搜索后端服务主入口
启动FastAPI应用并配置所有必要的组件
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入核心模块
from app.core import setup_logging, init_database, setup_exception_handlers
from app.core.logging_config import get_logger
from app.api import (
    search_router,
    index_router,
    config_router,
    system_router,
    websocket_router
)

# 配置日志系统
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动时初始化数据库和其他组件，关闭时清理资源
    """
    # 启动时执行
    logger.info("=" * 50)
    logger.info("小遥搜索服务启动中...")
    logger.info("=" * 50)

    try:
        # 初始化数据库
        logger.info("初始化数据库...")
        init_database()
        logger.info("数据库初始化完成")

              # 初始化AI模型服务
        logger.info("加载AI模型...")
        try:
            from app.services.ai_model_manager import ai_model_service
            await ai_model_service.initialize()
            logger.info("AI模型服务加载完成")
        except Exception as e:
            logger.warning(f"AI模型服务初始化失败: {str(e)}")
            logger.info("继续运行，但AI功能可能不可用")

        logger.info("✅ 小遥搜索服务启动完成")
        logger.info(f"📖 API文档: http://127.0.0.1:8000/docs")
        logger.info(f"📋 ReDoc文档: http://127.0.0.1:8000/redoc")

    except Exception as e:
        logger.error(f"❌ 服务启动失败: {str(e)}")
        raise

    yield

    # 关闭时执行
    logger.info("小遥搜索服务关闭中...")
    try:
        # TODO: 清理资源
        # await cleanup_resources()
        logger.info("资源清理完成")
    except Exception as e:
        logger.error(f"资源清理失败: {str(e)}")

    logger.info("小遥搜索服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="小遥搜索 API",
    description="多模态AI智能搜索桌面应用后端服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS中间件，支持Electron跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],  # Electron渲染进程地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置异常处理器
setup_exception_handlers(app)

# 注册API路由
app.include_router(search_router)
app.include_router(index_router)
app.include_router(config_router)
app.include_router(system_router)
app.include_router(websocket_router)

# 根路径
@app.get("/")
async def root():
    """
    根路径，返回API基本信息
    """
    return {
        "name": "小遥搜索 API",
        "version": "1.0.0",
        "description": "多模态AI智能搜索桌面应用后端服务",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/api/system/health"
    }

# 启动服务
if __name__ == "__main__":
    import uvicorn

    # 从环境变量获取配置
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")

    logger.info(f"🚀 启动服务: http://{host}:{port}")
    logger.info(f"🔄 热重载: {'开启' if reload else '关闭'}")
    logger.info(f"📊 日志级别: {log_level}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )