/**
 * 简体中文语言包
 * XiaoyaoSearch - 小遥搜索
 */

export default {
  // 通用文本
  common: {
    search: '搜索',
    cancel: '取消',
    confirm: '确认',
    save: '保存',
    delete: '删除',
    edit: '编辑',
    loading: '加载中...',
    success: '操作成功',
    error: '操作失败',
    warning: '警告',
    info: '提示',
    retry: '重试',
    close: '关闭',
    back: '返回',
    next: '下一步',
    previous: '上一步',
    submit: '提交',
    reset: '重置',
    refresh: '刷新',
    download: '下载',
    upload: '上传',
    copy: '复制',
    paste: '粘贴',
    select: '选择',
    selectAll: '全选',
    clear: '清空',
    apply: '应用',
    yes: '是',
    no: '否',
    enable: '启用',
    disable: '禁用',
    open: '打开',
    folder: '文件夹',
    file: '文件',
    languageChanged: '语言已切换',
    localeCode: 'zh-CN'
  },

  // 应用标题和副标题
  app: {
    title: '小遥搜索',
    subtitle: '多模态智能搜索，让文件触手可及',
    name: '小遥搜索'
  },

  // 首页
  home: {
    title: '小遥搜索',
    subtitle: '多模态智能搜索，让文件触手可及',
    textInput: '文本输入',
    voiceInput: '语音输入',
    imageInput: '图片输入',
    searchPlaceholder: '输入搜索内容...',
    startSearch: '开始搜索',
    advancedSearch: '高级搜索',
    recording: '正在录音...',
    clickToRecord: '点击开始语音输入',
    stopRecording: '停止录音',
    startRecording: '开始录音',
    dragImageHere: '拖拽图片到此处，或点击选择',
    supportImageFormats: '支持 JPG、JPEG、PNG 格式，最大 10MB',
    startAnalyze: '开始分析',
    remove: '移除',
    recordingTimeLimit: '录音时长达到上限(30秒)',
    startRecordingSuccess: '开始录音...',
    voiceRecognizing: '正在识别语音...',
    selectImageFirst: '请先选择图片',
    imageFormatError: '请上传 JPG、JPEG 或 PNG 格式的图片',
    imageSizeError: '图片大小不能超过10MB',
    imageAnalyzeComplete: '图片分析完成，找到 {count} 个相关文件',
    imageAnalyzeFailed: '图片分析失败',
    voiceRecognizeComplete: '语音转文字完成，找到 {count} 个相关文件',
    voiceRecognizeFailed: '语音转文字失败，请重试',
    searchComplete: '找到 {count} 个相关文件',
    searchFailed: '搜索失败，请重试',
    fileOpened: '已打开文件: {filename}',
    fileOpenFailed: '打开文件失败: {error}',
    filePathCopied: '文件路径已复制到剪贴板: {path}',
    noMoreResults: '没有更多结果了'
  },

  // 搜索
  search: {
    semantic: '语义搜索',
    fulltext: '全文搜索',
    hybrid: '混合搜索',
    searchType: '搜索类型',
    fileType: '文件类型',
    threshold: '相似度',
    results: '搜索结果',
    resultsCount: '找到 {count} 个结果',
    searchTime: '耗时 {time}s',
    loadMore: '加载更多结果',
    noResults: '没有找到相关文件',
    options: '搜索选项',
    searching: '正在搜索...',
    searchComplete: '搜索完成',
    query: '搜索查询',
    limit: '结果数量',
    sortBy: '排序方式',
    relevance: '相关度',
    dateDesc: '日期（从新到旧）',
    dateAsc: '日期（从旧到新）',
    nameAsc: '名称（A-Z）',
    nameDesc: '名称（Z-A）',
    sizeDesc: '大小（从大到小）',
    sizeAsc: '大小（从小到大）'
  },

  // 搜索结果卡片
  searchResult: {
    matchDegree: '匹配度',
    open: '打开',
    copyPath: '复制路径',
    semanticMatch: '语义匹配',
    fulltextMatch: '全文匹配',
    hybridMatch: '混合匹配',
    copySuccess: '文件路径已复制到剪贴板',
    copyFailed: '复制失败，请手动复制',
    justNow: '刚刚',
    minutesAgo: '{minutes}分钟前',
    hoursAgo: '{hours}小时前',
    yesterday: '昨天',
    daysAgo: '{days}天前'
  },

  // 文件类型
  fileType: {
    all: '全部文件',
    document: '文档',
    audio: '音频',
    video: '视频',
    image: '图片',
    other: '其他',
    text: '文本文件',
    pdf: 'PDF文档',
    word: 'Word文档',
    excel: 'Excel表格',
    powerpoint: 'PPT演示文稿',
    markdown: 'Markdown文档',
    code: '代码文件'
  },

  // 设置页面
  settings: {
    title: '设置',
    subtitle: '配置应用参数和AI模型',
    general: '通用设置',
    aiModel: 'AI模型配置',
    index: '索引管理',
    advanced: '高级设置',
    about: '关于',
    language: '语言',
    theme: '主题',
    themeLight: '浅色',
    themeDark: '深色',
    themeAuto: '跟随系统',
    startupLaunch: '开机自启',
    minimizeToTray: '最小化到托盘',
    notifications: '通知',
    autoUpdate: '自动更新',
    clearCache: '清除缓存',
    resetSettings: '重置设置',
    settingsReset: '设置已重置',
    cacheCleared: '缓存已清除'
  },

  // AI模型配置
  aiModel: {
    title: 'AI模型配置',
    subtitle: '配置云端API和本地模型',
    provider: '提供商',
    model: '模型',
    apiKey: 'API密钥',
    apiUrl: 'API地址',
    enable: '启用',
    disable: '禁用',
    test: '测试连接',
    testSuccess: '连接测试成功',
    testFailed: '连接测试失败',
    configSaved: '配置已保存',
    localModel: '本地模型',
    cloudApi: '云端API',
    textEmbedding: '文本嵌入',
    voiceRecognition: '语音识别',
    imageUnderstanding: '图像理解',
    llm: '大语言模型',
    ollama: 'Ollama',
    openai: 'OpenAI',
    claude: 'Claude',
    aliyun: '阿里云',
    modelPath: '模型路径',
    device: '设备',
    deviceCpu: 'CPU',
    deviceCuda: 'CUDA (GPU)',
    deviceMps: 'MPS (Apple Silicon)',
    batchSize: '批处理大小',
    maxLength: '最大长度',
    temperature: '温度',
    topP: 'Top P',
    topK: 'Top K',
    frequencyPenalty: '频率惩罚',
    presencePenalty: '存在惩罚'
  },

  // 索引管理
  index: {
    title: '索引管理',
    subtitle: '创建、更新和管理文件索引',
    create: '创建索引',
    update: '更新索引',
    rebuild: '重建索引',
    delete: '删除索引',
    pause: '暂停',
    resume: '继续',
    status: '状态',
    indexed: '已索引',
    total: '总计',
    progress: '进度',
    speed: '速度',
    remaining: '剩余',
    elapsed: '已用时间',
    createdAt: '创建时间',
    updatedAt: '更新时间',
    lastIndexed: '最后索引时间',
    processingTime: '处理时间',
    fileCount: '文件数量',
    totalSize: '总大小',
    errorCount: '错误数量',
    activeTasks: '活跃任务',
    successRate: '成功率',
    indexing: '正在索引...',
    indexingPaused: '索引已暂停',
    indexingComplete: '索引完成',
    indexingFailed: '索引失败',
    noIndex: '暂无索引',
    indexCreated: '索引已创建',
    indexUpdated: '索引已更新',
    indexDeleted: '索引已删除',
    indexPaused: '索引已暂停',
    indexResumed: '索引已继续',
    confirmDelete: '确认删除此索引？',
    confirmRebuild: '确认重建索引？此操作将删除现有索引并重新创建。',
    addPath: '添加路径',
    removePath: '移除路径',
    indexPaths: '索引路径',
    includePaths: '包含路径',
    excludePaths: '排除路径',
    scanDepth: '扫描深度',
    followSymlinks: '跟随符号链接',
    indexMetadata: '索引元数据',
    indexContent: '索引内容',
    autoUpdate: '自动更新',
    updateInterval: '更新间隔',
    realtime: '实时更新',
    durationMinutes: '{minutes}分{seconds}秒'
  },

  // 系统信息
  system: {
    version: '版本',
    build: '构建',
    platform: '平台',
    arch: '架构',
    nodeVersion: 'Node版本',
    electronVersion: 'Electron版本',
    chromeVersion: 'Chrome版本',
    pythonVersion: 'Python版本',
    status: '状态',
    running: '运行中',
    stopped: '已停止',
    connected: '已连接',
    disconnected: '已断开',
    healthy: '健康',
    unhealthy: '不健康',
    uptime: '运行时间',
    memory: '内存',
    cpu: 'CPU',
    disk: '磁盘',
    network: '网络'
  },

  // 关于页面
  about: {
    title: '关于作者',
    subtitle: '小遥搜索开发者信息',
    description: '小遥搜索是一款专为知识工作者、内容创作者和技术开发者设计的本地桌面应用。通过集成的AI模型，支持语音输入、文本输入、图片输入等多种方式，将用户的查询转换为语义进行智能搜索，实现对本地文件的深度检索。',
    version: '版本',
    license: '许可证',
    authorName: '作者',
    homepage: '主页',
    repository: '代码仓库',
    changelog: '更新日志',
    dependencies: '依赖项',
    acknowledgments: '致谢',
    privacyPolicy: '隐私政策',
    termsOfService: '服务条款',
    checkUpdate: '检查更新',
    updateAvailable: '有新版本可用',
    updateNotAvailable: '已是最新版本',
    downloadUpdate: '下载更新',
    installUpdate: '安装更新',
    author: {
      cardTitle: '关于作者',
      avatarAlt: '作者头像',
      description: 'IT解决方案架构师 | 一人公司实践者。专注于AI驱动的生产力工具开发，致力于为知识工作者打造更智能、更安全的本地搜索解决方案。倡导数据主权和隐私保护，相信优秀的工具应该赋能个人而非监控用户。',
      visionLabel: '开发理念：',
      visionText: '简约而不简单，智能而不 invasive',
      missionLabel: '品牌使命：',
      missionText: '打造真正为个人用户服务的AI工具，让技术赋能而非监控，守护您的数据主权',
      wechatPublicAccount: '微信公众号',
      wechatAccountName: '小遥搜索',
      wechatQrAlt: '微信公众号二维码',
      scanToFollow: '扫码关注',
      addWechatTitle: '添加作者微信',
      addWechatDesc: '交流产品体验',
      authorWechatQrAlt: '作者微信二维码',
      scanToAdd: '扫码添加',
      qrPreparing: '二维码准备中'
    }
  },

  // 消息提示
  message: {
    success: '操作成功',
    error: '操作失败',
    warning: '警告',
    info: '提示',
    confirmDelete: '确认删除？',
    confirmLogout: '确认退出？',
    unsavedChanges: '有未保存的更改，确定要离开吗？',
    networkError: '网络连接失败',
    serverError: '服务器错误',
    requestTimeout: '请求超时',
    unauthorized: '未授权',
    forbidden: '禁止访问',
    notFound: '未找到',
    methodNotAllowed: '方法不允许',
    internalServerError: '内部服务器错误',
    serviceUnavailable: '服务不可用',
    unknownError: '未知错误'
  },

  // 验证消息
  validation: {
    required: '此字段为必填项',
    invalidFormat: '格式无效',
    tooShort: '长度过短',
    tooLong: '长度过长',
    invalidEmail: '邮箱格式无效',
    invalidUrl: 'URL格式无效',
    invalidNumber: '数字格式无效',
    outOfRange: '超出范围',
    duplicate: '重复的值',
    notMatch: '不匹配'
  },

  // 错误消息
  error: {
    loadFailed: '加载失败',
    saveFailed: '保存失败',
    deleteFailed: '删除失败',
    updateFailed: '更新失败',
    uploadFailed: '上传失败',
    downloadFailed: '下载失败',
    copyFailed: '复制失败',
    pasteFailed: '粘贴失败',
    searchFailed: '搜索失败',
    indexFailed: '索引失败',
    modelLoadFailed: '模型加载失败',
    apiConnectionFailed: 'API连接失败',
    fileNotFound: '文件未找到',
    pathNotFound: '路径未找到',
    permissionDenied: '权限被拒绝',
    diskFull: '磁盘空间不足',
    memoryInsufficient: '内存不足',
    networkUnavailable: '网络不可用',
    invalidParameter: '参数无效',
    missingParameter: '缺少参数',
    operationCancelled: '操作已取消',
    operationTimeout: '操作超时',
    microphoneAccessDenied: '无法访问麦克风，请检查权限设置',
    recordingFailed: '录音失败',
    voiceRecognizeFailed: '语音转文字失败',
    imageAnalyzeFailed: '图片分析失败',
    fileOpenFailed: '打开文件失败',
    configLoadFailed: '加载AI模型配置失败',
    configSaveFailed: '保存配置失败',
    speechConfigSaveFailed: '保存语音识别配置失败',
    llmConfigSaveFailed: '保存大语言模型配置失败',
    visionConfigSaveFailed: '保存视觉模型配置失败',
    embeddingConfigSaveFailed: '保存内嵌模型配置失败',
    speechModelTestFailed: '测试语音识别模型失败',
    llmModelTestFailed: '测试大语言模型失败',
    visionModelTestFailed: '测试视觉模型失败',
    embeddingModelTestFailed: '测试内嵌模型失败'
  },

  // HTTP 错误消息
  http: {
    requestError: '请求错误',
    responseError: '响应错误',
    badRequest: '请求参数错误',
    unauthorized: '未授权访问',
    forbidden: '禁止访问',
    notFound: '请求的资源不存在',
    validationFailed: '数据验证失败',
    internalServerError: '服务器内部错误',
    requestFailed: '请求失败',
    networkError: '网络连接失败，请检查后端服务是否运行',
    configError: '请求配置错误'
  },

  // 索引工具状态
  indexStatus: {
    statusPending: '等待中',
    statusProcessing: '处理中',
    statusCompleted: '已完成',
    statusFailed: '失败'
  },

  // 设置页面 - 语音设置
  settingsSpeech: {
    title: '语音设置',
    subtitle: '配置小遥搜索的基本参数',
    voiceRecognitionSettings: '语音识别设置',
    voiceRecognition: '语音识别',
    localFastWhisperService: '本地FastWhisper服务',
    localFastWhisperDesc: '使用本地部署的FastWhisper模型进行语音识别',
    modelVersion: '模型版本',
    modelBase: 'Base (快速)',
    modelSmall: 'Small (平衡)',
    modelMedium: 'Medium (精确)',
    modelLarge: 'Large (高精度)',
    runningDevice: '运行设备',
    deviceCpu: 'CPU',
    deviceCuda: 'CUDA (GPU)',
    checkAvailability: '检查可用性',
    saveSettings: '保存设置',
    saveSuccessRestart: '语音识别配置保存成功，重启应用后生效',
    pleaseSaveFirst: '请先保存语音识别配置'
  },

  // 设置页面 - 大语言模型
  settingsLLM: {
    title: '大语言模型',
    subtitle: '配置大语言模型参数',
    llmService: 'LLM服务',
    localOllamaService: '本地Ollama服务',
    localOllamaDesc: '使用本地部署的Ollama服务运行大语言模型',
    modelName: '模型名称',
    modelNamePlaceholder: '例如: qwen2.5:1.5b',
    modelNameHelp: '输入已安装的Ollama模型名称，支持任何格式',
    serviceUrl: '服务地址',
    serviceUrlPlaceholder: 'http://localhost:11434',
    testConnection: '测试连接',
    saveSuccessRestart: '大语言模型配置保存成功，重启应用后生效',
    pleaseSaveFirst: '请先保存大语言模型配置',
    testData: '你好，请介绍一下你自己'
  },

  // 设置页面 - 视觉模型
  settingsVision: {
    title: '视觉模型',
    subtitle: '配置图像理解模型',
    visionModel: '视觉模型',
    localCNClipService: '本地CN-CLIP模型',
    localCNClipDesc: '使用本地部署的中文CLIP模型进行图像理解',
    modelVersion: '模型版本',
    modelChineseClip: 'OFA-Sys/chinese-clip-vit-base-patch16',
    runningDevice: '运行设备',
    deviceCpu: 'CPU',
    deviceCuda: 'CUDA (GPU)',
    testConnection: '测试连接',
    saveSuccessRestart: '视觉模型配置保存成功，重启应用后生效',
    pleaseSaveFirst: '请先保存视觉模型配置'
  },

  // 设置页面 - 内嵌模型
  settingsEmbedding: {
    title: '内嵌模型',
    subtitle: '配置文本嵌入模型',
    textEmbeddingModel: '文本内嵌模型',
    localBgeM3Service: '本地BGE-M3模型',
    localBgeM3Desc: '使用本地部署的BGE-M3模型生成文本向量嵌入',
    modelVersion: '模型版本',
    modelBgeM3: 'BAAI/bge-m3',
    runningDevice: '运行设备',
    deviceCpu: 'CPU',
    deviceCuda: 'CUDA (GPU)',
    testConnection: '测试连接',
    saveSuccessRestart: '内嵌模型配置保存成功，重启应用后生效',
    pleaseSaveFirst: '请先保存内嵌模型配置',
    testData: '这是一个测试文本，用于验证文本嵌入模型的功能。'
  },

  // 设置页面 - 通用设置
  settingsGeneral: {
    title: '通用设置',
    subtitle: '配置应用基本参数',
    defaultResultCount: '默认返回结果数',
    similarityThreshold: '相似度阈值',
    maxFileSize: '最大文件大小',
    searchOptions: '搜索选项'
  },

  // 导航菜单
  nav: {
    home: '首页',
    settings: '设置',
    index: '索引',
    help: '帮助',
    about: '关于作者'
  },

  // 用户信息
  user: {
    name: '小遥用户',
    aboutAuthor: '关于作者'
  },

  // 系统状态
  status: {
    indexedFiles: '已索引文件',
    count: '个',
    indexSize: '索引大小',
    todaySearches: '今日搜索',
    times: '次',
    system: '系统',
    normal: '正常',
    abnormal: '异常',
    unknown: '未知',
    lastUpdate: '最后更新',
    statusUpdateFailed: '系统状态更新失败，使用缓存数据'
  },

  // 帮助页面
  help: {
    title: '帮助与关于',
    subtitle: '了解如何使用小遥搜索，解决常见问题',
    tabGuide: '快速入门',
    tabTutorial: '使用教程',
    tabFaq: '常见问题',
    tabAbout: '关于',
    guide: {
      step1: {
        title: '配置AI模型',
        description: '进入设置页面配置本地AI模型服务，确保所有服务正常运行',
        button: '前往设置'
      },
      step2: {
        title: '添加索引文件夹',
        description: '进入索引管理页面，添加需要搜索的文件夹并创建文件索引',
        button: '前往索引'
      },
      step3: {
        title: '开始多模态搜索',
        description: '在主页面使用语音、文本、图片多种方式进行智能搜索',
        button: '开始搜索'
      }
    },
    features: {
      title: '核心功能介绍',
      voice: {
        title: '语音搜索',
        description: '支持最长30秒的语音输入，FastWhisper本地识别'
      },
      image: {
        title: '图片搜索',
        description: '上传PNG/JPG图片，CN-CLIP模型理解内容'
      },
      semantic: {
        title: '语义理解',
        description: 'BGE-M3向量嵌入 + Ollama大语言模型理解'
      }
    },
    tutorial: {
      panel1: {
        header: '如何配置本地AI模型？',
        content: {
          stepsTitle: '本地模型配置步骤：',
          step1: { label: '语音识别模型：', text: '设置 → 语音设置 → 选择FastWhisper模型版本' },
          step2: { label: '大语言模型：', text: '设置 → 大语言模型 → 配置Ollama服务地址' },
          step3: { label: '视觉理解模型：', text: '设置 → 视觉模型 → 选择CN-CLIP模型' },
          step4: { label: '文本内嵌模型：', text: '设置 → 内嵌模型 → 选择BGE-M3模型' },
          step5: { label: '设备选择：', text: '根据硬件选择CPU或CUDA加速' },
          tip: '建议：首次使用时建议先用CPU模式，确保功能正常后再启用GPU加速'
        }
      },
      panel2: {
        header: '如何进行多模态搜索？',
        content: {
          modesTitle: '多模态搜索方式：',
          mode1: { label: '文本搜索：', text: '直接在搜索框输入关键词，支持自然语言' },
          mode2: { label: '语音搜索：', text: '点击麦克风按钮，说出搜索内容（30秒内）' },
          mode3: { label: '图片搜索：', text: '上传PNG/JPG图片，AI理解图片内容后搜索相关图片' },
          fileTypesTitle: '支持的文件类型：',
          fileType1: { label: '文档：', text: 'txt, markdown, pdf, xls/xlsx, ppt/pptx, doc/docx' },
          fileType2: { label: '音频：', text: 'mp3, wav' },
          fileType3: { label: '视频：', text: 'mp4, avi' },
          fileType4: { label: '图片：', text: 'png, jpg, jpeg' },
          note: '注意：当前版本，图片搜索仅支持图搜图'
        }
      },
      panel3: {
        header: '如何管理文件索引？',
        content: {
          guideTitle: '索引管理指南：',
          guide1: { label: '添加文件夹：', text: '索引管理 → 添加文件夹 → 选择文件类型' },
          guide2: { label: '监控进度：', text: '查看索引状态、进度、错误信息' },
          guide3: { label: '智能更新：', text: '自动判断是否需要增量更新或完全重建' },
          guide4: { label: '查看详情：', text: '了解索引统计信息、处理时间、错误日志' },
          statusTitle: '索引状态说明：',
          status1: { label: '等待中：', text: '索引任务已创建，等待处理' },
          status2: { label: '处理中：', text: '正在扫描文件和建立索引' },
          status3: { label: '已完成：', text: '索引构建完成，可以搜索' },
          status4: { label: '失败：', text: '索引过程中出现错误' }
        }
      },
      panel4: {
        header: '搜索技巧与优化',
        content: {
          tipsTitle: '搜索优化技巧：',
          tip1: { label: '自然语言：', text: '使用日常语言描述要搜索的内容' },
          tip2: { label: '关键词组合：', text: '使用多个相关关键词提高准确性' },
          tip3: { label: '文件类型过滤：', text: '指定特定文件类型缩小搜索范围' },
          tip4: { label: '相似度调节：', text: '设置 → 通用设置 → 调整相似度阈值' },
          resultsTitle: '结果理解：',
          result1: { label: '相关度分数：', text: '显示文件与查询的匹配程度' },
          result2: { label: '内容摘要：', text: '展示文件中的相关内容片段' },
          result3: { label: '文件路径：', text: '显示文件完整路径便于定位' }
        }
      }
    },
    faq: {
      panel1: {
        header: '语音识别不工作怎么办？',
        content: {
          causesTitle: '可能的原因：',
          cause1: 'FastWhisper模型未正确安装或配置',
          cause2: '麦克风权限未授予应用',
          cause3: '环境噪音过大影响识别',
          cause4: '模型版本与设备不兼容',
          solutionsTitle: '解决方法：',
          solution1: '设置 → 语音设置 → 检查可用性',
          solution2: '尝试不同的模型版本（tiny/base/small）',
          solution3: '在安静环境下进行语音输入',
          solution4: '检查系统麦克风权限设置'
        }
      },
      panel2: {
        header: 'Ollama连接失败？',
        content: {
          checkTitle: '检查步骤：',
          check1: '确认Ollama服务已启动：http://localhost:11434',
          check2: '检查模型是否已安装：ollama list',
          check3: '验证服务地址配置是否正确',
          check4: '测试网络连接和防火墙设置',
          commandsTitle: '常用命令：',
          command1: '安装模型：',
          command2: '查看模型：',
          command3: '运行模型：'
        }
      },
      panel3: {
        header: '图片搜索无结果？',
        content: {
          reasonsTitle: '可能原因：',
          reason1: 'CN-CLIP模型未正确加载',
          reason2: '图片格式不支持（仅支持PNG/JPG）',
          reason3: '图片内容过于复杂或不清晰',
          reason4: '索引中没有相关内容的文件',
          tipsTitle: '优化建议：',
          tip1: '设置 → 视觉模型 → 检测可用性',
          tip2: '使用清晰、内容明确的图片',
          tip3: '尝试包含文字或明显特征的图片',
          tip4: '确保已索引相关类型的文件'
        }
      },
      panel4: {
        header: '索引构建速度慢？',
        content: {
          factorsTitle: '影响因素：',
          factor1: '文件数量和大小',
          factor2: '选择的文件类型',
          factor3: '硬件性能（CPU/GPU）',
          factor4: '模型加载时间',
          methodsTitle: '优化方法：',
          method1: '分批建立索引，避免一次处理过多文件',
          method2: '选择必要的文件类型，减少处理负担',
          method3: '启用GPU加速（如果有）',
          method4: '在系统空闲时进行大量文件索引'
        }
      },
      panel5: {
        header: '搜索结果不准确？',
        content: {
          improvementsTitle: '改进方法：',
          improvement1: '使用更具体、更详细的描述',
          improvement2: '尝试不同的表达方式',
          improvement3: '调整相似度阈值（设置 → 通用设置）',
          improvement4: '确保相关文件已正确索引',
          improvement5: '检查BGE-M3模型是否正常工作',
          advancedTitle: '进阶技巧：',
          advanced1: '结合多种模态输入（如语音+文字）',
          advanced2: '使用同义词或相关概念',
          advanced3: '针对文件类型优化搜索词'
        }
      }
    },
    about: {
      appDescription: '支持多模态AI智能搜索的跨平台本地桌面应用（Windows/MacOS/Linux），通过语音、文本、图像多种输入方式，为知识工作者提供更智能的文件检索体验。',
      tagline: '本地优先 · AI增强 · 隐私安全',
      features: {
        voice: {
          title: '语音搜索',
          description: '30秒语音输入，FastWhisper本地识别'
        },
        image: {
          title: '图像理解',
          description: '上传图片，CN-CLIP智能分析内容'
        },
        semantic: {
          title: '语义搜索',
          description: 'BGE-M3向量嵌入，理解查询意图'
        }
      },
      techHighlight: {
        title: '完全本地化，隐私无忧',
        description: '所有AI模型均本地部署，您的数据永远不会离开您的设备。支持离线使用，确保信息安全和隐私保护。'
      }
    }
  }
}