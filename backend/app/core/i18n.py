"""
国际化(i18n)核心模块
XiaoyaoSearch - 小遥搜索

提供多语言支持，支持从JSON文件加载翻译，支持嵌套键和参数格式化。
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache
from loguru import logger


class I18N:
    """
    国际化翻译类

    支持功能：
    - 从JSON文件加载语言包
    - 嵌套键访问（如 'common.success'）
    - 参数格式化（如 '找到 {count} 个结果'）
    - LRU缓存优化性能
    - 自动回退到默认语言
    """

    def __init__(self, locale_dir: str = "app/locales"):
        """
        初始化i18n实例

        Args:
            locale_dir: 语言包目录路径
        """
        self.locale_dir = Path(locale_dir)
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._load_locales()

    def _load_locales(self):
        """加载所有语言包"""
        try:
            # 遍历语言包目录中的所有JSON文件
            for locale_file in self.locale_dir.glob("*.json"):
                locale_code = locale_file.stem  # 获取文件名作为语言代码

                try:
                    with open(locale_file, 'r', encoding='utf-8') as f:
                        self._translations[locale_code] = json.load(f)
                        logger.debug(f"Loaded locale: {locale_code} from {locale_file}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse locale file {locale_file}: {e}")
                except Exception as e:
                    logger.error(f"Failed to load locale {locale_code}: {e}")

            logger.info(f"Loaded {len(self._translations)} locales: {list(self._translations.keys())}")

        except Exception as e:
            logger.error(f"Failed to load locales from {self.locale_dir}: {e}")

    @lru_cache(maxsize=1024)
    def translate(self, key: str, locale: str = "zh_CN", **kwargs) -> str:
        """
        翻译文本（带缓存）

        Args:
            key: 翻译键，支持点号分隔的嵌套键，如 'common.success'
            locale: 语言代码，默认为 'zh_CN'
            **kwargs: 格式化参数

        Returns:
            翻译后的文本，如果找不到翻译则返回键本身

        Examples:
            >>> i18n.translate('common.success', 'zh_CN')
            '操作成功'
            >>> i18n.translate('search.results_count', 'zh_CN', count=10)
            '找到 10 个结果'
        """
        # 标准化语言代码（处理 zh-CN 和 zh_CN）
        locale = locale.replace('-', '_')

        # 如果语言包不存在，回退到中文
        if locale not in self._translations:
            logger.warning(f"Locale '{locale}' not found, falling back to 'zh_CN'")
            locale = "zh_CN"

        # 支持嵌套键访问
        keys = key.split('.')
        value = self._translations[locale]

        try:
            for k in keys:
                value = value[k]
        except (KeyError, TypeError):
            # 如果找不到翻译，返回键本身
            logger.warning(f"Translation key '{key}' not found in locale '{locale}'")
            return key

        # 确保返回的是字符串
        if not isinstance(value, str):
            logger.warning(f"Translation value for '{key}' is not a string: {type(value)}")
            return str(value)

        # 支持参数格式化
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to format translation '{key}' with {kwargs}: {e}")
                return value

        return value

    def t(self, key: str, locale: str = "zh_CN", **kwargs) -> str:
        """
        翻译文本简写方法

        Args:
            key: 翻译键
            locale: 语言代码
            **kwargs: 格式化参数

        Returns:
            翻译后的文本
        """
        return self.translate(key, locale, **kwargs)

    def get_available_locales(self) -> list[str]:
        """
        获取所有可用的语言代码

        Returns:
            语言代码列表
        """
        return list(self._translations.keys())

    def has_locale(self, locale: str) -> bool:
        """
        检查是否存在指定语言包

        Args:
            locale: 语言代码

        Returns:
            是否存在
        """
        locale = locale.replace('-', '_')
        return locale in self._translations

    def has_key(self, key: str, locale: str = "zh_CN") -> bool:
        """
        检查是否存在指定翻译键

        Args:
            key: 翻译键
            locale: 语言代码

        Returns:
            是否存在
        """
        locale = locale.replace('-', '_')

        if locale not in self._translations:
            return False

        keys = key.split('.')
        value = self._translations[locale]

        try:
            for k in keys:
                value = value[k]
            return True
        except (KeyError, TypeError):
            return False

    def reload(self):
        """重新加载所有语言包"""
        self._translations.clear()
        self.translate.cache_clear()  # 清除缓存
        self._load_locales()
        logger.info("Reloaded all locales")


# 全局i18n实例
i18n = I18N()


def get_locale_from_header(accept_language: Optional[str] = None) -> str:
    """
    从 Accept-Language 请求头中解析语言代码

    Args:
        accept_language: Accept-Language 请求头的值

    Returns:
        标准化后的语言代码

    Examples:
        >>> get_locale_from_header('zh-CN')
        'zh_CN'
        >>> get_locale_from_header('en-US')
        'en_US'
        >>> get_locale_from_header(None)
        'zh_CN'
    """
    if not accept_language:
        return "zh_CN"

    # 解析语言代码（支持格式：zh-CN, zh_CN, zh）
    locale = accept_language.split(',')[0].strip()
    locale = locale.replace('-', '_')

    # 如果是简短语言代码（如 'zh'），扩展为完整代码
    if locale == 'zh':
        locale = 'zh_CN'
    elif locale == 'en':
        locale = 'en_US'

    # 检查是否支持该语言
    if i18n.has_locale(locale):
        return locale
    else:
        logger.warning(f"Unsupported locale '{locale}', falling back to 'zh_CN'")
        return "zh_CN"


def t(key: str, locale: str = "zh_CN", **kwargs) -> str:
    """
    全局翻译函数简写

    Args:
        key: 翻译键
        locale: 语言代码
        **kwargs: 格式化参数

    Returns:
        翻译后的文本

    Examples:
        >>> t('common.success')
        '操作成功'
        >>> t('search.results_count', count=10)
        '找到 10 个结果'
    """
    return i18n.translate(key, locale, **kwargs)


__all__ = [
    'I18N',
    'i18n',
    'get_locale_from_header',
    't'
]