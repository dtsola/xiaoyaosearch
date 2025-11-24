"""
索引任务数据模型
定义文件索引任务的数据库表结构
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime


class IndexJobModel(Base):
    """
    索引任务表模型

    管理文件索引任务的创建和执行状态
    """
    __tablename__ = "index_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    folder_path = Column(String(1000), nullable=False, comment="索引文件夹路径")
    job_type = Column(String(20), nullable=False, comment="任务类型(create/update/rebuild/delete)")
    status = Column(String(20), nullable=False, default="pending", comment="任务状态(pending/processing/completed/failed)")
    total_files = Column(Integer, default=0, comment="总文件数")
    processed_files = Column(Integer, default=0, comment="已处理文件数")
    error_count = Column(Integer, default=0, comment="错误文件数")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    error_message = Column(Text, nullable=True, comment="错误信息")
    created_at = Column(DateTime, nullable=False, default=func.now(), comment="创建时间")

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 索引任务字典
        """
        # 计算进度百分比
        progress = 0
        if self.total_files > 0:
            progress = int((self.processed_files / self.total_files) * 100)

        return {
            "index_id": self.id,
            "folder_path": self.folder_path,
            "job_type": self.job_type,
            "status": self.status,
            "progress": progress,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "error_count": self.error_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def get_job_types(cls) -> list:
        """
        获取支持的任务类型

        Returns:
            list: 支持的任务类型列表
        """
        return ["create", "update", "rebuild", "delete"]

    @classmethod
    def get_job_statuses(cls) -> list:
        """
        获取支持的任务状态

        Returns:
            list: 支持的任务状态列表
        """
        return ["pending", "processing", "completed", "failed"]

    def start_job(self) -> None:
        """开始任务"""
        self.status = "processing"
        self.started_at = datetime.now()

    def complete_job(self) -> None:
        """完成任务"""
        self.status = "completed"
        self.completed_at = datetime.now()

    def fail_job(self, error_message: str) -> None:
        """任务失败"""
        self.status = "failed"
        self.completed_at = datetime.now()
        self.error_message = error_message

    def update_progress(self, processed_files: int, error_count: int = None) -> None:
        """
        更新任务进度

        Args:
            processed_files: 已处理文件数
            error_count: 错误文件数（可选）
        """
        self.processed_files = processed_files
        if error_count is not None:
            self.error_count = error_count

    def get_duration(self) -> float:
        """
        获取任务执行时长（秒）

        Returns:
            float: 执行时长，如果任务未开始则返回0
        """
        if not self.started_at:
            return 0.0

        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()

    def __repr__(self) -> str:
        """模型字符串表示"""
        return f"<IndexJobModel(id={self.id}, type={self.job_type}, status={self.status})>"