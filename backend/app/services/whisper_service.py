"""
FasterWhisper语音识别模型服务
提供高效的语音转文字功能
"""
import asyncio
import logging
import os
import tempfile
import time
from typing import Dict, Any, Optional, List, Union, BinaryIO
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
import torch
import librosa
import soundfile as sf

from app.services.ai_model_base import BaseAIModel, ModelType, ProviderType, ModelStatus, AIModelException
from app.utils.enum_helpers import get_enum_value

logger = logging.getLogger(__name__)


class WhisperTranscriptionService(BaseAIModel):
    """
    FasterWhisper语音识别服务

    提供高效的语音转文字功能，支持多种音频格式
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化Whisper语音识别服务

        Args:
            config: 模型配置参数
        """
        default_config = {
            "model_size": "base",  # tiny, base, small, medium, large-v3
            "compute_type": "auto",  # auto, int8, float16, float32
            "device": "cpu",
            "language": "zh",  # 中文
            "task": "transcribe",  # transcribe or translate
            "max_file_size": 50 * 1024 * 1024,  # 50MB
            "max_duration": 30,  # 最大30秒
            "supported_formats": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"],
            "beam_size": 5,
            "best_of": 5,
            "temperature": 0.0,
            "compression_ratio_threshold": 2.4,
            "log_prob_threshold": -1.0,
            "no_speech_threshold": 0.6
        }

        if config:
            default_config.update(config)

        super().__init__(
            model_name=f"faster-whisper-{default_config['model_size']}",
            model_type=ModelType.SPEECH,
            provider=ProviderType.LOCAL,
            config=default_config
        )

        # 模型相关属性
        self.model = None
        self.device = self._setup_device()

        logger.info(f"初始化FasterWhisper语音识别服务，模型大小: {self.config['model_size']}")

    def _setup_device(self) -> str:
        """
        设置计算设备

        Returns:
            str: 设备字符串
        """
        device_str = self.config.get("device", "cpu")
        if device_str == "auto":
            device_str = "cuda" if torch.cuda.is_available() else "cpu"

        compute_type = self.config.get("compute_type", "auto")
        if compute_type == "auto":
            if device_str == "cuda":
                compute_type = "float16"
            else:
                compute_type = "int8"

        self.config["compute_type"] = compute_type

        if device_str == "cuda":
            logger.info(f"使用GPU设备: {torch.cuda.get_device_name()}")
        else:
            logger.info("使用CPU设备")

        return device_str

    async def load_model(self) -> bool:
        """
        加载Whisper模型

        Returns:
            bool: 加载是否成功
        """
        try:
            self.update_status(ModelStatus.LOADING)
            logger.info(f"开始加载Whisper模型: {self.model_name}")

            # 在线程池中执行模型加载
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._load_model_sync)

            self.update_status(ModelStatus.LOADED)
            logger.info(f"Whisper模型加载成功，模型大小: {self.config['model_size']}")
            return True

        except Exception as e:
            error_msg = f"Whisper模型加载失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(ModelStatus.ERROR, error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    def _load_model_sync(self):
        """同步加载模型"""
        model_size = self.config["model_size"]
        device = self.device
        compute_type = self.config["compute_type"]

        logger.info(f"下载并加载Whisper模型 {model_size} 到 {device} (计算类型: {compute_type})")

        # 创建Whisper模型实例
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

        logger.info("Whisper模型加载完成")

    async def unload_model(self) -> bool:
        """
        卸载Whisper模型

        Returns:
            bool: 卸载是否成功
        """
        try:
            logger.info(f"开始卸载Whisper模型: {self.model_name}")

            # 清理模型
            if self.model:
                del self.model
                self.model = None

            # 清理GPU内存
            if self.device == "cuda":
                torch.cuda.empty_cache()

            self.update_status(ModelStatus.UNLOADED)
            logger.info("Whisper模型卸载成功")
            return True

        except Exception as e:
            error_msg = f"Whisper模型卸载失败: {str(e)}"
            logger.error(error_msg)
            return False

    async def predict(self, audio_input: Union[str, bytes, BinaryIO, np.ndarray], **kwargs) -> Dict[str, Any]:
        """
        语音转文字预测

        Args:
            audio_input: 音频输入，可以是文件路径、字节数据、文件对象或numpy数组
            **kwargs: 其他预测参数
                - language: 指定语言代码
                - task: 任务类型 (transcribe/translate)
                - beam_size: 束搜索大小
                - best_of: 最佳候选数量
                - temperature: 温度参数

        Returns:
            Dict[str, Any]: 转录结果，包含文本、时间戳、置信度等信息

        Raises:
            AIModelException: 预测失败时抛出异常
        """
        if self.status != ModelStatus.LOADED:
            raise AIModelException(
                f"模型未加载，当前状态: {get_enum_value(self.status)}",
                model_name=self.model_name
            )

        try:
            # 预处理音频输入
            audio_path = await self._preprocess_audio(audio_input)

            # 获取预测参数
            language = kwargs.get("language", self.config.get("language"))
            task = kwargs.get("task", self.config.get("task", "transcribe"))
            beam_size = kwargs.get("beam_size", self.config.get("beam_size", 5))
            best_of = kwargs.get("best_of", self.config.get("best_of", 5))
            temperature = kwargs.get("temperature", self.config.get("temperature", 0.0))

            logger.info(f"开始语音转录，音频文件: {audio_path}, 语言: {language}")

            # 在线程池中执行语音转录
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._transcribe_sync, audio_path, language, task, beam_size, best_of, temperature
            )

            # 清理临时文件
            if audio_path != audio_input and os.path.exists(audio_path):
                os.remove(audio_path)

            self.record_usage()
            logger.info(f"语音转录完成，识别文本长度: {len(result['text'])}")
            return result

        except Exception as e:
            error_msg = f"语音转录失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)

    async def _preprocess_audio(self, audio_input: Union[str, bytes, BinaryIO, np.ndarray]) -> str:
        """
        预处理音频输入

        Args:
            audio_input: 音频输入

        Returns:
            str: 处理后的音频文件路径
        """
        # 如果是文件路径
        if isinstance(audio_input, str):
            if not os.path.exists(audio_input):
                raise AIModelException(f"音频文件不存在: {audio_input}", model_name=self.model_name)

            # 检查文件大小
            file_size = os.path.getsize(audio_input)
            if file_size > self.config.get("max_file_size", 50 * 1024 * 1024):
                raise AIModelException(
                    f"音频文件过大，当前大小: {file_size} bytes，最大限制: {self.config['max_file_size']} bytes",
                    model_name=self.model_name
                )

            # 检查文件格式
            file_ext = Path(audio_input).suffix.lower()
            if file_ext not in self.config.get("supported_formats", []):
                raise AIModelException(
                    f"不支持的音频格式: {file_ext}，支持的格式: {self.config['supported_formats']}",
                    model_name=self.model_name
                )

            # 检查音频时长
            try:
                duration = librosa.get_duration(path=audio_input)
                if duration > self.config.get("max_duration", 30):
                    raise AIModelException(
                        f"音频时长过长，当前时长: {duration:.1f}秒，最大限制: {self.config['max_duration']}秒",
                        model_name=self.model_name
                    )
            except Exception as e:
                logger.warning(f"无法获取音频时长: {str(e)}")

            return audio_input

        # 如果是字节数据或文件对象，保存为临时文件
        elif isinstance(audio_input, (bytes, BinaryIO)):
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"whisper_input_{int(time.time())}.wav")

            try:
                if isinstance(audio_input, bytes):
                    # 假设是WAV格式的字节数据
                    with open(temp_file, "wb") as f:
                        f.write(audio_input)
                else:
                    # 文件对象
                    audio_input.seek(0)
                    with open(temp_file, "wb") as f:
                        f.write(audio_input.read())

                return temp_file

            except Exception as e:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                raise AIModelException(f"保存音频数据失败: {str(e)}", model_name=self.model_name)

        # 如果是numpy数组
        elif isinstance(audio_input, np.ndarray):
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"whisper_input_{int(time.time())}.wav")

            try:
                sf.write(temp_file, audio_input, 16000)  # 假设采样率为16kHz
                return temp_file

            except Exception as e:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                raise AIModelException(f"保存音频数组失败: {str(e)}", model_name=self.model_name)

        else:
            raise AIModelException(f"不支持的音频输入类型: {type(audio_input)}", model_name=self.model_name)

    def _transcribe_sync(self, audio_path: str, language: str, task: str, beam_size: int, best_of: int, temperature: float) -> Dict[str, Any]:
        """
        同步执行语音转录

        Args:
            audio_path: 音频文件路径
            language: 语言代码
            task: 任务类型
            beam_size: 束搜索大小
            best_of: 最佳候选数量
            temperature: 温度参数

        Returns:
            Dict[str, Any]: 转录结果
        """
        start_time = time.time()

        # 执行转录
        segments, info = self.model.transcribe(
            audio_path,
            language=language if language != "auto" else None,
            task=task,
            beam_size=beam_size,
            best_of=best_of,
            temperature=temperature,
            compression_ratio_threshold=self.config.get("compression_ratio_threshold", 2.4),
            log_prob_threshold=self.config.get("log_prob_threshold", -1.0),
            no_speech_threshold=self.config.get("no_speech_threshold", 0.6)
        )

        # 处理转录结果
        segments_list = []
        full_text = ""
        total_confidence = 0.0
        segment_count = 0

        for segment in segments:
            segment_data = {
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "tokens": segment.tokens,
                "temperature": segment.temperature,
                "avg_logprob": segment.avg_logprob,
                "compression_ratio": segment.compression_ratio,
                "no_speech_prob": segment.no_speech_prob
            }
            segments_list.append(segment_data)

            # 累积文本
            if segment.text.strip():
                full_text += segment.text.strip() + " "
                segment_count += 1
                # 计算置信度（基于平均对数概率）
                confidence = np.exp(segment.avg_logprob) if segment.avg_logprob < 0 else 1.0
                total_confidence += confidence

        # 计算平均置信度
        avg_confidence = total_confidence / segment_count if segment_count > 0 else 0.0

        # 处理结果
        result = {
            "text": full_text.strip(),
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "segments": segments_list,
            "avg_confidence": float(avg_confidence),
            "processing_time": time.time() - start_time,
            "model_size": self.config["model_size"],
            "task": task
        }

        return result

    async def transcribe_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        转录音频文件

        Args:
            file_path: 音频文件路径
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 转录结果
        """
        return await self.predict(file_path, **kwargs)

    async def transcribe_bytes(self, audio_bytes: bytes, **kwargs) -> Dict[str, Any]:
        """
        转录音频字节数据

        Args:
            audio_bytes: 音频字节数据
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 转录结果
        """
        return await self.predict(audio_bytes, **kwargs)

    async def batch_transcribe(self, audio_inputs: List[Union[str, bytes]], **kwargs) -> List[Dict[str, Any]]:
        """
        批量转录音频

        Args:
            audio_inputs: 音频输入列表
            **kwargs: 其他参数

        Returns:
            List[Dict[str, Any]]: 转录结果列表
        """
        results = []
        for i, audio_input in enumerate(audio_inputs):
            try:
                result = await self.predict(audio_input, **kwargs)
                result["batch_index"] = i
                results.append(result)
            except Exception as e:
                logger.error(f"批量转录第{i}个音频失败: {str(e)}")
                results.append({
                    "batch_index": i,
                    "error": str(e),
                    "success": False
                })

        return results

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict[str, Any]: 模型信息
        """
        return {
            "model_name": self.model_name,
            "model_type": get_enum_value(self.model_type),
            "provider": get_enum_value(self.provider),
            "model_size": self.config.get("model_size", "base"),
            "device": self.device,
            "compute_type": self.config.get("compute_type", "auto"),
            "language": self.config.get("language", "zh"),
            "task": self.config.get("task", "transcribe"),
            "max_duration": self.config.get("max_duration", 30),
            "max_file_size": self.config.get("max_file_size", 50 * 1024 * 1024),
            "supported_formats": self.config.get("supported_formats", []),
            "beam_size": self.config.get("beam_size", 5),
            "best_of": self.config.get("best_of", 5)
        }

    def _get_test_input(self) -> str:
        """获取健康检查的测试输入"""
        # 创建一个简短的静音音频作为测试
        sample_rate = 16000
        duration = 1  # 1秒静音
        silence = np.zeros(sample_rate * duration, dtype=np.float32)
        temp_file = os.path.join(tempfile.gettempdir(), "whisper_test.wav")
        sf.write(temp_file, silence, sample_rate)
        return temp_file

    async def benchmark_performance(self, test_audio_files: List[str], num_runs: int = 3) -> Dict[str, Any]:
        """
        性能基准测试

        Args:
            test_audio_files: 测试音频文件列表
            num_runs: 运行次数

        Returns:
            Dict[str, Any]: 性能测试结果
        """
        try:
            logger.info(f"开始Whisper性能基准测试，音频数量: {len(test_audio_files)}, 运行次数: {num_runs}")

            times = []
            total_duration = 0.0

            # 计算总音频时长
            for audio_file in test_audio_files:
                try:
                    duration = librosa.get_duration(path=audio_file)
                    total_duration += duration
                except Exception as e:
                    logger.warning(f"无法获取音频时长: {audio_file}, 错误: {str(e)}")

            for run in range(num_runs):
                start_time = time.time()
                await self.batch_transcribe(test_audio_files)
                end_time = time.time()
                run_time = end_time - start_time
                times.append(run_time)
                logger.info(f"第{run + 1}次运行耗时: {run_time:.3f}秒")

            avg_time = np.mean(times)
            realtime_factor = total_duration / avg_time if avg_time > 0 else 0.0  # 实时因子

            results = {
                "model_name": self.model_name,
                "num_files": len(test_audio_files),
                "total_audio_duration": total_duration,
                "num_runs": num_runs,
                "times": times,
                "avg_time": float(avg_time),
                "min_time": float(np.min(times)),
                "max_time": float(np.max(times)),
                "realtime_factor": float(realtime_factor),  # 音频时长/处理时间
                "device": self.device
            }

            logger.info(f"性能基准测试完成，平均耗时: {avg_time:.3f}秒，实时因子: {realtime_factor:.2f}")
            return results

        except Exception as e:
            error_msg = f"性能基准测试失败: {str(e)}"
            logger.error(error_msg)
            raise AIModelException(error_msg, model_name=self.model_name)


# 创建Whisper服务实例的工厂函数
def create_whisper_service(config: Dict[str, Any] = None) -> WhisperTranscriptionService:
    """
    创建Whisper语音识别服务实例

    Args:
        config: 模型配置参数

    Returns:
        WhisperTranscriptionService: Whisper服务实例
    """
    return WhisperTranscriptionService(config or {})