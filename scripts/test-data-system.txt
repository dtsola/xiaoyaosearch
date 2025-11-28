# 小遥搜索 - 系统健康检查接口测试数据
# backend/app/api/system.py 接口手动测试数据
# 使用方法: 使用 curl 或 Postman 等工具发送以下请求

# ==============================================
# 基础信息
# API基础URL: http://127.0.0.1:8000
# Content-Type: application/json
# ==============================================

# ==============================================
# 1. 基础健康检查 (GET)
# ==============================================
curl -X GET "http://127.0.0.1:8000/api/system/health"

# 带详细头的健康检查
curl -X GET "http://127.0.0.1:8000/api/system/health" \
  -H "Accept: application/json" \
  -H "User-Agent: PostmanRuntime/7.32.3" \
  -v

# ==============================================
# 2. 并发测试
# ==============================================

# 2.1 简单并发测试
# Linux/macOS: 使用后台进程并发请求
for i in {1..10}; do curl -X GET "http://127.0.0.1:8000/api/system/health" & done
wait

# 2.2 连续请求测试
# 测试API稳定性和响应时间
for i in {1..100}; do
  curl -s -X GET "http://127.0.0.1:8000/api/system/health" > /dev/null
  echo "Request $i completed"
done

# ==============================================
# 3. 错误测试
# ==============================================

# 3.1 错误HTTP方法
curl -X GET "http://127.0.0.1:8000/api/system/nonexistent"
curl -X POST "http://127.0.0.1:8000/api/system/health"  # 错误方法
curl -X PUT "http://127.0.0.1:8000/api/system/health"   # 错误方法
curl -X DELETE "http://127.0.0.1:8000/api/system/health" # 错误方法

# 3.2 错误Content-Type
curl -X GET "http://127.0.0.1:8000/api/system/health" \
  -H "Content-Type: application/xml"

# 3.3 超长URL参数测试
curl -X GET "http://127.0.0.1:8000/api/system/health?$(python -c 'print(\"a\"*1000)')"

# ==============================================
# 4. 特殊参数测试
# ==============================================

# 4.1 带查询参数的请求
curl -X GET "http://127.0.0.1:8000/api/system/health?debug=true&verbose=1"

# 4.2 带自定义Header的请求
curl -X GET "http://127.0.0.1:8000/api/system/health" \
  -H "X-Request-ID: test-12345" \
  -H "X-Client-Version: 1.0.0" \
  -H "X-Test-Mode: development"

# 4.3 不同Accept类型
curl -X GET "http://127.0.0.1:8000/api/system/health" \
  -H "Accept: text/html"
curl -X GET "http://127.0.0.1:8000/api/system/health" \
  -H "Accept: text/plain"
curl -X GET "http://127.0.0.1:8000/api/system/health" \
  -H "Accept: */*"

# ==============================================
# 5. Postman 使用说明
# ==============================================

# 1. 新建请求，选择 GET 方法
# 2. 输入 URL: http://127.0.0.1:8000/api/system/health
# 3. Headers 标签页添加：
#    - Accept: application/json
#    - User-Agent: PostmanRuntime/7.32.3
# 4. 点击 Send 发送请求

# ==============================================
# 6. 预期响应格式
# ==============================================

# 成功响应格式:
{
  "success": true,
  "data": {
    "status": "healthy",  // 可能值: healthy/warning/unhealthy
    "timestamp": "2024-01-20T15:30:00.123456",
    "system": {
      "cpu_percent": 25.5,
      "memory": {
        "total": "16.0GB",
        "used": "8.2GB",
        "percent": 51.2
      },
      "disk": {
        "total": "500.0GB",
        "used": "250.5GB",
        "percent": 50.1
      }
    },
    "database": {
      "status": "connected",
      "connection_pool": "1/1"
    },
    "ai_models": {
      "bge_m3": {
        "status": "loaded",
        "memory_usage": "2.1GB"
      },
      "faster_whisper": {
        "status": "not_loaded",
        "error": null
      }
    },
    "indexes": {
      "faiss_index": {
        "status": "ready",
        "document_count": 15420,
        "index_size": "2313000KB",
        "dimension": 768,
        "last_updated": "2024-01-20T15:30:00.123456"
      },
      "whoosh_index": {
        "status": "ready",
        "document_count": 15420,
        "index_size": "771000KB",
        "last_updated": "2024-01-20T15:30:00.123456"
      }
    },
    "services": {
      "fastapi": {
        "status": "running",
        "uptime": "2h 15m",
        "version": "1.0.0"
      },
      "database": {
        "status": "connected",
        "connection_pool": "1/1"
      }
    }
  },
  "message": "系统健康检查完成"
}

# 错误响应格式:
{
  "success": true,
  "data": {
    "status": "unhealthy",
    "error": "系统内存使用率过高",
    "timestamp": "2024-01-20T15:30:00.123456"
  },
  "message": "健康检查发现问题"
}

# ==============================================
# 7. 响应验证要点
# ==============================================

# 验证要点:
# 1. HTTP状态码为 200
# 2. response中success字段为true
# 3. data.status字段为 healthy/warning/unhealthy之一
# 4. system字段包含CPU、内存、磁盘使用率信息
# 5. database.status字段为connected
# 6. ai_models字段包含各AI模型状态信息
# 7. indexes字段包含faiss和whoosh索引状态信息
# 8. services字段包含fastapi和database服务状态信息

# ==============================================
# 8. 性能测试
# ==============================================

# 8.1 响应时间测试
time curl -X GET "http://127.0.0.1:8000/api/system/health"

# 8.2 批量响应时间测试
for i in {1..20}; do
  start_time=$(date +%s%N)
  curl -s -X GET "http://127.0.0.1:8000/api/system/health" > /dev/null
  end_time=$(date +%s%N)
  response_time=$((($end_time - $start_time) / 1000000))
  echo "Request $i: ${response_time}ms"
done

# ==============================================
# 9. 压力测试
# ==============================================

# 9.1 高并发测试配合系统压力
# 先启动CPU压力测试，然后进行并发API请求
stress --cpu 2 --timeout 30s &
STRESS_PID=$!
for i in {1..50}; do
  curl -X GET "http://127.0.0.1:8000/api/system/health" &
  sleep 0.1
done
wait
kill $STRESS_PID 2>/dev/null

# 9.2 超时测试
# 设置较短的超时时间测试连接
curl -X GET "http://127.0.0.1:8000/api/system/health" \
  --connect-timeout 5 \
  --max-time 10

# ==============================================
# 10. 完整测试脚本 (Bash版本)
# ==============================================

#!/bin/bash
# 健康检查完整测试脚本

echo "开始系统健康检查测试..."

# 基础健康检查
echo "1. 基础健康检查"
response=$(curl -s -X GET "http://127.0.0.1:8000/api/system/health")
status_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://127.0.0.1:8000/api/system/health")

if [ $status_code -eq 200 ]; then
    echo "✓ 基础健康检查通过 (HTTP $status_code)"
    echo "响应: $response"
else
    echo "✗ 基础健康检查失败 (HTTP $status_code)"
fi

# 连续请求测试
echo ""
echo "2. 连续请求测试 (10次)"
success_count=0
for i in {1..10}; do
    status=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://127.0.0.1:8000/api/system/health")
    if [ $status -eq 200 ]; then
        ((success_count++))
        echo -n "✓ "
    else
        echo -n "✗ "
    fi
done
echo ""
echo "成功率: $success_count/10 ($(($success_count * 10))%)"

# 响应时间测试
echo ""
echo "3. 响应时间测试"
total_time=0
for i in {1..5}; do
    start_time=$(date +%s%N)
    curl -s -X GET "http://127.0.0.1:8000/api/system/health" > /dev/null
    end_time=$(date +%s%N)
    response_time=$((($end_time - $start_time) / 1000000))
    total_time=$(($total_time + $response_time))
    echo "请求 $i: ${response_time}ms"
done
avg_time=$(($total_time / 5))
echo "平均响应时间: ${avg_time}ms"

echo ""
echo "系统健康检查测试完成"

# ==============================================
# 11. 故障模拟测试
# ==============================================

# 11.1 数据库连接故障模拟
# 观察database.status是否为connected
# - 停止数据库服务
# - 检查CPU负载是否过高
# - SQLite文件权限问题

# 11.2 AI模型故障模拟
# 观察ai_models字段是否有error信息
# - AI模型文件缺失
# - GPU内存不足
# - 模型加载错误

# 11.3 索引状态故障模拟
# 观察indexes字段是否有error信息
# - 索引文件损坏
# - 索引文件权限问题
# - 磁盘空间不足

# 11.4 系统资源故障模拟
# 当memory.percent > 90% 或 disk.percent > 95%时
# - 模拟内存耗尽
# - 模拟磁盘空间不足
# - 观察系统状态变化

# ==============================================
# 12. 完整测试脚本 (Python版本)
# ==============================================

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查完整测试脚本
"""

import requests
import time
import statistics
from datetime import datetime

def test_system_health():
    """健康检查完整测试"""

    base_url = "http://127.0.0.1:8000"
    endpoint = "/api/system/health"
    url = base_url + endpoint

    print("开始系统健康检查测试...")
    print(f"测试地址: {url}")

    # 测试1: 基础健康检查
    print("\n1. 基础健康检查测试")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ 基础健康检查通过")
            print(f"状态: {data['data']['status']}")
            print(f"CPU使用率: {data['data']['system']['cpu_percent']}%")
            print(f"内存使用率: {data['data']['system']['memory']['percent']}%")
            print(f"磁盘使用率: {data['data']['system']['disk']['percent']}%")
        else:
            print(f"✗ 基础健康检查失败 (HTTP {response.status_code})")
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")

    # 测试2: 连续多次请求测试
    print("\n2. 连续多次请求测试 (10次)")
    response_times = []
    success_count = 0

    for i in range(10):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 毫秒

            if response.status_code == 200:
                success_count += 1
                response_times.append(response_time)
                print(f"✓ 请求 {i+1}: {response_time:.0f}ms")
            else:
                print(f"✗ 请求 {i+1}: HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ 请求 {i+1}: 异常 {str(e)}")

    if response_times:
        avg_time = statistics.mean(response_times)
        print(f"\n平均响应时间: {avg_time:.2f}ms")
        print(f"成功率: {success_count}/10 ({success_count*10}%)")

    # 测试3: 并发请求测试
    print("\n3. 并发请求测试 (5个并发)")
    import concurrent.futures
    import threading

    def test_request():
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(test_request) for _ in range(5)]
        results = [future.result() for future in futures]
    end_time = time.time()

    concurrent_time = (end_time - start_time) * 1000
    success_count = sum(results)
    print(f"并发测试结果: {success_count}/5 成功, 耗时: {concurrent_time:.0f}ms")

    print("\n系统健康检查测试完成")

if __name__ == "__main__":
    test_system_health()