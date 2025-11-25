#!/bin/bash

echo "初始化小遥搜索开发环境..."

# 1. 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 2. 检查Node.js版本
node_version=$(node --version 2>&1)
echo "Node.js版本: $node_version"

# 3. 创建Python虚拟环境
echo "创建Python虚拟环境..."
cd backend
python3 -m venv venv

# Windows系统使用不同的激活命令
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# 4. 安装Python依赖
echo "安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. 安装前端依赖
echo "安装前端依赖..."
cd ../frontend
npm install

# 6. 创建数据目录
echo "创建数据目录结构..."
mkdir -p ../data/database
mkdir -p ../data/indexes/faiss
mkdir -p ../data/indexes/whoosh
mkdir -p ../data/configs
mkdir -p ../models/bge-m3
mkdir -p ../models/faster-whisper
mkdir -p ../models/cn-clip

# 7. 创建环境配置文件
echo "创建环境配置文件..."
cd ../backend
cat > .env << EOF
# 小遥搜索后端环境配置
APP_NAME=小遥搜索
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# 数据库配置
DATABASE_URL=sqlite:///../data/database/xiaoyaosearch.db

# AI模型配置
BGE_M3_MODEL_PATH=../data/models/bge-m3
FASTER_WHISPER_MODEL_SIZE=base
CN_CLIP_MODEL_PATH=../data/models/cn-clip

# 索引配置
FAISS_INDEX_PATH=../data/indexes/faiss
WHOOSH_INDEX_PATH=../data/indexes/whoosh

# 云端API配置（可选）
ALIBABA_CLOUD_ACCESS_KEY_ID=
ALIBABA_CLOUD_ACCESS_KEY_SECRET=
ALIBABA_CLOUD_REGION=cn-hangzhou
EOF

cd ../frontend
cat > .env << EOF
# 小遥搜索前端环境配置
VITE_APP_TITLE=小遥搜索
VITE_API_BASE_URL=http://localhost:8000
VITE_AI_MODEL_ENDPOINT=http://localhost:8000/api
EOF

echo "环境初始化完成"
echo ""
echo "启动开发服务:"
echo "1. 启动后端: cd backend && source venv/bin/activate && python main.py"
echo "2. 启动前端: cd frontend && npm run electron:dev"
echo ""
echo "或者使用启动脚本: ./start_dev.sh"