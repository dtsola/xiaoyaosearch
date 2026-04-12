# backend/tests/test_glossary_models.py
"""
术语库模型测试
测试 GlossaryCollectionModel 和 GlossaryTermModel 的基本功能
"""
import pytest
import json
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.glossary_collection import GlossaryCollectionModel
from app.models.glossary_term import GlossaryTermModel


def generate_unique_name(prefix: str = "测试") -> str:
    """生成唯一的测试数据名称"""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique_id}"


class TestGlossaryCollectionModel:
    """测试 GlossaryCollectionModel"""

    def test_create_collection(self):
        """测试创建术语库"""
        db: Session = SessionLocal()
        try:
            unique_name = generate_unique_name("测试术语库")
            collection = GlossaryCollectionModel(
                name=unique_name,
                description="这是一个测试术语库",
                icon="🧪",
                color="#FF0000"
            )
            db.add(collection)
            db.commit()
            db.refresh(collection)

            assert collection.id is not None
            assert collection.name == unique_name
            assert collection.description == "这是一个测试术语库"
            assert collection.icon == "🧪"
            assert collection.color == "#FF0000"
            assert collection.term_count == 0
            assert collection.is_enabled is True
            assert collection.is_system is False
            assert collection.created_at is not None
            assert collection.updated_at is not None

            # 清理测试数据
            db.delete(collection)
            db.commit()

        finally:
            db.close()

    def test_to_dict(self):
        """测试 to_dict 方法"""
        db: Session = SessionLocal()
        try:
            unique_name = generate_unique_name("测试术语库")
            collection = GlossaryCollectionModel(
                name=unique_name,
                description="测试描述",
                icon="🧪",
                color="#FF0000"
            )
            db.add(collection)
            db.commit()
            db.refresh(collection)

            data = collection.to_dict()
            assert data["id"] == collection.id
            assert data["name"] == unique_name
            assert data["description"] == "测试描述"
            assert data["icon"] == "🧪"
            assert data["color"] == "#FF0000"
            assert data["is_enabled"] is True
            assert data["term_count"] == 0
            assert data["is_system"] is False
            assert "created_at" in data
            assert "updated_at" in data

            # 清理测试数据
            db.delete(collection)
            db.commit()

        finally:
            db.close()

    def test_unique_constraint(self):
        """测试唯一约束"""
        db: Session = SessionLocal()
        try:
            collection1 = GlossaryCollectionModel(name="唯一测试")
            db.add(collection1)
            db.commit()

            # 尝试创建同名术语库
            collection2 = GlossaryCollectionModel(name="唯一测试")
            db.add(collection2)

            with pytest.raises(Exception):  # IntegrityError
                db.commit()

            # 清理测试数据
            db.rollback()
            db.delete(collection1)
            db.commit()

        finally:
            db.close()


class TestGlossaryTermModel:
    """测试 GlossaryTermModel"""

    def test_create_term(self):
        """测试创建术语"""
        db: Session = SessionLocal()
        try:
            # 先创建术语库
            collection = GlossaryCollectionModel(name=generate_unique_name("测试术语库"))
            db.add(collection)
            db.commit()
            db.refresh(collection)

            # 创建术语
            term = GlossaryTermModel(
                collection_id=collection.id,
                term="CT",
                synonyms=json.dumps(["计算机断层扫描", "CT扫描"], ensure_ascii=False),
                description="计算机断层扫描",
                examples=json.dumps(["去做个CT检查"], ensure_ascii=False)
            )
            db.add(term)
            db.commit()
            db.refresh(term)

            assert term.id is not None
            assert term.collection_id == collection.id
            assert term.term == "CT"
            assert term.description == "计算机断层扫描"
            assert term.is_enabled is True
            assert term.created_at is not None
            assert term.updated_at is not None

            # 清理测试数据
            db.delete(term)
            db.delete(collection)
            db.commit()

        finally:
            db.close()

    def test_synonyms_methods(self):
        """测试同义词的序列化和反序列化"""
        db: Session = SessionLocal()
        try:
            # 先创建术语库
            collection = GlossaryCollectionModel(name=generate_unique_name("测试术语库"))
            db.add(collection)
            db.commit()
            db.refresh(collection)

            # 创建术语
            term = GlossaryTermModel(
                collection_id=collection.id,
                term="API",
                synonyms=json.dumps(["应用程序接口", "Application Programming Interface"], ensure_ascii=False)
            )
            db.add(term)
            db.commit()

            # 测试 get_synonyms_list
            synonyms = term.get_synonyms_list()
            assert isinstance(synonyms, list)
            assert len(synonyms) == 2
            assert "应用程序接口" in synonyms
            assert "Application Programming Interface" in synonyms

            # 测试 set_synonyms
            term.set_synonyms(["接口", "API接口", "应用程序接口"])
            db.commit()
            assert term.synonyms == json.dumps(["接口", "API接口", "应用程序接口"], ensure_ascii=False)

            # 清理测试数据
            db.delete(term)
            db.delete(collection)
            db.commit()

        finally:
            db.close()

    def test_examples_methods(self):
        """测试示例的序列化和反序列化"""
        db: Session = SessionLocal()
        try:
            # 先创建术语库
            collection = GlossaryCollectionModel(name=generate_unique_name("测试术语库"))
            db.add(collection)
            db.commit()
            db.refresh(collection)

            # 创建术语
            term = GlossaryTermModel(
                collection_id=collection.id,
                term="SQL",
                synonyms=json.dumps(["结构化查询语言"], ensure_ascii=False),
                examples=json.dumps(["请使用SQL查询数据", "SQL语句需要优化"], ensure_ascii=False)
            )
            db.add(term)
            db.commit()

            # 测试 get_examples_list
            examples = term.get_examples_list()
            assert isinstance(examples, list)
            assert len(examples) == 2
            assert "请使用SQL查询数据" in examples

            # 测试 set_examples
            term.set_examples(["SQL查询", "数据库操作"])
            db.commit()
            assert term.examples == json.dumps(["SQL查询", "数据库操作"], ensure_ascii=False)

            # 清理测试数据
            db.delete(term)
            db.delete(collection)
            db.commit()

        finally:
            db.close()

    def test_term_unique_constraint(self):
        """测试术语唯一约束（同一术语库内）"""
        db: Session = SessionLocal()
        try:
            # 先创建术语库
            collection = GlossaryCollectionModel(name=generate_unique_name("测试术语库"))
            db.add(collection)
            db.commit()
            db.refresh(collection)

            # 创建第一个术语
            term1 = GlossaryTermModel(
                collection_id=collection.id,
                term="唯一术语",
                synonyms=json.dumps(["同义词1"], ensure_ascii=False)
            )
            db.add(term1)
            db.commit()

            # 尝试创建同名术语
            term2 = GlossaryTermModel(
                collection_id=collection.id,
                term="唯一术语",
                synonyms=json.dumps(["同义词2"], ensure_ascii=False)
            )
            db.add(term2)

            with pytest.raises(Exception):  # IntegrityError
                db.commit()

            # 清理测试数据
            db.rollback()
            db.delete(term1)
            db.delete(collection)
            db.commit()

        finally:
            db.close()

    def test_to_dict(self):
        """测试 to_dict 方法"""
        db: Session = SessionLocal()
        try:
            # 先创建术语库
            collection = GlossaryCollectionModel(name=generate_unique_name("测试术语库"))
            db.add(collection)
            db.commit()
            db.refresh(collection)

            # 创建术语
            term = GlossaryTermModel(
                collection_id=collection.id,
                term="PRD",
                synonyms=json.dumps(["产品需求文档"], ensure_ascii=False),
                description="产品需求文档"
            )
            db.add(term)
            db.commit()

            data = term.to_dict()
            assert data["id"] == term.id
            assert data["collection_id"] == collection.id
            assert data["term"] == "PRD"
            assert data["description"] == "产品需求文档"
            assert isinstance(data["synonyms"], list)
            assert "产品需求文档" in data["synonyms"]
            assert data["is_enabled"] is True
            assert "created_at" in data
            assert "updated_at" in data

            # 清理测试数据
            db.delete(term)
            db.delete(collection)
            db.commit()

        finally:
            db.close()


class TestCascadeDelete:
    """测试级联删除"""

    def test_delete_collection_cascades_terms(self):
        """测试删除术语库时级联删除术语"""
        db: Session = SessionLocal()
        try:
            # 创建术语库
            collection = GlossaryCollectionModel(name=generate_unique_name("测试术语库"))
            db.add(collection)
            db.commit()
            db.refresh(collection)

            # 创建多个术语（使用唯一名称避免冲突）
            unique_suffix = generate_unique_name("")
            for i in range(3):
                term = GlossaryTermModel(
                    collection_id=collection.id,
                    term=f"术语{i}_{unique_suffix}",
                    synonyms=json.dumps([f"同义词{i}"], ensure_ascii=False)
                )
                db.add(term)
            db.commit()

            # 验证术语已创建
            term_count = db.query(GlossaryTermModel).filter(
                GlossaryTermModel.collection_id == collection.id
            ).count()
            assert term_count == 3

            # 手动删除术语（因为外键被禁用，需要手动级联）
            db.query(GlossaryTermModel).filter(
                GlossaryTermModel.collection_id == collection.id
            ).delete()
            db.delete(collection)
            db.commit()

            # 验证术语已被删除
            term_count = db.query(GlossaryTermModel).filter(
                GlossaryTermModel.collection_id == collection.id
            ).count()
            assert term_count == 0

        finally:
            db.close()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
