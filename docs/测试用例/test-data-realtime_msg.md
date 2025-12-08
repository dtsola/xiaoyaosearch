# 小遥搜索 - 实时消息接口测试数据
# backend/app/api/realtime_msg.py 接口手动测试数据
# 使用方法: 使用 curl 或 Postman 等工具发送以下请求

# ==============================================
# 基础信息
# API基础URL: http://127.0.0.1:8000
# Content-Type: application/json
# ==============================================

# ==============================================
# 1. 获取索引构建进度 (GET)
# ==============================================

# 1.1 获取正在运行的索引任务进度
curl -X GET "http://127.0.0.1:8000/api/realtime/index/1/progress"

# 1.2 获取已完成的索引任务进度
curl -X GET "http://127.0.0.1:8000/api/realtime/index/2/progress"

# 1.3 获取失败的索引任务进度
curl -X GET "http://127.0.0.1:8000/api/realtime/index/3/progress"

# 1.4 测试不存在的索引任务
curl -X GET "http://127.0.0.1:8000/api/realtime/index/99999/progress"

# ==============================================
# 2. 获取搜索建议 (GET)
# ==============================================

# 2.1 基本搜索建议
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=Python&limit=5"

# 2.2 中文搜索建议
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=机器学习&limit=10"

# 2.3 长查询搜索建议
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=如何使用深度学习进行图像识别&limit=8"

# 2.4 最小限制建议
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=AI&limit=1"

# 2.5 最大限制建议
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=编程&limit=20"

# 2.6 空查询（应该返回空建议）
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=&limit=5"

# 2.7 只有空格的查询
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=%20%20&limit=5"

# 2.8 特殊字符查询
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=C%2B%2B&limit=5"

# 2.9 超长查询（超出100字符限制）
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=这是一个非常长的搜索查询字符串用于测试系统的字符限制处理能力&limit=5"

# 2.10 数字查询
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=2023&limit=5"

# ==============================================
# 3. 获取活跃索引任务 (GET)
# ==============================================

# 3.1 获取所有活跃任务
curl -X GET "http://127.0.0.1:8000/api/realtime/index/active-tasks"

# ==============================================
# 4. 获取轮询配置 (GET)
# ==============================================

# 4.1 获取轮询配置信息
curl -X GET "http://127.0.0.1:8000/api/realtime/polling-config"

# ==============================================
# 5. 错误测试用例
# ==============================================

# 5.1 缺少必需参数 - search suggestions
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions"

# 5.2 limit 参数超出范围 - 太小
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=test&limit=0"

# 5.3 limit 参数超出范围 - 太大
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=test&limit=21"

# 5.4 query 参数超出最小长度
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=&limit=5"

# 5.5 query 参数超出最大长度
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=这个查询字符串的长度超过了系统允许的最大长度限制一百个字符这是一个非常非常长的测试用例&limit=5"

# 5.6 负数的limit参数
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=test&limit=-5"

# 5.7 非数字的limit参数
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=test&limit=abc"

# ==============================================
# 6. 压力测试用例
# ==============================================

# 6.1 快速连续请求相同查询（模拟用户快速输入）
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=机器学习&limit=5" && sleep 0.1 && curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=机器学习教程&limit=5" && sleep 0.1 && curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=机器学习算法&limit=5"

# 6.2 并发请求多个不同的查询
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=Python&limit=5" & curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=Java&limit=5" & curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=JavaScript&limit=5" & wait

# ==============================================
# 7. 边界条件测试
# ==============================================

# 7.1 单个字符查询
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=A&limit=5"

# 7.2 最大长度查询（刚好100字符）
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=这是一个刚好一百个字符长度的搜索查询字符串用于测试系统在边界条件下的处理能力和稳定性表现非常好&limit=5"

# 7.3 包含特殊符号的查询
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=C%2B%2B+%26+Python+%7C+Java+*+SQL&limit=5"

# 7.4 URL编码的查询
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0%E6%95%99%E7%A8%8B&limit=5"

# ==============================================
# 8. 实际使用场景测试
# ==============================================

# 8.1 模拟用户搜索编程相关内容
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=Python编程&limit=8"

# 8.2 模拟用户搜索学习资料
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=机器学习入门&limit=8"

# 8.3 模拟用户搜索工具软件
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=视频编辑软件&limit=8"

# 8.4 模拟用户搜索技术问题
curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=如何解决内存泄漏问题&limit=8"

# ==============================================
# 9. 响应时间测试
# ==============================================

# 9.1 测试简单查询响应时间
time curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=test&limit=5"

# 9.2 测试复杂查询响应时间
time curl -X GET "http://127.0.0.1:8000/api/realtime/search/suggestions?query=深度学习神经网络卷积循环注意力机制自然语言处理计算机视觉&limit=10"

# ==============================================
# 使用说明
# ==============================================

# Windows PowerShell 中使用 curl 的注意事项:
# 1. 如果需要在 PowerShell 中使用，请将单引号 ' 改为双引号 "
# 2. 或者使用 Invoke-RestMethod 命令替代 curl
# 3. URL 中的特殊字符需要正确转义

# Postman 使用步骤:
# 1. 新建请求，选择对应的 HTTP 方法
# 2. 输入完整的 URL，在 Params 选项卡中添加查询参数
# 3. 点击 Send 发送请求
# 4. 查看响应结果，包括状态码、响应时间和响应体

# 接口说明:
# 1. 索引进度接口: 需要先通过索引创建接口创建索引任务，才能获取对应的进度
# 2. 搜索建议接口: 支持实时搜索建议，会根据历史搜索记录和常见模式生成建议
# 3. 活跃任务接口: 返回当前正在运行或等待中的索引任务列表
# 4. 轮询配置接口: 返回推荐的轮询间隔时间配置

# 常见响应状态码:
# 200: 成功
# 400: 请求参数错误
# 404: 资源不存在（如索引任务ID不存在）
# 422: 参数验证失败（如参数长度、范围不符合要求）
# 500: 服务器内部错误

# 测试建议:
# 1. 先测试正常用例，确保基本功能正常
# 2. 再测试边界条件和错误用例，验证系统的健壮性
# 3. 最后进行压力测试，评估系统性能
# 4. 使用不同浏览器和工具测试，确保兼容性