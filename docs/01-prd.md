# PRD：小遥搜索 XiaoyaoSearch MVP版本

## 1. 产品定位（一句话）
为知识工作者、内容创作者和技术开发者提供多模态AI智能搜索能力的本地桌面应用

## 2. 用户故事（核心场景）

**场景1：语音搜索回忆内容**
- 作为内容创作者
- 我想要通过语音描述"我昨天录制的那个关于AI趋势的讨论"
- 以便于快速找到具体的音频文件和相关内容

**场景2：图片相似搜索**
- 作为设计师
- 我想要上传一张设计图寻找相似的文字描述或相关文档
- 以便于定位到相关的项目文件和参考资料

**场景3：语义内容搜索**
- 作为研究员
- 我想要搜索"关于机器学习算法优化的方法"
- 以便于在大量文档中找到相关的研究笔记和论文

**场景4：跨文件类型检索**
- 作为开发者
- 我想要搜索"之前讨论的API接口设计问题"
- 以便于找到相关的代码文件、会议记录和技术文档

## 3. 功能清单（MVP范围）

### P0功能（必须有）
- [ ] 多模态输入功能：支持语音输入（30秒内）、文本输入、图片上传（PNG/JPG）
- [ ] AI语义转换：将用户输入转换为搜索语义，支持自然语言理解
- [ ] 本地文件索引：支持对指定文件夹建立文件索引，包含文件名和内容
- [ ] 多格式文件搜索：支持视频（mp4、avi）、音频（mp3、wav）、文档（txt、markdown、office、pdf）
- [ ] 搜索结果展示：按相关度排序，支持预览和快速定位
- [ ] AI模型配置：支持云端API和本地Ollama模型切换；嵌入模型支持本地BGE-M3和云端API切换（互斥，切换需重建索引） 🚧 规划中

### P1功能（最好有）
- [x] **国际化支持（i18n）**：中英文双语界面，语言切换器，720+翻译键全覆盖 ✅ 已完成
- [ ] **专业术语库系统** 🚧 规划中 - 建立多术语库集合系统，支持用户自定义领域术语库（医疗、法律、IT等），实现精准查询扩展，解决搜索"PRD"无法返回"产品需求文档"等问题（详见[特性PRD](特性开发/search-optimization-glossary/search-optimization-glossary-01-prd.md)）
- [ ] **云端嵌入模型调用能力** 🚧 规划中 - 支持OpenAI兼容的云端嵌入模型服务，用户可选择使用云端嵌入模型（如OpenAI、DeepSeek、阿里云通义千问、Moonshot等）替代本地BGE-M3模型，两者互斥，切换时需要重建索引（详见[特性PRD](特性开发/embedding-openai/embedding-openai-01-prd.md)）
- [ ] **OpenAI兼容大模型服务** 🚧 规划中 - 支持OpenAI兼容的云端大语言模型服务，用户可选择使用云端大模型（如阿里云通义千问、DeepSeek、Moonshot等）替代或补充本地Ollama模型（详见[特性PRD](特性开发/openai/openai-01-prd.md)）
- [ ] **插件化架构与数据源扩展（语雀+飞书+钉钉）** 🚧 规划中 - 建立插件化框架支持多数据源扩展，优先实现语雀知识库数据源、飞书文档数据源和钉钉文档数据源（详见[语雀PRD](特性开发/plugins+yuque/plugins+yuque-01-prd.md) | [飞书PRD](特性开发/plugins+feishu/plugins+feishu-01-prd.md) | [钉钉PRD](特性开发/plugins+dingding/plugins+dingding-01-prd.md)）
- [ ] **MCP服务器支持** 🚧 规划中 - 为小遥搜索添加 Model Context Protocol (MCP) 服务器能力，使 Claude Desktop 等 AI 应用能够连接小遥搜索进行本地文件智能搜索（详见[特性PRD](特性开发/mcp/mcp-01-prd.md)）
- [ ] **Agent Skill工具规范** 🚧 规划中 - 为 Claude Code 提供小遥搜索 MCP 工具调用能力的 Agent Skill 规范定义（详见[特性PRD](特性开发/agent-skills/agent-skills-01-prd.md)）
- [ ] **视频画面搜索** ⏸️ 已暂停 - 通过图片搜索视频内容，快速定位视频中的关键画面（详见[特性PRD](特性开发/videosearch/videosearch-01-prd.md)）
- [ ] 语音识别模型配置：支持云端API和本地FastWhisper
- [ ] 视觉模型配置：支持云端API和本地视觉模型
- [ ] 索引管理：文件夹选择、索引重建、删除索引
- [ ] 搜索历史记录：保存和管理用户搜索历史

### P2功能（未来考虑）
- [ ] 高级筛选：按文件类型、时间、大小筛选
- [ ] 收藏夹功能：重要文件收藏和分类
- [ ] 导出功能：搜索结果导出为报告

## 4. 核心流程图
```
用户启动应用 → 首次设置配置 → 选择索引文件夹 → 建立文件索引
    ↓
输入搜索内容（语音/文本/图片）→ AI语义转换 → 执行本地搜索
    ↓
展示搜索结果 → 文件预览 → 打开文件位置 → 满意度反馈
```

## 5. 页面结构

### 搜索主页面
- 搜索输入框（支持语音、文本、图片输入）
- AI模型状态指示器
- 搜索结果列表（文件预览、相关度评分）
- 快捷操作按钮（预览、打开位置、收藏）

### 设置页面
- **嵌入模型设置** 🚧 规划中
  - 模型类型选择：本地 BGE-M3 或云端API（互斥，切换时需重建索引）
  - 本地配置：模型名称、运行设备（CPU/CUDA）
  - 云端配置：API密钥、端点地址、模型名称、超时时间、批处理大小
  - 支持供应商：OpenAI、DeepSeek、阿里云通义千问、Moonshot等兼容服务
  - 详见：[云端嵌入模型PRD](特性开发/embedding-openai/embedding-openai-01-prd.md)
- **LLM模型设置**
  - 模型类型选择：Ollama（本地）或 OpenAI 兼容（云端） 🚧 规划中
  - 本地Ollama配置：模型名称、服务地址
  - OpenAI兼容配置：API密钥、端点地址、模型名称（支持阿里云通义千问、DeepSeek、Moonshot等） 🚧 规划中
- **语音识别设置**
  - 云端API配置：API地址、访问令牌
  - 本地FastWhisper（一键启用）
- **视觉模型设置**
  - 云端API配置：API地址、访问令牌、视觉模型名称
  - 本地视觉模型（一键启用）
- **数据源配置** 🚧 规划中
  - 插件管理：插件列表、上传、启用、禁用
  - 语雀数据源：API Token、知识库ID配置
  - 飞书数据源：本地文件路径配置，支持飞书导出Markdown自动识别
  - 钉钉数据源：本地文件路径配置，支持钉钉导出工具生成的 .xyddjson 元数据文件自动识别
  - 同步状态：同步进度、文档数量统计
  - 多源配置：支持同时启用多个数据源
- **术语库配置** 🚧 规划中
  - 术语库管理：创建、编辑、删除术语库（如"医疗术语库"、"IT术语库"）
  - 术语管理：在术语库中添加、编辑、删除术语
  - 查询扩展：根据选择的术语库扩展查询词
  - 术语库选择：选择默认使用的术语库组合
  - CSV导入/导出：支持导入外部术语库（CSV格式）
  - 详见：[专业术语库系统PRD](特性开发/search-optimization-glossary/search-optimization-glossary-01-prd.md)

### 索引管理页面
- 文件夹选择器
- 索引状态监控
- 重建/删除索引操作
- 索引统计信息

### 帮助与关于页面
- 使用教程
- 常见问题
- 版本信息
- 联系支持

## 6. 数据埋点计划

### 6.1 核心埋点事件

| 事件 | 触发时机 | 关键参数 |
|------|---------|---------|
| app_start | 应用启动 | app_version, platform, current_lang, device_lang |
| search_input | 用户输入搜索内容 | input_type(voice/text/image), input_length |
| search_execute | 执行搜索 | ai_model, search_type |
| search_result | 搜索结果返回 | result_count, response_time |
| file_preview | 预览文件 | file_type, file_size |
| file_open | 打开文件 | file_path, open_type |
| model_switch | 切换AI模型 | old_model, new_model |
| folder_index | 文件夹索引操作 | folder_path, action(create/update/delete) |
| settings_change | 设置变更 | setting_type, old_value, new_value |
| error_occurred | 错误发生 | error_type, error_message |
| language_switch | 用户切换语言 | from_lang, to_lang |
| language_init | 应用初始化语言 | current_lang, device_lang |

### 6.2 云端嵌入模型增量埋点

| 事件 | 触发时机 | 关键参数 | 业务价值 |
|------|---------|---------|---------|
| cloud_embedding_configured | 用户配置云端嵌入模型 | provider, model_name | 了解用户偏好 |
| cloud_embedding_test | 测试云端嵌入连接 | provider, success | 监控配置成功率 |
| cloud_embedding_used | 使用云端嵌入搜索 | provider, model_name, query_length | 统计使用频率 |
| cloud_embedding_failed | 云端嵌入调用失败 | provider, error_code | 监控服务质量 |
| embedding_model_switched | 切换嵌入模型 | old_provider, new_provider, index_rebuilt | 监控模型切换行为 |
| index_rebuild_started | 开始索引重建 | total_files, estimated_time | 监控重建性能 |
| index_rebuild_completed | 索引重建完成 | total_files, duration, failed_files | 监控重建质量 |

### 6.3 插件化架构增量埋点

| 事件 | 触发时机 | 关键参数 | 业务价值 |
|------|---------|---------|---------|
| datasource_installed | 安装插件时 | plugin_id, plugin_name | 了解插件使用情况 |
| datasource_enabled | 启用数据源时 | source_type | 统计数据源分布 |
| datasource_sync_started | 开始同步时 | source_type | 监控同步频率 |
| datasource_sync_completed | 同步完成时 | source_type, item_count, duration | 监控同步性能 |
| datasource_search_triggered | 搜索数据源时 | source_type | 了解数据源使用率 |

### 6.4 专业术语库增量埋点

| 事件 | 触发时机 | 关键参数 | 业务价值 |
|------|---------|---------|---------|
| glossary_view | 查看术语详情 | term_id, term_name | 了解术语使用情况 |
| glossary_add | 添加术语 | term, category | 统计术语增长 |
| glossary_search | 搜索术语 | query, results_count | 了解术语查询需求 |
| term_match | 术语匹配 | query, matched_term, is_expanded | 评估术语匹配效果 |
| term_expanded_search | 使用扩展搜索 | query, expanded_terms, results_count | 评估扩展效果 |

详见：[专业术语库PRD](特性开发/search-optimization-glossary/search-optimization-glossary-01-prd.md)

## 7. 非功能需求

### 性能要求
- 应用启动时间 < 3秒
- 搜索响应时间 < 2秒
- 文件预览加载时间 < 1秒
- 支持10万+文件的本地索引
- 插件加载时间 < 500ms（插件化架构）
- 数据源同步速度 > 30篇/秒（语雀数据源）
- 多数据源搜索延迟 < 200ms（插件化架构）
- 术语匹配响应时间 < 50ms（专业术语库）
- 术语扩展搜索时间 < 1.2倍原时间（专业术语库）
- 术语列表加载 < 500ms（专业术语库）
- 云端嵌入API响应时间 < 2s（单次）（云端嵌入模型）
- 批量嵌入吞吐量 > 100 texts/min（云端嵌入模型）
- 索引重建速度 > 10 files/min（云端嵌入模型）

### 兼容性要求
- Windows 10/11 x64
- macOS 10.15+ (Intel/M1)
- 最低内存要求：4GB RAM
- 推荐内存要求：8GB+ RAM
- 磁盘空间：500MB应用 + 索引空间

### 安全要求
- 本地数据加密存储
- API密钥安全保存（AES加密存储，日志脱敏显示）
- 用户数据不上传云端（仅上传搜索查询用于云端嵌入，索引数据本地存储）
- 支持隐私模式（不记录搜索历史）
- API Token加密存储（使用系统密钥库）（插件化架构）
- API密钥加密存储（云端嵌入模型）（云端嵌入模型）
- 术语管理权限控制（管理员/普通用户）（专业术语库）
- 插件代码沙箱隔离（限制文件系统访问）（插件化架构）
- 插件上传包验证（文件类型、大小限制）（插件化架构）
- API调用频率限制（防止滥用）（插件化架构）
- 插件代码沙箱隔离（限制文件系统访问）（插件化架构）
- 插件上传包验证（文件类型、大小限制）（插件化架构）
- API调用频率限制（防止滥用）（插件化架构）

### 可用性要求
- **国际化支持（i18n）** ✅ 已完成
  - 支持语言：简体中文（zh-CN）、英语（en-US）
  - 翻译覆盖：720+ 翻译键，覆盖所有页面和组件
  - 语言切换：顶部导航栏语言切换器，即时生效无需重启
  - 语言持久化：LocalStorage 自动保存用户语言偏好
  - UI组件国际化：Ant Design Vue 组件库语言同步切换
  - 日期时间国际化：Day.js 支持相对时间和绝对时间格式
  - 错误信息国际化：HTTP 错误信息支持前端翻译
- **OpenAI兼容大模型服务** 🚧 规划中
  - 核心能力：支持OpenAI兼容的云端大语言模型服务，用户可选择使用云端大模型（如阿里云通义千问、DeepSeek、Moonshot等）替代或补充本地Ollama模型
  - 技术基础：OpenAI API标准兼容，aiohttp异步HTTP客户端，BaseAIModel统一接口
  - 模型支持：本地Ollama（已有）、OpenAI兼容云端（P0）
  - 配置管理：前端动态表单根据类型显示不同配置项，API密钥加密存储
  - 供应商支持：OpenAI、阿里云通义千问、DeepSeek、Moonshot等兼容供应商
  - 详见：[OpenAI兼容大模型服务PRD](特性开发/openai/openai-01-prd.md)
- **云端嵌入模型调用能力** 🚧 规划中
  - 核心能力：支持OpenAI兼容的云端嵌入模型服务，用户可选择使用云端嵌入模型（如OpenAI、DeepSeek、阿里云通义千问、Moonshot等）替代本地BGE-M3模型
  - 技术基础：OpenAI Embeddings API标准兼容，aiohttp异步HTTP客户端，BaseAIModel统一接口
  - 模型支持：本地BGE-M3（已有，1024维）、云端嵌入模型（P0，使用模型原始维度）
  - 配置管理：前端动态表单根据类型显示不同配置项，本地/云端互斥选择，API密钥加密存储
  - 索引重建：切换嵌入模型时需重建索引（不同模型的向量空间不兼容），采用独立端点+内存状态管理方案
  - 供应商支持：OpenAI、DeepSeek、阿里云通义千问、Moonshot等兼容Embeddings API的服务
  - 详见：[云端嵌入模型PRD](特性开发/embedding-openai/embedding-openai-01-prd.md)
- **插件化架构与数据源扩展** 🚧 规划中
  - 核心能力：建立插件化框架，支持多数据源扩展，优先实现语雀知识库数据源、飞书文档数据源和钉钉文档数据源
  - 技术基础：Python importlib动态加载 + ABC接口抽象 + Pydantic配置验证
  - 数据源支持：本地文件系统（已有）、语雀知识库（P0）、飞书文档（P0）、钉钉文档（P0）
  - 配置管理：通过API接口完成插件上传、启用、配置和管理
  - 多源搜索：统一索引服务，支持跨数据源语义搜索
  - 插件安全：沙箱隔离、API Token加密存储、插件包验证
  - 详见：[插件化架构PRD](特性开发/plugins+yuque/plugins+yuque-01-prd.md) | [飞书数据源PRD](特性开发/plugins+feishu/plugins+feishu-01-prd.md) | [钉钉数据源PRD](特性开发/plugins+dingding/plugins+dingding-01-prd.md)
- **专业术语库系统** 🚧 规划中
  - 核心能力：建立多术语库集合系统，支持用户自定义领域术语库（医疗、法律、IT等），实现精准查询扩展
  - 技术基础：SQLite术语库存储 + Faiss术语匹配 + 术语扩展服务
  - 主要功能：术语库集合管理、术语管理、查询扩展、术语库选择、CSV导入/导出、预置术语库
  - 用户价值：解决搜索"PRD"无法返回"产品需求文档"等问题，支持领域隔离避免术语混淆
  - 配置管理：搜索设置中选择默认使用的术语库组合，支持快速启用/禁用
  - 详见：[专业术语库系统PRD](特性开发/search-optimization-glossary/search-optimization-glossary-01-prd.md)
- **MCP服务器支持** 🚧 规划中
  - 核心能力：为小遥搜索添加 Model Context Protocol (MCP) 服务器能力，使 Claude Desktop 等 AI 应用能够连接小遥搜索进行本地文件智能搜索
  - 技术基础：mcp-python-sdk + FastAPI SSE 端点 + 适配器模式
  - 搜索工具：语义搜索、全文搜索、语音搜索、图像搜索、混合搜索
  - 架构方案：集成到 FastAPI 进程，共享 AI 模型和搜索服务，节省内存
  - Claude集成：通过 SSE 传输端点连接 Claude Desktop，支持自然语言查询本地文档
  - 详见：[MCP服务器支持PRD](特性开发/mcp/mcp-01-prd.md)
- **Agent Skill工具规范** 🚧 规划中
  - 核心能力：为 Claude Code 提供小遥搜索 MCP 工具调用能力的 Agent Skill 规范定义
  - 技术基础：Claude Code Skill 格式 + MCP 工具描述规范
  - 工具定义：语义搜索、全文搜索、混合搜索、图像搜索、语音搜索
  - 配置指导：MCP 服务器连接配置、工具调用示例
  - 详见：[Agent Skill特性PRD](特性开发/agent-skills/agent-skills-01-prd.md)
- **视频画面搜索** ⏸️ 已暂停
  - 核心能力：通过图片检索视频内容，快速定位视频中的关键画面
  - 暂停原因：优先开发插件化架构与语雀+飞书数据源特性
  - 技术基础：复用现有CN-CLIP图像搜索能力
  - 搜索范围：支持常见视频格式（mp4、avi、mkv、mov、wmv、flv、webm）
  - 搜索精度：按可配置间隔提取关键帧（默认10秒），可设置提取时长上限
  - 结果展示：显示匹配的视频文件、时间戳位置、相似度分数
  - 配置管理：通过后端.env文件启用，支持提取间隔和时长配置
  - 详见：[视频画面搜索特性PRD](特性开发/videosearch/videosearch-01-prd.md)
- 无障碍访问支持
- 键盘快捷键支持
- 深色/浅色主题切换

---
**预计开发时间：** 8-10周
**上线时间目标：** 2026年2月底
