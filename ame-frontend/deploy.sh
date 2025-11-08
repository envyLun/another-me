#!/bin/bash

# Another Me Frontend - Docker 快速部署脚本

set -e

IMAGE_NAME="another-me-frontend"
CONTAINER_NAME="another-me-frontend"
PORT=${1:-80}

echo "🚀 开始部署 Another Me 前端..."
echo ""

# 构建镜像
echo "📦 构建 Docker 镜像..."
docker build -t ${IMAGE_NAME}:latest .

# 停止旧容器
if docker ps -a | grep -q ${CONTAINER_NAME}; then
    echo "🛑 停止旧容器..."
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
fi

# 启动新容器
echo "▶️  启动容器..."
docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${PORT}:80 \
    --restart unless-stopped \
    ${IMAGE_NAME}:latest

echo ""
echo "✅ 部署完成！"
echo ""
echo "📍 访问地址: http://localhost:${PORT}"
echo "📋 查看日志: docker logs -f ${CONTAINER_NAME}"
echo "🛑 停止服务: docker stop ${CONTAINER_NAME}"
echo ""
