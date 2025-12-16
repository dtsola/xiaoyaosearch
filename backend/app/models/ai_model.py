"""
AI模型配置数据模型
定义AI模型配置的数据库表结构
"""
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
    def get_default_configs(cls) -> dict:
        """
        获取默认模型配置

        Returns:
            dict: 默认配置字典
        """
        # 检测是否有CUDA可用
        device = cls._get_optimal_device()

        return {
            "bge_m3_local": {
                "model_type": "embedding",
                "provider": "local",
                "model_name": "BAAI/bge-m3",
                "config": {
                    "model_path": "embedding/BAAI/bge-m3",
                    "device": device,
                    "embedding_dim": 1024,
                    "max_length": 8192,
                    "normalize_embeddings": True
                }
            },
            "faster_whisper_local": {
                "model_type": "speech",
                "provider": "local",
                "model_name": "Systran/faster-whisper-base",
                "config": {
                    "model_path": "faster-whisper/Systran/faster-whisper-base",
                    "model_size": "Systran/faster-whisper-base",
                    "compute_type": "auto",
                    "device": device,
                    "language": "zh"
                }
            },
            "cn_clip_local": {
                "model_type": "vision",
                "provider": "local",
                "model_name": "OFA-Sys/chinese-clip-vit-base-patch16",
                "config": {
                    "model_path": "cn-clip/OFA-Sys/chinese-clip-vit-base-patch16",
                    "device": device
                }
            },
            "ollama_local": {
                "model_type": "llm",
                "provider": "local",
                "model_name": "qwen2.5:1.5b",
                "config": {
                    "base_url": "http://localhost:11434",
                    "model": "qwen2.5:1.5b",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "timeout": 30
                }
            }
        }

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<AIModelModel(id={self.id}, type={self.model_type}, provider={self.provider}, name={self.model_name})>"