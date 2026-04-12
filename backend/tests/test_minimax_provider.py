# backend/tests/test_minimax_provider.py
"""
MiniMax 大语言模型 Provider 单元测试
测试 MiniMax 通过 OpenAI 兼容接口集成的关键行为
"""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import importlib.util

# 直接导入需要的模块，避免触发需要 whoosh/torch 的完整 app 初始化
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_module(relative_path):
    """从相对路径加载模块，不触发完整 app 初始化"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_path = os.path.join(base, relative_path)
    spec = importlib.util.spec_from_file_location("module_" + relative_path.replace("/", "_"), abs_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ai_model_base = _load_module("app/services/ai_model_base.py")
BaseAIModel = ai_model_base.BaseAIModel
ModelType = ai_model_base.ModelType
ProviderType = ai_model_base.ProviderType
ModelStatus = ai_model_base.ModelStatus
AIModelException = ai_model_base.AIModelException

sys.modules["app.services.ai_model_base"] = ai_model_base
sys.modules["app.utils.enum_helpers"] = _load_module("app/utils/enum_helpers.py")

openai_llm_svc = _load_module("app/services/openai_llm_service.py")
OpenAILLMService = openai_llm_svc.OpenAILLMService
create_openai_compatible_service = openai_llm_svc.create_openai_compatible_service


MINIMAX_VALID_CONFIG = {
    "api_key": "test-minimax-api-key",
    "endpoint": "https://api.minimax.io/v1",
    "model": "MiniMax-M2.7",
    "temperature": 1.0,
    "max_tokens": 2048,
}


class TestMiniMaxProviderInit:
    """测试 MiniMax Provider 初始化"""

    def test_creates_instance_with_valid_config(self):
        """能够用有效配置创建实例"""
        service = OpenAILLMService(MINIMAX_VALID_CONFIG.copy())
        assert service is not None
        assert service.model == "MiniMax-M2.7"

    def test_uses_minimax_endpoint(self):
        """默认端点应为 api.minimax.io"""
        service = OpenAILLMService(MINIMAX_VALID_CONFIG.copy())
        assert "minimax.io" in service.endpoint

    def test_auto_sets_minimax_endpoint_when_default_openai(self):
        """当模型名为 MiniMax-* 但端点为 OpenAI 默认时，自动切换到 MiniMax 端点"""
        config = {
            "api_key": "test-key",
            "model": "MiniMax-M2.7",
        }
        service = OpenAILLMService(config)
        assert "minimax.io" in service.endpoint

    def test_raises_without_api_key(self):
        """缺少 api_key 时应抛出异常"""
        with pytest.raises(ValueError, match="api_key"):
            OpenAILLMService({"model": "MiniMax-M2.7"})

    def test_raises_without_model(self):
        """缺少 model 时应抛出异常"""
        with pytest.raises(ValueError, match="model"):
            OpenAILLMService({"api_key": "test-key"})

    def test_highspeed_model_supported(self):
        """支持 MiniMax-M2.7-highspeed 模型"""
        config = MINIMAX_VALID_CONFIG.copy()
        config["model"] = "MiniMax-M2.7-highspeed"
        service = OpenAILLMService(config)
        assert service.model == "MiniMax-M2.7-highspeed"

    def test_factory_function_creates_service(self):
        """工厂函数能够正确创建服务"""
        service = create_openai_compatible_service(MINIMAX_VALID_CONFIG.copy())
        assert isinstance(service, OpenAILLMService)


class TestMiniMaxTemperatureConstraint:
    """测试 MiniMax temperature 约束（范围 (0.0, 1.0]，不能为 0）"""

    def test_temperature_zero_is_corrected_to_one(self):
        """temperature=0 时应自动修正为 1.0"""
        config = MINIMAX_VALID_CONFIG.copy()
        config["temperature"] = 0
        service = OpenAILLMService(config)
        assert service.config["temperature"] == 1.0

    def test_negative_temperature_is_corrected(self):
        """temperature<0 时应自动修正为 1.0"""
        config = MINIMAX_VALID_CONFIG.copy()
        config["temperature"] = -0.5
        service = OpenAILLMService(config)
        assert service.config["temperature"] == 1.0

    def test_valid_temperature_is_preserved(self):
        """合法的 temperature（0 < t <= 1.0）应保持不变"""
        config = MINIMAX_VALID_CONFIG.copy()
        config["temperature"] = 0.7
        service = OpenAILLMService(config)
        assert service.config["temperature"] == 0.7

    def test_temperature_one_is_preserved(self):
        """temperature=1.0 应保持不变"""
        config = MINIMAX_VALID_CONFIG.copy()
        config["temperature"] = 1.0
        service = OpenAILLMService(config)
        assert service.config["temperature"] == 1.0

    def test_non_minimax_model_temperature_zero_not_changed(self):
        """非 MiniMax 模型的 temperature=0 不应被修改"""
        config = {
            "api_key": "test-key",
            "model": "gpt-3.5-turbo",
            "temperature": 0,
        }
        service = OpenAILLMService(config)
        assert service.config["temperature"] == 0


class TestMiniMaxDefaultConfig:
    """测试 MiniMax 在 get_default_configs() 中的预置配置"""

    def _get_configs(self):
        with patch.dict(sys.modules, {"torch": MagicMock()}):
            mod = _load_module("app/models/ai_model.py")
            return mod.AIModelModel.get_default_configs()

    def test_minimax_preset_in_default_configs(self):
        """get_default_configs() 应包含 MiniMax 预置"""
        configs = self._get_configs()
        assert "minimax_cloud" in configs

    def test_minimax_preset_model_type(self):
        """MiniMax 预置的 model_type 应为 llm"""
        configs = self._get_configs()
        assert configs["minimax_cloud"]["model_type"] == "llm"

    def test_minimax_preset_provider(self):
        """MiniMax 预置的 provider 应为 cloud"""
        configs = self._get_configs()
        assert configs["minimax_cloud"]["provider"] == "cloud"

    def test_minimax_preset_model_name(self):
        """MiniMax 预置的默认模型应为 MiniMax-M2.7"""
        configs = self._get_configs()
        assert configs["minimax_cloud"]["model_name"] == "MiniMax-M2.7"

    def test_minimax_preset_endpoint(self):
        """MiniMax 预置的端点应包含 minimax.io"""
        configs = self._get_configs()
        assert "minimax.io" in configs["minimax_cloud"]["config"]["endpoint"]

    def test_minimax_preset_temperature(self):
        """MiniMax 预置的 temperature 默认为 1.0"""
        configs = self._get_configs()
        assert configs["minimax_cloud"]["config"]["temperature"] == 1.0


class TestMiniMaxAPIKeyFromEnv:
    """测试通过环境变量 MINIMAX_API_KEY 配置"""

    def test_minimax_preset_reads_env_api_key(self):
        """MiniMax 预置配置应从 MINIMAX_API_KEY 环境变量读取 API 密钥"""
        with patch.dict(os.environ, {"MINIMAX_API_KEY": "sk-test-env-key"}):
            with patch.dict(sys.modules, {"torch": MagicMock()}):
                mod = _load_module("app/models/ai_model.py")
                configs = mod.AIModelModel.get_default_configs()
            assert configs["minimax_cloud"]["config"]["api_key"] == "sk-test-env-key"


class TestMiniMaxPredictTemperature:
    """测试 predict() 调用时的 temperature 处理"""

    @pytest.mark.asyncio
    async def test_predict_clamps_zero_temperature_for_minimax(self):
        """predict() 调用时若 temperature=0 且模型是 MiniMax，应修正为 1.0"""
        service = OpenAILLMService(MINIMAX_VALID_CONFIG.copy())
        service.status = ModelStatus.LOADED

        captured_request = {}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{"message": {"content": "测试响应"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15}
        })

        class FakeContextManager:
            async def __aenter__(self):
                return mock_response
            async def __aexit__(self, *args):
                return None

        def fake_post(url, json=None, headers=None):
            captured_request.update(json or {})
            return FakeContextManager()

        mock_session = MagicMock()
        mock_session.post = fake_post
        service.session = mock_session

        await service.predict("你好", temperature=0)

        assert captured_request.get("temperature") == 1.0
