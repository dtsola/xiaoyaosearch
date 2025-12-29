"""
AI模型配置API路由
提供AI模型配置和测试相关的API接口
"""
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging_config import get_logger
from app.core.exceptions import ResourceNotFoundException, ValidationException
from app.core.i18n import i18n, get_locale_from_header
from app.schemas.requests import AIModelConfigRequest, AIModelTestRequest
from app.schemas.responses import (
    AIModelInfo, AIModelsResponse, AIModelTestResponse, SuccessResponse
)
from app.schemas.enums import ModelType, ProviderType
from app.models.ai_model import AIModelModel
from app.utils.enum_helpers import get_enum_value, is_embedding_model, is_speech_model, is_vision_model, is_llm_model

router = APIRouter(prefix="/api/config", tags=["AI模型配置"])
logger = get_logger(__name__)


def get_locale(accept_language: Optional[str] = Header(None)) -> str:
    """从请求头获取语言设置"""
    return get_locale_from_header(accept_language)


@router.post("/ai-model", response_model=SuccessResponse, summary="更新AI模型配置")
async def update_ai_model_config(
    request: AIModelConfigRequest,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale)
):
    """
    更新AI模型配置

    - **model_type**: 模型类型 (embedding/speech/vision/llm)
    - **provider**: 提供商类型 (local/cloud)
    - **model_name**: 模型名称
    - **config**: 模型配置参数（支持部分更新）
    """
    logger.info(f"更新AI模型配置: type={request.model_type}, provider={request.provider}, name={request.model_name}")

    try:
        # 检查是否已存在相同模型类型的配置（按model_type更新，而不是按model_name）
        model_type_value = get_enum_value(request.model_type)
        logger.info(f"查找模型类型: {model_type_value} (原始: {request.model_type})")

        existing_model = db.query(AIModelModel).filter(
            AIModelModel.model_type == model_type_value,
            AIModelModel.is_active == True
        ).first()

        logger.info(f"查询结果: {existing_model}")
        if existing_model:
            logger.info(f"找到现有模型: ID={existing_model.id}, 名称={existing_model.model_name}")
        else:
            logger.info("未找到现有模型，将创建新的")

        if existing_model:
            # 合并现有配置和新配置 - 只更新前端传入的参数
            existing_config = {}
            if existing_model.config_json:
                try:
                    existing_config = json.loads(existing_model.config_json)
                except json.JSONDecodeError:
                    logger.warning(f"无法解析现有模型配置JSON: {existing_model.config_json}")
                    existing_config = {}

            # 检查模型名称是否发生变化
            model_name_changed = existing_model.model_name != request.model_name
            logger.info(f"模型名称变化检测: {existing_model.model_name} -> {request.model_name}, 变化={model_name_changed}")

            # 如果模型名称变了且不是LLM类型，重新计算model_path
            if model_name_changed and request.model_type != 'llm':
                new_model_path = AIModelModel.calculate_model_path(
                    request.model_type,
                    request.model_name
                )
                logger.info(f"模型名称变化，更新model_path: {new_model_path}")

                # 将新的model_path添加到配置中
                merged_config = existing_config.copy()
                merged_config['model_path'] = new_model_path

                # 对于embedding模型，还需要更新model_name配置
                if request.model_type == 'embedding':
                    merged_config['model_name'] = request.model_name

                # 对于speech模型，需要更新model_size配置
                elif request.model_type == 'speech':
                    merged_config['model_size'] = request.model_name

                # 对于vision模型，需要更新model_name配置
                elif request.model_type == 'vision':
                    merged_config['model_name'] = request.model_name

                logger.info(f"已更新模型路径相关配置参数")
            else:
                # 模型名称没变或者是LLM类型，正常合并配置
                merged_config = existing_config.copy()
                for key, value in request.config.items():
                    merged_config[key] = value
                    logger.info(f"更新配置参数: {key} = {value}")

            # 更新现有配置
            # 如果前端传了model_name，则更新，否则保持原有
            if request.model_name and request.model_name != get_enum_value(request.model_type):
                existing_model.model_name = request.model_name
                logger.info(f"更新模型名称: {existing_model.model_name} -> {request.model_name}")

            existing_model.provider = get_enum_value(request.provider)
            existing_model.config_json = json.dumps(merged_config, ensure_ascii=False)
            existing_model.updated_at = datetime.utcnow()
            db.commit()
            model_id = existing_model.id
            logger.info(f"更新现有AI模型配置: id={model_id}, model_type={request.model_type}, final_name={existing_model.model_name}")
        else:
            # 创建新配置
            # 准备新配置，如果是非LLM类型，需要计算model_path
            new_config = request.config.copy()

            if request.model_type != 'llm':
                new_model_path = AIModelModel.calculate_model_path(
                    request.model_type,
                    request.model_name
                )
                new_config['model_path'] = new_model_path
                logger.info(f"为新模型计算model_path: {new_model_path}")

                # 对于不同类型模型，添加相应的配置参数
                if request.model_type == 'embedding':
                    new_config['model_name'] = request.model_name
                elif request.model_type == 'speech':
                    new_config['model_size'] = request.model_name
                elif request.model_type == 'vision':
                    new_config['model_name'] = request.model_name

            new_model = AIModelModel(
                model_type=get_enum_value(request.model_type),
                provider=get_enum_value(request.provider),
                model_name=request.model_name,
                config_json=json.dumps(new_config, ensure_ascii=False)
            )
            db.add(new_model)
            db.commit()
            db.refresh(new_model)
            model_id = new_model.id
            logger.info(f"创建新AI模型配置: id={model_id}")

        # 构建响应数据
        response_data = {
            "model_id": model_id,
            "model_type": get_enum_value(request.model_type),
            "provider": get_enum_value(request.provider),
            "model_name": request.model_name
        }

        message = i18n.t('model.config_update_success', locale)

        return SuccessResponse(
            data=response_data,
            message=message
        )

    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"更新AI模型配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=i18n.t('model.config_update_failed', locale))


@router.get("/ai-models", response_model=AIModelsResponse, summary="获取所有AI模型配置")
async def get_ai_models(
    model_type: Optional[ModelType] = None,
    provider: Optional[ProviderType] = None,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale)
):
    """
    获取所有AI模型配置

    - **model_type**: 模型类型过滤
    - **provider**: 提供商类型过滤
    """
    logger.info(f"获取AI模型配置列表: type={model_type}, provider={provider}")

    try:
        # 首先检查是否有任何模型配置
        total_models = db.query(AIModelModel).count()

        # 如果没有模型配置，初始化默认配置
        if total_models == 0:
            logger.info("数据库中没有AI模型配置，开始初始化默认配置")
            await _initialize_default_ai_models(db)

        # 构建查询
        query = db.query(AIModelModel)

        # 应用过滤条件
        if model_type:
            query = query.filter(AIModelModel.model_type == get_enum_value(model_type))
        if provider:
            query = query.filter(AIModelModel.provider == get_enum_value(provider))

        # 查询所有配置
        models = query.order_by(AIModelModel.created_at.desc()).all()

        # 转换为响应格式
        model_list = []
        for model in models:
            model_info = AIModelInfo(
                id=model.id,
                model_type=model.model_type,
                provider=model.provider,
                model_name=model.model_name,
                config_json=model.config_json,
                is_active=model.is_active,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
            model_list.append(model_info)

        logger.info(f"返回AI模型配置: 数量={len(model_list)}")

        return AIModelsResponse(
            data=model_list,
            message=i18n.t('model.get_success', locale)
        )

    except Exception as e:
        logger.error(f"获取AI模型配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=i18n.t('model.get_failed', locale))


@router.post("/ai-model/{model_id}/test", response_model=AIModelTestResponse, summary="测试AI模型")
async def test_ai_model(
    model_id: int,
    request: AIModelTestRequest = None,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale)
):
    """
    测试AI模型连通性

    - **model_id**: 模型配置ID
    - **test_data**: 测试数据（可选）
    - **config_override**: 临时配置覆盖（可选）
    """
    logger.info(f"测试AI模型: id={model_id}")

    try:
        # 查询模型配置
        model_config = db.query(AIModelModel).filter(
            AIModelModel.id == model_id
        ).first()

        if not model_config:
            raise ResourceNotFoundException("AI模型配置", str(model_id))

        # 解析配置
        config = json.loads(model_config.config_json)
        if request and request.config_override:
            config.update(request.config_override)

        # 执行真实的模型测试
        import time
        start_time = time.time()

        test_passed = False
        test_message = i18n.t('model.test_start', locale, model_name=model_config.model_name)

        try:
            # 导入AI模型服务
            from app.services.ai_model_manager import ai_model_service

            # 根据模型类型执行相应测试
            if is_embedding_model(model_config.model_type):
                # 测试文本嵌入模型
                test_text = "这是一个测试文本，用于验证文本嵌入模型的功能。"
                embedding_result = await ai_model_service.text_embedding(test_text)

                if embedding_result is not None:
                    # 检查向量维度
                    if hasattr(embedding_result, 'shape'):
                        dimension = embedding_result.shape[1] if len(embedding_result.shape) > 1 else len(embedding_result)
                    elif hasattr(embedding_result, '__len__'):
                        dimension = len(embedding_result)
                    else:
                        dimension = 'unknown'

                    test_passed = True
                    test_message = i18n.t('model.text_embedding_success', locale, dimension=dimension)
                else:
                    test_passed = False
                    test_message = i18n.t('model.text_embedding_failed', locale)

            elif is_speech_model(model_config.model_type):
                # 测试语音识别模型（使用真实音频文件）
                test_audio_path = "../data/test-data/test.mp3"  # 真实音频文件路径
                try:
                    # 读取音频文件
                    with open(test_audio_path, 'rb') as f:
                        test_audio = f.read()

                    speech_result = await ai_model_service.speech_to_text(test_audio)
                    if speech_result and "text" in speech_result:
                        test_passed = True
                        test_message = i18n.t('model.speech_success', locale)
                    else:
                        test_passed = False
                        test_message = i18n.t('model.speech_failed', locale)
                except FileNotFoundError:
                    test_passed = False
                    test_message = i18n.t('model.speech_file_not_found', locale, path=test_audio_path)
                except Exception as e:
                    test_passed = False
                    test_message = i18n.t('model.speech_test_error', locale, error=str(e))

            elif is_vision_model(model_config.model_type):
                # 测试图像理解模型（使用真实图片文件）
                test_image_path = "../data/test-data/pokemon.jpeg"  # 真实图片文件路径
                test_texts = ["描述这张图片的内容", "这张图片展示了什么", "这是一张宝可梦图片"]
                try:
                    vision_result = await ai_model_service.image_understanding(test_image_path, test_texts)
                    if vision_result and "best_match" in vision_result:
                        test_passed = True
                        test_message = i18n.t('model.vision_success', locale)
                    else:
                        test_passed = False
                        test_message = i18n.t('model.vision_failed', locale)
                except Exception as e:
                    test_passed = False
                    test_message = i18n.t('model.vision_test_error', locale, error=str(e))

            elif is_llm_model(model_config.model_type):
                # 测试大语言模型
                test_message = "你好，请介绍一下你自己"
                try:
                    llm_result = await ai_model_service.text_generation(test_message)
                    # 检查可能的返回字段：content 或 text
                    generated_text = None
                    if llm_result:
                        if "content" in llm_result:
                            generated_text = llm_result["content"]
                        elif "text" in llm_result:
                            generated_text = llm_result["text"]

                    if generated_text:
                        test_passed = True
                        generated_text_preview = generated_text[:100]  # 只取前100字符
                        test_message = i18n.t('model.llm_success', locale)
                    else:
                        test_passed = False
                        test_message = i18n.t('model.llm_failed', locale)
                except Exception as e:
                    test_passed = False
                    test_message = i18n.t('model.llm_test_error', locale, error=str(e))

            else:
                test_passed = False
                test_message = i18n.t('model.unknown_type', locale, type=model_config.model_type)

        except ImportError:
            test_passed = False
            test_message = i18n.t('model.service_unavailable', locale)
        except Exception as e:
            test_passed = False
            test_message = i18n.t('model.test_failed_with_error', locale, error=str(e))

        response_time = time.time() - start_time

        logger.info(f"AI模型测试完成: id={model_id}, 通过={test_passed}, 耗时={response_time:.2f}秒")

        return AIModelTestResponse(
            data={
                "model_id": model_id,
                "test_passed": test_passed,
                "response_time": round(response_time, 3),
                "test_message": test_message,
                "test_data": request.test_data if request else None,
                "config_used": config
            },
            message=i18n.t('model.test_complete', locale)
        )

    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"测试AI模型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=i18n.t('model.test_failed', locale))


@router.put("/ai-model/{model_id}/toggle", response_model=SuccessResponse, summary="启用/禁用AI模型")
async def toggle_ai_model(
    model_id: int,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale)
):
    """
    启用或禁用AI模型

    - **model_id**: 模型配置ID
    """
    logger.info(f"切换AI模型状态: id={model_id}")

    try:
        # 查询模型配置
        model_config = db.query(AIModelModel).filter(
            AIModelModel.id == model_id
        ).first()

        if not model_config:
            raise ResourceNotFoundException("AI模型配置", str(model_id))

        # 切换状态
        old_status = model_config.is_active
        model_config.is_active = not model_config.is_active
        db.commit()

        status_text = i18n.t('model.enabled', locale) if model_config.is_active else i18n.t('model.disabled', locale)
        logger.info(f"AI模型状态已切换: id={model_id}, {old_status} -> {model_config.is_active}")

        return SuccessResponse(
            data={
                "model_id": model_id,
                "is_active": model_config.is_active,
                "old_status": old_status
            },
            message=i18n.t('model.toggle_success', locale, status=status_text)
        )

    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"切换AI模型状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=i18n.t('model.toggle_failed', locale))


@router.delete("/ai-model/{model_id}", response_model=SuccessResponse, summary="删除AI模型配置")
async def delete_ai_model_config(
    model_id: int,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale)
):
    """
    删除AI模型配置

    - **model_id**: 模型配置ID
    """
    logger.info(f"删除AI模型配置: id={model_id}")

    try:
        # 查询模型配置
        model_config = db.query(AIModelModel).filter(
            AIModelModel.id == model_id
        ).first()

        if not model_config:
            raise ResourceNotFoundException("AI模型配置", str(model_id))

        # 删除配置
        db.delete(model_config)
        db.commit()

        logger.info(f"AI模型配置已删除: id={model_id}, name={model_config.model_name}")

        return SuccessResponse(
            data={
                "deleted_model_id": model_id,
                "model_name": model_config.model_name,
                "model_type": model_config.model_type
            },
            message=i18n.t('model.delete_success', locale)
        )

    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"删除AI模型配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=i18n.t('model.delete_failed', locale))


@router.get("/ai-models/default", response_model=AIModelsResponse, summary="获取默认AI模型配置")
async def get_default_ai_models(
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale)
):
    """
    获取系统默认的AI模型配置
    """
    logger.info("获取默认AI模型配置")

    try:
        # 获取默认配置
        default_configs = AIModelModel.get_default_configs()

        # 检查数据库中是否已存在这些配置
        existing_models = []
        for config_key, config_data in default_configs.items():
            existing_model = db.query(AIModelModel).filter(
                AIModelModel.model_type == config_data["model_type"],
                AIModelModel.provider == config_data["provider"],
                AIModelModel.model_name == config_data["model_name"]
            ).first()

            if existing_model:
                model_info = AIModelInfo(
                    id=existing_model.id,
                    model_type=existing_model.model_type,
                    provider=existing_model.provider,
                    model_name=existing_model.model_name,
                    config_json=existing_model.config_json,
                    is_active=existing_model.is_active,
                    created_at=existing_model.created_at,
                    updated_at=existing_model.updated_at
                )
                existing_models.append(model_info)

        logger.info(f"返回默认AI模型配置: 数量={len(existing_models)}")

        return AIModelsResponse(
            data=existing_models,
            message=i18n.t('model.get_default_success', locale)
        )

    except Exception as e:
        logger.error(f"获取默认AI模型配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=i18n.t('model.get_default_failed', locale))


async def _initialize_default_ai_models(db: Session):
    """
    初始化默认AI模型配置到数据库

    Args:
        db: 数据库会话
    """
    try:
        logger.info("开始初始化默认AI模型配置")

        # 获取默认配置
        default_configs = AIModelModel.get_default_configs()

        # 创建默认模型配置记录
        created_models = []

        for config_key, config_data in default_configs.items():
            # 检查是否已存在相同的配置
            existing_model = db.query(AIModelModel).filter(
                AIModelModel.model_type == config_data["model_type"],
                AIModelModel.provider == config_data["provider"],
                AIModelModel.model_name == config_data["model_name"]
            ).first()

            if not existing_model:
                # 创建新的模型配置
                new_model = AIModelModel(
                    model_type=config_data["model_type"],
                    provider=config_data["provider"],
                    model_name=config_data["model_name"],
                    config_json=json.dumps(config_data["config"], ensure_ascii=False),
                    is_active=True
                )
                db.add(new_model)
                created_models.append(config_data["model_name"])
                logger.info(f"创建默认AI模型配置: {config_data['model_type']} - {config_data['model_name']}")
            else:
                logger.info(f"AI模型配置已存在，跳过: {config_data['model_type']} - {config_data['model_name']}")

        # 提交所有更改
        db.commit()

        if created_models:
            logger.info(f"成功初始化 {len(created_models)} 个默认AI模型配置: {', '.join(created_models)}")
        else:
            logger.info("所有默认AI模型配置都已存在")

    except Exception as e:
        logger.error(f"初始化默认AI模型配置失败: {str(e)}")
        db.rollback()
        raise


# 添加缺失的导入
from datetime import datetime
import asyncio