# 专业术语库系统 - 接口文档增量

> **特性状态**：已完成 
> **创建时间**：2026-04-11
> **最后更新**：2026-04-11
> **关联文档**：[技术方案](./search-optimization-glossary-03-技术方案.md) | [任务清单](./search-optimization-glossary-04-开发任务清单.md)

---

## 目录

1. [接口变更概述](#1-接口变更概述)
2. [术语库管理API](#2-术语库管理api)
3. [术语管理API](#3-术语管理api)
4. [CSV导入导出API](#4-csv导入导出api)
5. [术语扩展API](#5-术语扩展api)
6. [搜索API扩展](#6-搜索api扩展)
7. [数据模型变更](#7-数据模型变更)
8. [设置API扩展](#8-设置api扩展)

---

## 1. 接口变更概述

### 1.1 变更统计

| API模块 | 新增接口 | 修改接口 | 删除接口 |
|---------|---------|---------|---------|
| 术语库管理 | 4 | 0 | 0 |
| 术语管理 | 4 | 0 | 0 |
| CSV导入导出 | 2 | 0 | 0 |
| 术语扩展 | 1 | 0 | 0 |
| 搜索服务 | 0 | 1 | 0 |
| 设置管理 | 0 | 1 | 0 |
| **合计** | **11** | **2** | **0** |

### 1.2 变更摘要

**新增接口**：
- 术语库集合管理：创建、查询、更新、删除
- 术语管理：添加、查询、更新、删除
- CSV导入导出：批量导入、导出
- 术语扩展：查询扩展功能

**修改接口**：
- 搜索API：响应增加术语扩展信息
- 设置API：增加术语库配置项

---

## 2. 术语库管理API

### 2.1 获取术语库列表

**接口**：`GET /api/glossary/collections`

**描述**：获取术语库集合列表，支持分页和筛选。

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量 |
| is_enabled | boolean | 否 | null | 是否启用（null=全部） |
| search | string | 否 | null | 搜索关键词（匹配名称） |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "医疗术语库",
        "description": "医学领域的专业术语",
        "icon": "🏥",
        "color": "#F44336",
        "is_enabled": true,
        "term_count": 150,
        "is_system": false,
        "created_at": "2026-04-01T00:00:00",
        "updated_at": "2026-04-10T12:30:00"
      },
      {
        "id": 2,
        "name": "法律术语库",
        "description": "法律领域的专业术语",
        "icon": "⚖️",
        "color": "#D32F2F",
        "is_enabled": true,
        "term_count": 80,
        "is_system": true,
        "created_at": "2026-04-01T00:00:00",
        "updated_at": "2026-04-10T12:30:00"
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 20
  }
}
```

### 2.2 创建术语库

**接口**：`POST /api/glossary/collections`

**描述**：创建新的术语库集合。

**请求体**：

```json
{
  "name": "医疗术语库",
  "description": "医学领域的专业术语",
  "icon": "🏥",
  "color": "#F44336"
}
```

**请求参数说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 术语库名称，1-100字符，全局唯一 |
| description | string | 否 | 术语库描述 |
| icon | string | 否 | 图标（emoji或图标名称） |
| color | string | 否 | 显示颜色（hex格式，如#F44336） |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "医疗术语库",
    "description": "医学领域的专业术语",
    "icon": "🏥",
    "color": "#F44336",
    "is_enabled": true,
    "term_count": 0,
    "is_system": false,
    "created_at": "2026-04-11T10:00:00",
    "updated_at": "2026-04-11T10:00:00"
  },
  "message": "glossary.collection.created"
}
```

**错误响应**：

```json
{
  "success": false,
  "error": {
    "code": "duplicate_collection_name",
    "message": "术语库名称已存在"
  }
}
```

### 2.3 更新术语库

**接口**：`PUT /api/glossary/collections/{id}`

**描述**：更新术语库信息。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 术语库ID |

**请求体**：

```json
{
  "name": "医疗术语库（更新）",
  "description": "医学领域的专业术语",
  "icon": "🏥",
  "color": "#E64A19"
}
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "医疗术语库（更新）",
    "description": "医学领域的专业术语",
    "icon": "🏥",
    "color": "#E64A19",
    "is_enabled": true,
    "term_count": 150,
    "is_system": false,
    "updated_at": "2026-04-11T10:30:00"
  },
  "message": "glossary.collection.updated"
}
```

### 2.4 删除术语库

**接口**：`DELETE /api/glossary/collections/{id}`

**描述**：删除术语库集合及其所有术语（级联删除）。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 术语库ID |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "deleted_id": 1,
    "deleted_terms": 150
  },
  "message": "glossary.collection.deleted"
}
```

**错误响应**：

```json
{
  "success": false,
  "error": {
    "code": "collection_not_found",
    "message": "术语库不存在"
  }
}
```

---

## 3. 术语管理API

### 3.1 获取术语列表

**接口**：`GET /api/glossary/collections/{collection_id}/terms`

**描述**：获取指定术语库的术语列表，支持分页和搜索。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_id | integer | 是 | 术语库ID |

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量 |
| search | string | 否 | null | 搜索关键词（匹配术语名称或同义词） |
| is_enabled | boolean | 否 | null | 是否启用（null=全部） |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "collection_id": 1,
    "collection_name": "医疗术语库",
    "items": [
      {
        "id": 1,
        "term": "CT",
        "synonyms": ["计算机断层扫描", "CT扫描", "Computed Tomography"],
        "description": "计算机断层扫描，一种医学影像技术",
        "examples": null,
        "is_enabled": true,
        "created_at": "2026-04-01T00:00:00",
        "updated_at": "2026-04-10T12:30:00"
      }
    ],
    "total": 150,
    "page": 1,
    "page_size": 20
  }
}
```

### 3.2 添加术语

**接口**：`POST /api/glossary/collections/{collection_id}/terms`

**描述**：向指定术语库添加新术语。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_id | integer | 是 | 术语库ID |

**请求体**：

```json
{
  "term": "CT",
  "synonyms": ["计算机断层扫描", "CT扫描", "Computed Tomography"],
  "description": "计算机断层扫描",
  "examples": ["患者进行了CT检查"]
}
```

**请求参数说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| term | string | 是 | 术语名称，1-100字符，同一术语库内唯一 |
| synonyms | array | 是 | 同义词列表，至少包含一个术语 |
| description | string | 否 | 术语描述 |
| examples | array | 否 | 使用示例 |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "id": 1,
    "term": "CT",
    "synonyms": ["计算机断层扫描", "CT扫描", "Computed Tomography"],
    "description": "计算机断层扫描",
    "examples": ["患者进行了CT检查"],
    "is_enabled": true,
    "collection_id": 1,
    "created_at": "2026-04-11T10:00:00",
    "updated_at": "2026-04-11T10:00:00"
  },
  "message": "glossary.term.created"
}
```

**错误响应**：

```json
{
  "success": false,
  "error": {
    "code": "duplicate_term_in_collection",
    "message": "术语在该术语库中已存在"
  }
}
```

### 3.3 更新术语

**接口**：`PUT /api/glossary/collections/{collection_id}/terms/{term_id}`

**描述**：更新术语信息。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_id | integer | 是 | 术语库ID |
| term_id | integer | 是 | 术语ID |

**请求体**：

```json
{
  "term": "CT",
  "synonyms": ["计算机断层扫描", "CT扫描", "Computed Tomography", "CAT Scan"],
  "description": "计算机断层扫描，一种医学影像技术",
  "examples": ["患者进行了CT检查", "CT显示肺部清晰"],
  "is_enabled": true
}
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "id": 1,
    "term": "CT",
    "synonyms": ["计算机断层扫描", "CT扫描", "Computed Tomography", "CAT Scan"],
    "description": "计算机断层扫描，一种医学影像技术",
    "examples": ["患者进行了CT检查", "CT显示肺部清晰"],
    "is_enabled": true,
    "updated_at": "2026-04-11T10:30:00"
  },
  "message": "glossary.term.updated"
}
```

### 3.4 删除术语

**接口**：`DELETE /api/glossary/collections/{collection_id}/terms/{term_id}`

**描述**：删除指定术语。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_id | integer | 是 | 术语库ID |
| term_id | integer | 是 | 术语ID |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "deleted_id": 1
  },
  "message": "glossary.term.deleted"
}
```

---

## 4. CSV导入导出API

### 4.1 导入CSV

**接口**：`POST /api/glossary/collections/{collection_id}/import`

**描述**：从CSV文件批量导入术语到指定术语库。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_id | integer | 是 | 术语库ID |

**请求**：

- Content-Type: `multipart/form-data`
- 参数名：`file`
- 类型：文件

**CSV格式要求**：

```csv
术语名称,同义词,描述
CT,计算机断层扫描;CT扫描;Computed Tomography,计算机断层扫描
MRI,磁共振成像;MRI扫描;Magnetic Resonance Imaging,磁共振成像
PRD,产品需求文档;PRD文档;Product Requirement Document,产品需求文档
```

**CSV格式说明**：

| 字段 | 必填 | 格式 | 说明 |
|------|------|------|------|
| 术语名称 | 是 | 纯文本 | 术语的标准名称 |
| 同义词 | 是 | 分号分隔 | 多个同义词用分号(;)分隔，至少一个 |
| 描述 | 否 | 纯文本 | 术语的详细解释 |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "imported_count": 50,
    "failed_count": 2,
    "errors": [
      {
        "row": 3,
        "term": "X光",
        "error": "同义词格式错误，应使用分号分隔"
      },
      {
        "row": 15,
        "term": "API",
        "error": "术语在该术语库中已存在"
      }
    ]
  },
  "message": "glossary.import.completed"
}
```

**错误处理**：
- 某行导入失败不影响其他行
- 重复的术语名称自动跳过
- 格式错误的行记录到errors列表

### 4.2 导出CSV

**接口**：`GET /api/glossary/collections/{collection_id}/export`

**描述**：导出指定术语库的所有术语为CSV文件。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_id | integer | 是 | 术语库ID |

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| format | string | 否 | csv | 导出格式（目前只支持csv） |

**响应**：

- Content-Type: `text/csv; charset=utf-8`
- Content-Disposition: `attachment; filename="glossary_collection_1_20260411.csv"`

**CSV内容示例**：

```csv
术语名称,同义词,描述
CT,计算机断层扫描;CT扫描;Computed Tomography,计算机断层扫描
MRI,磁共振成像;MRI扫描;Magnetic Resonance Imaging,磁共振成像
PRD,产品需求文档;PRD文档;Product Requirement Document,产品需求文档
```

---

## 5. 术语扩展API

### 5.1 查询扩展

**接口**：`POST /api/glossary/expand`

**描述**：根据查询词和术语库配置，返回扩展的查询词列表。

**请求体**：

```json
{
  "query": "PRD",
  "collection_ids": null
}
```

**请求参数说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 原始查询词 |
| collection_ids | array | 否 | null | 使用的术语库ID列表，null=全部 |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "original_query": "PRD",
    "matched_terms": [
      {
        "id": 5,
        "term": "PRD",
        "collection_name": "产品术语库",
        "synonyms": ["产品需求文档", "需求文档", "PRD文档"]
      }
    ],
    "expanded_queries": ["PRD", "产品需求文档", "需求文档", "PRD文档"],
    "used_collections": ["产品术语库", "IT术语库"]
  }
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| original_query | string | 原始查询词 |
| matched_terms | array | 匹配的术语列表 |
| expanded_queries | array | 扩展后的查询词列表（去重） |
| used_collections | array | 实际使用的术语库名称列表 |

---

## 6. 搜索API扩展

### 6.1 修改搜索响应

**原接口**：`POST /api/search`

**变更点**：响应数据增加术语扩展相关字段

**新增响应字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| expanded_queries | array | 扩展的查询词列表（当启用术语扩展时） |
| used_collections | array | 使用的术语库名称列表（当启用术语扩展时） |

**响应示例（启用术语扩展）**：

```json
{
  "success": true,
  "data": {
    "query": "PRD",
    "expanded_queries": ["PRD", "产品需求文档", "需求文档"],
    "used_collections": ["产品术语库"],
    "total": 5,
    "results": [
      {
        "id": "chunk_001",
        "filename": "产品需求文档.md",
        "path": "/docs/产品需求文档.md",
        "score": 0.95,
        "content_preview": "这是一个产品需求文档..."
      }
    ]
  }
}
```

**响应示例（未启用术语扩展）**：

```json
{
  "success": true,
  "data": {
    "query": "PRD",
    "total": 2,
    "results": [...]
  }
}
```

### 6.2 术语扩展配置

**设置API**：`GET/PUT /api/settings`

**新增配置项**：

```json
{
  "default_glossary_collections": "all"
}
```

或

```json
{
  "default_glossary_collections": [1, 2, 3]
}
```

**配置说明**：

| 值 | 类型 | 说明 |
|----|------|------|
| "all" | string | 使用所有已启用的术语库（默认） |
| [1,2,3] | array | 使用指定ID的术语库 |

---

## 7. 数据模型变更

### 7.1 新增表

#### glossary_collections（术语库集合表）

```sql
CREATE TABLE glossary_collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(20),
    is_enabled BOOLEAN DEFAULT 1,
    term_count INTEGER DEFAULT 0,
    is_system BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 主键 |
| name | string | 术语库名称，全局唯一 |
| description | text | 术语库描述 |
| icon | string | 图标（emoji或图标名称） |
| color | string | 显示颜色（hex格式） |
| is_enabled | boolean | 是否启用 |
| term_count | integer | 术语数量（冗余字段，触发器更新） |
| is_system | boolean | 是否为系统预置 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### glossary_terms（术语表）

```sql
CREATE TABLE glossary_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    term VARCHAR(100) NOT NULL,
    synonyms TEXT NOT NULL,
    description TEXT,
    examples TEXT,
    is_enabled BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES glossary_collections(id) ON DELETE CASCADE,
    UNIQUE (collection_id, term)
);
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 主键 |
| collection_id | integer | 关联的术语库ID（外键） |
| term | string | 术语名称 |
| synonyms | text | 同义词（JSON数组字符串） |
| description | text | 术语描述 |
| examples | text | 使用示例（JSON数组字符串） |
| is_enabled | boolean | 是否启用 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 7.2 修改表

#### app_settings（设置表）

**新增配置项**：

```sql
INSERT INTO app_settings (setting_key, setting_value, setting_type, description)
VALUES ('default_glossary_collections', 'all', 'string', '默认使用的术语库（all=全部，或数组形式的ID列表）');
```

---

## 8. 设置API扩展

### 8.1 获取术语库设置

**接口**：`GET /api/settings`

**新增响应字段**：

```json
{
  "success": true,
  "data": {
    "default_glossary_collections": "all"
  }
}
```

### 8.2 更新术语库设置

**接口**：`PUT /api/settings`

**新增请求字段**：

```json
{
  "default_glossary_collections": [1, 2, 3]
}
```

或

```json
{
  "default_glossary_collections": "all"
}
```

---

## 9. 错误码参考

### 9.1 新增错误码

| 错误码 | HTTP状态码 | 说明 | 前端翻译键 |
|--------|-----------|------|-----------|
| duplicate_collection_name | 400 | 术语库名称已存在 | glossary.error.duplicate_name |
| collection_not_found | 404 | 术语库不存在 | glossary.error.collection_not_found |
| system_collection_readonly | 403 | 系统预置术语库只读 | glossary.error.system_readonly |
| duplicate_term_in_collection | 400 | 术语在该术语库中已存在 | glossary.error.duplicate_term |
| term_not_found | 404 | 术语不存在 | glossary.error.term_not_found |
| csv_format_error | 400 | CSV格式错误 | glossary.error.csv_format |
| collection_not_empty | 400 | 术语库不为空时无法删除 | glossary.error.collection_not_empty |

### 9.2 国际化错误消息

```json
// zh_CN.json
{
  "glossary": {
    "error": {
      "duplicate_name": "术语库名称已存在",
      "collection_not_found": "术语库不存在",
      "system_readonly": "系统预置术语库只能编辑，不能删除",
      "duplicate_term": "该术语已存在",
      "term_not_found": "术语不存在",
      "csv_format": "CSV格式错误：{details}",
      "collection_not_empty": "术语库包含{count}个术语，请先删除所有术语"
    }
  }
}

// en_US.json
{
  "glossary": {
    "error": {
      "duplicate_name": "Collection name already exists",
      "collection_not_found": "Collection not found",
      "system_readonly": "System preset collection can only be edited, not deleted",
      "duplicate_term": "Term already exists",
      "term_not_found": "Term not found",
      "csv_format": "CSV format error: {details}",
      "collection_not_empty": "Collection contains {count} terms, please delete all terms first"
    }
  }
}
```

---

## 10. 使用示例

### 10.1 完整流程示例

```javascript
// 1. 创建术语库
const response1 = await fetch('/api/glossary/collections', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'IT术语库',
    description: 'IT技术领域的专业术语',
    icon: '💻',
    color: '#2196F3'
  })
}).then(r => r.json());
// 返回: { success: true, data: { id: 1, ... } }

// 2. 添加术语
const response2 = await fetch('/api/glossary/collections/1/terms', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    term: 'API',
    synonyms: ['接口', '应用程序接口', 'Application Programming Interface'],
    description: '应用程序编程接口'
  })
}).then(r => r.json());
// 返回: { success: true, data: { id: 1, ... } }

// 3. 测试术语扩展
const response3 = await fetch('/api/glossary/expand', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'API',
    collection_ids: null
  })
}).then(r => r.json());
// 返回: { success: true, data: { expanded_queries: ['API', '接口', '应用程序接口'], ... } }

// 4. 使用扩展搜索
const response4 = await fetch('/api/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'API',
    search_type: 'hybrid',
    use_glossary: true
  })
}).then(r => r.json());
// 返回包含 expanded_queries 和 used_collections 的搜索结果
```

### 10.2 Python后端使用示例

```python
import httpx

# 创建术语库
response = httpx.post("http://127.0.0.1:8000/api/glossary/collections", json={
    "name": "医疗术语库",
    "icon": "🏥",
    "color": "#F44336"
})
print(response.json())

# 添加术语
response = httpx.post(f"http://127.0.0.1:8000/api/glossary/collections/1/terms", json={
    "term": "CT",
    "synonyms": ["计算机断层扫描", "CT扫描"],
    "description": "计算机断层扫描"
})
print(response.json())

# 术语扩展
response = httpx.post("http://127.0.0.1:8000/api/glossary/expand", json={
    "query": "CT"
})
print(response.json())
# 返回: {"expanded_queries": ["CT", "计算机断层扫描", "CT扫描"], ...}
```

---

## 11. 版本兼容性

### 11.1 向后兼容

- 所有新增接口不影响现有功能
- 术语扩展为可选功能，默认关闭
- 搜索API新增字段为可选，旧客户端无需修改

### 11.2 数据库迁移

- 使用Alembic进行数据库版本管理
- 迁移脚本自动执行
- 支持回滚

---

**文档结束**

> **使用说明**：
> 1. 本文档为专业术语库特性的增量接口文档
> 2. 与主接口文档 [接口文档.md](../../接口文档.md) 配合使用
> 3. 实施时请参考 [技术方案](./search-optimization-glossary-03-技术方案.md)
