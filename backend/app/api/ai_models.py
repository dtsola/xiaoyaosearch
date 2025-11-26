"""
AI模型管理API路由
提供AI模型状态管理、配置和监控的API接口
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.logging_config import get_logger
from app.services.ai_model_manager import ai_model_service

logger = get_logger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI模型管理"])


class ModelStatusResponse(BaseModel):
    """模型状态响应模型"""
    success: bool
    data: Dict[str, Any]
    message: str


class ModelListResponse(BaseModel):
    """模型列表响应模型"""
    success: bool
    data: Dict[str, List[Dict[str, Any]]]
    message: str


class ModelActionResponse(BaseModel):
    """模型操作响应模型"""
    success: bool
    data: Dict[str, Any]
    message: str


@router.get("/status", response_model=ModelStatusResponse, summary="获取所有AI模型状态")
async def get_ai_models_status():
    """
    获取所有AI模型的状态信息

    Returns:
        ModelStatusResponse: 包含所有AI模型状态信息的响应
    """
    try:
        status_info = await ai_model_service.get_model_status()
        logger.info("获取AI模型状态成功")

        return ModelStatusResponse(
            success=True,
            data=status_info,
            message="获取AI模型状态成功"
        )

    except Exception as e:
        logger.error(f"获取AI模型状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取AI模型状态失败: {str(e)}")


@router.get("/models", response_model=ModelListResponse, summary="获取可用模型列表")
async def get_available_models():
    """
    获取所有可用的AI模型列表

    Returns:
        ModelListResponse: 按类型分组的可用模型列表
    """
    try:
        models_info = await ai_model_service.get_available_models()
        logger.info("获取可用模型列表成功")

        return ModelListResponse(
            success=True,
            data=models_info,
            message="获取可用模型列表成功"
        )

    except Exception as e:
        logger.error(f"获取可用模型列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取可用模型列表失败: {str(e)}")


@router.post("/load/{model_id}", response_model=ModelActionResponse, summary="加载指定模型")
async def load_model(model_id: str):
    """
    加载指定的AI模型

    Args:
        model_id: 模型ID

    Returns:
        ModelActionResponse: 模型加载结果
    """
    try:
        result = await ai_model_service.load_model(model_id)

        if result:
            message = f"模型 {model_id} 加载成功"
            logger.info(message)
        else:
            message = f"模型 {model_id} 加载失败"
            logger.warning(message)

        return ModelActionResponse(
            success=result,
            data={"model_id": model_id, "loaded": result},
            message=message
        )

    except Exception as e:
        logger.error(f"加载模型 {model_id} 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"加载模型失败: {str(e)}")


@router.post("/unload/{model_id}", response_model=ModelActionResponse, summary="卸载指定模型")
async def unload_model(model_id: str):
    """
    卸载指定的AI模型

    Args:
        model_id: 模型ID

    Returns:
        ModelActionResponse: 模型卸载结果
    """
    try:
        result = await ai_model_service.unload_model(model_id)

        if result:
            message = f"模型 {model_id} 卸载成功"
            logger.info(message)
        else:
            message = f"模型 {model_id} 卸载失败"
            logger.warning(message)

        return ModelActionResponse(
            success=result,
            data={"model_id": model_id, "unloaded": result},
            message=message
        )

    except Exception as e:
        logger.error(f"卸载模型 {model_id} 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"卸载模型失败: {str(e)}")


@router.post("/load-all", response_model=ModelActionResponse, summary="加载所有模型")
async def load_all_models():
    """
    加载所有AI模型

    Returns:
        ModelActionResponse: 所有模型加载结果
    """
    try:
        results = await ai_model_service.load_all_models()
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        message = f"成功加载 {success_count}/{total_count} 个模型"
        logger.info(message)

        return ModelActionResponse(
            success=success_count > 0,
            data={
                "total_models": total_count,
                "successful_loads": success_count,
                "failed_loads": total_count - success_count,
                "details": results
            },
            message=message
        )

    except Exception as e:
        logger.error(f"加载所有模型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"加载所有模型失败: {str(e)}")


@router.post("/unload-all", response_model=ModelActionResponse, summary="卸载所有模型")
async def unload_all_models():
    """
    卸载所有AI模型

    Returns:
        ModelActionResponse: 所有模型卸载结果
    """
    try:
        results = await ai_model_service.unload_all_models()
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        message = f"成功卸载 {success_count}/{total_count} 个模型"
        logger.info(message)

        return ModelActionResponse(
            success=success_count > 0,
            data={
                "total_models": total_count,
                "successful_unloads": success_count,
                "failed_unloads": total_count - success_count,
                "details": results
            },
            message=message
        )

    except Exception as e:
        logger.error(f"卸载所有模型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"卸载所有模型失败: {str(e)}")


@router.get("/health", response_model=ModelStatusResponse, summary="AI模型健康检查")
async def health_check():
    """
    执行AI模型健康检查

    Returns:
        ModelStatusResponse: 健康检查结果
    """
    try:
        health_results = await ai_model_service.health_check()
        healthy_count = sum(1 for healthy in health_results.values() if healthy)
        total_count = len(health_results)

        message = f"健康检查完成: {healthy_count}/{total_count} 个模型健康"
        logger.info(message)

        return ModelStatusResponse(
            success=healthy_count > 0,
            data={
                "total_models": total_count,
                "healthy_models": healthy_count,
                "unhealthy_models": total_count - healthy_count,
                "details": health_results
            },
            message=message
        )

    except Exception as e:
        logger.error(f"AI模型健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI模型健康检查失败: {str(e)}")


@router.post("/benchmark", response_model=ModelActionResponse, summary="AI模型性能基准测试")
async def benchmark_models(model_types: Optional[List[str]] = None):
    """
    执行AI模型性能基准测试

    Args:
        model_types: 要测试的模型类型列表，可选

    Returns:
        ModelActionResponse: 性能测试结果
    """
    try:
        results = await ai_model_service.benchmark_models(model_types)
        message = "性能基准测试完成"
        logger.info(message)

        return ModelActionResponse(
            success=True,
            data={
                "model_types": model_types or "all",
                "benchmark_results": results
            },
            message=message
        )

    except Exception as e:
        logger.error(f"AI模型性能基准测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI模型性能基准测试失败: {str(e)}")


@router.get("/text-embedding", summary="文本嵌入测试")
async def test_text_embedding(text: str = "这是一个测试文本"):
    """
    测试文本嵌入功能

    Args:
        text: 要测试的文本

    Returns:
        Dict[str, Any]: 文本嵌入结果
    """
    try:
        # 检查AI模型服务是否已初始化
        if not hasattr(ai_model_service, 'model_manager'):
            logger.warning("AI模型服务未初始化，尝试初始化")
            await ai_model_service.initialize()

        # 获取文本嵌入模型
        embedding_model = await ai_model_service.get_model("embedding")
        if not embedding_model:
            logger.error("文本嵌入模型不可用")
            return {
                "success": False,
                "data": {
                    "text": text,
                    "error": "文本嵌入模型不可用",
                    "model_status": await ai_model_service.get_model_status()
                },
                "message": "文本嵌入模型未加载"
            }

        # 执行文本嵌入
        embeddings = await ai_model_service.text_embedding(text)

        # 处理不同类型的嵌入结果
        if hasattr(embeddings, 'shape'):
            # NumPy数组或类似结构
            embedding_shape = embeddings.shape
            if hasattr(embeddings, 'flatten'):
                embedding_sample = embeddings.flatten()[:10].tolist()
            else:
                embedding_sample = str(embeddings)[:100]
        elif hasattr(embeddings, '__len__'):
            # 列表或类似结构
            embedding_shape = (len(embeddings),)
            embedding_sample = embeddings[:10] if len(embeddings) > 10 else embeddings
        else:
            # 其他类型
            embedding_shape = "unknown"
            embedding_sample = str(embeddings)[:100]

        return {
            "success": True,
            "data": {
                "text": text,
                "embedding_shape": embedding_shape,
                "embedding_sample": embedding_sample,
                "model_name": embedding_model.model_name if hasattr(embedding_model, 'model_name') else "unknown"
            },
            "message": "文本嵌入测试成功"
        }

    except Exception as e:
        logger.error(f"文本嵌入测试失败: {str(e)}")
        # 返回详细的错误信息而不是抛出异常
        error_detail = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "text": text
        }

        # 尝试获取模型状态信息
        try:
            model_status = await ai_model_service.get_model_status()
            error_detail["model_status"] = model_status
        except:
            error_detail["model_status"] = "无法获取模型状态"

        return {
            "success": False,
            "data": error_detail,
            "message": f"文本嵌入测试失败: {str(e)}"
        }