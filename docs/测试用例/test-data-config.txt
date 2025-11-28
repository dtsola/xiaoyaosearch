# 小遥搜索 - AI模型配置接口测试数据
# backend/app/api/config.py 接口手动测试数据
# 使用方法: 使用 curl 或 Postman 等工具发送以下请求

# ==============================================
# 基础信息
# API基础URL: http://127.0.0.1:8000
# Content-Type: application/json
# ==============================================

# ==============================================
# 1. 获取所有AI模型配置 (GET)
# ==============================================
curl -X GET "http://127.0.0.1:8000/api/config/ai-models"

# 带过滤条件 - 按模型类型过滤
curl -X GET "http://127.0.0.1:8000/api/config/ai-models?model_type=embedding"

# 带过滤条件 - 按提供商过滤
curl -X GET "http://127.0.0.1:8000/api/config/ai-models?provider=local"

# 带过滤条件 - 组合过滤
curl -X GET "http://127.0.0.1:8000/api/config/ai-models?model_type=llm&provider=cloud"

# ==============================================
# 2. 获取默认AI模型配置 (GET)
# ==============================================
curl -X GET "http://127.0.0.1:8000/api/config/ai-models/default"

# ==============================================
# 3. 创建AI模型配置 (POST)
# ==============================================

# 3.1 创建文本嵌入模型配置
curl -X POST "http://127.0.0.1:8000/api/config/ai-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "embedding",
    "provider": "local",
    "model_name": "bge-m3-chinese",
    "config": {
      "model_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\models\\embedding\\BAAI\\bge-m3",
      "device": "cpu",
      "max_length": 512,
      "batch_size": 32,
      "normalize_embeddings": true
    }
  }'

# 3.2 创建语音识别模型配置
curl -X POST "http://127.0.0.1:8000/api/config/ai-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "speech",
    "provider": "local",
    "model_name": "faster-whisper-base",
    "config": {
      "model_size": "base",
      "device": "cpu",
      "compute_type": "default",
      "language": "zh"
    }
  }'

# 3.3 创建图像理解模型配置
curl -X POST "http://127.0.0.1:8000/api/config/ai-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "vision",
    "provider": "local",
    "model_name": "chinese-clip-vit-base",
    "config": {
      "model_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\models\\cn-clip\\OFA-Sys\\chinese-clip-vit-base-patch16",
      "device": "cpu"
    }
  }'

# 3.4 创建大语言模型配置 (本地Ollama)
curl -X POST "http://127.0.0.1:8000/api/config/ai-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "llm",
    "provider": "local",
    "model_name": "ollama-qwen2.5",
    "config": {
      "base_url": "http://localhost:11434",
      "model": "qwen2.5:1.5b",
      "temperature": 0.7,
      "max_tokens": 2000,
      "timeout": 30
    }
  }'

# 3.5 创建大语言模型配置 (云端API)
curl -X POST "http://127.0.0.1:8000/api/config/ai-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "llm",
    "provider": "cloud",
    "model_name": "openai-gpt-3.5-turbo",
    "config": {
      "api_key": "your-openai-api-key-here",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-3.5-turbo",
      "temperature": 0.7,
      "max_tokens": 2000,
      "timeout": 30
    }
  }'

# 3.6 创建阿里云通义千问配置
curl -X POST "http://127.0.0.1:8000/api/config/ai-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "llm",
    "provider": "cloud",
    "model_name": "aliyun-qwen-turbo",
    "config": {
      "api_key": "your-aliyun-access-key-id",
      "api_secret": "your-aliyun-access-key-secret",
      "model": "qwen-turbo",
      "temperature": 0.7,
      "max_tokens": 2000,
      "region": "cn-hangzhou"
    }
  }'

# ==============================================
# 4. 测试AI模型连通性 (POST)
# 注意: 需要将 {model_id} 替换为实际的模型ID
# ==============================================

# 4.1 测试文本嵌入模型
curl -X POST "http://127.0.0.1:8000/api/config/ai-model/{model_id}/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_data": "这是一个测试文本，用于验证文本嵌入模型的功能",
    "config_override": {
      "device": "cpu",
      "max_length": 256
    }
  }'

# 4.2 测试语音识别模型
curl -X POST "http://127.0.0.1:8000/api/config/ai-model/{model_id}/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_data": "test_audio_data",
    "config_override": {
      "language": "zh",
      "model_size": "base"
    }
  }'

# 4.3 测试图像理解模型
curl -X POST "http://127.0.0.1:8000/api/config/ai-model/{model_id}/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_data": "test_image_data",
    "config_override": {
      "device": "cpu"
    }
  }'

# 4.4 测试大语言模型
curl -X POST "http://127.0.0.1:8000/api/config/ai-model/{model_id}/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_data": "你好，请介绍一下你自己",
    "config_override": {
      "temperature": 0.5,
      "max_tokens": 100
    }
  }'

# ==============================================
# 5. 启用/禁用AI模型 (PUT)
# 注意: 需要将 {model_id} 替换为实际的模型ID
# ==============================================
curl -X PUT "http://127.0.0.1:8000/api/config/ai-model/{model_id}/toggle"

# ==============================================
# 6. 删除AI模型配置 (DELETE)
# 注意: 需要将 {model_id} 替换为实际的模型ID
# ==============================================
curl -X DELETE "http://127.0.0.1:8000/api/config/ai-model/{model_id}"

# ==============================================
# 7. 错误测试用例
# ==============================================

# 7.1 无效的模型类型
curl -X POST "http://127.0.0.1:8000/api/config/ai-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "invalid_type",
    "provider": "local",
    "model_name": "test-model",
    "config": {}
  }'

# 7.2 无效的提供商类型
curl -X POST "http://127.0.0.1:8000/api/config/ai-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "embedding",
    "provider": "invalid_provider",
    "model_name": "test-model",
    "config": {}
  }'

# 7.3 空的模型名称
curl -X POST "http://127.0.0.1:8000/api/config/ai-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "embedding",
    "provider": "local",
    "model_name": "",
    "config": {}
  }'

# 7.4 缺少必要字段
curl -X POST "http://127.0.0.1:8000/api/config/ai-model" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "embedding",
    "provider": "local"
    # 缺少 model_name 和 config
  }'

# 7.5 操作不存在的模型ID
curl -X PUT "http://127.0.0.1:8000/api/config/ai-model/99999/toggle"
curl -X DELETE "http://127.0.0.1:8000/api/config/ai-model/99999"
curl -X POST "http://127.0.0.1:8000/api/config/ai-model/99999/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_data": "test"
  }'

# ==============================================
# 使用说明
# ==============================================

# Windows PowerShell 中使用 curl 的注意事项:
# 1. 如果需要在 PowerShell 中使用，请将单引号 ' 改为双引号 "
# 2. 或者使用 Invoke-RestMethod 命令替代 curl
# 3. JSON 中的双引号需要转义为 \"

# Postman 使用步骤:
# 1. 新建请求，选择对应的 HTTP 方法 (GET/POST/PUT/DELETE)
# 2. 输入完整的 URL
# 3. 如果是 POST/PUT 请求，在 Body 选项卡中选择 raw 和 JSON 格式
# 4. 粘贴对应的 JSON 数据
# 5. 点击 Send 发送请求

# 模型ID获取方法:
# 1. 先调用 "获取所有AI模型配置" 接口
# 2. 从返回结果中的 data 数组里找到对应的 id 字段
# 3. 将这个 id 替换到需要 {model_id} 的请求中

# 常见响应状态码:
# 200: 成功
# 400: 请求参数错误
# 404: 资源不存在
# 422: 参数验证失败
# 500: 服务器内部错误