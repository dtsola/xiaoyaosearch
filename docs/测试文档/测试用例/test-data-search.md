# 小遥搜索 - 搜索服务接口测试数据
# backend/app/api/search.py 接口手动测试数据
# 使用方法: 使用 curl 或 Postman 等工具发送以下请求

# ==============================================
# 基础信息
# API基础URL: http://127.0.0.1:8000
# Content-Type: application/json (除多模态搜索外)
# ==============================================

# ==============================================
# 1. 文本搜索 (POST)
# ==============================================

# 1.1 基础语义搜索
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "小遥",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 0.7,
    "file_types": null
  }'

# 1.2 全文搜索
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "机器学习算法",
    "input_type": "text",
    "search_type": "fulltext",
    "limit": 10,
    "threshold": 0.5,
    "file_types": null
  }'

# 1.3 混合搜索
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "深度学习神经网络应用",
    "input_type": "text",
    "search_type": "hybrid",
    "limit": 30,
    "threshold": 0.6,
    "file_types": null
  }'

# 1.4 按文件类型过滤 - 仅搜索文档
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "项目计划",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 15,
    "threshold": 0.7,
    "file_types": ["document", "text"]
  }'

# 1.5 按文件类型过滤 - 仅搜索视频
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "技术教程",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 10,
    "threshold": 0.7,
    "file_types": ["video"]
  }'

# 1.6 按文件类型过滤 - 仅搜索音频
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "播客内容",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 10,
    "threshold": 0.7,
    "file_types": ["audio"]
  }'

# 1.7 高相似度阈值搜索
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python编程",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 0.9,
    "file_types": null
  }'

# 1.8 低相似度阈值搜索（获取更多结果）
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "数据分析",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 50,
    "threshold": 0.3,
    "file_types": null
  }'

# 1.9 短查询搜索
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 0.7,
    "file_types": null
  }'

# 1.10 长查询搜索
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "如何在企业环境中实施机器学习解决方案以提高业务效率和竞争力",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 0.7,
    "file_types": null
  }'

# ==============================================
# 2. 多模态搜索 (POST) - 需要实际文件
# ==============================================

# 2.1 语音搜索 (需要上传音频文件)
curl -X POST "http://127.0.0.1:8000/api/search/multimodal" \
  -F "input_type=voice" \
  -F "file=@test_audio.mp3" \
  -F "search_type=hybrid" \
  -F "limit=20" \
  -F "threshold=0.7"

# 2.2 图像搜索 (需要上传图片文件)
curl -X POST "http://127.0.0.1:8000/api/search/multimodal" \
  -F "input_type=image" \
  -F "file=@test_image.jpg" \
  -F "search_type=semantic" \
  -F "limit=15" \
  -F "threshold=0.7"

# 2.3 语音+全文搜索
curl -X POST "http://127.0.0.1:8000/api/search/multimodal" \
  -F "input_type=voice" \
  -F "file=@test_speech.wav" \
  -F "search_type=fulltext" \
  -F "limit=10" \
  -F "threshold=0.5"

# 2.4 图像+混合搜索（高阈值）
curl -X POST "http://127.0.0.1:8000/api/search/multimodal" \
  -F "input_type=image" \
  -F "file=@test_photo.png" \
  -F "search_type=hybrid" \
  -F "limit=30" \
  -F "threshold=0.8"

# ==============================================
# 3. 搜索历史 (GET)
# ==============================================

# 3.1 获取搜索历史（默认参数）
curl -X GET "http://127.0.0.1:8000/api/search/history"

# 3.2 获取搜索历史（自定义分页）
curl -X GET "http://127.0.0.1:8000/api/search/history?limit=10&offset=20"

# 3.3 按搜索类型过滤 - 仅语义搜索
curl -X GET "http://127.0.0.1:8000/api/search/history?search_type=semantic"

# 3.4 按搜索类型过滤 - 仅全文搜索
curl -X GET "http://127.0.0.1:8000/api/search/history?search_type=fulltext"

# 3.5 按搜索类型过滤 - 仅混合搜索
curl -X GET "http://127.0.0.1:8000/api/search/history?search_type=hybrid"

# 3.6 按输入类型过滤 - 仅文本输入
curl -X GET "http://127.0.0.1:8000/api/search/history?input_type=text"

# 3.7 按输入类型过滤 - 仅语音输入
curl -X GET "http://127.0.0.1:8000/api/search/history?input_type=voice"

# 3.8 按输入类型过滤 - 仅图像输入
curl -X GET "http://127.0.0.1:8000/api/search/history?input_type=image"

# 3.9 组合过滤 - 语音输入的混合搜索
curl -X GET "http://127.0.0.1:8000/api/search/history?input_type=voice&search_type=hybrid"

# 3.10 大批量获取历史记录
curl -X GET "http://127.0.0.1:8000/api/search/history?limit=100&offset=0"

# ==============================================
# 4. 搜索建议 (GET)
# ==============================================

# 4.1 基础搜索建议
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=人工智能&limit=5"

# 4.2 短查询建议
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=机器&limit=8"

# 4.3 长查询建议
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=深度学习在计算机视觉中的应用&limit=3"

# 4.4 英文查询建议
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=python&limit=10"

# 4.5 数字查询建议
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=2024&limit=5"

# 4.6 空查询（测试错误处理）
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=&limit=5"

# 4.7 超长查询建议
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=这是一个非常非常长的查询语句用来测试系统的建议功能是否能够正常处理超长文本输入&limit=3"

# 4.8 特殊字符查询
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=C++&limit=5"

# 4.9 中英文混合查询
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=AI人工智能&limit=7"

# 4.10 单字符查询
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=数&limit=10"

# ==============================================
# 5. 删除操作 (DELETE)
# ==============================================

# 5.1 删除单条搜索历史记录
# 注意: 需要将 {history_id} 替换为实际的历史记录ID
curl -X DELETE "http://127.0.0.1:8000/api/search/history/{history_id}"

# 5.2 清除所有搜索历史
curl -X DELETE "http://127.0.0.1:8000/api/search/history"

# ==============================================
# 6. 错误测试用例
# ==============================================

# 6.1 文本搜索 - 缺少必要字段
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "",
    "input_type": "text",
    "search_type": "semantic"
    # 缺少 limit 和 threshold
  }'

# 6.2 文本搜索 - 无效的输入类型
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试查询",
    "input_type": "invalid_type",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 0.7
  }'

# 6.3 文本搜索 - 无效的搜索类型
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试查询",
    "input_type": "text",
    "search_type": "invalid_search_type",
    "limit": 20,
    "threshold": 0.7
  }'

# 6.4 文本搜索 - 超出限制的查询长度
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "这是一个超过500字符限制的超长查询语句，用来测试系统是否能够正确处理超出最大长度限制的查询输入。这个查询语句被设计为故意超出系统的最大长度限制，以验证错误处理机制是否正常工作。通过这个测试用例，我们可以确保系统能够优雅地处理异常输入，并返回适当的错误信息给用户。这个超长查询语句包含了足够的字符数量来触发长度限制验证，并且保持了一定的可读性以便于测试和理解。",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 0.7
  }'

# 6.5 文本搜索 - 超出限制的结果数量
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试查询",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 200,
    "threshold": 0.7
  }'

# 6.6 文本搜索 - 无效的阈值范围
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试查询",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 1.5
  }'

# 6.7 多模态搜索 - 缺少文件
curl -X POST "http://127.0.0.1:8000/api/search/multimodal" \
  -F "input_type=voice" \
  -F "search_type=hybrid"
  # 缺少 file 参数

# 6.8 多模态搜索 - 无效的输入类型
curl -X POST "http://127.0.0.1:8000/api/search/multimodal" \
  -F "input_type=text" \
  -F "file=@test_file.txt" \
  -F "search_type=semantic"

# 6.9 搜索历史 - 无效的分页参数
curl -X GET "http://127.0.0.1:8000/api/search/history?limit=-1&offset=-10"

# 6.10 搜索历史 - 超出限制的分页参数
curl -X GET "http://127.0.0.1:8000/api/search/history?limit=1000"

# 6.11 删除不存在的搜索历史记录
curl -X DELETE "http://127.0.0.1:8000/api/search/history/99999"

# 6.12 搜索建议 - 空查询
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query="

# 6.13 搜索建议 - 超出限制的建议数量
curl -X GET "http://127.0.0.1:8000/api/search/suggestions?query=test&limit=1000"

# ==============================================
# 7. 性能测试用例
# ==============================================

# 7.1 大量结果搜索测试
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "项目",
    "input_type": "text",
    "search_type": "fulltext",
    "limit": 100,
    "threshold": 0.1,
    "file_types": null
  }'

# 7.2 复杂混合搜索测试
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工智能机器学习深度学习神经网络计算机视觉自然语言处理",
    "input_type": "text",
    "search_type": "hybrid",
    "limit": 50,
    "threshold": 0.6,
    "file_types": ["document", "video", "audio"]
  }'

# 7.3 并发搜索测试（在多个终端中同时执行）
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "并发测试查询",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 0.7,
    "file_types": null
  }'

# ==============================================
# 8. 边界条件测试
# ==============================================

# 8.1 最小有效查询
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "A",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 1,
    "threshold": 0.0,
    "file_types": null
  }'

# 8.2 最大有效查询长度（500字符）
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "这是一个正好500字符的查询语句。这个查询被设计用来测试系统处理最大长度查询的能力。通过这个测试，我们可以验证系统在处理边界条件时的稳定性和正确性。这个查询包含了足够的内容来达到500字符的限制，同时保持了一定的语义连贯性以便进行有效的搜索测试。系统应该能够正确处理这个长度的查询，并返回相关的搜索结果。如果系统能够正确处理这个边界情况，那么我们就可以确信系统的输入验证机制工作正常。这个查询的长度正好达到系统的最大限制，是测试边界条件的重要用例。",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 0.7,
    "file_types": null
  }'

# 8.3 最小阈值搜索
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 0.0,
    "file_types": null
  }'

# 8.4 最大阈值搜索
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试",
    "input_type": "text",
    "search_type": "semantic",
    "limit": 20,
    "threshold": 1.0,
    "file_types": null
  }'

# 8.5 最大结果数量
curl -X POST "http://127.0.0.1:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "文档",
    "input_type": "text",
    "search_type": "fulltext",
    "limit": 100,
    "threshold": 0.0,
    "file_types": null
  }'

# ==============================================
# 使用说明
# ==============================================

# Windows PowerShell 中使用 curl 的注意事项:
# 1. 如果需要在 PowerShell 中使用，请将单引号 ' 改为双引号 "
# 2. 或者使用 Invoke-RestMethod 命令替代 curl
# 3. JSON 中的双引号需要转义为 \"
# 4. 多模态搜索的文件上传需要使用 PowerShell 的 Invoke-RestMethod 或 curl 的 -F 参数

# Postman 使用步骤:
# 1. 新建请求，选择对应的 HTTP 方法 (GET/POST/DELETE)
# 2. 输入完整的 URL
# 3. 如果是 POST 请求，在 Body 选项卡中选择 raw 和 JSON 格式
# 4. 如果是多模态搜索，选择 form-data 格式并添加文件字段
# 5. 点击 Send 发送请求

# 测试文件准备:
# 1. 语音搜索测试需要准备音频文件 (mp3, wav 格式)
# 2. 图像搜索测试需要准备图片文件 (jpg, png, jpeg 格式)
# 3. 文件大小不超过 50MB
# 4. 将测试文件放在与脚本相同目录下

# 历史记录ID获取方法:
# 1. 先调用 "获取搜索历史" 接口
# 2. 从返回结果中的 data.history 数组里找到对应的 id 字段
# 3. 将这个 id 替换到需要 {history_id} 的请求中

# 常见响应状态码:
# 200: 成功
# 400: 请求参数错误
# 404: 资源不存在
# 422: 参数验证失败
# 500: 服务器内部错误
# 503: 服务不可用（如AI模型服务未启动）

# 测试建议执行顺序:
# 1. 先执行基础的文本搜索测试 (1.1-1.3)
# 2. 测试文件类型过滤功能 (1.4-1.6)
# 3. 测试边界条件和参数验证 (1.7-1.10, 6.1-6.6)
# 4. 测试搜索历史功能 (3.1-3.10, 5.1-5.2)
# 5. 测试搜索建议功能 (4.1-4.10)
# 6. 如有测试文件，测试多模态搜索 (2.1-2.4)
# 7. 执行错误测试用例验证系统健壮性
# 8. 进行性能测试评估系统响应能力