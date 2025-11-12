# 小遥搜索API API Documentation

**Version:** 0.1.0
**Description:** 
        # 小遥搜索API

        跨平台本地文件智能搜索服务，提供强大的文件搜索、AI查询理解和隐私保护功能。

        ## 主要功能

        ### 🔍 智能语义搜索
        - **向量搜索**: 基于BGE模型的中文语义理解
        - **混合搜索**: 结合向量搜索和传统文本搜索
        - **多模态支持**: 文本、图像、音频文件搜索
        - **相关性排序**: 智能相关性评分和结果排序

        ### 📁 文件管理
        - **文件索引**: 自动文件发现和索引建立
        - **元数据提取**: 文件内容分析和元数据提取
        - **预览功能**: 文件内容快速预览
        - **批量操作**: 支持批量文件处理

        ### 🤖 AI驱动查询
        - **自然语言理解**: 支持自然语言查询
        - **查询扩展**: 自动查询词扩展和同义词处理
        - **意图识别**: 查询意图智能识别
        - **个性化推荐**: 基于用户行为的搜索推荐

        ### 🔒 安全与隐私
        - **本地部署**: 数据完全本地存储和处理
        - **用户认证**: JWT令牌认证机制
        - **访问控制**: 细粒度权限控制
        - **审计日志**: 完整的操作审计记录

        ## 技术架构

        ### 后端技术栈
        - **FastAPI**: 高性能异步Web框架
        - **SQLAlchemy**: ORM数据库操作
        - **BGE**: 中文语义向量模型
        - **Whoosh**: 全文搜索引擎
        - **Faiss**: 向量相似度搜索
        - **Whisper**: 音频转文字
        - **CLIP**: 图文多模态理解

        ### 数据存储
        - **SQLite**: 轻量级关系数据库
        - **向量索引**: Faiss向量存储
        - **倒排索引**: Whoosh文本索引

        ## API使用指南

        ### 认证方式
        API使用JWT Bearer Token进行认证：
        ```
        Authorization: Bearer <your_token>
        ```

        ### 响应格式
        所有API响应都遵循统一格式：
        ```json
        {
            "code": 200,
            "message": "success",
            "data": {},
            "timestamp": "2023-12-07T10:30:00Z"
        }
        ```

        ### 错误处理
        错误响应包含详细的错误信息：
        ```json
        {
            "detail": "错误描述",
            "error_code": "ERROR_CODE",
            "details": {},
            "timestamp": "2023-12-07T10:30:00Z"
        }
        ```

        ### 分页查询
        列表接口支持分页查询：
        ```
        GET /api/v1/search?page=1&size=20
        ```

        ## 开发指南

        ### 环境要求
        - Python 3.8+
        - 8GB+ RAM
        - 足够的存储空间用于索引

        ### 快速开始
        1. 安装依赖: `pip install -r requirements.txt`
        2. 初始化数据库: `python database_cli.py init`
        3. 启动服务: `python main.py`
        4. 访问文档: `http://localhost:8000/api/v1/docs`

        ### 配置说明
        详细配置请参考 `.env` 文件或环境变量设置。

        ## 许可证
        MIT License - 详见 [LICENSE](https://opensource.org/licenses/MIT) 文件

        ## 支持与反馈
        - GitHub: https://github.com/xiaoyaosearch
        - Email: support@xiaoyao.local
        - 文档: https://docs.xiaoyao.local
        

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

This API uses JWT Bearer Token authentication.

```http
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### /

#### GET /

**Summary:** Root

**Description:** 根路径健康检查

**Responses:**

- `200`: Successful Response

---

### /health

#### GET /health

**Summary:** Health Check

**Description:** 详细健康检查

**Responses:**

- `200`: Successful Response

---

### /api/v1/v1/search/

#### GET /api/v1/v1/search/

**Summary:** Search Files

**Description:** 搜索文件

**Tags:** API v1, 搜索

**Parameters:**

- `q` (string) **[required]**: 搜索查询
- `type` (): 文件类型过滤
- `start_date` (): 开始日期
- `end_date` (): 结束日期
- `size` (integer): 返回结果数量
- `page` (integer): 页码

**Responses:**

- `200`: 搜索成功
- `400`: 搜索参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 搜索服务异常

---

### /api/v1/v1/search/understand

#### POST /api/v1/v1/search/understand

**Summary:** Understand Query

**Description:** 理解用户查询意图

**Tags:** API v1, 搜索

**Parameters:**

- `query` (string) **[required]**: 用户查询

**Responses:**

- `200`: 搜索成功
- `400`: 搜索参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 搜索服务异常

---

### /api/v1/v1/search/suggestions

#### GET /api/v1/v1/search/suggestions

**Summary:** Get Search Suggestions

**Description:** 获取搜索建议

**Tags:** API v1, 搜索

**Parameters:**

- `q` (string) **[required]**: 查询前缀
- `limit` (integer): 建议数量

**Responses:**

- `200`: 搜索成功
- `400`: 搜索参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 搜索服务异常

---

### /api/v1/v1/files/

#### GET /api/v1/v1/files/

**Summary:** List Files

**Description:** 获取文件列表

**Tags:** API v1, 文件管理

**Parameters:**

- `directory_id` (): 目录ID
- `type` (): 文件类型过滤
- `indexed_only` (boolean): 仅显示已索引文件
- `page` (integer): 页码
- `size` (integer): 每页数量

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 文件不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 文件冲突

---

### /api/v1/v1/files/{file_id}

#### GET /api/v1/v1/files/{file_id}

**Summary:** Get File Info

**Description:** 获取文件详细信息

**Tags:** API v1, 文件管理

**Parameters:**

- `file_id` (string) **[required]**: 

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 文件不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 文件冲突

---

#### DELETE /api/v1/v1/files/{file_id}

**Summary:** Delete File

**Description:** 删除文件

**Tags:** API v1, 文件管理

**Parameters:**

- `file_id` (string) **[required]**: 

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 文件不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 文件冲突

---

### /api/v1/v1/files/{file_id}/preview

#### GET /api/v1/v1/files/{file_id}/preview

**Summary:** Preview File

**Description:** 预览文件内容

**Tags:** API v1, 文件管理

**Parameters:**

- `file_id` (string) **[required]**: 
- `highlights` (): 高亮关键词

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 文件不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 文件冲突

---

### /api/v1/v1/files/{file_id}/open

#### POST /api/v1/v1/files/{file_id}/open

**Summary:** Open File

**Description:** 使用系统默认应用打开文件

**Tags:** API v1, 文件管理

**Parameters:**

- `file_id` (string) **[required]**: 

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 文件不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 文件冲突

---

### /api/v1/v1/files/upload

#### POST /api/v1/v1/files/upload

**Summary:** Upload File

**Description:** 上传文件

**Tags:** API v1, 文件管理

**Parameters:**

- `directory_id` (): 目标目录ID

**Request Body:**

- Content-Type: multipart/form-data
- Schema: Body_upload_file_api_v1_v1_files_upload_post

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 文件不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 文件冲突

---

### /api/v1/v1/directories/

#### GET /api/v1/v1/directories/

**Summary:** List Directories

**Description:** 获取所有索引目录

**Tags:** API v1, 目录管理

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 目录不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 目录冲突

---

#### POST /api/v1/v1/directories/

**Summary:** Add Directory

**Description:** 添加索引目录

**Tags:** API v1, 目录管理

**Request Body:**

- Content-Type: application/json
- Schema: DirectoryCreate

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 目录不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 目录冲突

---

### /api/v1/v1/directories/{directory_id}

#### GET /api/v1/v1/directories/{directory_id}

**Summary:** Get Directory

**Description:** 获取目录详细信息

**Tags:** API v1, 目录管理

**Parameters:**

- `directory_id` (string) **[required]**: 

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 目录不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 目录冲突

---

#### DELETE /api/v1/v1/directories/{directory_id}

**Summary:** Remove Directory

**Description:** 移除索引目录

**Tags:** API v1, 目录管理

**Parameters:**

- `directory_id` (string) **[required]**: 
- `remove_files` (boolean): 是否同时删除相关文件索引

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 目录不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 目录冲突

---

### /api/v1/v1/directories/{directory_id}/scan

#### POST /api/v1/v1/directories/{directory_id}/scan

**Summary:** Scan Directory

**Description:** 扫描目录

**Tags:** API v1, 目录管理

**Parameters:**

- `directory_id` (string) **[required]**: 
- `full_scan` (boolean): 是否进行全量扫描

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 目录不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 目录冲突

---

### /api/v1/v1/directories/{directory_id}/status

#### GET /api/v1/v1/directories/{directory_id}/status

**Summary:** Get Directory Status

**Description:** 获取目录扫描状态

**Tags:** API v1, 目录管理

**Parameters:**

- `directory_id` (string) **[required]**: 

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 目录不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误
- `409`: 目录冲突

---

### /api/v1/v1/users/current

#### GET /api/v1/v1/users/current

**Summary:** Get Current User

**Description:** 获取当前用户信息

**Tags:** API v1, 用户管理

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 服务器内部错误

---

### /api/v1/v1/users/

#### POST /api/v1/v1/users/

**Summary:** Create User

**Description:** 创建用户

**Tags:** API v1, 用户管理

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 服务器内部错误

---

### /api/v1/v1/settings/

#### GET /api/v1/v1/settings/

**Summary:** Get Settings

**Description:** 获取用户设置

**Tags:** API v1, 设置管理

**Responses:**

- `200`: 操作成功
- `400`: 设置参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 设置格式错误
- `500`: 服务器内部错误

---

#### PUT /api/v1/v1/settings/

**Summary:** Update Settings

**Description:** 更新用户设置

**Tags:** API v1, 设置管理

**Request Body:**

- Content-Type: application/json

**Responses:**

- `200`: 操作成功
- `400`: 设置参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 设置格式错误
- `500`: 服务器内部错误

---

### /api/v1/v1/settings/reset

#### POST /api/v1/v1/settings/reset

**Summary:** Reset Settings

**Description:** 重置用户设置

**Tags:** API v1, 设置管理

**Responses:**

- `200`: 操作成功
- `400`: 设置参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 设置格式错误
- `500`: 服务器内部错误

---

### /api/v1/v1/settings/export

#### POST /api/v1/v1/settings/export

**Summary:** Export Settings

**Description:** 导出设置

**Tags:** API v1, 设置管理

**Responses:**

- `200`: 操作成功
- `400`: 设置参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 设置格式错误
- `500`: 服务器内部错误

---

### /api/v1/v1/settings/import

#### POST /api/v1/v1/settings/import

**Summary:** Import Settings

**Description:** 导入设置

**Tags:** API v1, 设置管理

**Request Body:**

- Content-Type: application/json

**Responses:**

- `200`: 操作成功
- `400`: 设置参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 设置格式错误
- `500`: 服务器内部错误

---

### /api/v1/v1/database/health

#### GET /api/v1/v1/database/health

**Summary:** Get Database Health

**Description:** 获取数据库健康状态

Returns:
    DatabaseHealthResponse: 数据库健康状态信息

**Tags:** API v1, 数据库管理

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 数据库操作失败
- `503`: 数据库不可用

---

### /api/v1/v1/database/info

#### GET /api/v1/v1/database/info

**Summary:** Get Database Info

**Description:** 获取数据库详细信息

Returns:
    DatabaseInfoResponse: 数据库详细信息

**Tags:** API v1, 数据库管理

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 数据库操作失败
- `503`: 数据库不可用

---

### /api/v1/v1/database/backup

#### POST /api/v1/v1/database/backup

**Summary:** Create Database Backup

**Description:** 创建数据库备份

Args:
    backup_dir: 备份目录路径（可选）

Returns:
    BackupResponse: 备份结果

**Tags:** API v1, 数据库管理

**Parameters:**

- `backup_dir` (): 

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 数据库操作失败
- `503`: 数据库不可用

---

### /api/v1/v1/database/backups

#### GET /api/v1/v1/database/backups

**Summary:** List Database Backups

**Description:** 列出所有数据库备份文件

Args:
    backup_dir: 备份目录路径（可选）

Returns:
    BackupListResponse: 备份文件列表

**Tags:** API v1, 数据库管理

**Parameters:**

- `backup_dir` (): 

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 数据库操作失败
- `503`: 数据库不可用

---

### /api/v1/v1/database/restore

#### POST /api/v1/v1/database/restore

**Summary:** Restore Database From Backup

**Description:** 从备份恢复数据库

Args:
    request: 恢复请求参数

Returns:
    RestoreResponse: 恢复结果

**Tags:** API v1, 数据库管理

**Request Body:**

- Content-Type: application/json
- Schema: RestoreRequest

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 数据库操作失败
- `503`: 数据库不可用

---

### /api/v1/v1/database/backups/cleanup

#### DELETE /api/v1/v1/database/backups/cleanup

**Summary:** Cleanup Old Database Backups

**Description:** 清理旧的数据库备份文件

Args:
    keep_count: 保留的备份数量
    backup_dir: 备份目录路径（可选）

Returns:
    CleanupResponse: 清理结果

**Tags:** API v1, 数据库管理

**Parameters:**

- `keep_count` (integer): 
- `backup_dir` (): 

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 数据库操作失败
- `503`: 数据库不可用

---

### /api/v1/v1/database/vacuum

#### POST /api/v1/v1/database/vacuum

**Summary:** Vacuum Database

**Description:** 清理数据库碎片，优化数据库文件大小
仅适用于SQLite数据库

Returns:
    dict: 清理结果

**Tags:** API v1, 数据库管理

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 数据库操作失败
- `503`: 数据库不可用

---

### /api/v1/v1/database/analyze

#### POST /api/v1/v1/database/analyze

**Summary:** Analyze Database

**Description:** 分析数据库统计信息，优化查询性能
仅适用于SQLite数据库

Returns:
    dict: 分析结果

**Tags:** API v1, 数据库管理

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 数据库操作失败
- `503`: 数据库不可用

---

### /api/v1/v1/database/stats

#### GET /api/v1/v1/database/stats

**Summary:** Get Database Statistics

**Description:** 获取数据库统计信息

Returns:
    dict: 数据库统计信息

**Tags:** API v1, 数据库管理

**Responses:**

- `200`: 操作成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 数据库操作失败
- `503`: 数据库不可用

---

### /api/v1/v1/info

#### GET /api/v1/v1/info

**Summary:** 获取API信息

**Description:** 获取API版本和配置信息

**Tags:** API v1

**Responses:**

- `200`: Successful Response
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 请求参数验证失败
- `500`: 服务器内部错误

---

