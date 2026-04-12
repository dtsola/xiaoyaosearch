"""
迁移脚本：删除 glossary_terms 表的 examples 列

执行方式：
    python -m migrations.drop_examples_column
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine, DATABASE_PATH
import logging

logger = logging.getLogger(__name__)


def migrate():
    """
    删除 glossary_terms 表的 examples 列

    由于SQLite不支持直接删除列，需要重建表
    """
    try:
        logger.info(f"开始迁移数据库: {DATABASE_PATH}")

        with engine.connect() as conn:
            # 1. 创建新表（不含examples列）
            logger.info("创建新表 glossary_terms_new...")
            conn.execute(text("""
                CREATE TABLE glossary_terms_new (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    collection_id INTEGER NOT NULL,
                    term VARCHAR(100) NOT NULL,
                    synonyms TEXT NOT NULL,
                    description TEXT,
                    is_enabled BOOLEAN NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    UNIQUE (collection_id, term),
                    FOREIGN KEY(collection_id) REFERENCES glossary_collections (id) ON DELETE CASCADE
                )
            """))

            # 2. 复制数据（排除examples列）
            logger.info("复制数据到新表...")
            conn.execute(text("""
                INSERT INTO glossary_terms_new (id, collection_id, term, synonyms, description, is_enabled, created_at, updated_at)
                SELECT id, collection_id, term, synonyms, description, is_enabled, created_at, updated_at
                FROM glossary_terms
            """))

            # 3. 删除旧表
            logger.info("删除旧表...")
            conn.execute(text("DROP TABLE glossary_terms"))

            # 4. 重命名新表
            logger.info("重命名新表...")
            conn.execute(text("ALTER TABLE glossary_terms_new RENAME TO glossary_terms"))

            # 5. 重建索引
            logger.info("重建索引...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_glossary_terms_collection_id ON glossary_terms (collection_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_glossary_terms_term ON glossary_terms (term)"))

            conn.commit()

        logger.info("✅ 数据库迁移完成！已删除 glossary_terms.examples 列")

    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {str(e)}")
        raise


if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 确认操作
    print(f"⚠️  即将修改数据库: {DATABASE_PATH}")
    print("📋 操作内容：删除 glossary_terms 表的 examples 列")
    print("💡 建议：先备份数据库文件")

    response = input("是否继续？(yes/no): ").strip().lower()
    if response == 'yes':
        migrate()
    else:
        print("❌ 已取消迁移操作")
