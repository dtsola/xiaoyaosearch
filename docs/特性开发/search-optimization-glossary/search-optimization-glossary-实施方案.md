# 专业术语库系统 - 实施方案

> **文档类型**：实施方案
> **特性状态**：已完成 
> **创建时间**：2026-04-11
> **最后更新**：2026-04-11
> **预计工期**：11.5天
> **实施优先级**：P0（高优先级）

---

## 1. 实施概述

### 1.1 实施目标

建立**多术语库集合系统**，支持用户自定义领域术语库，在搜索时选择性使用，实现精准查询扩展，解决BGE-M3向量模型对英文缩写词理解不足的问题。

### 1.2 核心价值

| 价值点 | 说明 | 预期效果 |
|--------|------|----------|
| **搜索精度提升** | 通过术语扩展，搜索"PRD"也能匹配"产品需求文档" | 搜索召回率提升30%+ |
| **用户体验优化** | 零配置使用预置术语库，支持自定义扩展 | 用户满意度提升40%+ |
| **领域专业化** | 支持医疗、法律、IT等多领域术语库 | 覆盖80%+专业场景 |
| **数据可迁移** | CSV导入导出，便于备份和共享 | 数据迁移成功率100% |

### 1.3 技术架构

```
前端层 (Vue 3)
  ├─ GlossaryCollections.vue（术语库管理页面）
  ├─ Settings.vue（术语库设置选项卡）
  └─ SearchResultCard.vue（显示术语扩展信息）

API层 (FastAPI)
  ├─ /api/glossary/collections（术语库管理）
  ├─ /api/glossary/terms（术语管理）
  ├─ /api/glossary/expand（查询扩展）
  └─ /api/glossary/import/export（CSV导入导出）

服务层 (Python)
  ├─ GlossaryCollectionService（术语库服务）
  ├─ GlossaryTermService（术语服务）
  └─ GlossaryService（术语匹配和扩展）

数据层 (SQLite)
  ├─ glossary_collections（术语库表）
  └─ glossary_terms（术语表）

搜索集成
  └─ ChunkSearchService（集成术语扩展）
```

---

## 2. 实施阶段规划

### 2.1 阶段划分

| 阶段 | 任务数 | 预计时间 | 里程碑 | 状态 |
|------|--------|----------|--------|------|
| 第一阶段：数据库与模型 | 7 | 1.5天 | M1: 数据库与模型完成 | ⬜ 待开始 |
| 第二阶段：后端服务与API | 10 | 3.5天 | M2: 后端API完成 | ⬜ 待开始 |
| 第三阶段：搜索集成 | 3 | 0.5天 | M3: 搜索集成完成 | ⬜ 待开始 |
| 第四阶段：前端实现 | 10 | 3天 | M4: 前端页面完成 | ⬜ 待开始 |
| 第五阶段：测试与优化 | 10 | 2天 | M5: 测试通过 | ⬜ 待开始 |
| 第六阶段：文档与发布 | 3 | 1天 | M6: 特性发布 | ⬜ 待开始 |
| **总计** | **43** | **11.5天** | - | - |

### 2.2 依赖关系

```
第一阶段（数据库与模型）
    ↓
第二阶段（后端服务与API）
    ↓
┌───────────┬───────────┐
│           │           │
第三阶段    第四阶段    （并行开发）
（搜索集成） （前端实现）
│           │
└─────┬─────┘
      ↓
第五阶段（测试与优化）
      ↓
第六阶段（文档与发布）
```

---

## 3. 第一阶段：数据库与模型（1.5天）

### 3.1 阶段目标

完成数据库表结构创建、ORM模型定义、Pydantic Schema定义。

### 3.2 任务清单

#### 任务1.1：创建数据库迁移脚本（0.5小时）

**操作步骤**：

1. 创建Alembic迁移文件
```bash
cd backend
alembic revision -m "add_glossary_tables"
```

2. 编辑迁移文件 `alembic/versions/xxx_add_glossary_tables.py`

```python
# alembic/versions/xxx_add_glossary_tables.py
"""添加专业术语库系统表

Revision ID: 004_add_glossary_tables
Revises: 003_add_plugin_source_fields
Create Date: 2026-04-11
"""
from alembic import op
import sqlalchemy as sa

revision = '004_add_glossary_tables'
down_revision = '003_add_plugin_source_fields'
branch_labels = None
depends_on = None


def upgrade():
    """升级：创建术语库相关表"""

    # 1. 创建glossary_collections表
    op.create_table(
        'glossary_collections',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.Text(), nullable=True),
        sa.Column('color', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), default=True, nullable=False),
        sa.Column('term_count', sa.Integer(), default=0, nullable=False),
        sa.Column('is_system', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_gc_name', 'glossary_collections', ['name'])
    op.create_index('idx_gc_enabled', 'glossary_collections', ['is_enabled'])
    op.create_index('idx_gc_system', 'glossary_collections', ['is_system'])

    # 2. 创建glossary_terms表
    op.create_table(
        'glossary_terms',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('collection_id', sa.Integer(), nullable=False),
        sa.Column('term', sa.Text(), nullable=False),
        sa.Column('synonyms', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('examples', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['collection_id'], ['glossary_collections.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('collection_id', 'term')
    )
    op.create_index('idx_gt_collection', 'glossary_terms', ['collection_id'])
    op.create_index('idx_gt_term', 'glossary_terms', ['term'])
    op.create_index('idx_gt_enabled', 'glossary_terms', ['is_enabled'])

    # 3. 创建触发器
    op.execute("""
        CREATE TRIGGER update_collection_term_count_insert
        AFTER INSERT ON glossary_terms
        FOR EACH ROW
        WHEN NEW.is_enabled = 1
        BEGIN
          UPDATE glossary_collections
          SET term_count = term_count + 1,
              updated_at = CURRENT_TIMESTAMP
          WHERE id = NEW.collection_id;
        END
    """)

    op.execute("""
        CREATE TRIGGER update_collection_term_count_delete
        AFTER DELETE ON glossary_terms
        FOR EACH ROW
        WHEN OLD.is_enabled = 1
        BEGIN
          UPDATE glossary_collections
          SET term_count = term_count - 1,
              updated_at = CURRENT_TIMESTAMP
          WHERE id = OLD.collection_id;
        END
    """)

    op.execute("""
        CREATE TRIGGER update_collection_term_count_update
        AFTER UPDATE OF is_enabled ON glossary_terms
        FOR EACH ROW
        WHEN NEW.is_enabled != OLD.is_enabled
        BEGIN
          UPDATE glossary_collections
          SET term_count = term_count + CASE
              WHEN NEW.is_enabled = 1 THEN 1
              ELSE -1
          END,
          updated_at = CURRENT_TIMESTAMP
          WHERE id = NEW.collection_id;
        END
    """)

    # 4. 插入默认配置
    op.execute("""
        INSERT INTO app_settings (setting_key, setting_value, setting_type, description, updated_at)
        VALUES ('default_glossary_collections', 'all', 'json', '默认使用的术语库ID列表，"all"表示全部', CURRENT_TIMESTAMP)
        ON CONFLICT(setting_key) DO UPDATE SET setting_value = 'all', updated_at = CURRENT_TIMESTAMP
    """)


def downgrade():
    """降级：删除术语库相关表"""
    op.execute("DROP TRIGGER IF EXISTS update_collection_term_count_insert")
    op.execute("DROP TRIGGER IF EXISTS update_collection_term_count_delete")
    op.execute("DROP TRIGGER IF EXISTS update_collection_term_count_update")

    op.drop_index('idx_gt_enabled', table_name='glossary_terms')
    op.drop_index('idx_gt_term', table_name='glossary_terms')
    op.drop_index('idx_gt_collection', table_name='glossary_terms')
    op.drop_index('idx_gc_system', table_name='glossary_collections')
    op.drop_index('idx_gc_enabled', table_name='glossary_collections')
    op.drop_index('idx_gc_name', table_name='glossary_collections')

    op.drop_table('glossary_terms')
    op.drop_table('glossary_collections')

    op.execute("DELETE FROM app_settings WHERE setting_key = 'default_glossary_collections'")
```

**验证标准**：
- [ ] 迁移文件创建成功
- [ ] upgrade()方法完整
- [ ] downgrade()方法完整
- [ ] 触发器定义正确

---

#### 任务1.2：执行数据库迁移（0.25小时）

**操作步骤**：

```bash
# 执行迁移
cd backend
alembic upgrade head

# 验证表创建
sqlite3 data/database/xiaoyao_search.db <<EOF
.tables
.schema glossary_collections
.schema glossary_terms
EOF
```

**验证标准**：
- [ ] glossary_collections表创建成功
- [ ] glossary_terms表创建成功
- [ ] 所有索引创建成功
- [ ] 所有触发器创建成功
- [ ] app_settings表包含default_glossary_collections配置

---

#### 任务1.3：创建GlossaryCollectionModel（0.5小时）

**操作步骤**：

创建文件 `backend/app/models/glossary_collection.py`：

```python
# backend/app/models/glossary_collection.py
"""
术语库集合数据模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class GlossaryCollectionModel(Base):
    """
    术语库集合模型

    存储术语库的基本信息和配置
    """
    __tablename__ = "glossary_collections"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    # 基础信息
    name = Column(String(100), unique=True, nullable=False, comment="术语库名称")
    description = Column(Text, nullable=True, comment="术语库描述")
    icon = Column(String(50), nullable=True, comment="图标（emoji）")
    color = Column(String(20), nullable=True, comment="颜色代码")

    # 状态字段
    is_enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")
    term_count = Column(Integer, default=0, nullable=False, comment="术语数量")
    is_system = Column(Boolean, default=False, nullable=False, comment="是否系统预置")

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 术语库信息字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "is_enabled": self.is_enabled,
            "term_count": self.term_count,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<GlossaryCollectionModel(id={self.id}, name={self.name}, term_count={self.term_count})>"
```

**验证标准**：
- [ ] 模型继承自Base类
- [ ] 所有字段定义完整
- [ ] to_dict()方法实现
- [ ] __repr__()方法实现

---

#### 任务1.4：创建GlossaryTermModel（0.5小时）

**操作步骤**：

创建文件 `backend/app/models/glossary_term.py`：

```python
# backend/app/models/glossary_term.py
"""
术语数据模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from app.core.database import Base


class GlossaryTermModel(Base):
    """
    术语模型

    存储术语的详细信息，包括同义词、描述和示例
    """
    __tablename__ = "glossary_terms"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    # 外键关联
    collection_id = Column(Integer, ForeignKey('glossary_collections.id', ondelete='CASCADE'), nullable=False, comment="术语库ID")

    # 术语字段
    term = Column(String(100), nullable=False, comment="术语名称")
    synonyms = Column(Text, nullable=False, comment="同义词（JSON数组）")
    description = Column(Text, nullable=True, comment="术语描述")
    examples = Column(Text, nullable=True, comment="示例用法（JSON数组）")

    # 状态字段
    is_enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 术语信息字典
        """
        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "term": self.term,
            "synonyms": self.get_synonyms_list(),
            "description": self.description,
            "examples": self.get_examples_list(),
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def get_synonyms_list(self) -> list:
        """
        获取同义词列表

        Returns:
            list: 同义词列表
        """
        try:
            if isinstance(self.synonyms, str):
                return json.loads(self.synonyms)
            return self.synonyms if self.synonyms else []
        except (json.JSONDecodeError, TypeError):
            return []

    def get_examples_list(self) -> list:
        """
        获取示例列表

        Returns:
            list: 示例列表
        """
        try:
            if isinstance(self.examples, str):
                return json.loads(self.examples)
            return self.examples if self.examples else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_synonyms(self, synonyms: list):
        """
        设置同义词

        Args:
            synonyms: 同义词列表
        """
        self.synonyms = json.dumps(synonyms, ensure_ascii=False)

    def set_examples(self, examples: list):
        """
        设置示例

        Args:
            examples: 示例列表
        """
        self.examples = json.dumps(examples, ensure_ascii=False)

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<GlossaryTermModel(id={self.id}, term={self.term}, collection_id={self.collection_id})>"
```

**验证标准**：
- [ ] 模型继承自Base类
- [ ] 外键关系定义正确
- [ ] unique约束定义正确
- [ ] to_dict()方法实现
- [ ] JSON序列化/反序列化方法实现

---

#### 任务1.5：创建Pydantic请求Schema（1小时）

**操作步骤**：

创建文件 `backend/app/schemas/glossary.py`：

```python
# backend/app/schemas/glossary.py
"""
术语库相关的Pydantic模式定义
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


# ==================== 术语库Schema ====================

class GlossaryCollectionBase(BaseModel):
    """术语库基础模式"""
    name: str = Field(..., min_length=1, max_length=100, description="术语库名称")
    description: Optional[str] = Field(None, description="术语库描述")
    icon: Optional[str] = Field(None, max_length=50, description="图标（emoji）")
    color: Optional[str] = Field(None, max_length=20, description="颜色代码")


class GlossaryCollectionCreate(GlossaryCollectionBase):
    """创建术语库请求模式"""
    pass


class GlossaryCollectionUpdate(GlossaryCollectionBase):
    """更新术语库请求模式"""
    is_enabled: Optional[bool] = Field(None, description="是否启用")


class GlossaryCollectionResponse(GlossaryCollectionBase):
    """术语库响应模式"""
    id: int
    is_enabled: bool
    term_count: int
    is_system: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GlossaryCollectionListResponse(BaseModel):
    """术语库列表响应模式"""
    items: List[GlossaryCollectionResponse]
    total: int
    page: int
    page_size: int


# ==================== 术语Schema ====================

class GlossaryTermBase(BaseModel):
    """术语基础模式"""
    term: str = Field(..., min_length=1, max_length=100, description="术语名称")
    synonyms: List[str] = Field(..., min_items=1, description="同义词列表")
    description: Optional[str] = Field(None, description="术语描述")
    examples: Optional[List[str]] = Field(None, description="示例用法")

    @validator('synonyms')
    def validate_synonyms(cls, v):
        """验证同义词列表"""
        if not v or len(v) == 0:
            raise ValueError('同义词列表不能为空')
        # 去重
        return list(set(v))


class GlossaryTermCreate(GlossaryTermBase):
    """创建术语请求模式"""
    pass


class GlossaryTermUpdate(BaseModel):
    """更新术语请求模式"""
    term: Optional[str] = Field(None, min_length=1, max_length=100, description="术语名称")
    synonyms: Optional[List[str]] = Field(None, min_items=1, description="同义词列表")
    description: Optional[str] = Field(None, description="术语描述")
    examples: Optional[List[str]] = Field(None, description="示例用法")
    is_enabled: Optional[bool] = Field(None, description="是否启用")


class GlossaryTermResponse(GlossaryTermBase):
    """术语响应模式"""
    id: int
    collection_id: int
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GlossaryTermListResponse(BaseModel):
    """术语列表响应模式"""
    collection_id: int
    collection_name: str
    items: List[GlossaryTermResponse]
    total: int
    page: int
    page_size: int


# ==================== 查询扩展Schema ====================

class GlossaryExpandRequest(BaseModel):
    """查询扩展请求模式"""
    query: str = Field(..., min_length=1, description="查询词")
    collection_ids: Optional[List[int]] = Field(None, description="术语库ID列表，null表示全部")


class MatchedTerm(BaseModel):
    """匹配的术语"""
    id: int
    term: str
    synonyms: List[str]
    collection_id: int
    collection_name: str


class GlossaryExpandResponse(BaseModel):
    """查询扩展响应模式"""
    original_query: str
    matched_terms: List[MatchedTerm]
    expanded_queries: List[str]
    used_collections: List[str]


# ==================== CSV导入导出Schema ====================

class GlossaryImportResponse(BaseModel):
    """CSV导入响应模式"""
    imported_count: int = Field(..., description="成功导入数量")
    failed_count: int = Field(..., description="失败数量")
    errors: List[dict] = Field(default_factory=list, description="错误详情")


# ==================== 用户设置Schema ====================

class GlossarySettingsUpdate(BaseModel):
    """术语库设置更新模式"""
    enable_expansion: bool = Field(..., description="是否启用术语扩展")
    default_mode: str = Field(..., pattern="^(all|custom)$", description="默认模式：all或custom")
    selected_collections: Optional[List[int]] = Field(None, description="选中的术语库ID列表（仅custom模式）")
```

**验证标准**：
- [ ] 所有请求Schema定义完整
- [ ] 所有响应Schema定义完整
- [ ] 字段验证规则完整
- [ ] 自定义验证器实现

---

#### 任务1.6：创建Pydantic响应Schema（0.5小时）

（已包含在任务1.5中）

---

#### 任务1.7：测试数据库表结构（0.25小时）

**操作步骤**：

```python
# backend/tests/test_glossary_models.py
"""
术语库模型测试
"""
import pytest
from sqlalchemy.orm import Session
from app.models.glossary_collection import GlossaryCollectionModel
from app.models.glossary_term import GlossaryTermModel
from app.core.database import SessionLocal


def test_create_collection():
    """测试创建术语库"""
    db: Session = SessionLocal()
    try:
        collection = GlossaryCollectionModel(
            name="测试术语库",
            description="这是一个测试术语库",
            icon="🧪",
            color="#FF0000"
        )
        db.add(collection)
        db.commit()
        db.refresh(collection)

        assert collection.id is not None
        assert collection.name == "测试术语库"
        assert collection.term_count == 0
        assert collection.is_enabled is True

    finally:
        db.close()


def test_create_term():
    """测试创建术语"""
    db: Session = SessionLocal()
    try:
        # 先创建术语库
        collection = GlossaryCollectionModel(name="测试术语库")
        db.add(collection)
        db.commit()
        db.refresh(collection)

        # 创建术语
        term = GlossaryTermModel(
            collection_id=collection.id,
            term="CT",
            synonyms='["计算机断层扫描", "CT扫描"]',
            description="计算机断层扫描"
        )
        db.add(term)
        db.commit()

        # 验证触发器自动更新term_count
        db.refresh(collection)
        assert collection.term_count == 1

    finally:
        db.close()


def test_unique_constraint():
    """测试唯一约束"""
    db: Session = SessionLocal()
    try:
        collection = GlossaryCollectionModel(name="测试术语库")
        db.add(collection)
        db.commit()

        # 尝试创建同名术语库
        duplicate = GlossaryCollectionModel(name="测试术语库")
        db.add(duplicate)
        
        with pytest.raises(Exception):  # Integri tyError
            db.commit()

    finally:
        db.close()
```

**运行测试**：

```bash
cd backend
pytest tests/test_glossary_models.py -v
```

**验证标准**：
- [ ] 能正常插入和查询数据
- [ ] 触发器自动更新term_count
- [ ] 级联删除正常工作
- [ ] 唯一约束正常工作

---

### 3.3 里程碑验收

**M1: 数据库与模型完成**

- [ ] 数据库迁移脚本执行成功
- [ ] glossary_collections表创建成功
- [ ] glossary_terms表创建成功
- [ ] 所有索引创建成功
- [ ] 所有触发器创建成功
- [ ] ORM模型定义完整
- [ ] Pydantic Schema定义完整
- [ ] 单元测试通过

---

## 4. 第二阶段：后端服务与API（3.5天）

### 4.1 阶段目标

实现术语库服务层、术语服务层、查询扩展服务层和所有API端点。

### 4.2 任务清单

#### 任务2.1：实现GlossaryCollectionService（2小时）

**操作步骤**：

创建文件 `backend/app/services/glossary_collection_service.py`：

```python
# backend/app/services/glossary_collection_service.py
"""
术语库集合服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.glossary_collection import GlossaryCollectionModel
from app.models.glossary_term import GlossaryTermModel
from app.schemas.glossary import (
    GlossaryCollectionCreate,
    GlossaryCollectionUpdate,
    GlossaryCollectionResponse,
    GlossaryCollectionListResponse
)
from app.core.logging_config import logger


class GlossaryCollectionService:
    """术语库集合服务"""

    def __init__(self, db: Session):
        self.db = db

    async def get_collections(
        self,
        page: int = 1,
        page_size: int = 20,
        is_enabled: Optional[bool] = None
    ) -> GlossaryCollectionListResponse:
        """
        获取术语库列表（分页）

        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            is_enabled: 是否启用（None=全部）

        Returns:
            GlossaryCollectionListResponse: 术语库列表响应
        """
        query = self.db.query(GlossaryCollectionModel)

        if is_enabled is not None:
            query = query.filter(GlossaryCollectionModel.is_enabled == is_enabled)

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return GlossaryCollectionListResponse(
            items=[GlossaryCollectionResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size
        )

    async def get_collection_by_id(self, collection_id: int) -> Optional[GlossaryCollectionResponse]:
        """
        根据ID获取术语库

        Args:
            collection_id: 术语库ID

        Returns:
            GlossaryCollectionResponse: 术语库响应，不存在返回None
        """
        collection = self.db.query(GlossaryCollectionModel).filter(
            GlossaryCollectionModel.id == collection_id
        ).first()

        if not collection:
            return None

        return GlossaryCollectionResponse.model_validate(collection)

    async def create_collection(
        self,
        data: GlossaryCollectionCreate
    ) -> GlossaryCollectionResponse:
        """
        创建术语库

        Args:
            data: 创建术语库请求

        Returns:
            GlossaryCollectionResponse: 创建的术语库响应

        Raises:
            ValueError: 名称已存在
        """
        # 检查名称是否已存在
        existing = self.db.query(GlossaryCollectionModel).filter(
            GlossaryCollectionModel.name == data.name
        ).first()

        if existing:
            raise ValueError(f"术语库名称 '{data.name}' 已存在")

        collection = GlossaryCollectionModel(
            name=data.name,
            description=data.description,
            icon=data.icon,
            color=data.color
        )

        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)

        logger.info(f"创建术语库成功: {collection.name} (ID: {collection.id})")
        return GlossaryCollectionResponse.model_validate(collection)

    async def update_collection(
        self,
        collection_id: int,
        data: GlossaryCollectionUpdate
    ) -> GlossaryCollectionResponse:
        """
        更新术语库

        Args:
            collection_id: 术语库ID
            data: 更新数据

        Returns:
            GlossaryCollectionResponse: 更新后的术语库响应

        Raises:
            ValueError: 术语库不存在或名称冲突
        """
        collection = self.db.query(GlossaryCollectionModel).filter(
            GlossaryCollectionModel.id == collection_id
        ).first()

        if not collection:
            raise ValueError(f"术语库 ID={collection_id} 不存在")

        # 如果修改名称，检查新名称是否冲突
        if data.name and data.name != collection.name:
            existing = self.db.query(GlossaryCollectionModel).filter(
                GlossaryCollectionModel.name == data.name,
                GlossaryCollectionModel.id != collection_id
            ).first()

            if existing:
                raise ValueError(f"术语库名称 '{data.name}' 已存在")

        # 更新字段
        if data.name is not None:
            collection.name = data.name
        if data.description is not None:
            collection.description = data.description
        if data.icon is not None:
            collection.icon = data.icon
        if data.color is not None:
            collection.color = data.color
        if data.is_enabled is not None:
            collection.is_enabled = data.is_enabled

        self.db.commit()
        self.db.refresh(collection)

        logger.info(f"更新术语库成功: {collection.name} (ID: {collection.id})")
        return GlossaryCollectionResponse.model_validate(collection)

    async def delete_collection(self, collection_id: int) -> bool:
        """
        删除术语库

        Args:
            collection_id: 术语库ID

        Returns:
            bool: 是否删除成功

        Raises:
            ValueError: 术语库不存在或为系统预置
        """
        collection = self.db.query(GlossaryCollectionModel).filter(
            GlossaryCollectionModel.id == collection_id
        ).first()

        if not collection:
            raise ValueError(f"术语库 ID={collection_id} 不存在")

        if collection.is_system:
            raise ValueError("系统预置术语库不可删除，只能禁用")

        # 级联删除术语（由外键ON DELETE CASCADE自动处理）
        self.db.delete(collection)
        self.db.commit()

        logger.info(f"删除术语库成功: {collection.name} (ID: {collection_id})")
        return True

    async def get_enabled_collections(self) -> List[GlossaryCollectionResponse]:
        """
        获取所有启用的术语库

        Returns:
            List[GlossaryCollectionResponse]: 启用的术语库列表
        """
        collections = self.db.query(GlossaryCollectionModel).filter(
            GlossaryCollectionModel.is_enabled == True
        ).all()

        return [GlossaryCollectionResponse.model_validate(c) for c in collections]
```

**验证标准**：
- [ ] get_collections()方法实现
- [ ] create_collection()方法实现
- [ ] update_collection()方法实现
- [ ] delete_collection()方法实现
- [ ] 包含分页支持
- [ ] 错误处理完整

---

#### 任务2.2：实现GlossaryTermService（3小时）

**操作步骤**：

创建文件 `backend/app/services/glossary_term_service.py`：

```python
# backend/app/services/glossary_term_service.py
"""
术语服务
"""
import csv
import io
import json
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.glossary_term import GlossaryTermModel
from app.models.glossary_collection import GlossaryCollectionModel
from app.schemas.glossary import (
    GlossaryTermCreate,
    GlossaryTermUpdate,
    GlossaryTermResponse,
    GlossaryTermListResponse,
    GlossaryImportResponse
)
from app.core.logging_config import logger


class GlossaryTermService:
    """术语服务"""

    def __init__(self, db: Session):
        self.db = db

    async def get_terms(
        self,
        collection_id: int,
        page: int = 1,
        page_size: int = 20,
        is_enabled: Optional[bool] = None
    ) -> GlossaryTermListResponse:
        """
        获取术语列表（分页）

        Args:
            collection_id: 术语库ID
            page: 页码（从1开始）
            page_size: 每页数量
            is_enabled: 是否启用（None=全部）

        Returns:
            GlossaryTermListResponse: 术语列表响应
        """
        # 获取术语库信息
        collection = self.db.query(GlossaryCollectionModel).filter(
            GlossaryCollectionModel.id == collection_id
        ).first()

        if not collection:
            raise ValueError(f"术语库 ID={collection_id} 不存在")

        # 查询术语
        query = self.db.query(GlossaryTermModel).filter(
            GlossaryTermModel.collection_id == collection_id
        )

        if is_enabled is not None:
            query = query.filter(GlossaryTermModel.is_enabled == is_enabled)

        total = query.count()
        items = query.order_by(GlossaryTermModel.term.asc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        return GlossaryTermListResponse(
            collection_id=collection_id,
            collection_name=collection.name,
            items=[GlossaryTermResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size
        )

    async def get_term_by_id(self, term_id: int) -> Optional[GlossaryTermResponse]:
        """
        根据ID获取术语

        Args:
            term_id: 术语ID

        Returns:
            GlossaryTermResponse: 术语响应，不存在返回None
        """
        term = self.db.query(GlossaryTermModel).filter(
            GlossaryTermModel.id == term_id
        ).first()

        if not term:
            return None

        return GlossaryTermResponse.model_validate(term)

    async def create_term(
        self,
        collection_id: int,
        data: GlossaryTermCreate
    ) -> GlossaryTermResponse:
        """
        创建术语

        Args:
            collection_id: 术语库ID
            data: 创建术语请求

        Returns:
            GlossaryTermResponse: 创建的术语响应

        Raises:
            ValueError: 术语库不存在或术语已存在
        """
        # 检查术语库是否存在
        collection = self.db.query(GlossaryCollectionModel).filter(
            GlossaryCollectionModel.id == collection_id
        ).first()

        if not collection:
            raise ValueError(f"术语库 ID={collection_id} 不存在")

        # 检查术语是否已存在
        existing = self.db.query(GlossaryTermModel).filter(
            GlossaryTermModel.collection_id == collection_id,
            GlossaryTermModel.term == data.term
        ).first()

        if existing:
            raise ValueError(f"术语 '{data.term}' 在术语库 '{collection.name}' 中已存在")

        term = GlossaryTermModel(
            collection_id=collection_id,
            term=data.term,
            synonyms=json.dumps(data.synonyms, ensure_ascii=False),
            description=data.description,
            examples=json.dumps(data.examples or [], ensure_ascii=False)
        )

        self.db.add(term)
        self.db.commit()
        self.db.refresh(term)

        logger.info(f"创建术语成功: {term.term} (ID: {term.id})")
        return GlossaryTermResponse.model_validate(term)

    async def update_term(
        self,
        collection_id: int,
        term_id: int,
        data: GlossaryTermUpdate
    ) -> GlossaryTermResponse:
        """
        更新术语

        Args:
            collection_id: 术语库ID
            term_id: 术语ID
            data: 更新数据

        Returns:
            GlossaryTermResponse: 更新后的术语响应

        Raises:
            ValueError: 术语不存在或术语名称冲突
        """
        term = self.db.query(GlossaryTermModel).filter(
            GlossaryTermModel.id == term_id,
            GlossaryTermModel.collection_id == collection_id
        ).first()

        if not term:
            raise ValueError(f"术语 ID={term_id} 不存在")

        # 如果修改术语名称，检查新名称是否冲突
        if data.term and data.term != term.term:
            existing = self.db.query(GlossaryTermModel).filter(
                GlossaryTermModel.collection_id == collection_id,
                GlossaryTermModel.term == data.term,
                GlossaryTermModel.id != term_id
            ).first()

            if existing:
                raise ValueError(f"术语 '{data.term}' 已存在")

        # 更新字段
        if data.term is not None:
            term.term = data.term
        if data.synonyms is not None:
            term.synonyms = json.dumps(data.synonyms, ensure_ascii=False)
        if data.description is not None:
            term.description = data.description
        if data.examples is not None:
            term.examples = json.dumps(data.examples, ensure_ascii=False)
        if data.is_enabled is not None:
            term.is_enabled = data.is_enabled

        self.db.commit()
        self.db.refresh(term)

        logger.info(f"更新术语成功: {term.term} (ID: {term.id})")
        return GlossaryTermResponse.model_validate(term)

    async def delete_term(self, collection_id: int, term_id: int) -> bool:
        """
        删除术语

        Args:
            collection_id: 术语库ID
            term_id: 术语ID

        Returns:
            bool: 是否删除成功

        Raises:
            ValueError: 术语不存在
        """
        term = self.db.query(GlossaryTermModel).filter(
            GlossaryTermModel.id == term_id,
            GlossaryTermModel.collection_id == collection_id
        ).first()

        if not term:
            raise ValueError(f"术语 ID={term_id} 不存在")

        self.db.delete(term)
        self.db.commit()

        logger.info(f"删除术语成功: {term.term} (ID: {term_id})")
        return True

    async def import_from_csv(
        self,
        collection_id: int,
        csv_content: str
    ) -> GlossaryImportResponse:
        """
        从CSV导入术语

        Args:
            collection_id: 术语库ID
            csv_content: CSV文件内容

        Returns:
            GlossaryImportResponse: 导入结果响应
        """
        # 检查术语库是否存在
        collection = self.db.query(GlossaryCollectionModel).filter(
            GlossaryCollectionModel.id == collection_id
        ).first()

        if not collection:
            raise ValueError(f"术语库 ID={collection_id} 不存在")

        # 解析CSV
        csv_file = io.StringIO(csv_content)
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
                if not synonyms:
                    raise ValueError("同义词不能为空")

                # 检查术语是否已存在
                existing = self.db.query(GlossaryTermModel).filter(
                    GlossaryTermModel.collection_id == collection_id,
                    GlossaryTermModel.term == term_name
                ).first()

                if existing:
                    errors.append({
                        "row": row_num,
                        "term": term_name,
                        "error": "术语已存在"
                    })
                    failed_count += 1
                    continue

                # 创建术语
                term = GlossaryTermModel(
                    collection_id=collection_id,
                    term=term_name,
                    synonyms=json.dumps(synonyms, ensure_ascii=False),
                    description=row.get("描述", "").strip()
                )
                self.db.add(term)
                imported_count += 1

            except Exception as e:
                errors.append({
                    "row": row_num,
                    "term": row.get("术语名称", ""),
                    "error": str(e)
                })
                failed_count += 1

        self.db.commit()

        logger.info(f"CSV导入完成: 成功{imported_count}条, 失败{failed_count}条")
        return GlossaryImportResponse(
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors
        )

    async def export_to_csv(self, collection_id: int) -> str:
        """
        导出术语为CSV

        Args:
            collection_id: 术语库ID

        Returns:
            str: CSV文件内容
        """
        # 检查术语库是否存在
        collection = self.db.query(GlossaryCollectionModel).filter(
            GlossaryCollectionModel.id == collection_id
        ).first()

        if not collection:
            raise ValueError(f"术语库 ID={collection_id} 不存在")

        # 查询所有术语
        terms = self.db.query(GlossaryTermModel).filter(
            GlossaryTermModel.collection_id == collection_id
        ).order_by(GlossaryTermModel.term.asc()).all()

        # 生成CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow(["术语名称", "同义词", "描述", "示例"])

        # 写入数据
        for term in terms:
            synonyms = term.get_synonyms_list()
            examples = term.get_examples_list()

            writer.writerow([
                term.term,
                ";".join(synonyms),
                term.description or "",
                ";".join(examples) if examples else ""
            ])

        csv_content = output.getvalue()
        logger.info(f"CSV导出完成: {collection.name}, 共{len(terms)}条术语")

        return csv_content
```

**验证标准**：
- [ ] get_terms()方法实现
- [ ] create_term()方法实现
- [ ] update_term()方法实现
- [ ] delete_term()方法实现
- [ ] import_from_csv()方法实现
- [ ] export_to_csv()方法实现

---

#### 任务2.3：实现GlossaryService（2小时）

**操作步骤**：

创建文件 `backend/app/services/glossary_service.py`：

```python
# backend/app/services/glossary_service.py
"""
术语匹配和扩展服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.glossary_term import GlossaryTermModel
from app.models.glossary_collection import GlossaryCollectionModel
from app.schemas.glossary import (
    GlossaryExpandRequest,
    GlossaryExpandResponse,
    MatchedTerm
)
from app.core.logging_config import logger


class GlossaryService:
    """术语匹配和扩展服务"""

    def __init__(self, db: Session):
        self.db = db

    async def expand_query(
        self,
        query: str,
        collection_ids: Optional[List[int]] = None
    ) -> GlossaryExpandResponse:
        """
        扩展查询词

        Args:
            query: 原始查询词
            collection_ids: 术语库ID列表，None表示全部

        Returns:
            GlossaryExpandResponse: 查询扩展响应
        """
        # 获取匹配的术语
        matched_terms = await self.match_terms(query, collection_ids)

        # 收集所有查询词
        expanded_queries = [query]
        collection_names = set()

        for term in matched_terms:
            expanded_queries.extend(term.synonyms)
            collection_names.add(term.collection_name)

        # 去重
        expanded_queries = list(set(expanded_queries))

        return GlossaryExpandResponse(
            original_query=query,
            matched_terms=matched_terms,
            expanded_queries=expanded_queries,
            used_collections=list(collection_names)
        )

    async def match_terms(
        self,
        query: str,
        collection_ids: Optional[List[int]] = None
    ) -> List[MatchedTerm]:
        """
        匹配查询中的术语

        Args:
            query: 查询词
            collection_ids: 术语库ID列表，None表示全部

        Returns:
            List[MatchedTerm]: 匹配的术语列表
        """
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

        # 模糊匹配（匹配术语名称或同义词）
        db_query = db_query.filter(
            (GlossaryTermModel.term.contains(query)) |
            (GlossaryTermModel.synonyms.contains(query))
        )

        results = db_query.all()

        # 解析结果
        matched_terms = []
        for row in results:
            import json
            synonyms = json.loads(row.synonyms) if isinstance(row.synonyms, str) else row.synonyms
            matched_terms.append(MatchedTerm(
                id=row.id,
                term=row.term,
                synonyms=synonyms,
                collection_id=row.collection_id,
                collection_name=row.collection_name
            ))

        logger.debug(f"查询 '{query}' 匹配到 {len(matched_terms)} 个术语")
        return matched_terms
```

**验证标准**：
- [ ] expand_query()方法实现
- [ ] match_terms()方法实现
- [ ] 查询逻辑正确
- [ ] 去重逻辑正确

---

由于篇幅限制，我将分多个部分继续编写实施方案。这是第一部分，包含了：

1. 实施概述
2. 实施阶段规划
3. 第一阶段：数据库与模型（详细步骤）
4. 第二阶段部分任务（后端服务与API）

是否继续编写剩余部分？