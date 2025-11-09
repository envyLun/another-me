#!/bin/bash
# AME 冗余模块清理脚本
# 生成时间: 2025-11-09
# 警告: 此脚本将永久删除旧模块，请确保已备份！

set -e  # 遇到错误立即退出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "AME 架构优化 - 冗余模块清理脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 确认提示
echo -e "${YELLOW}警告: 此操作将删除以下目录和文件:${NC}"
echo "  - engines/"
echo "  - mem/"
echo "  - rag/"
echo "  - rag_generator/"
echo "  - storage/"
echo "  - retrieval/"
echo "  - search/"
echo ""
echo -e "${RED}删除的文件将无法恢复！${NC}"
echo ""
read -p "确认继续? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "操作已取消"
    exit 0
fi

echo ""
echo "=========================================="
echo "Phase 1: 备份当前状态"
echo "=========================================="

BACKUP_DIR="../ame_backup_$(date +%Y%m%d_%H%M%S)"
echo "创建备份目录: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# 备份即将删除的目录
if [ -d "engines" ]; then
    echo "备份 engines/ ..."
    cp -r engines "$BACKUP_DIR/"
fi

if [ -d "mem" ]; then
    echo "备份 mem/ ..."
    cp -r mem "$BACKUP_DIR/"
fi

if [ -d "rag" ]; then
    echo "备份 rag/ ..."
    cp -r rag "$BACKUP_DIR/"
fi

if [ -d "rag_generator" ]; then
    echo "备份 rag_generator/ ..."
    cp -r rag_generator "$BACKUP_DIR/"
fi

if [ -d "storage" ]; then
    echo "备份 storage/ ..."
    cp -r storage "$BACKUP_DIR/"
fi

if [ -d "retrieval" ]; then
    echo "备份 retrieval/ ..."
    cp -r retrieval "$BACKUP_DIR/"
fi

if [ -d "search" ]; then
    echo "备份 search/ ..."
    cp -r search "$BACKUP_DIR/"
fi

echo -e "${GREEN}✓ 备份完成: $BACKUP_DIR${NC}"
echo ""

echo "=========================================="
echo "Phase 2: 删除冗余模块"
echo "=========================================="

# 删除旧引擎目录
if [ -d "engines" ]; then
    echo "删除 engines/ ..."
    rm -rf engines/
    echo -e "${GREEN}✓ 已删除 engines/${NC}"
else
    echo -e "${YELLOW}⊘ engines/ 不存在，跳过${NC}"
fi

# 删除旧 MEM 目录
if [ -d "mem" ]; then
    echo "删除 mem/ ..."
    rm -rf mem/
    echo -e "${GREEN}✓ 已删除 mem/${NC}"
else
    echo -e "${YELLOW}⊘ mem/ 不存在，跳过${NC}"
fi

# 删除旧 RAG 目录
if [ -d "rag" ]; then
    echo "删除 rag/ ..."
    rm -rf rag/
    echo -e "${GREEN}✓ 已删除 rag/${NC}"
else
    echo -e "${YELLOW}⊘ rag/ 不存在，跳过${NC}"
fi

# 删除旧 RAG Generator
if [ -d "rag_generator" ]; then
    echo "删除 rag_generator/ ..."
    rm -rf rag_generator/
    echo -e "${GREEN}✓ 已删除 rag_generator/${NC}"
else
    echo -e "${YELLOW}⊘ rag_generator/ 不存在，跳过${NC}"
fi

# 删除旧 Storage 目录
if [ -d "storage" ]; then
    echo "删除 storage/ ..."
    rm -rf storage/
    echo -e "${GREEN}✓ 已删除 storage/${NC}"
else
    echo -e "${YELLOW}⊘ storage/ 不存在，跳过${NC}"
fi

# 删除旧 Retrieval 目录
if [ -d "retrieval" ]; then
    echo "删除 retrieval/ ..."
    rm -rf retrieval/
    echo -e "${GREEN}✓ 已删除 retrieval/${NC}"
else
    echo -e "${YELLOW}⊘ retrieval/ 不存在，跳过${NC}"
fi

# 删除旧 Search 目录
if [ -d "search" ]; then
    echo "删除 search/ ..."
    rm -rf search/
    echo -e "${GREEN}✓ 已删除 search/${NC}"
else
    echo -e "${YELLOW}⊘ search/ 不存在，跳过${NC}"
fi

echo ""
echo "=========================================="
echo "Phase 3: 清理 __init__.py 导入"
echo "=========================================="

INIT_FILE="__init__.py"
if [ -f "$INIT_FILE" ]; then
    echo "备份 $INIT_FILE ..."
    cp "$INIT_FILE" "${INIT_FILE}.bak"
    
    echo "清理旧模块导入 ..."
    # 注释掉旧模块的导入
    sed -i.tmp '/from \.engines\./s/^/# DEPRECATED: /' "$INIT_FILE"
    sed -i.tmp '/from \.mem\./s/^/# DEPRECATED: /' "$INIT_FILE"
    sed -i.tmp '/from \.rag\./s/^/# DEPRECATED: /' "$INIT_FILE"
    sed -i.tmp '/from \.rag_generator\./s/^/# DEPRECATED: /' "$INIT_FILE"
    sed -i.tmp '/from \.storage\.falkor_store/s/^/# DEPRECATED: /' "$INIT_FILE"
    sed -i.tmp '/from \.retrieval\./s/^/# DEPRECATED: /' "$INIT_FILE"
    sed -i.tmp '/from \.search\./s/^/# DEPRECATED: /' "$INIT_FILE"
    
    # 删除临时文件
    rm -f "${INIT_FILE}.tmp"
    
    echo -e "${GREEN}✓ 已更新 __init__.py${NC}"
else
    echo -e "${YELLOW}⊘ __init__.py 不存在，跳过${NC}"
fi

echo ""
echo "=========================================="
echo "Phase 4: 验证清理结果"
echo "=========================================="

echo "检查剩余目录结构 ..."
echo ""
tree -L 1 -d --charset ascii || ls -1

echo ""
echo "统计代码行数 ..."
if command -v cloc &> /dev/null; then
    cloc . --exclude-dir=__pycache__,tests,.pytest_cache
else
    echo -e "${YELLOW}⊘ cloc 未安装，跳过代码统计${NC}"
    echo "   (可通过 'brew install cloc' 或 'pip install cloc' 安装)"
fi

echo ""
echo "=========================================="
echo "清理完成!"
echo "=========================================="
echo ""
echo -e "${GREEN}✓ 冗余模块已删除${NC}"
echo -e "${GREEN}✓ 备份已保存至: $BACKUP_DIR${NC}"
echo ""
echo "下一步操作:"
echo "  1. 运行测试: pytest tests/"
echo "  2. 检查导入错误: python -c 'import ame'"
echo "  3. 开始 Services Layer 重构"
echo ""
echo "如需恢复，请执行:"
echo "  cp -r $BACKUP_DIR/* ."
echo ""
