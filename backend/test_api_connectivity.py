"""
文件索引系统API连通性测试

测试文件索引系统的所有API接口，验证接口的连通性和基本功能。
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
import logging
import json
import requests
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.file_scanner import FileScanner
from app.core.database import SessionLocal, init_database
from app.models.file import FileModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APITestClient:
    """API测试客户端"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def test_health_check(self) -> bool:
        """测试系统健康检查接口"""
        logger.info("测试系统健康检查接口")
        try:
            response = self.session.get(f"{self.base_url}/api/system/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 健康检查成功: {data}")
                return True
            else:
                logger.error(f"❌ 健康检查失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 健康检查异常: {e}")
            return False

    def test_index_status(self) -> bool:
        """测试索引系统状态接口"""
        logger.info("测试索引系统状态接口")
        try:
            response = self.session.get(f"{self.base_url}/api/index/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 索引状态查询成功")
                logger.info(f"  索引统计: {data.get('data', {}).get('index_stats', {})}")
                logger.info(f"  支持格式: {len(data.get('data', {}).get('supported_formats', {}).get('parser_formats', []))}")
                return True
            else:
                logger.error(f"❌ 索引状态查询失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 索引状态查询异常: {e}")
            return False

    def test_create_index(self, test_dir: str) -> bool:
        """测试创建索引接口"""
        logger.info(f"测试创建索引接口: {test_dir}")
        try:
            payload = {
                "folder_path": test_dir,
                "recursive": True
            }
            response = self.session.post(f"{self.base_url}/api/index/create", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 创建索引请求成功")
                logger.info(f"  任务ID: {data.get('data', {}).get('index_id')}")
                logger.info(f"  状态: {data.get('data', {}).get('status')}")
                return True
            else:
                logger.error(f"❌ 创建索引失败: HTTP {response.status_code}")
                if response.text:
                    logger.error(f"  错误信息: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ 创建索引异常: {e}")
            return False

    def test_index_list(self) -> bool:
        """测试索引列表接口"""
        logger.info("测试索引列表接口")
        try:
            response = self.session.get(f"{self.base_url}/api/index/list?limit=5", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 索引列表查询成功")
                logger.info(f"  返回数量: {len(data.get('data', {}).get('indexes', []))}")
                return True
            else:
                logger.error(f"❌ 索引列表查询失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 索引列表查询异常: {e}")
            return False

    def test_indexed_files(self) -> bool:
        """测试已索引文件列表接口"""
        logger.info("测试已索引文件列表接口")
        try:
            response = self.session.get(f"{self.base_url}/api/index/files?limit=5", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 已索引文件列表查询成功")
                logger.info(f"  文件数量: {data.get('data', {}).get('total', 0)}")
                return True
            else:
                logger.error(f"❌ 已索引文件列表查询失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 已索引文件列表查询异常: {e}")
            return False

    def test_backup_index(self) -> bool:
        """测试索引备份接口"""
        logger.info("测试索引备份接口")
        try:
            payload = {"backup_name": f"test_backup_{asyncio.get_event_loop().time()}"}
            response = self.session.post(f"{self.base_url}/api/index/backup", json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ 索引备份成功")
                logger.info(f"  备份路径: {data.get('data', {}).get('backup_path', 'N/A')}")
                return True
            else:
                logger.error(f"❌ 索引备份失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 索引备份异常: {e}")
            return False


def create_test_files(test_dir: Path) -> list[Path]:
    """创建测试文件"""
    test_files = []

    # 创建文本文档
    txt_file = test_dir / "api_test_document.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("这是一个API测试文档。\n")
        f.write("用于测试文件索引系统的API接口功能。\n")
        f.write("包含中文内容用于测试索引和搜索功能。")
    test_files.append(txt_file)

    # 创建Markdown文档
    md_file = test_dir / "api_test_markdown.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# API测试Markdown文档\n\n")
        f.write("这是一个用于测试API功能的Markdown文档。\n\n")
        f.write("## 功能特点\n")
        f.write("- API连通性测试\n")
        f.write("- 索引功能验证\n")
        f.write("- 搜索服务测试")
    test_files.append(md_file)

    logger.info(f"创建了 {len(test_files)} 个API测试文件")
    return test_files


def setup_database():
    """初始化数据库表结构"""
    logger.info("初始化数据库表结构")
    try:
        init_database()
        logger.info("✅ 数据库表结构创建成功")
        return True
    except Exception as e:
        logger.error(f"❌ 数据库表结构创建失败: {e}")
        return False


async def run_api_tests():
    """运行API连通性测试"""
    logger.info("开始文件索引系统API连通性测试")

    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        logger.info(f"创建临时测试目录: {test_dir}")

        try:
            # 1. 初始化数据库
            if not setup_database():
                return False

            # 2. 创建测试文件
            test_files = create_test_files(test_dir)

            # 3. 等待后端服务启动
            logger.info("等待后端服务启动...")
            import time
            time.sleep(3)

            # 4. 创建API测试客户端
            api_client = APITestClient()

            # 5. 运行API测试
            test_results = []

            # 基础连通性测试
            test_results.append(("系统健康检查", api_client.test_health_check()))
            test_results.append(("索引系统状态", api_client.test_index_status()))

            # 功能接口测试
            test_results.append(("创建索引", api_client.test_create_index(str(test_dir))))
            test_results.append(("索引列表", api_client.test_index_list()))
            test_results.append(("已索引文件列表", api_client.test_indexed_files()))

            # 管理接口测试
            test_results.append(("索引备份", api_client.test_backup_index()))

            # 输出测试结果
            logger.info("\n" + "="*50)
            logger.info("API连通性测试结果汇总:")
            logger.info("="*50)

            all_passed = True
            for test_name, result in test_results:
                status = "✅ 通过" if result else "❌ 失败"
                logger.info(f"{test_name:20} {status}")
                if not result:
                    all_passed = False

            logger.info("="*50)

            if all_passed:
                logger.info("🎉 所有API连通性测试通过！")
                logger.info("📝 注意：实际的索引执行是后台异步任务，需要稍等片刻完成。")
                logger.info("📋 建议：检查索引任务状态确认索引构建是否成功。")
                return True
            else:
                logger.error("❌ 部分API测试失败，请检查后端服务状态。")
                return False

        except Exception as e:
            logger.error(f"API测试过程中发生异常: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    logger.info("文件索引系统API连通性测试")
    logger.info("="*50)

    # 检查环境
    if os.name == 'nt':  # Windows
        logger.info("检测到Windows环境")
    else:
        logger.info("检测到Linux/Unix环境")

    logger.info("请确保后端服务已启动:")
    logger.info("1. cd backend")
    logger.info("2. ./venv/Scripts/python.exe main.py")
    logger.info("")
    logger.info("等待3秒后开始API测试...")

    import time
    time.sleep(3)

    # 运行测试
    try:
        result = asyncio.run(run_api_tests())
        return result
    except KeyboardInterrupt:
        logger.info("用户中断测试")
        return False
    except Exception as e:
        logger.error(f"测试执行异常: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)