# 专业术语库系统 - 技术方案

> **文档类型**：技术方案
> **特性状态**：规划中
> **创建时间**：2026-04-11
> **最后更新**：2026-04-11

---

## 1. 方案概述

### 1.1 技术目标

建立**多术语库集合系统**，支持用户自定义领域术语库（医疗、法律、IT等），在搜索时选择性使用，实现精准查询扩展。核心解决当前BGE-M3向量模型对英文缩写词语义理解不足的问题。

### 1.2 设计原则

- **领域隔离**：不同领域术语独立管理，避免术语混淆
- **用户可控**：用户可选择默认使用的术语库组合
- **向后兼容**：不影响现有搜索功能，术语扩展为可选功能
- **性能优先**：批量查询优化，术语匹配<50ms
- **数据可迁移**：支持CSV导入/导出，便于数据备份和共享

### 1.3 技术选型

| 技术/框架 | 用途 | 选择理由 |
|----------|------|---------|
| SQLAlchemy | ORM | 与现有数据库层一致 |
| FastAPI | API框架 | 与现有API层一致 |
| Vue 3 + Ant Design Vue | 前端框架 | 与现有前端一致 |
| JSON | 数据格式 | 灵活存储同义词数组 |
| Python csv | CSV解析 | 标准库，无额外依赖 |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              前端层 (Vue 3)                               │
├─────────────────────────────────────────────────────────────────────────┤
│  GlossaryCollections.vue  │  Settings.vue(术语库选项卡)  │  Search.vue │
└────────────┬──────────────────────────────────────────────────────────────┘
             │ HTTP/REST API
┌────────────▼──────────────────────────────────────────────────────────────┐
│                              API层 (FastAPI)                               │
├─────────────────────────────────────────────────────────────────────────┤
│  /api/glossary/collections  │  /api/glossary/terms  │  /api/glossary/expand│
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                           服务层 (Service Layer)                           │
├───────────────────────────────────────────────────────────────────────────┤
│  GlossaryCollectionService  │  GlossaryTermService  │  GlossaryService    │
└────────────┬──────────────────────────────────────────┬───────────────────┘
             │                                          │
┌────────────▼──────────────────────────────────────────▼───────────────────┐
│                          数据层 (SQLAlchemy ORM)                           │
├───────────────────────────────────────────────────────────────────────────┤
│  GlossaryCollectionModel  │  GlossaryTermModel  │  AppSettingsModel      │
└────────────┬──────────────────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────────────┐
│                        数据库层 (SQLite)                                   │
├───────────────────────────────────────────────────────────────────────────┤
│  glossary_collections  │  glossary_terms  │  app_settings                │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                        搜索集成 (ChunkSearchService)                      │
├───────────────────────────────────────────────────────────────────────────┤
│  用户搜索 → GlossaryService.expand_query() → 扩展查询词 → 多词搜索 → 合并结果 │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流设计

#### 2.2.1 术语扩展搜索流程

```
用户输入查询 "PRD"
    ↓
[1] ChunkSearchService.search()
    ↓
[2] GlossaryService.expand_query(query, collection_ids)
    ↓
[3] GlossaryTermService.get_terms_by_collections(collection_ids)
    ↓
[4] 数据库查询 glossary_terms
    SELECT * FROM glossary_terms
    WHERE collection_id IN (1, 2, 3)
      AND is_enabled = 1
      AND (term LIKE '%PRD%' OR synonyms LIKE '%PRD%')
    ↓
[5] 返回匹配术语
    ↓
[6] 提取所有同义词
    ↓
[7] 去重
    ↓
[8] 返回扩展查询词列表
    ↓
[9] ChunkSearchService 对每个扩展词执行搜索
    ↓
[10] 合并去重搜索结果
    ↓
[11] 返回综合结果 + 使用的术语库信息
```

---

## 3. 数据库设计

### 3.1 表结构设计

#### 3.1.1 术语库集合表 (glossary_collections)

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

CREATE INDEX idx_gc_name ON glossary_collections(name);
CREATE INDEX idx_gc_enabled ON glossary_collections(is_enabled);
```

#### 3.1.2 术语表 (glossary_terms)

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
    FOREIGN KEY (collection_id) REFERENCES glossary_collections(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_gt_collection_term ON glossary_terms(collection_id, term);
CREATE INDEX idx_gt_collection ON glossary_terms(collection_id);
CREATE INDEX idx_gt_term ON glossary_terms(term);
```

#### 3.1.3 触发器

```sql
-- 自动更新术语库的术语数量
CREATE TRIGGER update_collection_term_count_insert
AFTER INSERT ON glossary_terms
FOR EACH ROW
WHEN NEW.is_enabled = 1
BEGIN
  UPDATE glossary_collections
  SET term_count = term_count + 1
  WHERE id = NEW.collection_id;
END;

-- 自动更新时间戳
CREATE TRIGGER update_collection_timestamp
AFTER UPDATE ON glossary_collections
FOR EACH ROW
BEGIN
  UPDATE glossary_collections SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

---

## 4. API设计

### 4.1 API端点列表

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/glossary/collections` | GET | 获取术语库列表 |
| `/api/glossary/collections` | POST | 创建术语库 |
| `/api/glossary/collections/{id}` | PUT | 更新术语库 |
| `/api/glossary/collections/{id}` | DELETE | 删除术语库 |
| `/api/glossary/collections/{id}/terms` | GET | 获取术语列表 |
| `/api/glossary/collections/{id}/terms` | POST | 添加术语 |
| `/api/glossary/collections/{id}/terms/{term_id}` | PUT | 更新术语 |
| `/api/glossary/collections/{id}/terms/{term_id}` | DELETE | 删除术语 |
| `/api/glossary/collections/{id}/import` | POST | 导入CSV |
| `/api/glossary/collections/{id}/export` | GET | 导出CSV |
| `/api/glossary/expand` | POST | 查询扩展 |

### 4.2 核心API设计

#### 4.2.1 创建术语库

```
POST /api/glossary/collections

请求体:
{
  "name": "医疗术语库",
  "description": "医学领域的专业术语",
  "icon": "🏥",
  "color": "#F44336"
}

响应:
{
  "success": true,
  "data": {
    "id": 1,
    "name": "医疗术语库",
    "icon": "🏥",
    "color": "#F44336",
    "is_enabled": true,
    "term_count": 0,
    "is_system": false
  },
  "message": "glossary.collection.created"
}
```

#### 4.2.2 获取术语列表

```
GET /api/glossary/collections/{collection_id}/terms?page=1&page_size=20

响应:
{
  "success": true,
  "data": {
    "collection_id": 1,
    "collection_name": "医疗术语库",
    "items": [
      {
        "id": 1,
        "term": "CT",
        "synonyms": ["计算机断层扫描", "CT扫描"],
        "description": "计算机断层扫描"
      }
    ],
    "total": 150
  }
}
```

#### 4.2.3 导入CSV

```
POST /api/glossary/collections/{collection_id}/import
Content-Type: multipart/form-data

CSV格式:
术语名称,同义词,描述
CT,计算机断层扫描;CT扫描,计算机断层扫描

响应:
{
  "success": true,
  "data": {
    "imported_count": 50,
    "failed_count": 2,
    "errors": [...]
  }
}
```

#### 4.2.4 查询扩展

```
POST /api/glossary/expand

请求体:
{
  "query": "PRD",
  "collection_ids": null  // null=全部
}

响应:
{
  "success": true,
  "data": {
    "original_query": "PRD",
    "matched_terms": [...],
    "expanded_queries": ["PRD", "产品需求文档", "需求文档"],
    "used_collections": ["产品术语库"]
  }
}
```

---

## 5. 核心服务设计

### 5.1 GlossaryCollectionService

```python
# backend/app/services/glossary_collection_service.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.glossary_collection import GlossaryCollectionModel

class GlossaryCollectionService:
    """术语库集合服务"""

    def __init__(self, db: Session):
        self.db = db

    async def get_collections(
        self,
        page: int = 1,
        page_size: int = 20,
        is_enabled: Optional[bool] = None
    ) -> dict:
        """获取术语库列表（分页）"""
        query = self.db.query(GlossaryCollectionModel)

        if is_enabled is not None:
            query = query.filter(GlossaryCollectionModel.is_enabled == is_enabled)

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    async def create_collection(self, name: str, description: str = None, 
                                icon: str = None, color: str = None):
        """创建术语库"""
        collection = GlossaryCollectionModel(
            name=name,
            description=description,
            icon=icon,
            color=color
        )
        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)
        return collection
```

### 5.2 GlossaryTermService

```python
# backend/app/services/glossary_term_service.py

import csv
import json
import io
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile

class GlossaryTermService:
    """术语服务"""

    async def import_from_csv(
        self,
        collection_id: int,
        file: UploadFile
    ) -> dict:
        """从CSV导入术语"""
        contents = await file.read()
        csv_file = io.TextIOWrapper(io.BytesIO(contents), encoding='utf-8')
        csv_reader = csv.DictReader(csv_file)

        imported_count = 0
        failed_count = 0
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                term_name = row.get("术语名称", "").strip()
                if not term_name:
                    raise ValueError("术语名称不能为空")

                synonyms_str = row.get("同义词", "")
                synonyms = [s.strip() for s in synonyms_str.split(";") if s.strip()]

                # 创建术语
                term_data = {
                    "collection_id": collection_id,
                    "term": term_name,
                    "synonyms": json.dumps(synonyms, ensure_ascii=False),
                    "description": row.get("描述", "").strip()
                }

                term = GlossaryTermModel(**term_data)
                self.db.add(term)
                imported_count += 1

            except Exception as e:
                errors.append({"row": row_num, "term": row.get("术语名称", ""), "error": str(e)})
                failed_count += 1

        self.db.commit()
        return {"imported_count": imported_count, "failed_count": failed_count, "errors": errors}
```

### 5.3 GlossaryService

```python
# backend/app/services/glossary_service.py

from typing import List, Optional
from sqlalchemy.orm import Session

class GlossaryService:
    """术语匹配和扩展服务"""

    def __init__(self, db: Session):
        self.db = db

    async def expand_query(
        self,
        query: str,
        collection_ids: Optional[List[int]] = None
    ) -> dict:
        """扩展查询词"""
        # 获取匹配的术语
        matched_terms = await self.match_terms(query, collection_ids)

        # 收集所有查询词
        expanded_queries = [query]
        collection_names = set()

        for term in matched_terms:
            expanded_queries.extend(term["synonyms"])
            collection_names.add(term["collection_name"])

        # 去重
        expanded_queries = list(set(expanded_queries))

        return {
            "original_query": query,
            "matched_terms": matched_terms,
            "expanded_queries": expanded_queries,
            "used_collections": list(collection_names)
        }

    async def match_terms(
        self,
        query: str,
        collection_ids: Optional[List[int]] = None
    ) -> List[dict]:
        """匹配查询中的术语"""
        # 构建查询
        db_query = self.db.query(
            GlossaryTermModel.id,
            GlossaryTermModel.term,
            GlossaryTermModel.synonyms,
            GlossaryTermModel.collection_id,
            GlossaryCollectionModel.name.label("collection_name")
        ).join(
            GlossaryCollectionModel,
            GlossaryTermModel.collection_id == GlossaryCollectionModel.id
        ).filter(
            GlossaryTermModel.is_enabled == True,
            GlossaryCollectionModel.is_enabled == True
        )

        if collection_ids:
            db_query = db_query.filter(
                GlossaryTermModel.collection_id.in_(collection_ids)
            )

        # 模糊匹配
        db_query = db_query.filter(
            (GlossaryTermModel.term.contains(query)) |
            (GlossaryTermModel.synonyms.contains(query))
        )

        results = db_query.all()

        # 解析结果
        matched_terms = []
        for row in results:
            synonyms = json.loads(row.synonyms) if isinstance(row.synonyms, str) else row.synonyms
            matched_terms.append({
                "id": row.id,
                "term": row.term,
                "synonyms": synonyms,
                "collection_id": row.collection_id,
                "collection_name": row.collection_name
            })

        return matched_terms
```

---

## 6. 搜索集成

### 6.1 修改 ChunkSearchService

```python
# backend/app/services/chunk_search_service.py

from app.services.glossary_service import GlossaryService
from app.core.database import SessionLocal

class ChunkSearchService:
    async def search(
        self,
        query: str,
        search_type: str = "hybrid",
        top_k: int = 10,
        use_glossary: bool = True
    ) -> dict:
        """执行搜索（集成术语扩展）"""

        expanded_queries = [query]
        used_collections = []

        if use_glossary:
            db = SessionLocal()
            try:
                glossary_service = GlossaryService(db)

                # 获取用户设置的默认术语库
                default_collections = await self._get_default_glossary_collections()

                collection_ids = None if default_collections == "all" else default_collections

                # 扩展查询
                expand_result = await glossary_service.expand_query(query, collection_ids)
                expanded_queries = expand_result["expanded_queries"]
                used_collections = expand_result["used_collections"]

            finally:
                db.close()

        # 对每个扩展词执行搜索
        all_results = []
        for expanded_query in expanded_queries:
            results = await self._chunk_search(
                query=expanded_query,
                search_type=search_type,
                top_k=top_k
            )
            all_results.extend(results)

        # 合并去重
        final_results = self._merge_and_deduplicate(all_results, top_k)

        return {
            "query": query,
            "expanded_queries": expanded_queries,
            "used_collections": used_collections,
            "results": final_results
        }

    def _merge_and_deduplicate(self, results: List[dict], top_k: int) -> List[dict]:
        """合并去重搜索结果"""
        seen = set()
        merged = []

        for result in results:
            chunk_id = result.get("chunk_id")
            if chunk_id and chunk_id not in seen:
                seen.add(chunk_id)
                merged.append(result)

        return merged[:top_k]
```

---

## 7. 前端实现

### 7.1 设置页面新增术语库选项卡

```vue
<!-- frontend/src/renderer/src/views/Settings.vue (扩展) -->

<a-tab-pane key="glossary" :tab="t('settingsGlossary.title')">
  <div class="settings-section">
    <h3>{{ t('settingsGlossary.title') }}</h3>
    <a-form layout="vertical">
      <a-form-item>
        <a-checkbox v-model:checked="glossaryEnabled">
          {{ t('settingsGlossary.enableExpansion') }}
        </a-checkbox>
      </a-form-item>

      <a-form-item :label="t('settingsGlossary.defaultCollections')">
        <a-radio-group v-model:value="glossaryMode">
          <a-radio value="all">{{ t('settingsGlossary.useAll') }}</a-radio>
          <a-radio value="custom">{{ t('settingsGlossary.selectSpecific') }}</a-radio>
        </a-radio-group>
      </a-form-item>

      <a-form-item v-if="glossaryMode === 'custom'">
        <a-checkbox-group v-model:value="selectedCollections">
          <a-space direction="vertical" style="width: 100%">
            <a-checkbox 
              v-for="collection in collections" 
              :key="collection.id" 
              :value="collection.id"
            >
              {{ collection.icon }} {{ collection.name }} ({{ collection.term_count }})
              <a-button 
                type="link" 
                size="small" 
                @click="goToGlossaryManagement"
                style="margin-left: 8px"
              >
                管理→
              </a-button>
            </a-checkbox>
          </a-space>
        </a-checkbox-group>
      </a-form-item>

      <a-form-item>
        <a-space>
          <a-button type="primary" @click="createNewCollection">
            + {{ t('settingsGlossary.newCollection') }}
          </a-button>
          <a-button @click="saveGlossarySettings">
            {{ t('common.save') }}
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </div>
</a-tab-pane>
```

---

## 8. 国际化支持

### 8.1 中文翻译

```json
// frontend/src/locales/zh_CN.json (扩展)

{
  "settingsGlossary": {
    "title": "术语库",
    "enableExpansion": "启用术语扩展（搜索时自动使用术语库扩展查询词）",
    "defaultCollections": "默认术语库",
    "useAll": "使用所有术语库（推荐）",
    "selectSpecific": "选择特定术语库",
    "newCollection": "新建术语库",
    "manage": "管理"
  },
  "glossary": {
    "title": "术语库管理",
    "name": "名称",
    "description": "描述",
    "icon": "图标",
    "color": "颜色",
    "termName": "术语名称",
    "synonyms": "同义词",
    "addSynonym": "添加同义词",
    "terms": "术语",
    "createSuccess": "术语库创建成功",
    "saveSuccess": "保存成功"
  }
}
```

---

## 9. 实施步骤

### 9.1 第一阶段：核心功能（1-2周）

**后端开发**：
- [ ] 创建数据库模型（GlossaryCollectionModel、GlossaryTermModel）
- [ ] 创建Pydantic模式（请求/响应）
- [ ] 实现GlossaryCollectionService
- [ ] 实现GlossaryTermService
- [ ] 实现GlossaryService（术语匹配和扩展）
- [ ] 创建API路由（glossary.py）
- [ ] 数据库迁移脚本
- [ ] 预置术语库初始化脚本

**前端开发**：
- [ ] 创建GlossaryCollections.vue（三栏布局）
- [ ] 创建术语库相关组件
- [ ] 实现Pinia store（glossary.js）
- [ ] 实现API服务（glossary.js）
- [ ] 添加路由配置
- [ ] 国际化翻译

**测试**：
- [ ] 单元测试（服务层）
- [ ] API测试
- [ ] 前端组件测试

### 9.2 第二阶段：搜索集成（1周）

**后端开发**：
- [ ] 修改ChunkSearchService，集成术语扩展
- [ ] 修改搜索API，返回扩展信息
- [ ] 用户设置服务扩展

**前端开发**：
- [ ] 修改搜索组件，显示术语扩展信息
- [ ] 修改搜索设置页面，添加术语库选择

**测试**：
- [ ] 搜索功能回归测试
- [ ] 术语扩展功能测试

### 9.3 第三阶段：优化和完善（3-5天）

- [ ] 性能优化（批量查询、缓存）
- [ ] 错误处理完善
- [ ] 用户体验优化
- [ ] 文档更新

---

## 10. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 术语匹配性能问题 | 搜索变慢 | 批量查询优化、LRU缓存、数据库索引 |
| 扩展查询结果过多 | 结果质量下降 | 优化结果合并算法、设置结果上限 |
| 数据库迁移失败 | 无法上线 | 提前测试、准备回滚方案 |

---

## 11. 后续规划

### 11.1 短期优化（1-2个迭代）
- [ ] 术语审核机制
- [ ] 术语推荐功能
- [ ] 术语使用可视化

### 11.2 中期规划（3-6个月）
- [ ] 自动术语发现（基于文档分析）
- [ ] 术语关联图谱
- [ ] 团队协作术语库

---

**文档结束**

> **使用说明**：
> 1. 本文档为专业术语库特性的完整技术方案
> 2. 实施时请按照9章节"实施步骤"进行
> 3. 与PRD和原型文档配合使用
