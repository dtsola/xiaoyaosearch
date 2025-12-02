# 小遥搜索 - 索引管理接口测试数据
# backend/app/api/index.py 接口手动测试数据
# 使用方法: 使用 curl 或 Postman 等工具发送以下请求

# ==============================================
# 基础信息
# API基础URL: http://127.0.0.1:8000
# Content-Type: application/json
# ==============================================

# ==============================================
# 1. 创建索引 (POST)
# ==============================================

# 1.1 创建完整索引（使用DefaultConfig默认支持的所有文件类型）
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\test-data",
    "recursive": true
  }'

# 1.2 创建索引（仅搜索当前文件夹，使用默认文件类型）
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\test-data",
    "recursive": false
  }'

# 1.3 创建索引（指定文件类型）
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\test-data",
    "recursive": true,
    "file_types": [".txt", ".md", ".pdf", ".docx", ".mp3", ".mp4", ".jpg", ".png"]
  }'

# 1.4 创建索引（仅指定文件类型）
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\test-data",
    "recursive": true,
    "file_types": [".pdf", ".docx"]
  }'

# ==============================================
# 2. 更新索引 (POST)
# ==============================================

# 2.1 增量更新索引（使用DefaultConfig默认支持的所有文件类型）
curl -X POST "http://127.0.0.1:8000/api/index/update" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\test-data",
    "recursive": true
  }'

# 2.2 增量更新索引（仅搜索当前文件夹，使用默认文件类型）
curl -X POST "http://127.0.0.1:8000/api/index/update" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\test-data",
    "recursive": false
  }'

# 2.3 增量更新索引（指定文件类型）
curl -X POST "http://127.0.0.1:8000/api/index/update" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\test-data",
    "recursive": true,
    "file_types": [".txt", ".md", ".pdf"]
  }'

# ==============================================
# 3. 获取索引系统状态 (GET)
# ==============================================
curl -X GET "http://127.0.0.1:8000/api/index/status"

# ==============================================
# 4. 查询指定索引状态 (GET)
# ==============================================
# 注意: 需要将 {index_id} 替换为实际的索引任务ID
curl -X GET "http://127.0.0.1:8000/api/index/status/1"

# 查询不存在的索引ID
curl -X GET "http://127.0.0.1:8000/api/index/status/99999"

# ==============================================
# 5. 获取索引任务列表 (GET)
# ==============================================

# 5.1 获取所有索引任务列表
curl -X GET "http://127.0.0.1:8000/api/index/list"

# 5.2 按状态过滤 - 获取已完成的任务
curl -X GET "http://127.0.0.1:8000/api/index/list?status=completed"

# 5.3 按状态过滤 - 获取正在处理的任务
curl -X GET "http://127.0.0.1:8000/api/index/list?status=processing"

# 5.4 按状态过滤 - 获取失败的任务
curl -X GET "http://127.0.0.1:8000/api/index/list?status=failed"

# 5.5 分页查询
curl -X GET "http://127.0.0.1:8000/api/index/list?limit=5&offset=0"

# 5.6 组合查询 - 按状态过滤 + 分页
curl -X GET "http://127.0.0.1:8000/api/index/list?status=completed&limit=3&offset=0"

# ==============================================
# 6. 删除索引 (DELETE)
# ==============================================
# 注意: 需要将 {index_id} 替换为实际的索引任务ID
curl -X DELETE "http://127.0.0.1:8000/api/index/1"

# ==============================================
# 7. 停止索引 (POST)
# ==============================================
# 注意: 需要将 {index_id} 替换为实际的正在运行的索引任务ID
curl -X POST "http://127.0.0.1:8000/api/index/1/stop"

# ==============================================
# 8. 备份索引 (POST)
# ==============================================

# 8.1 使用默认备份名称（时间戳）
curl -X POST "http://127.0.0.1:8000/api/index/backup"

# 8.2 指定备份名称
curl -X POST "http://127.0.0.1:8000/api/index/backup?backup_name=index_backup_20251201"

# ==============================================
# 9. 获取已索引文件列表 (GET)
# ==============================================

# 9.1 获取所有已索引文件
curl -X GET "http://127.0.0.1:8000/api/index/files"

# 9.2 按文件夹路径过滤
curl -X GET "http://127.0.0.1:8000/api/index/files?folder_path=D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\test-data"

# 9.3 按文件类型过滤
curl -X GET "http://127.0.0.1:8000/api/index/files?file_type=pdf"

# 9.4 按索引状态过滤
curl -X GET "http://127.0.0.1:8000/api/index/files?index_status=completed"

# 9.5 分页查询
curl -X GET "http://127.0.0.1:8000/api/index/files?limit=10&offset=0"

# 9.6 组合过滤 - 文件夹 + 文件类型 + 分页
curl -X GET "http://127.0.0.1:8000/api/index/files?folder_path=D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data&file_type=txt&limit=5&offset=0"

# ==============================================
# 10. 删除文件索引 (DELETE)
# ==============================================
# 注意: 需要将 {file_id} 替换为实际的文件ID
curl -X DELETE "http://127.0.0.1:8000/api/index/files/1"

# ==============================================
# 11. 错误测试用例
# ==============================================

# 11.1 创建索引 - 文件夹不存在
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\nonexistent\\folder",
    "recursive": true
  }'

# 11.2 创建索引 - 路径不是文件夹
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\README.md",
    "recursive": true
  }'

# 11.3 创建索引 - 缺少必要字段
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{
    "recursive": true
    # 缺少 folder_path
  }'

# 11.4 更新索引 - 文件夹不存在
curl -X POST "http://127.0.0.1:8000/api/index/update" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\nonexistent\\folder"
  }'

# 11.5 删除索引 - 索引ID不存在
curl -X DELETE "http://127.0.0.1:8000/api/index/99999"

# 11.6 停止索引 - 索引ID不存在
curl -X POST "http://127.0.0.1:8000/api/index/99999/stop"

# 11.7 停止索引 - 任务不在运行状态
curl -X POST "http://127.0.0.1:8000/api/index/1/stop"

# 11.8 删除文件索引 - 文件ID不存在
curl -X DELETE "http://127.0.0.1:8000/api/index/files/99999"

# 11.9 无效的状态参数
curl -X GET "http://127.0.0.1:8000/api/index/list?status=invalid_status"

# 11.10 无效的分页参数
curl -X GET "http://127.0.0.1:8000/api/index/list?limit=-1&offset=-10"

# ==============================================
# 12. 完整工作流程测试
# ==============================================

# 12.1 创建索引 -> 查询状态 -> 获取列表
# 步骤1: 创建索引
curl -X POST "http://127.0.0.1:8000/api/index/create" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:\\MyWorkProjects\\freelance\\indiehacker\\xiaoyaosearch\\data\\test-data",
    "recursive": true,
    "file_types": [".txt", ".md"]
  }'

# 步骤2: 获取索引列表，找到刚创建的任务ID
curl -X GET "http://127.0.0.1:8000/api/index/list?limit=1"

# 步骤3: 查询具体任务状态（使用上一步获得的index_id）
curl -X GET "http://127.0.0.1:8000/api/index/status/{index_id}"

# 12.2 索引管理流程
# 步骤1: 获取系统状态
curl -X GET "http://127.0.0.1:8000/api/index/status"

# 步骤2: 获取已索引文件
curl -X GET "http://127.0.0.1:8000/api/index/files?limit=5"

# 步骤3: 备份索引
curl -X POST "http://127.0.0.1:8000/api/index/backup?backup_name=test_workflow_backup"

# ==============================================
# 使用说明
# ==============================================

# Windows PowerShell 中使用 curl 的注意事项:
# 1. 如果需要在 PowerShell 中使用，请将单引号 ' 改为双引号 "
# 2. 或者使用 Invoke-RestMethod 命令替代 curl
# 3. JSON 中的双引号需要转义为 \"
# 4. 文件路径中的反斜杠需要转义为 \\

# Postman 使用步骤:
# 1. 新建请求，选择对应的 HTTP 方法 (GET/POST/PUT/DELETE)
# 2. 输入完整的 URL
# 3. 如果是 POST 请求，在 Body 选项卡中选择 raw 和 JSON 格式
# 4. 粘贴对应的 JSON 数据
# 5. 点击 Send 发送请求

# 索引ID获取方法:
# 1. 先调用 "获取索引任务列表" 接口
# 2. 从返回结果中的 indexes 数组里找到对应的 index_id 字段
# 3. 将这个 index_id 替换到需要 {index_id} 的请求中

# 文件ID获取方法:
# 1. 先调用 "获取已索引文件列表" 接口
# 2. 从返回结果中的 files 数组里找到对应的 id 字段
# 3. 将这个 id 替换到需要 {file_id} 的请求中

# 常见响应状态码:
# 200: 成功
# 400: 请求参数错误
# 404: 资源不存在
# 422: 参数验证失败
# 500: 服务器内部错误

# 状态参数说明:
# pending: 等待中
# processing: 处理中
# completed: 已完成
# failed: 失败

# 文件类型过滤说明:
# 支持的文件类型包括但不限于:
# - 文档: .txt, .md, .pdf, .docx, .xlsx, .pptx
# - 音频: .mp3, .wav, .m4a
# - 视频: .mp4, .avi, .mov
# - 图片: .jpg, .jpeg, .png, .gif