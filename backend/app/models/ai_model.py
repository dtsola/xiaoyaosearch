"""
AI模型配置数据模型
定义AI模型配置的数据库表结构
"""
import os
from pathlib import Path
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime


class AIModelModel(Base):
    """
    AI模型配置表模型

    存储各种AI模型的配置参数和状态
    """
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    model_type = Column(String(50), nullable=False, comment="模型类型(embedding/speech/vision/llm)")
    provider = Column(String(20), nullable=False, comment="提供商类型(local/cloud)")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    config_json = Column(Text, nullable=False, comment="JSON格式配置参数")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: AI模型配置字典
        """
        return {
            "id": self.id,
            "model_type": self.model_type,
            "provider": self.provider,
            "model_name": self.model_name,
            "config_json": self.config_json,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_model_types(cls) -> list:
        """
        获取支持的模型类型

        Returns:
            list: 支持的模型类型列表
        """
        return ["embedding", "speech", "vision", "llm"]

    @classmethod
    def get_provider_types(cls) -> list:
        """
        获取支持的提供商类型

        Returns:
            list: 支持的提供商类型列表
        """
        return ["local", "cloud"]

    @classmethod
    def _get_optimal_device(cls) -> str:
        """
        获取最优设备配置

        Returns:
            str: 设备类型 ("cuda" 或 "cpu")
        """
        try:
            # 尝试导入torch来检测CUDA
            import torch

            if torch.cuda.is_available():
                # 检查CUDA设备数量
                device_count = torch.cuda.device_count()
                if device_count > 0:
                    # 获取第一个CUDA设备的名称
                    device_name = torch.cuda.get_device_name(0)
                    cls._log_cuda_info(device_name, device_count)
                    return "cuda"
                else:
                    print("CUDA可用但未找到设备，使用CPU")
                    return "cpu"
            else:
                print("CUDA不可用，使用CPU")
                return "cpu"

        except ImportError:
            print("PyTorch未安装，无法检测CUDA，使用CPU")
            return "cpu"
        except Exception as e:
            print(f"检测CUDA时发生错误: {str(e)}，使用CPU")
            return "cpu"

    @classmethod
    def get_project_root(cls) -> Path:
        """
        获取项目根目录路径

        Returns:
            Path: 项目根目录路径
        """
        # 从当前文件路径向上查找，找到包含 .git 目录或 setup.py 的根目录
        current_path = Path(__file__).resolve()

        # 从 app/models/ai_model.py 向上查找项目根目录
        # 当前路径: .../xiaoyaosearch/backend/app/models/ai_model.py
        # 需要找到: .../xiaoyaosearch/
        # backend/app/models -> backend/app -> backend -> 项目根目录
        project_root = current_path.parent.parent.parent.parent  # 回退4级目录

        # 验证是否是正确的项目根目录（检查项目特征目录）
        # 检查是否有 frontend 或 scripts 目录（项目根目录的标志）
        if not (project_root.joinpath("frontend").exists() or
                project_root.joinpath("scripts").exists() or
                project_root.joinpath(".git").exists()):
            # 如果没找到，尝试其他方法
            # 查找包含 .git 目录的父目录
            search_path = current_path
            while search_path.parent != search_path:  # 避免到达根目录
                if search_path.joinpath(".git").exists():
                    project_root = search_path
                    break
                search_path = search_path.parent
            else:
                # 如果还是没找到，使用默认的计算方式
                project_root = current_path.parent.parent.parent.parent

        return project_root

    @classmethod
    def _log_cuda_info(cls, device_name: str, device_count: int):
        """
        记录CUDA设备信息

        Args:
            device_name: CUDA设备名称
            device_count: CUDA设备数量
        """
        try:
            import torch

            print(f"检测到CUDA设备:")
            print(f"  - 设备数量: {device_count}")
            print(f"  - 主设备: {device_name}")
            print(f"  - CUDA版本: {torch.version.cuda}")

            # 显示所有设备信息
            for i in range(device_count):
                props = torch.cuda.get_device_properties(i)
                memory_gb = props.total_memory / 1024**3
                print(f"  - 设备{i}: {props.name} ({memory_gb:.1f}GB)")

        except Exception as e:
            print(f"记录CUDA信息时发生错误: {str(e)}")

    @classmethod
    def calculate_model_path(cls, model_type: str, model_name: str) -> str:
        """
        根据模型类型和名称计算模型路径

        Args:
            model_type: 模型类型 (embedding/speech/vision)
            model_name: 模型名称

        Returns:
            str: 模型路径
        """
        project_root = cls.get_project_root()

        path_mapping = {
            "embedding": f"data/models/embedding/{model_name}",
            "speech": f"data/models/faster-whisper/{model_name}",
            "vision": f"data/models/cn-clip/{model_name}"
        }

        model_path = path_mapping.get(model_type, "")
        if model_path:
            return str(project_root / model_path)
        return ""

    @classmethod
    def get_default_configs(cls) -> dict:
        """
        获取默认模型配置（基于数据库当前配置）

        Returns:
            dict: 默认配置字典
        """
        # 检测是否有CUDA可用
        device = cls._get_optimal_device()

        # 获取项目根目录
        project_root = cls.get_project_root()

        return {
            "bge_m3_local": {
                "model_type": "embedding",
                "provider": "local",
                "model_name": "BAAI/bge-m3",
                "config": {
                    "model_name": "BAAI/bge-m3",
                    "device": device,
                    "embedding_dim": 1024,
                    "max_length": 8192,
                    "normalize_embeddings": True,
                    "batch_size": 32,
                    "pooling_strategy": "cls",
                    "use_sentence_transformers": False,
                    "cache_dir": None,
                    "trust_remote_code": True,
                    "model_path": str(project_root / "data/models/embedding/BAAI/bge-m3")
                }
            },
            "faster_whisper_local": {
                "model_type": "speech",
                "provider": "local",
                "model_name": "Systran/faster-whisper-base",
                "config": {
                    "model_size": "Systran/faster-whisper-base",
                    "compute_type": "float16",
                    "device": device,
                    "language": "zh",
                    "task": "transcribe",
                    "max_file_size": 52428800,
                    "max_duration": 30,
                    "supported_formats": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"],
                    "beam_size": 5,
                    "best_of": 5,
                    "temperature": 0.0,
                    "compression_ratio_threshold": 2.4,
                    "log_prob_threshold": -1.0,
                    "no_speech_threshold": 0.6,
                    "model_path": str(project_root / "data/models/faster-whisper/Systran/faster-whisper-base")
                }
            },
            "cn_clip_local": {
                "model_type": "vision",
                "provider": "local",
                "model_name": "OFA-Sys/chinese-clip-vit-base-patch16",
                "config": {
                    "model_name": "OFA-Sys/chinese-clip-vit-base-patch16",
                    "device": device,
                    "max_image_size": 512,
                    "supported_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"],
                    "max_file_size": 10485760,
                    "normalize_embeddings": True,
                    "batch_size": 16,
                    "use_chinese_clip": True,
                    "model_path": str(project_root / "data/models/cn-clip/OFA-Sys/chinese-clip-vit-base-patch16")
                }
            },
            "ollama_local": {
                "model_type": "llm",
                "provider": "local",
                "model_name": "qwen2.5:1.5b",
                "config": {
                    "model_name": "qwen2.5:1.5b",
                    "base_url": "http://localhost:11434",
                    "timeout": 30,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "num_predict": 2048,
                    "num_ctx": 2048,
                    "seed": None,
                    "use_cloud_fallback": True,
                    "cloud_provider": "aliyun",
                    "cloud_config": {
                        "aliyun": {
                            "model": "qwen-turbo",
                            "api_key": None,
                            "api_secret": None,
                            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1"
                        },
                        "openai": {
                            "model": "gpt-3.5-turbo",
                            "api_key": None,
                            "endpoint": "https://api.openai.com/v1"
                        }
                    },
                    "device": device
                }
            },
            "minimax_cloud": {
                "model_type": "llm",
                "provider": "cloud",
                "model_name": "MiniMax-M2.7",
                "config": {
                    "api_key": os.environ.get("MINIMAX_API_KEY", ""),
                    "endpoint": "https://api.minimax.io/v1",
                    "model": "MiniMax-M2.7",
                    "timeout": 60,
                    "temperature": 1.0,
                    "max_tokens": 2048,
                    "top_p": 1.0
                }
            }
        }

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<AIModelModel(id={self.id}, type={self.model_type}, provider={self.provider}, name={self.model_name})>"