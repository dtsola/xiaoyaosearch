/**
 * English Language Pack
 * XiaoyaoSearch - 小遥搜索
 */

export default {
  // Common Text
  common: {
    search: 'Search',
    cancel: 'Cancel',
    confirm: 'Confirm',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    loading: 'Loading...',
    success: 'Success',
    error: 'Error',
    warning: 'Warning',
    info: 'Info',
    retry: 'Retry',
    close: 'Close',
    back: 'Back',
    next: 'Next',
    previous: 'Previous',
    submit: 'Submit',
    reset: 'Reset',
    refresh: 'Refresh',
    download: 'Download',
    upload: 'Upload',
    copy: 'Copy',
    paste: 'Paste',
    select: 'Select',
    selectAll: 'Select All',
    clear: 'Clear',
    apply: 'Apply',
    yes: 'Yes',
    no: 'No',
    enable: 'Enable',
    disable: 'Disable',
    open: 'Open',
    folder: 'Folder',
    file: 'File',
    languageChanged: 'Language changed',
    localeCode: 'en-US'
  },

  // App Title and Subtitle
  app: {
    title: 'XiaoyaoSearch',
    subtitle: 'Multimodal AI Search for Local Files',
    name: 'XiaoyaoSearch'
  },

  // Home Page
  home: {
    title: 'XiaoyaoSearch',
    subtitle: 'Multimodal AI Search for Local Files',
    textInput: 'Text Input',
    voiceInput: 'Voice Input',
    imageInput: 'Image Input',
    searchPlaceholder: 'Enter search content...',
    startSearch: 'Start Search',
    advancedSearch: 'Advanced Search',
    recording: 'Recording...',
    clickToRecord: 'Click to start voice input',
    stopRecording: 'Stop Recording',
    startRecording: 'Start Recording',
    dragImageHere: 'Drag image here or click to select',
    supportImageFormats: 'Support JPG, JPEG, PNG formats, max 10MB',
    startAnalyze: 'Start Analyze',
    remove: 'Remove',
    recordingTimeLimit: 'Recording time limit reached (30s)',
    startRecordingSuccess: 'Start recording...',
    voiceRecognizing: 'Recognizing voice...',
    selectImageFirst: 'Please select an image first',
    imageFormatError: 'Please upload JPG, JPEG or PNG format image',
    imageSizeError: 'Image size cannot exceed 10MB',
    imageAnalyzeComplete: 'Image analysis complete, found {count} related files',
    imageAnalyzeFailed: 'Image analysis failed',
    voiceRecognizeComplete: 'Voice recognition complete, found {count} related files',
    voiceRecognizeFailed: 'Voice recognition failed, please try again',
    searchComplete: 'Found {count} related files',
    searchFailed: 'Search failed, please try again',
    fileOpened: 'File opened: {filename}',
    fileOpenFailed: 'Failed to open file: {error}',
    filePathCopied: 'File path copied to clipboard: {path}',
    noMoreResults: 'No more results'
  },

  // Search
  search: {
    semantic: 'Semantic Search',
    fulltext: 'Full-text Search',
    hybrid: 'Hybrid Search',
    searchType: 'Search Type',
    fileType: 'File Type',
    threshold: 'Similarity',
    results: 'Search Results',
    resultsCount: 'Found {count} results',
    searchTime: '{time}s elapsed',
    loadMore: 'Load More Results',
    noResults: 'No related files found',
    options: 'Search Options',
    searching: 'Searching...',
    searchComplete: 'Search Complete',
    query: 'Search Query',
    limit: 'Result Limit',
    sortBy: 'Sort By',
    relevance: 'Relevance',
    dateDesc: 'Date (Newest)',
    dateAsc: 'Date (Oldest)',
    nameAsc: 'Name (A-Z)',
    nameDesc: 'Name (Z-A)',
    sizeDesc: 'Size (Largest)',
    sizeAsc: 'Size (Smallest)'
  },

  // Search Result Card
  searchResult: {
    matchDegree: 'Match Degree',
    open: 'Open',
    copyPath: 'Copy Path',
    semanticMatch: 'Semantic Match',
    fulltextMatch: 'Full-text Match',
    hybridMatch: 'Hybrid Match',
    copySuccess: 'File path copied to clipboard',
    copyFailed: 'Copy failed, please copy manually',
    justNow: 'Just now',
    minutesAgo: '{minutes} minutes ago',
    hoursAgo: '{hours} hours ago',
    yesterday: 'Yesterday',
    daysAgo: '{days} days ago'
  },

  // File Types
  fileType: {
    all: 'All Files',
    document: 'Documents',
    audio: 'Audio',
    video: 'Video',
    image: 'Images',
    other: 'Other',
    text: 'Text Files',
    pdf: 'PDF Documents',
    word: 'Word Documents',
    excel: 'Excel Spreadsheets',
    powerpoint: 'PowerPoint Presentations',
    markdown: 'Markdown Documents',
    code: 'Code Files'
  },

  // Settings Page
  settings: {
    title: 'Settings',
    subtitle: 'Configure application and AI models',
    general: 'General Settings',
    aiModel: 'AI Model Configuration',
    index: 'Index Management',
    advanced: 'Advanced Settings',
    about: 'About',
    language: 'Language',
    theme: 'Theme',
    themeLight: 'Light',
    themeDark: 'Dark',
    themeAuto: 'System',
    startupLaunch: 'Launch at Startup',
    minimizeToTray: 'Minimize to Tray',
    notifications: 'Notifications',
    autoUpdate: 'Auto Update',
    clearCache: 'Clear Cache',
    resetSettings: 'Reset Settings',
    settingsReset: 'Settings have been reset',
    cacheCleared: 'Cache has been cleared'
  },

  // AI Model Configuration
  aiModel: {
    title: 'AI Model Configuration',
    subtitle: 'Configure cloud APIs and local models',
    provider: 'Provider',
    model: 'Model',
    apiKey: 'API Key',
    apiUrl: 'API URL',
    enable: 'Enable',
    disable: 'Disable',
    test: 'Test Connection',
    testSuccess: 'Connection test successful',
    testFailed: 'Connection test failed',
    configSaved: 'Configuration saved',
    localModel: 'Local Model',
    cloudApi: 'Cloud API',
    textEmbedding: 'Text Embedding',
    voiceRecognition: 'Voice Recognition',
    imageUnderstanding: 'Image Understanding',
    llm: 'Large Language Model',
    ollama: 'Ollama',
    openai: 'OpenAI',
    claude: 'Claude',
    aliyun: 'Alibaba Cloud',
    modelPath: 'Model Path',
    device: 'Device',
    deviceCpu: 'CPU',
    deviceCuda: 'CUDA (GPU)',
    deviceMps: 'MPS (Apple Silicon)',
    batchSize: 'Batch Size',
    maxLength: 'Max Length',
    temperature: 'Temperature',
    topP: 'Top P',
    topK: 'Top K',
    frequencyPenalty: 'Frequency Penalty',
    presencePenalty: 'Presence Penalty'
  },

  // Index Management
  index: {
    title: 'Index Management',
    subtitle: 'Create, update and manage file indexes',
    create: 'Create Index',
    update: 'Update Index',
    rebuild: 'Rebuild Index',
    delete: 'Delete Index',
    pause: 'Pause',
    resume: 'Resume',
    status: 'Status',
    indexed: 'Indexed',
    total: 'Total',
    progress: 'Progress',
    speed: 'Speed',
    remaining: 'Remaining',
    elapsed: 'Elapsed',
    createdAt: 'Created At',
    updatedAt: 'Updated At',
    lastIndexed: 'Last Indexed',
    processingTime: 'Processing Time',
    fileCount: 'File Count',
    totalSize: 'Total Size',
    errorCount: 'Error Count',
    activeTasks: 'Active Tasks',
    successRate: 'Success Rate',
    indexing: 'Indexing...',
    indexingPaused: 'Indexing Paused',
    indexingComplete: 'Indexing Complete',
    indexingFailed: 'Indexing Failed',
    noIndex: 'No Index',
    indexCreated: 'Index created',
    indexUpdated: 'Index updated',
    indexDeleted: 'Index deleted',
    indexPaused: 'Index paused',
    indexResumed: 'Index resumed',
    confirmDelete: 'Confirm to delete this index?',
    confirmRebuild: 'Confirm to rebuild index? This will delete the existing index and recreate.',
    addPath: 'Add Path',
    removePath: 'Remove Path',
    indexPaths: 'Index Paths',
    includePaths: 'Include Paths',
    excludePaths: 'Exclude Paths',
    scanDepth: 'Scan Depth',
    followSymlinks: 'Follow Symlinks',
    indexMetadata: 'Index Metadata',
    indexContent: 'Index Content',
    autoUpdate: 'Auto Update',
    updateInterval: 'Update Interval',
    realtime: 'Real-time Update',
    durationMinutes: '{minutes}m {seconds}s'
  },

  // System Information
  system: {
    version: 'Version',
    build: 'Build',
    platform: 'Platform',
    arch: 'Architecture',
    nodeVersion: 'Node Version',
    electronVersion: 'Electron Version',
    chromeVersion: 'Chrome Version',
    pythonVersion: 'Python Version',
    status: 'Status',
    running: 'Running',
    stopped: 'Stopped',
    connected: 'Connected',
    disconnected: 'Disconnected',
    healthy: 'Healthy',
    unhealthy: 'Unhealthy',
    uptime: 'Uptime',
    memory: 'Memory',
    cpu: 'CPU',
    disk: 'Disk',
    network: 'Network'
  },

  // About Page
  about: {
    title: 'About Author',
    subtitle: 'XiaoyaoSearch Developer Information',
    description: 'XiaoyaoSearch is a local desktop application designed for knowledge workers, content creators, and technical developers. Through integrated AI models, it supports multiple input methods such as voice, text, and images to convert user queries into semantic intelligence for deep retrieval of local files.',
    version: 'Version',
    license: 'License',
    authorName: 'Author',
    homepage: 'Homepage',
    repository: 'Repository',
    changelog: 'Changelog',
    dependencies: 'Dependencies',
    acknowledgments: 'Acknowledgments',
    privacyPolicy: 'Privacy Policy',
    termsOfService: 'Terms of Service',
    checkUpdate: 'Check for Updates',
    updateAvailable: 'New version available',
    updateNotAvailable: 'Up to date',
    downloadUpdate: 'Download Update',
    installUpdate: 'Install Update',
    author: {
      cardTitle: 'About Author',
      avatarAlt: 'Author avatar',
      description: 'IT Solution Architect | One-Person Company Practitioner. Focused on AI-driven productivity tool development, dedicated to creating smarter and safer local search solutions for knowledge workers. Advocates for data sovereignty and privacy protection, believes excellent tools should empower individuals rather than monitor users.',
      visionLabel: 'Development Philosophy:',
      visionText: 'Simple but not simplistic, smart but not invasive',
      missionLabel: 'Brand Mission:',
      missionText: 'Create AI tools that truly serve individual users, let technology empower rather than monitor, protect your data sovereignty',
      wechatPublicAccount: 'WeChat Official Account',
      wechatAccountName: 'XiaoyaoSearch',
      wechatQrAlt: 'WeChat Official Account QR Code',
      scanToFollow: 'Scan to Follow',
      addWechatTitle: 'Add Author WeChat',
      addWechatDesc: 'Connect for Product Experience',
      authorWechatQrAlt: 'Author WeChat QR Code',
      scanToAdd: 'Scan to Add',
      qrPreparing: 'QR Code Preparing'
    }
  },

  // Messages
  message: {
    success: 'Operation successful',
    error: 'Operation failed',
    warning: 'Warning',
    info: 'Information',
    confirmDelete: 'Confirm to delete?',
    confirmLogout: 'Confirm to logout?',
    unsavedChanges: 'There are unsaved changes, are you sure to leave?',
    networkError: 'Network connection failed',
    serverError: 'Server error',
    requestTimeout: 'Request timeout',
    unauthorized: 'Unauthorized',
    forbidden: 'Forbidden',
    notFound: 'Not found',
    methodNotAllowed: 'Method not allowed',
    internalServerError: 'Internal server error',
    serviceUnavailable: 'Service unavailable',
    unknownError: 'Unknown error'
  },

  // Validation Messages
  validation: {
    required: 'This field is required',
    invalidFormat: 'Invalid format',
    tooShort: 'Too short',
    tooLong: 'Too long',
    invalidEmail: 'Invalid email format',
    invalidUrl: 'Invalid URL format',
    invalidNumber: 'Invalid number format',
    outOfRange: 'Out of range',
    duplicate: 'Duplicate value',
    notMatch: 'Does not match'
  },

  // Error Messages
  error: {
    loadFailed: 'Load failed',
    saveFailed: 'Save failed',
    deleteFailed: 'Delete failed',
    updateFailed: 'Update failed',
    uploadFailed: 'Upload failed',
    downloadFailed: 'Download failed',
    copyFailed: 'Copy failed',
    pasteFailed: 'Paste failed',
    searchFailed: 'Search failed',
    indexFailed: 'Index failed',
    modelLoadFailed: 'Model load failed',
    apiConnectionFailed: 'API connection failed',
    fileNotFound: 'File not found',
    pathNotFound: 'Path not found',
    permissionDenied: 'Permission denied',
    diskFull: 'Disk full',
    memoryInsufficient: 'Insufficient memory',
    networkUnavailable: 'Network unavailable',
    invalidParameter: 'Invalid parameter',
    missingParameter: 'Missing parameter',
    operationCancelled: 'Operation cancelled',
    operationTimeout: 'Operation timeout',
    microphoneAccessDenied: 'Unable to access microphone, please check permissions',
    recordingFailed: 'Recording failed',
    voiceRecognizeFailed: 'Voice to text failed',
    imageAnalyzeFailed: 'Image analysis failed',
    fileOpenFailed: 'Failed to open file',
    configLoadFailed: 'Failed to load AI model configuration',
    configSaveFailed: 'Failed to save configuration',
    speechConfigSaveFailed: 'Failed to save speech recognition configuration',
    llmConfigSaveFailed: 'Failed to save LLM configuration',
    visionConfigSaveFailed: 'Failed to save vision model configuration',
    embeddingConfigSaveFailed: 'Failed to save embedding model configuration',
    speechModelTestFailed: 'Speech recognition model test failed',
    llmModelTestFailed: 'LLM test failed',
    visionModelTestFailed: 'Vision model test failed',
    embeddingModelTestFailed: 'Embedding model test failed'
  },

  // HTTP Error Messages
  http: {
    requestError: 'Request error',
    responseError: 'Response error',
    badRequest: 'Bad request',
    unauthorized: 'Unauthorized',
    forbidden: 'Forbidden',
    notFound: 'Resource not found',
    validationFailed: 'Validation failed',
    internalServerError: 'Internal server error',
    requestFailed: 'Request failed',
    networkError: 'Network connection failed, please check if backend service is running',
    configError: 'Request configuration error'
  },

  // Index Status
  indexStatus: {
    statusPending: 'Pending',
    statusProcessing: 'Processing',
    statusCompleted: 'Completed',
    statusFailed: 'Failed'
  },

  // Settings Page - Speech Settings
  settingsSpeech: {
    title: 'Speech Settings',
    subtitle: 'Configure basic parameters',
    voiceRecognitionSettings: 'Voice Recognition Settings',
    voiceRecognition: 'Voice Recognition',
    localFastWhisperService: 'Local FastWhisper Service',
    localFastWhisperDesc: 'Use locally deployed FastWhisper model for speech recognition',
    modelVersion: 'Model Version',
    modelBase: 'Base (Fast)',
    modelSmall: 'Small (Balanced)',
    modelMedium: 'Medium (Accurate)',
    modelLarge: 'Large (High Accuracy)',
    runningDevice: 'Running Device',
    deviceCpu: 'CPU',
    deviceCuda: 'CUDA (GPU)',
    checkAvailability: 'Check Availability',
    saveSettings: 'Save Settings',
    saveSuccessRestart: 'Speech recognition configuration saved successfully, restart application to take effect',
    pleaseSaveFirst: 'Please save speech recognition configuration first'
  },

  // Settings Page - LLM Settings
  settingsLLM: {
    title: 'Large Language Model',
    subtitle: 'Configure LLM parameters',
    llmService: 'LLM Service',
    localOllamaService: 'Local Ollama Service',
    localOllamaDesc: 'Use locally deployed Ollama service to run large language models',
    modelName: 'Model Name',
    modelNamePlaceholder: 'e.g.: qwen2.5:1.5b',
    modelNameHelp: 'Enter installed Ollama model name, any format supported',
    serviceUrl: 'Service URL',
    serviceUrlPlaceholder: 'http://localhost:11434',
    testConnection: 'Test Connection',
    saveSuccessRestart: 'LLM configuration saved successfully, restart application to take effect',
    pleaseSaveFirst: 'Please save LLM configuration first',
    testData: 'Hello, please introduce yourself'
  },

  // Settings Page - Vision Model Settings
  settingsVision: {
    title: 'Vision Model',
    subtitle: 'Configure image understanding model',
    visionModel: 'Vision Model',
    localCNClipService: 'Local CN-CLIP Model',
    localCNClipDesc: 'Use locally deployed Chinese CLIP model for image understanding',
    modelVersion: 'Model Version',
    modelChineseClip: 'OFA-Sys/chinese-clip-vit-base-patch16',
    runningDevice: 'Running Device',
    deviceCpu: 'CPU',
    deviceCuda: 'CUDA (GPU)',
    testConnection: 'Test Connection',
    saveSuccessRestart: 'Vision model configuration saved successfully, restart application to take effect',
    pleaseSaveFirst: 'Please save vision model configuration first'
  },

  // Settings Page - Embedding Model Settings
  settingsEmbedding: {
    title: 'Embedding Model',
    subtitle: 'Configure text embedding model',
    textEmbeddingModel: 'Text Embedding Model',
    localBgeM3Service: 'Local BGE-M3 Model',
    localBgeM3Desc: 'Use locally deployed BGE-M3 model to generate text vector embeddings',
    modelVersion: 'Model Version',
    modelBgeM3: 'BAAI/bge-m3',
    runningDevice: 'Running Device',
    deviceCpu: 'CPU',
    deviceCuda: 'CUDA (GPU)',
    testConnection: 'Test Connection',
    saveSuccessRestart: 'Embedding model configuration saved successfully, restart application to take effect',
    pleaseSaveFirst: 'Please save embedding model configuration first',
    testData: 'This is a test text used to verify the functionality of the text embedding model.'
  },

  // Settings Page - General Settings
  settingsGeneral: {
    title: 'General Settings',
    subtitle: 'Configure application basic parameters',
    defaultResultCount: 'Default Result Count',
    similarityThreshold: 'Similarity Threshold',
    maxFileSize: 'Max File Size',
    searchOptions: 'Search Options'
  },

  // Navigation Menu
  nav: {
    home: 'Home',
    settings: 'Settings',
    index: 'Index',
    help: 'Help',
    about: 'About Author'
  },

  // User Information
  user: {
    name: 'Xiaoyao User',
    aboutAuthor: 'About Author'
  },

  // System Status
  status: {
    indexedFiles: 'Indexed Files',
    count: '',
    indexSize: 'Index Size',
    todaySearches: 'Today Searches',
    times: 'times',
    system: 'System',
    normal: 'Normal',
    abnormal: 'Abnormal',
    unknown: 'Unknown',
    lastUpdate: 'Last Update',
    statusUpdateFailed: 'System status update failed, using cached data'
  },

  // Help Page
  help: {
    title: 'Help & About',
    subtitle: 'Learn how to use XiaoyaoSearch and solve common problems',
    tabGuide: 'Quick Start',
    tabTutorial: 'Tutorial',
    tabFaq: 'FAQ',
    tabAbout: 'About',
    guide: {
      step1: {
        title: 'Configure AI Models',
        description: 'Go to settings page to configure local AI model services, ensure all services are running properly',
        button: 'Go to Settings'
      },
      step2: {
        title: 'Add Index Folder',
        description: 'Go to index management page, add folders to search and create file indexes',
        button: 'Go to Index'
      },
      step3: {
        title: 'Start Multimodal Search',
        description: 'Use voice, text, and image inputs for intelligent search on the main page',
        button: 'Start Search'
      }
    },
    features: {
      title: 'Core Features',
      voice: {
        title: 'Voice Search',
        description: 'Supports up to 30s voice input, FastWhisper local recognition'
      },
      image: {
        title: 'Image Search',
        description: 'Upload PNG/JPG images, CN-CLIP model understands content'
      },
      semantic: {
        title: 'Semantic Understanding',
        description: 'BGE-M3 vector embedding + Ollama LLM understanding'
      }
    },
    tutorial: {
      panel1: {
        header: 'How to configure local AI models?',
        content: {
          stepsTitle: 'Local Model Configuration Steps:',
          step1: { label: 'Speech Recognition Model:', text: 'Settings → Speech Settings → Select FastWhisper model version' },
          step2: { label: 'Large Language Model:', text: 'Settings → LLM Settings → Configure Ollama service address' },
          step3: { label: 'Vision Understanding Model:', text: 'Settings → Vision Model → Select CN-CLIP model' },
          step4: { label: 'Text Embedding Model:', text: 'Settings → Embedding Model → Select BGE-M3 model' },
          step5: { label: 'Device Selection:', text: 'Choose CPU or CUDA acceleration based on your hardware' },
          tip: 'Tip: For first-time use, it is recommended to use CPU mode first, ensure functionality works before enabling GPU acceleration'
        }
      },
      panel2: {
        header: 'How to perform multimodal search?',
        content: {
          modesTitle: 'Multimodal Search Methods:',
          mode1: { label: 'Text Search:', text: 'Enter keywords in the search box, natural language supported' },
          mode2: { label: 'Voice Search:', text: 'Click microphone button, speak search content (within 30s)' },
          mode3: { label: 'Image Search:', text: 'Upload PNG/JPG image, AI understands image content and searches related images' },
          fileTypesTitle: 'Supported File Types:',
          fileType1: { label: 'Documents:', text: 'txt, markdown, pdf, xls/xlsx, ppt/pptx, doc/docx' },
          fileType2: { label: 'Audio:', text: 'mp3, wav' },
          fileType3: { label: 'Video:', text: 'mp4, avi' },
          fileType4: { label: 'Images:', text: 'png, jpg, jpeg' },
          note: 'Note: Current version, image search only supports image-to-image search'
        }
      },
      panel3: {
        header: 'How to manage file indexes?',
        content: {
          guideTitle: 'Index Management Guide:',
          guide1: { label: 'Add Folder:', text: 'Index Management → Add Folder → Select file types' },
          guide2: { label: 'Monitor Progress:', text: 'View index status, progress, error messages' },
          guide3: { label: 'Smart Update:', text: 'Automatically determine whether incremental update or full rebuild is needed' },
          guide4: { label: 'View Details:', text: 'Understand index statistics, processing time, error logs' },
          statusTitle: 'Index Status Description:',
          status1: { label: 'Pending:', text: 'Index task created, waiting for processing' },
          status2: { label: 'Processing:', text: 'Scanning files and building index' },
          status3: { label: 'Completed:', text: 'Index built successfully, ready for search' },
          status4: { label: 'Failed:', text: 'Error occurred during indexing' }
        }
      },
      panel4: {
        header: 'Search Tips & Optimization',
        content: {
          tipsTitle: 'Search Optimization Tips:',
          tip1: { label: 'Natural Language:', text: 'Use everyday language to describe what you want to search' },
          tip2: { label: 'Keyword Combination:', text: 'Use multiple related keywords to improve accuracy' },
          tip3: { label: 'File Type Filter:', text: 'Specify specific file types to narrow search scope' },
          tip4: { label: 'Similarity Adjustment:', text: 'Settings → General Settings → Adjust similarity threshold' },
          resultsTitle: 'Result Understanding:',
          result1: { label: 'Relevance Score:', text: 'Shows match degree between file and query' },
          result2: { label: 'Content Summary:', text: 'Displays relevant content fragments from files' },
          result3: { label: 'File Path:', text: 'Shows full file path for easy location' }
        }
      }
    },
    faq: {
      panel1: {
        header: 'Voice recognition not working?',
        content: {
          causesTitle: 'Possible Causes:',
          cause1: 'FastWhisper model not properly installed or configured',
          cause2: 'Microphone permission not granted to application',
          cause3: 'Environmental noise too loud affecting recognition',
          cause4: 'Model version incompatible with device',
          solutionsTitle: 'Solutions:',
          solution1: 'Settings → Speech Settings → Check Availability',
          solution2: 'Try different model versions (tiny/base/small)',
          solution3: 'Perform voice input in quiet environment',
          solution4: 'Check system microphone permission settings'
        }
      },
      panel2: {
        header: 'Ollama connection failed?',
        content: {
          checkTitle: 'Check Steps:',
          check1: 'Confirm Ollama service started: http://localhost:11434',
          check2: 'Check if model installed: ollama list',
          check3: 'Verify service address configuration is correct',
          check4: 'Test network connection and firewall settings',
          commandsTitle: 'Common Commands:',
          command1: 'Install model:',
          command2: 'View models:',
          command3: 'Run model:'
        }
      },
      panel3: {
        header: 'No results for image search?',
        content: {
          reasonsTitle: 'Possible Causes:',
          reason1: 'CN-CLIP model not properly loaded',
          reason2: 'Image format not supported (only PNG/JPG)',
          reason3: 'Image content too complex or unclear',
          reason4: 'No related content files in index',
          tipsTitle: 'Optimization Suggestions:',
          tip1: 'Settings → Vision Model → Check Availability',
          tip2: 'Use clear, content-defined images',
          tip3: 'Try images containing text or obvious features',
          tip4: 'Ensure relevant file types are indexed'
        }
      },
      panel4: {
        header: 'Index building slow?',
        content: {
          factorsTitle: 'Affecting Factors:',
          factor1: 'File count and size',
          factor2: 'Selected file types',
          factor3: 'Hardware performance (CPU/GPU)',
          factor4: 'Model loading time',
          methodsTitle: 'Optimization Methods:',
          method1: 'Build indexes in batches, avoid processing too many files at once',
          method2: 'Select necessary file types, reduce processing burden',
          method3: 'Enable GPU acceleration (if available)',
          method4: 'Perform large file indexing during system idle time'
        }
      },
      panel5: {
        header: 'Inaccurate search results?',
        content: {
          improvementsTitle: 'Improvement Methods:',
          improvement1: 'Use more specific and detailed descriptions',
          improvement2: 'Try different expressions',
          improvement3: 'Adjust similarity threshold (Settings → General Settings)',
          improvement4: 'Ensure relevant files are properly indexed',
          improvement5: 'Check if BGE-M3 model is working properly',
          advancedTitle: 'Advanced Tips:',
          advanced1: 'Combine multiple modal inputs (e.g., voice + text)',
          advanced2: 'Use synonyms or related concepts',
          advanced3: 'Optimize search terms for file types'
        }
      }
    },
    about: {
      appDescription: 'Cross-platform local desktop application (Windows/MacOS/Linux) supporting multimodal AI intelligent search. Provides smarter file retrieval experience for knowledge workers through voice, text, and image inputs.',
      tagline: 'Local First · AI Enhanced · Privacy Secure',
      features: {
        voice: {
          title: 'Voice Search',
          description: '30s voice input, FastWhisper local recognition'
        },
        image: {
          title: 'Image Understanding',
          description: 'Upload images, CN-CLIP intelligent content analysis'
        },
        semantic: {
          title: 'Semantic Search',
          description: 'BGE-M3 vector embedding, understands query intent'
        }
      },
      techHighlight: {
        title: 'Fully Local, Privacy Worry-Free',
        description: 'All AI models deployed locally, your data never leaves your device. Supports offline use, ensuring information security and privacy protection.'
      }
    }
  }
}