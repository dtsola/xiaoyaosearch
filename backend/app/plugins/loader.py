"""
插件加载器模块

负责插件的发现、加载、管理和生命周期控制。
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import importlib.util
import sys
import yaml
import asyncio
from datetime import datetime
import logging

from .base import BasePlugin, PluginType, PluginStatus
from app.core.logging_config import logger

# 插件目录结构常量
DATASOURCE_DIR = "datasource"
AI_MODEL_DIR = "ai_model"
PLUGIN_FILE = "plugin.py"
CONFIG_FILE = "config.yaml"


class PluginLoadError(Exception):
    """插件加载错误"""
    pass


class PluginConfigError(Exception):
    """插件配置错误"""
    pass


class PluginLoader:
    """插件加载器

    职责：
    - 发现插件目录中的所有插件
    - 动态加载插件模块
    - 验证插件配置
    - 管理插件生命周期（初始化、清理）
    - 提供插件查询接口

    使用示例：
        loader = PluginLoader(plugin_dir=Path("data/plugins"))
        await loader.discover_and_load_all()
        datasource_plugins = loader.get_plugins_by_type(PluginType.DATASOURCE)
    """

    def __init__(self, plugin_dir: Path):
        """初始化插件加载器

        Args:
            plugin_dir: 插件根目录路径

        目录结构：
            plugin_dir/
            ├── datasource/
            │   ├── yuque/
            │   │   ├── plugin.py
            │   │   ├── config.yaml
            │   │   └── data/
            │   └── feishu/
            │       ├── plugin.py
            │       └── config.yaml
            └── ai_model/
                └── ...
        """
        self.plugin_dir = Path(plugin_dir)
        self._loaded_plugins: Dict[str, BasePlugin] = {}
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}
        self._load_errors: Dict[str, str] = {}
        self._discovery_time: Optional[datetime] = None

        # 创建插件目录（如果不存在）
        self._ensure_plugin_directories()

    def _ensure_plugin_directories(self):
        """确保插件目录结构存在"""
        try:
            self.plugin_dir.mkdir(parents=True, exist_ok=True)
            (self.plugin_dir / DATASOURCE_DIR).mkdir(exist_ok=True)
            (self.plugin_dir / AI_MODEL_DIR).mkdir(exist_ok=True)
            logger.info(f"插件目录已就绪: {self.plugin_dir}")
        except Exception as e:
            logger.error(f"创建插件目录失败: {e}")

    async def discover_and_load_all(self) -> Dict[str, BasePlugin]:
        """发现并加载所有插件

        遍历插件目录，自动发现并加载所有有效的插件。

        Returns:
            dict: 已成功加载的插件字典 {plugin_id: plugin_instance}

        注意：
            - 插件必须包含 plugin.py 和 config.yaml
            - 配置中 enabled=true 才会加载
            - 加载失败的插件会被记录到 _load_errors
        """
        logger.info("开始发现和加载插件...")
        start_time = datetime.now()
        self._discovery_time = start_time
        self._load_errors.clear()

        # 加载各类型插件
        await self._load_plugins_from_directory(DATASOURCE_DIR, PluginType.DATASOURCE)
        await self._load_plugins_from_directory(AI_MODEL_DIR, PluginType.AI_MODEL)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"插件发现完成: 成功 {len(self._loaded_plugins)} 个, "
            f"失败 {len(self._load_errors)} 个, "
            f"耗时 {duration:.2f} 秒"
        )

        return self._loaded_plugins

    async def _load_plugins_from_directory(self, dir_name: str, plugin_type: PluginType):
        """从指定目录加载插件

        Args:
            dir_name: 子目录名称（如 "datasource"）
            plugin_type: 插件类型
        """
        plugin_type_dir = self.plugin_dir / dir_name

        if not plugin_type_dir.exists():
            logger.debug(f"插件目录不存在: {plugin_type_dir}")
            return

        for plugin_path in plugin_type_dir.iterdir():
            # 跳过非目录和隐藏目录
            if not plugin_path.is_dir() or plugin_path.name.startswith('.'):
                continue

            await self._load_plugin(plugin_path, plugin_type)

    async def _load_plugin(self, plugin_path: Path, plugin_type: PluginType):
        """加载单个插件

        Args:
            plugin_path: 插件目录路径
            plugin_type: 插件类型

        加载流程：
        1. 检查必要文件（plugin.py, config.yaml）
        2. 加载并验证配置
        3. 动态导入插件模块
        4. 实例化插件类
        5. 调用 initialize() 初始化
        """
        plugin_id = plugin_path.name
        plugin_file = plugin_path / PLUGIN_FILE
        config_file = plugin_path / CONFIG_FILE

        # 检查必要文件
        if not plugin_file.exists():
            self._load_errors[plugin_id] = f"缺少 {PLUGIN_FILE} 文件"
            logger.warning(f"插件 {plugin_id} 缺少 {PLUGIN_FILE}")
            return

        # 动态导入插件模块
        try:
            plugin_instance = await self._import_plugin_module(
                plugin_path, plugin_id, plugin_type
            )

            if plugin_instance:
                requires_config = True
                if hasattr(plugin_instance, "requires_config"):
                    requires_config = plugin_instance.requires_config()

                # 加载配置。零配置插件允许缺少 config.yaml。
                if requires_config:
                    if not config_file.exists():
                        self._load_errors[plugin_id] = f"缺少 {CONFIG_FILE} 文件"
                        logger.warning(f"插件 {plugin_id} 缺少 {CONFIG_FILE}")
                        return
                    config = self._load_config(config_file)
                else:
                    if config_file.exists():
                        config = self._load_config(config_file)
                    else:
                        config = {
                            "plugin": {
                                "id": plugin_id,
                                "enabled": True,
                            },
                            plugin_type.value: {},
                        }
                        logger.info(f"插件 {plugin_id} 无需配置，使用默认配置启动")

                self._plugin_configs[plugin_id] = config

                plugin_config = config.get("plugin", {})
                if not plugin_config.get("enabled", False):
                    logger.info(f"插件 {plugin_id} 已禁用，跳过加载")
                    return

                datasource_config = config.get("datasource", {})
                if plugin_type == PluginType.AI_MODEL:
                    datasource_config = config.get("ai_model", {})

                # 初始化插件
                if await self._initialize_plugin(plugin_instance, datasource_config, plugin_id):
                    self._loaded_plugins[plugin_id] = plugin_instance
                    logger.info(f"✅ 插件加载成功: {plugin_id}")

        except Exception as e:
            self._load_errors[plugin_id] = f"加载失败: {str(e)}"
            logger.error(f"加载插件异常 {plugin_id}: {e}", exc_info=True)

    async def _import_plugin_module(
        self, plugin_path: Path, plugin_id: str, plugin_type: PluginType
    ) -> Optional[BasePlugin]:
        """动态导入插件模块

        Args:
            plugin_path: 插件目录路径
            plugin_id: 插件ID
            plugin_type: 插件类型

        Returns:
            插件实例，失败返回 None
        """
        plugin_file = plugin_path / PLUGIN_FILE
        module_name = f"plugin_{plugin_type.value}_{plugin_id}"

        spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        if spec is None or spec.loader is None:
            raise PluginLoadError(f"无法创建模块规范: {plugin_file}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise PluginLoadError(f"执行模块失败: {e}")

        # 查找插件类并实例化
        import inspect

        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # 检查是否是插件类
            if (
                isinstance(attr, type)
                and issubclass(attr, BasePlugin)
                and attr != BasePlugin
                # 排除抽象类（包括 DataSourcePlugin 等接口类）
                and not inspect.isabstract(attr)
            ):
                return attr()

        raise PluginLoadError(f"未找到有效的插件类（继承自 BasePlugin 且非抽象）")

    async def _initialize_plugin(
        self, plugin: BasePlugin, config: Dict[str, Any], plugin_id: str
    ) -> bool:
        """初始化插件

        Args:
            plugin: 插件实例
            config: 插件配置
            plugin_id: 插件ID

        Returns:
            bool: 初始化是否成功
        """
        try:
            # 验证配置
            if not await plugin.validate_config(config):
                logger.error(f"插件 {plugin_id} 配置验证失败")
                return False

            # 调用初始化方法
            success = await plugin.initialize(config)

            if not success:
                error_msg = plugin.error_message or "初始化失败"
                self._load_errors[plugin_id] = error_msg
                logger.error(f"插件 {plugin_id} 初始化失败: {error_msg}")
                return False

            return True

        except Exception as e:
            logger.error(f"插件 {plugin_id} 初始化异常: {e}", exc_info=True)
            return False

    def _load_config(self, config_file: Path) -> Dict[str, Any]:
        """加载 YAML 配置文件

        Args:
            config_file: 配置文件路径

        Returns:
            dict: 配置字典

        Raises:
            PluginConfigError: 配置文件解析失败
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise PluginConfigError("配置文件格式错误：根节点必须是字典")
                return config
        except yaml.YAMLError as e:
            raise PluginConfigError(f"YAML 解析失败: {e}")
        except Exception as e:
            raise PluginConfigError(f"读取配置文件失败: {e}")

    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """获取指定插件实例

        Args:
            plugin_id: 插件ID

        Returns:
            插件实例，不存在返回 None
        """
        return self._loaded_plugins.get(plugin_id)

    def get_plugins_by_type(self, plugin_type: str) -> Dict[str, BasePlugin]:
        """按类型获取插件

        Args:
            plugin_type: 插件类型字符串（如 "datasource"）

        Returns:
            dict: 该类型的所有插件 {plugin_id: plugin_instance}
        """
        result = {}
        for plugin_id, plugin in self._loaded_plugins.items():
            metadata = plugin.get_metadata()
            if metadata.get("type") == plugin_type:
                result[plugin_id] = plugin
        return result

    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """获取所有已加载的插件

        Returns:
            dict: 所有插件 {plugin_id: plugin_instance}
        """
        return self._loaded_plugins.copy()

    def get_load_errors(self) -> Dict[str, str]:
        """获取加载错误信息

        Returns:
            dict: 错误信息 {plugin_id: error_message}
        """
        return self._load_errors.copy()

    async def cleanup_all(self):
        """清理所有插件资源

        在应用关闭时调用，确保所有插件正确释放资源。
        """
        logger.info(f"开始清理 {len(self._loaded_plugins)} 个插件...")

        for plugin_id, plugin in list(self._loaded_plugins.items()):
            try:
                await plugin.cleanup()
                logger.debug(f"插件 {plugin_id} 清理完成")
            except Exception as e:
                logger.error(f"清理插件失败 {plugin_id}: {e}")

        self._loaded_plugins.clear()
        logger.info("插件清理完成")

    async def reload_plugin(self, plugin_id: str) -> bool:
        """重新加载指定插件

        Args:
            plugin_id: 插件ID

        Returns:
            bool: 重载是否成功
        """
        # TODO: 实现插件热重载
        logger.warning(f"插件热重载功能尚未实现: {plugin_id}")
        return False

    def get_plugin_count(self) -> int:
        """获取已加载插件数量"""
        return len(self._loaded_plugins)

    def get_status_summary(self) -> Dict[str, Any]:
        """获取加载器状态摘要

        Returns:
            dict: 状态信息
        """
        return {
            "plugin_dir": str(self.plugin_dir),
            "total_loaded": len(self._loaded_plugins),
            "total_errors": len(self._load_errors),
            "discovery_time": self._discovery_time.isoformat() if self._discovery_time else None,
            "plugins": {
                plugin_id: {
                    "metadata": plugin.get_metadata(),
                    "status": plugin.status.value,
                    "is_ready": plugin.is_ready
                }
                for plugin_id, plugin in self._loaded_plugins.items()
            },
            "errors": self._load_errors
        }
