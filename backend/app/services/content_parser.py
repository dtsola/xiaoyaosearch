"""
内容解析器

从各种文件格式中提取文本内容，支持文档、图片、音视频等多种格式。
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
from dataclasses import dataclass

# 文件处理库导入
try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False
    logging.warning("chardet未安装，编码检测功能不可用")

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2未安装，PDF内容提取功能不可用")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx未安装，Word文档内容提取功能不可用")

try:
    from openpyxl import load_workbook
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    logging.warning("openpyxl未安装，Excel文档内容提取功能不可用")

try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False
    logging.warning("python-pptx未安装，PowerPoint文档内容提取功能不可用")

logger = logging.getLogger(__name__)


@dataclass
class ParsedContent:
    """解析后的内容数据类"""
    text: str
    title: Optional[str] = None
    language: Optional[str] = None
    encoding: Optional[str] = None
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class ContentParser:
    """内容解析器

    支持从各种文件格式中提取文本内容：
    - 文档类：PDF、Word、Excel、PowerPoint
    - 文本类：TXT、Markdown、代码文件
    - 预留接口：音视频转文字、图片OCR
    """

    def __init__(self, max_content_length: int = 1024 * 1024):  # 1MB
        """初始化内容解析器

        Args:
            max_content_length: 最大内容长度限制（字符数）
        """
        self.max_content_length = max_content_length
        self.supported_formats = {
            '.pdf': self._parse_pdf,
            '.docx': self._parse_docx,
            '.xlsx': self._parse_excel,
            '.pptx': self._parse_pptx,
            '.txt': self._parse_text,
            '.md': self._parse_markdown,
            '.rtf': self._parse_text,  # 简化处理
            '.py': self._parse_code,
            '.js': self._parse_code,
            '.ts': self._parse_code,
            '.html': self._parse_html,
            '.css': self._parse_code,
            '.java': self._parse_code,
            '.cpp': self._parse_code,
            '.c': self._parse_code,
            '.go': self._parse_code,
            '.rs': self._parse_code,
            '.php': self._parse_code,
            '.rb': self._parse_code,
            '.swift': self._parse_code,
            '.kt': self._parse_code,
        }

        # 编码检测优先级
        self.encoding_priority = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin-1', 'ascii']

    def parse_content(self, file_path: str) -> ParsedContent:
        """解析文件内容

        Args:
            file_path: 文件路径

        Returns:
            ParsedContent: 解析后的内容
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 根据文件扩展名选择解析方法
            extension = path.suffix.lower()
            parser_func = self.supported_formats.get(extension)

            if not parser_func:
                logger.warning(f"不支持的文件格式: {extension}")
                return ParsedContent(
                    text="",
                    error=f"不支持的文件格式: {extension}"
                )

            # 执行解析
            parsed_content = parser_func(path)

            # 内容长度限制
            if len(parsed_content.text) > self.max_content_length:
                parsed_content.text = parsed_content.text[:self.max_content_length]
                parsed_content.text += "\n... [内容被截断]"

            # 语言检测（简化版）
            if not parsed_content.language:
                parsed_content.language = self._detect_language(parsed_content.text)

            return parsed_content

        except Exception as e:
            logger.error(f"解析文件内容失败 {file_path}: {e}")
            return ParsedContent(text="", error=str(e))

    def _parse_pdf(self, path: Path) -> ParsedContent:
        """解析PDF文件内容"""
        if not PDF_AVAILABLE:
            return ParsedContent(text="", error="PDF解析库不可用")

        try:
            text_parts = []
            title = None

            with open(path, 'rb') as file:
                reader = PdfReader(file)

                # 尝试提取标题
                if reader.metadata and reader.metadata.get('/Title'):
                    title = reader.metadata.get('/Title')

                # 提取每一页的文本
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_parts.append(f"[页面 {page_num + 1}]\n{page_text}")
                    except Exception as e:
                        logger.warning(f"提取PDF第{page_num + 1}页内容失败: {e}")

            text = "\n\n".join(text_parts)

            return ParsedContent(
                text=text,
                title=title,
                language=self._detect_language(text),
                confidence=0.8 if text else 0.0
            )

        except Exception as e:
            logger.error(f"解析PDF文件失败 {path}: {e}")
            return ParsedContent(text="", error=str(e))

    def _parse_docx(self, path: Path) -> ParsedContent:
        """解析Word文档内容"""
        if not DOCX_AVAILABLE:
            return ParsedContent(text="", error="Word文档解析库不可用")

        try:
            doc = Document(str(path))

            # 提取标题
            title = None
            if doc.core_properties.title:
                title = doc.core_properties.title
            elif doc.paragraphs and doc.paragraphs[0].text.strip():
                # 使用第一段作为标题
                title = doc.paragraphs[0].text.strip()

            # 提取段落文本
            paragraph_texts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraph_texts.append(para.text)

            # 提取表格内容
            table_texts = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        table_texts.append(" | ".join(row_text))

            # 组合文本
            text_parts = []
            if paragraph_texts:
                text_parts.extend(paragraph_texts)
            if table_texts:
                text_parts.append("\n[表格内容]\n" + "\n".join(table_texts))

            text = "\n\n".join(text_parts)

            return ParsedContent(
                text=text,
                title=title,
                language=self._detect_language(text),
                confidence=0.9 if text else 0.0
            )

        except Exception as e:
            logger.error(f"解析Word文档失败 {path}: {e}")
            return ParsedContent(text="", error=str(e))

    def _parse_excel(self, path: Path) -> ParsedContent:
        """解析Excel文件内容"""
        if not EXCEL_AVAILABLE:
            return ParsedContent(text="", error="Excel解析库不可用")

        try:
            workbook = load_workbook(str(path), read_only=True)
            text_parts = []

            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                sheet_data = []

                for row in sheet.iter_rows(values_only=True):
                    # 过滤空行
                    if any(cell is not None and str(cell).strip() for cell in row):
                        row_text = []
                        for cell in row:
                            if cell is not None:
                                cell_str = str(cell).strip()
                                if cell_str:
                                    row_text.append(cell_str)
                        if row_text:
                            sheet_data.append(" | ".join(row_text))

                if sheet_data:
                    text_parts.append(f"[工作表: {sheet_name}]\n" + "\n".join(sheet_data))

            text = "\n\n".join(text_parts)

            return ParsedContent(
                text=text,
                title=f"Excel文档 - {path.name}",
                language=self._detect_language(text),
                confidence=0.8 if text else 0.0
            )

        except Exception as e:
            logger.error(f"解析Excel文件失败 {path}: {e}")
            return ParsedContent(text="", error=str(e))

    def _parse_pptx(self, path: Path) -> ParsedContent:
        """解析PowerPoint文档内容"""
        if not PPTX_AVAILABLE:
            return ParsedContent(text="", error="PowerPoint解析库不可用")

        try:
            prs = Presentation(str(path))
            slide_texts = []

            for slide_num, slide in enumerate(prs.slides):
                slide_content = []

                # 提取幻灯片标题和内容
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_content.append(shape.text.strip())

                if slide_content:
                    slide_texts.append(f"[幻灯片 {slide_num + 1}]\n" + "\n".join(slide_content))

            text = "\n\n".join(slide_texts)

            # 提取标题
            title = None
            if prs.core_properties.title:
                title = prs.core_properties.title
            elif slide_texts:
                # 使用第一张幻灯片的内容作为标题
                first_slide = slide_texts[0].split('\n', 1)[1].split('\n')[0] if '\n' in slide_texts[0] else ""
                title = first_slide.strip()

            return ParsedContent(
                text=text,
                title=title,
                language=self._detect_language(text),
                confidence=0.8 if text else 0.0
            )

        except Exception as e:
            logger.error(f"解析PowerPoint文档失败 {path}: {e}")
            return ParsedContent(text="", error=str(e))

    def _parse_text(self, path: Path) -> ParsedContent:
        """解析纯文本文件"""
        try:
            content, encoding = self._read_text_file(path)

            if not content:
                return ParsedContent(text="", title=path.name, confidence=0.0)

            # 尝试提取标题（第一行）
            lines = content.split('\n')
            title = lines[0].strip() if lines and lines[0].strip() else path.name

            return ParsedContent(
                text=content,
                title=title,
                language=self._detect_language(content),
                encoding=encoding,
                confidence=0.9 if content else 0.0
            )

        except Exception as e:
            logger.error(f"解析文本文件失败 {path}: {e}")
            return ParsedContent(text="", error=str(e))

    def _parse_markdown(self, path: Path) -> ParsedContent:
        """解析Markdown文件"""
        try:
            content, encoding = self._read_text_file(path)

            if not content:
                return ParsedContent(text="", title=path.name, confidence=0.0)

            # 提取Markdown标题
            title = self._extract_markdown_title(content)

            # 清理Markdown语法
            clean_text = self._clean_markdown(content)

            return ParsedContent(
                text=clean_text,
                title=title,
                language=self._detect_language(content),
                encoding=encoding,
                confidence=0.9 if content else 0.0
            )

        except Exception as e:
            logger.error(f"解析Markdown文件失败 {path}: {e}")
            return ParsedContent(text="", error=str(e))

    def _parse_code(self, path: Path) -> ParsedContent:
        """解析代码文件"""
        try:
            content, encoding = self._read_text_file(path)

            if not content:
                return ParsedContent(text="", title=path.name, confidence=0.0)

            # 提取注释和文档字符串
            code_content = self._extract_code_comments(path.suffix, content)

            return ParsedContent(
                text=code_content,
                title=path.name,
                language=self._detect_language(content),
                encoding=encoding,
                confidence=0.7 if code_content else 0.0
            )

        except Exception as e:
            logger.error(f"解析代码文件失败 {path}: {e}")
            return ParsedContent(text="", error=str(e))

    def _parse_html(self, path: Path) -> ParsedContent:
        """解析HTML文件"""
        try:
            content, encoding = self._read_text_file(path)

            if not content:
                return ParsedContent(text="", title=path.name, confidence=0.0)

            # 简单的HTML标签清理
            clean_text = re.sub(r'<[^>]+>', ' ', content)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()

            # 提取title标签
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else path.name

            return ParsedContent(
                text=clean_text,
                title=title,
                language=self._detect_language(clean_text),
                encoding=encoding,
                confidence=0.6 if clean_text else 0.0
            )

        except Exception as e:
            logger.error(f"解析HTML文件失败 {path}: {e}")
            return ParsedContent(text="", error=str(e))

    def _read_text_file(self, path: Path) -> tuple[str, Optional[str]]:
        """读取文本文件，自动检测编码"""
        encodings_to_try = self.encoding_priority.copy()

        # 如果有chardet，先检测编码
        if CHARDET_AVAILABLE:
            try:
                with open(path, 'rb') as f:
                    raw_data = f.read(10240)  # 读取前10KB进行检测
                result = chardet.detect(raw_data)
                if result and result['confidence'] > 0.7:
                    detected_encoding = result['encoding']
                    if detected_encoding and detected_encoding not in encodings_to_try:
                        encodings_to_try.insert(0, detected_encoding)
            except Exception as e:
                logger.warning(f"编码检测失败 {path}: {e}")

        # 尝试不同编码读取文件
        for encoding in encodings_to_try:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content, encoding
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"读取文件失败 {path} (编码: {encoding}): {e}")
                continue

        # 如果所有编码都失败，使用默认编码并忽略错误
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content, 'utf-8'
        except Exception as e:
            logger.error(f"读取文件完全失败 {path}: {e}")
            return "", None

    def _extract_markdown_title(self, content: str) -> str:
        """从Markdown内容中提取标题"""
        lines = content.split('\n')

        # 查找一级标题
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()

        # 如果没有一级标题，使用第一行非空文本
        for line in lines:
            if line.strip():
                return line.strip()

        return ""

    def _clean_markdown(self, content: str) -> str:
        """清理Markdown语法，保留纯文本"""
        # 移除代码块
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        # 移除行内代码
        content = re.sub(r'`([^`]+)`', r'\1', content)
        # 移除标题标记
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        # 移除粗体和斜体标记
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        # 移除链接
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        # 移除图片
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', content)
        # 移除列表标记
        content = re.sub(r'^\s*[-*+]\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*\d+\.\s*', '', content, flags=re.MULTILINE)
        # 清理多余空白
        content = re.sub(r'\n\s*\n', '\n\n', content)

        return content.strip()

    def _extract_code_comments(self, extension: str, content: str) -> str:
        """从代码中提取注释和文档字符串"""
        lines = content.split('\n')
        comments = []

        # 不同语言的注释模式
        comment_patterns = {
            '.py': [
                r'^\s*"""[^"]*"""',  # 多行文档字符串
                r'^\s*\'\'\'[^\']*\'\'\'',
                r'^\s*#.*$',  # 单行注释
            ],
            '.js': [
                r'^\s*/\*.*?\*/',  # 多行注释
                r'^\s*//.*$',  # 单行注释
            ],
            '.ts': [
                r'^\s*/\*.*?\*/',
                r'^\s*//.*$',
            ],
            '.java': [
                r'^\s*/\*.*?\*/',
                r'^\s*//.*$',
            ],
            '.cpp': [
                r'^\s*/\*.*?\*/',
                r'^\s*//.*$',
            ],
            '.c': [
                r'^\s*/\*.*?\*/',
                r'^\s*//.*$',
            ],
            '.go': [
                r'^\s*/\*.*?\*/',
                r'^\s*//.*$',
            ],
            '.rs': [
                r'^\s*/\*.*?\*/',
                r'^\s*//.*$',
            ],
        }

        patterns = comment_patterns.get(extension, [r'^\s*//.*$', r'^\s*#.*$'])

        for line in lines:
            for pattern in patterns:
                if re.match(pattern, line, re.MULTILINE):
                    comment = re.sub(r'^\s*(/\*|\*/|\*|//|#)', '', line).strip()
                    if comment:
                        comments.append(comment)
                    break

        return '\n'.join(comments)

    def _detect_language(self, text: str) -> str:
        """简单的语言检测"""
        if not text or len(text) < 10:
            return "unknown"

        # 简单的中文检测
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))

        if chinese_chars > english_chars:
            return "zh"
        elif english_chars > 0:
            return "en"
        else:
            return "unknown"

    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return list(self.supported_formats.keys())


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试内容解析
    parser = ContentParser()

    # 测试当前目录的文件
    for file_path in Path(".").glob("*"):
        if file_path.is_file() and file_path.suffix in parser.get_supported_formats():
            print(f"\n解析文件内容: {file_path}")
            parsed = parser.parse_content(str(file_path))
            print(f"标题: {parsed.title}")
            print(f"语言: {parsed.language}")
            print(f"编码: {parsed.encoding}")
            print(f"置信度: {parsed.confidence}")
            print(f"内容长度: {len(parsed.text)} 字符")
            print(f"内容预览: {parsed.text[:200]}...")