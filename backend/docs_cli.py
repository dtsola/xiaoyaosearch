#!/usr/bin/env python3
"""
文档生成命令行工具
提供API文档生成、导出和管理功能
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any
import asyncio

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import create_application
from app.core.config import settings


def generate_openapi_json(output_path: str = None) -> str:
    """生成OpenAPI JSON文件"""
    if not output_path:
        output_path = os.path.join(project_root, "docs", "openapi.json")

    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 创建应用实例
    app = create_application()

    # 获取OpenAPI schema
    openapi_schema = app.openapi()

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

    return output_path


def generate_markdown_docs(output_path: str = None) -> str:
    """生成Markdown格式文档"""
    if not output_path:
        output_path = os.path.join(project_root, "docs", "api.md")

    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 创建应用实例
    app = create_application()

    # 获取OpenAPI schema
    schema = app.openapi()

    # 生成Markdown文档
    markdown_content = f"""# {schema['info']['title']} API Documentation

**Version:** {schema['info']['version']}
**Description:** {schema['info']['description']}

## Base URL

```
{schema['servers'][0]['url']}
```

## Authentication

This API uses JWT Bearer Token authentication.

```http
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

"""

    # 添加路径信息
    paths = schema.get('paths', {})
    for path, path_item in paths.items():
        markdown_content += f"### {path}\n\n"

        for method, operation in path_item.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                summary = operation.get('summary', '')
                description = operation.get('description', '')
                tags = operation.get('tags', [])

                markdown_content += f"#### {method.upper()} {path}\n\n"
                if summary:
                    markdown_content += f"**Summary:** {summary}\n\n"
                if description:
                    markdown_content += f"**Description:** {description}\n\n"
                if tags:
                    markdown_content += f"**Tags:** {', '.join(tags)}\n\n"

                # 添加参数信息
                parameters = operation.get('parameters', [])
                if parameters:
                    markdown_content += "**Parameters:**\n\n"
                    for param in parameters:
                        param_name = param.get('name', '')
                        param_type = param.get('schema', {}).get('type', '')
                        param_required = param.get('required', False)
                        param_desc = param.get('description', '')

                        markdown_content += f"- `{param_name}` ({param_type})"
                        if param_required:
                            markdown_content += " **[required]**"
                        markdown_content += f": {param_desc}\n"
                    markdown_content += "\n"

                # 添加请求体信息
                request_body = operation.get('requestBody', {})
                if request_body:
                    markdown_content += "**Request Body:**\n\n"
                    content = request_body.get('content', {})
                    for content_type, content_item in content.items():
                        markdown_content += f"- Content-Type: {content_type}\n"
                        schema_ref = content_item.get('schema', {}).get('$ref', '')
                        if schema_ref:
                            schema_name = schema_ref.split('/')[-1]
                            markdown_content += f"- Schema: {schema_name}\n"
                    markdown_content += "\n"

                # 添加响应信息
                responses = operation.get('responses', {})
                if responses:
                    markdown_content += "**Responses:**\n\n"
                    for status_code, response in responses.items():
                        description = response.get('description', '')
                        markdown_content += f"- `{status_code}`: {description}\n"
                    markdown_content += "\n"

                markdown_content += "---\n\n"

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return output_path


def generate_postman_collection(output_path: str = None) -> str:
    """生成Postman集合文件"""
    if not output_path:
        output_path = os.path.join(project_root, "docs", "postman_collection.json")

    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 创建应用实例
    app = create_application()

    # 获取OpenAPI schema
    schema = app.openapi()

    # 生成Postman集合
    collection = {
        "info": {
            "name": schema['info']['title'],
            "description": schema['info']['description'],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "variable": [
            {
                "key": "baseUrl",
                "value": schema['servers'][0]['url'],
                "type": "string"
            }
        ],
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{jwt_token}}",
                    "type": "string"
                }
            ]
        }
    }

    # 添加API端点
    paths = schema.get('paths', {})
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                item = {
                    "name": operation.get('summary', f"{method.upper()} {path}"),
                    "request": {
                        "method": method.upper(),
                        "header": [],
                        "url": {
                            "raw": "{{baseUrl}}{path}",
                            "host": ["{{baseUrl}}"],
                            "path": path.strip('/').split('/')
                        },
                        "description": operation.get('description', '')
                    },
                    "response": []
                }

                # 添加参数
                parameters = operation.get('parameters', [])
                if parameters:
                    for param in parameters:
                        param_item = {
                            "key": param.get('name', ''),
                            "value": param.get('schema', {}).get('default', ''),
                            "description": param.get('description', ''),
                            "type": "text"
                        }

                        if param.get('in') == 'query':
                            item["request"]["url"]["query"] = item["request"]["url"].get("query", [])
                            item["request"]["url"]["query"].append(param_item)
                        elif param.get('in') == 'header':
                            item["request"]["header"].append(param_item)

                # 添加请求体
                request_body = operation.get('requestBody', {})
                if request_body:
                    content = request_body.get('content', {})
                    for content_type, content_item in content.items():
                        if content_type == 'application/json':
                            item["request"]["body"] = {
                                "mode": "raw",
                                "raw": "{}",
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            }
                            item["request"]["header"].append({
                                "key": "Content-Type",
                                "value": "application/json",
                                "type": "text"
                            })
                            break

                collection["item"].append(item)

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)

    return output_path


def serve_docs(port: int = 8080):
    """启动文档服务器"""
    import uvicorn

    # 创建应用实例
    app = create_application()

    print(f"启动API文档服务器...")
    print(f"Swagger UI: http://localhost:{port}{settings.API_V1_STR}/docs")
    print(f"ReDoc: http://localhost:{port}{settings.API_V1_STR}/redoc")
    print(f"OpenAPI JSON: http://localhost:{port}{settings.API_V1_STR}/openapi.json")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="小遥搜索API文档生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s openapi                    # 生成OpenAPI JSON文件
  %(prog)s markdown                   # 生成Markdown文档
  %(prog)s postman                    # 生成Postman集合
  %(prog)s serve                      # 启动文档服务器
  %(prog)s all                        # 生成所有文档格式
        """
    )

    parser.add_argument(
        '--output-dir', '-o',
        default='docs',
        help='输出目录路径 (默认: docs)'
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8080,
        help='文档服务器端口 (默认: 8080)'
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # OpenAPI命令
    openapi_parser = subparsers.add_parser('openapi', help='生成OpenAPI JSON文件')

    # Markdown命令
    markdown_parser = subparsers.add_parser('markdown', help='生成Markdown文档')

    # Postman命令
    postman_parser = subparsers.add_parser('postman', help='生成Postman集合')

    # 服务命令
    serve_parser = subparsers.add_parser('serve', help='启动文档服务器')

    # 全部命令
    all_parser = subparsers.add_parser('all', help='生成所有文档格式')

    # 解析参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行命令
    try:
        if args.command == 'openapi':
            output_path = os.path.join(args.output_dir, 'openapi.json')
            path = generate_openapi_json(output_path)
            print(f"OpenAPI JSON文件生成成功: {path}")

        elif args.command == 'markdown':
            output_path = os.path.join(args.output_dir, 'api.md')
            path = generate_markdown_docs(output_path)
            print(f"Markdown文档生成成功: {path}")

        elif args.command == 'postman':
            output_path = os.path.join(args.output_dir, 'postman_collection.json')
            path = generate_postman_collection(output_path)
            print(f"Postman集合生成成功: {path}")

        elif args.command == 'serve':
            serve_docs(args.port)

        elif args.command == 'all':
            print("正在生成所有文档格式...")

            openapi_path = os.path.join(args.output_dir, 'openapi.json')
            path1 = generate_openapi_json(openapi_path)
            print(f"OpenAPI JSON文件生成成功: {path1}")

            markdown_path = os.path.join(args.output_dir, 'api.md')
            path2 = generate_markdown_docs(markdown_path)
            print(f"Markdown文档生成成功: {path2}")

            postman_path = os.path.join(args.output_dir, 'postman_collection.json')
            path3 = generate_postman_collection(postman_path)
            print(f"Postman集合生成成功: {path3}")

            print("所有文档生成完成!")

    except Exception as e:
        print(f"操作失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()