#!/usr/bin/env python3
"""
测试数据库表结构创建
"""
import os
import sys

# 确保当前目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("开始测试数据库表结构创建...")

    # 1. 导入必要的模块
    from app.core.database import engine, Base
    print("导入数据库模块")

    # 2. 导入所有模型
    from app.models.file import FileModel
    from app.models.file_content import FileContentModel
    from app.models.search_history import SearchHistoryModel
    from app.models.ai_model import AIModelModel
    from app.models.index_job import IndexJobModel
    print("导入所有模型")

    # 3. 检查FileModel字段
    print(f"FileModel字段数量: {len(FileModel.__table__.columns)}")
    for col in FileModel.__table__.columns:
        print(f"  - {col.name}: {col.type}")

    # 4. 检查Base.metadata中的表
    print(f"Base.metadata中的表数量: {len(Base.metadata.tables)}")
    for table_name in Base.metadata.tables:
        print(f"  - {table_name}")

    # 5. 删除并重新创建数据库
    db_path = "../data/database/xiaoyao_search.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("删除旧数据库文件")

    print("创建新的数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

    # 6. 验证实际数据库表结构
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"数据库中的表数量: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")

    # 检查files表结构
    cursor.execute("PRAGMA table_info(files)")
    columns = cursor.fetchall()
    print(f"files表字段数量: {len(columns)}")
    for col in columns:
        print(f"  - {col[1]}: {col[2]}")

    conn.close()
    print("数据库验证完成")

if __name__ == "__main__":
    main()