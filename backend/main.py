"""
小遥搜索后端服务主入口
启动FastAPI应用并配置所有必要的组件
"""
import os
import sys
from pathlib import Path

# 将 backend 目录添加到 Python 模块搜索路径
# 这样无论从哪里运行 main.py，都能正确找到 app 模块
backend_dir = Path(__file__).parent.absolute()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# 显式加载 backend/.env 到进程环境变量
# pydantic-settings 读取 .env 只填充 settings 对象，不会写回 os.environ，
# 因此必须在这里加载，否则下方 os.getenv 读不到 API_HOST/API_PORT 等配置，
# 只会使用代码中的默认值
from dotenv import load_dotenv

_dotenv_path = backend_dir / ".env"
if _dotenv_path.exists():
    load_dotenv(_dotenv_path)


def get_api_address() -> tuple[str, int]:
    """
    获取后端 API 的监听地址与端口

    优先读取 .env 中的 API_HOST / API_PORT，避免日志和启动参数里硬编码端口。
    返回值同时用于启动 uvicorn 和打印访问地址，保证两者始终一致。
    """
    host = os.getenv("API_HOST", "127.0.0.1")
    try:
        port = int(os.getenv("API_PORT", "8000"))
    except ValueError:
        port = 8000
    return host, port

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 首先配置AI模型相关的日志设置（必须在导入AI相关库之前）
from app.core.logging_config import setup_ai_logging
setup_ai_logging()

# 导入核心模块
from app.core import init_database, setup_exception_handlers
from app.core.logging_config import setup_logging, get_logger, logger

# 导入 MCP 模块
from app.mcp.server import create_mcp_server, register_mcp_tools

# 配置日志系统
setup_logging()
from app.api import (
    search_router,
    index_router,
    config_router,
    system_router,
    settings_router
)
from app.api.glossary_collections import router as glossary_collections_router
from app.api.glossary_terms import router as glossary_terms_router
from app.api.glossary import router as glossary_router
from app.api.glossary_settings import router as glossary_settings_router


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

        # 清理上次进程遗留的未完成任务（进程重启后不可能还有协程在跑）
        try:
            from datetime import datetime
            from app.core.database import SessionLocal
            from app.models.index_job import IndexJobModel

            db = SessionLocal()
            try:
                stale_jobs = db.query(IndexJobModel).filter(
                    IndexJobModel.status.in_(['pending', 'processing'])
                ).all()
                for job in stale_jobs:
                    job.status = 'failed'
                    job.error_message = '服务重启，任务中断'
                    job.completed_at = datetime.now()
                if stale_jobs:
                    db.commit()
                    logger.warning(f"已清理 {len(stale_jobs)} 个因服务重启中断的索引任务")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"清理中断的索引任务失败: {e}")

        # ========== 插件系统初始化 ==========
        logger.info("初始化插件系统...")
        try:
            from app.plugins.loader import PluginLoader
            from app.core.config import get_settings

            settings = get_settings()
            from pathlib import Path
            plugin_dir = Path(settings.plugin.plugin_dir)

            # 确保插件目录存在（相对于backend目录）
            if not plugin_dir.is_absolute():
                plugin_dir = backend_dir / plugin_dir
            plugin_dir.mkdir(parents=True, exist_ok=True)

            # 创建插件加载器
            app.state.plugin_loader = PluginLoader(plugin_dir)

            # 发现并加载所有插件
            loaded_plugins = await app.state.plugin_loader.discover_and_load_all()

            # 获取加载错误信息
            load_errors = app.state.plugin_loader.get_load_errors()

            logger.info(f"✅ 插件系统启动完成")
            logger.info(f"   - 成功加载: {len(loaded_plugins)} 个插件")
            if load_errors:
                logger.warning(f"   - 加载失败: {len(load_errors)} 个插件")
                for plugin_id, error in load_errors.items():
                    logger.warning(f"     * {plugin_id}: {error}")

            # 将插件加载器注入到索引服务
            from app.services.file_index_service import get_file_index_service
            index_service = get_file_index_service()
            index_service.set_plugin_loader(app.state.plugin_loader)
            logger.debug("插件加载器已注入到索引服务")

            # 自动执行数据源插件的同步（如果配置启用）
            if settings.plugin.auto_sync_on_startup:
                datasource_plugins = app.state.plugin_loader.get_plugins_by_type("datasource")
                if datasource_plugins:
                    logger.info(f"开始自动同步 {len(datasource_plugins)} 个数据源插件...")
                    for plugin_id, plugin in datasource_plugins.items():
                        if hasattr(plugin, 'sync'):
                            logger.info(f"  → 同步插件: {plugin_id}")
                            try:
                                sync_result = await plugin.sync()
                                if sync_result:
                                    logger.info(f"  ✅ 插件 {plugin_id} 同步完成")
                                else:
                                    logger.warning(f"  ⚠️ 插件 {plugin_id} 同步失败")
                            except Exception as e:
                                logger.error(f"  ❌ 插件 {plugin_id} 同步异常: {e}")
                    logger.info("数据源插件自动同步完成")
                else:
                    logger.info("没有需要同步的数据源插件")

        except Exception as e:
            logger.error(f"❌ 插件系统初始化失败: {str(e)}")
            logger.info("继续运行，但插件功能将不可用")
            app.state.plugin_loader = None
        # =====================================

        # 初始化AI模型服务
        logger.info("加载AI模型...")
        try:
            from app.services.ai_model_manager import ai_model_service
            await ai_model_service.initialize()
            ai_model_service._initialized = True  # 设置初始化标志
            logger.info("AI模型服务加载完成")
        except Exception as e:
            logger.warning(f"AI模型服务初始化失败: {str(e)}")
            logger.info("继续运行，但AI功能可能不可用")
            # 确保即使初始化失败也设置标志，避免重复尝试
            try:
                ai_model_service._initialized = False
            except:
                pass

        # ========== FastMCP 服务器初始化 ==========
        logger.info("初始化 FastMCP 服务器...")
        try:
            from app.core.config import get_settings
            settings = get_settings()

            if settings.mcp.sse_enabled:
                # 创建 FastMCP 服务器实例
                mcp_server = create_mcp_server()

                # 注册所有工具
                register_mcp_tools(mcp_server)

                # 获取 HTTP 应用（Starlette 应用）
                # 使用 transport="sse" 保持与 Claude Desktop 的兼容性
                mcp_app = mcp_server.http_app(path="/", transport="sse")

                # 挂载到 FastAPI（SSE 端点将是 /mcp/sse）
                # 注意：SSE 返回的 endpoint 路径是 /messages/...
                # 客户端需要将其视为 /mcp/messages/... 来访问
                app.mount("/mcp", mcp_app)

                # 保存到 app.state
                app.state.mcp_server = mcp_server
                app.state.mcp_app = mcp_app

                logger.info("✅ FastMCP 服务器初始化完成")
                mcp_host, mcp_port = get_api_address()
                logger.info(f"📡 MCP 端点: http://{mcp_host}:{mcp_port}/mcp")
            else:
                app.state.mcp_server = None
                app.state.mcp_app = None
                logger.info("FastMCP 服务器未启用")
        except Exception as e:
            logger.error(f"❌ FastMCP 服务器初始化失败: {str(e)}")
            app.state.mcp_server = None
            app.state.mcp_app = None
        # =====================================

        # 初始化索引缓存
        logger.info("初始化索引缓存...")
        try:
            from app.services.file_index_service import get_file_index_service
            index_service = get_file_index_service()
            await index_service.load_indexed_files_cache()
            logger.info("索引缓存初始化完成")
        except Exception as e:
            logger.warning(f"索引缓存初始化失败: {str(e)}")
            logger.info("继续运行，但首次增量更新可能较慢")

        # ========== 加载术语扩展配置 ==========
        logger.info("加载术语扩展配置...")
        try:
            from app.services.chunk_search_service import configure_glossary_expansion
            from app.api.glossary_settings import get_glossary_expansion_config_from_db
            from app.core.database import SessionLocal

            db = SessionLocal()
            try:
                config = get_glossary_expansion_config_from_db(db)
                configure_glossary_expansion(
                    enable=config.get('enable', False),
                    collection_ids=config.get('collection_ids'),
                    max_expansion_terms=config.get('max_expansion_terms', 3)
                )
                logger.info("✅ 术语扩展配置加载完成")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"术语扩展配置加载失败: {str(e)}")
            logger.info("继续运行，但术语扩展功能可能不可用")
        # =====================================

        # ========== 分块向量索引量化迁移（后台执行，不阻塞启动） ==========
        try:
            from app.core.config import get_settings as _get_settings

            if _get_settings().chunk.faiss_migrate_on_startup:
                import threading as _threading
                import time as _time

                def _run_index_migration():
                    _time.sleep(5)  # 等待启动流程稳定
                    try:
                        from app.services.chunk_index_service import get_chunk_index_service
                        service = get_chunk_index_service()
                        logger.info(
                            f"[索引迁移] 开始检查: 配置={_get_settings().chunk.faiss_quantizer}, "
                            f"索引={service.chunk_faiss_index_path}"
                        )
                        service.migrate_index_if_needed()
                    except Exception as migration_error:
                        logger.warning(f"[索引迁移] 后台迁移失败: {migration_error}")

                _threading.Thread(
                    target=_run_index_migration,
                    daemon=True,
                    name="index-quantizer-migration"
                ).start()
                logger.info("[索引迁移] 已安排后台检查分块向量索引")
        except Exception as e:
            logger.warning(f"[索引迁移] 启动迁移安排失败: {e}")

        logger.info("✅ 小遥搜索服务启动完成")
        doc_host, doc_port = get_api_address()
        logger.info(f"📖 API文档: http://{doc_host}:{doc_port}/docs")
        logger.info(f"📋 ReDoc文档: http://{doc_host}:{doc_port}/redoc")

    except Exception as e:
        logger.error(f"❌ 服务启动失败: {str(e)}")
        raise

    yield

    # 关闭时执行
    logger.info("小遥搜索服务关闭中...")
    try:
        # 清理插件资源
        if hasattr(app.state, 'plugin_loader') and app.state.plugin_loader:
            logger.info("清理插件资源...")
            await app.state.plugin_loader.cleanup_all()

        # 清理其他资源
        # TODO: 清理其他资源
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
        "http://127.0.0.1:5173",
        "http://[::1]:3000",
        "http://[::1]:5173"
    ],  # Electron渲染进程地址（包括IPv6）
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
app.include_router(settings_router)
app.include_router(glossary_collections_router)
app.include_router(glossary_terms_router)
app.include_router(glossary_router)
app.include_router(glossary_settings_router)

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


# MCP 健康检查端点
@app.get("/mcp/health")
async def mcp_health():
    """FastMCP 服务器健康检查"""
    tools = []
    if hasattr(app.state, 'mcp_server') and app.state.mcp_server:
        # FastMCP 通过 _tool_manager 获取工具列表
        tools = list(app.state.mcp_server._tool_manager._tools.keys())

    return {
        "status": "enabled" if hasattr(app.state, 'mcp_server') and app.state.mcp_server else "disabled",
        "server": "fastmcp",
        "tools_count": len(tools),
        "tools": tools
    }

# 启动服务
if __name__ == "__main__":
    import uvicorn

    # 从环境变量获取配置
    host, port = get_api_address()
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    # uvicorn 只接受小写日志级别（info/debug/warning/error/critical/trace），
    # 而 .env 中惯例写大写（如 LOG_LEVEL=INFO），这里统一归一化并做兜底校验
    log_level = os.getenv("LOG_LEVEL", "info").strip().lower()
    if log_level not in {"critical", "error", "warning", "info", "debug", "trace"}:
        logger.warning(f"无效的日志级别: {log_level!r}，已回退为 info")
        log_level = "info"

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