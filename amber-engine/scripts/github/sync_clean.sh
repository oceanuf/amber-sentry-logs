#!/bin/bash
# GitHub同步安全清理脚本 V1.0.0
# 基于[2614-001]档案馆单体仓库同步法典 V3.1
# 生效日期: 2026-03-30

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${RED}错误: 必须提供提交信息${NC}"
    echo "用法: $0 \"[前缀]: 描述 (关联任务号)\""
    echo "示例: $0 \"[ARCH]: 目录结构重构 (2614-001)\""
    exit 1
fi

COMMIT_MSG="$1"
REPO_ROOT="."

echo -e "${GREEN}=== GitHub同步安全清理脚本启动 ===${NC}"
echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "提交信息: $COMMIT_MSG"
echo "仓库根目录: $REPO_ROOT"
echo ""

# 步骤1: 安全检查 - 三不原则
echo -e "${YELLOW}[步骤1] 安全防线检查 (三不原则)${NC}"

# 1.1 检查硬编码Token
echo "检查硬编码Token..."
# 排除脚本自身的检查逻辑和注释
if grep -r "ghp_" "$REPO_ROOT" --include="*.sh" --include="*.py" --include="*.php" --include="*.js" --include="*.json" 2>/dev/null | grep -v "sync_clean.sh" | grep -v "github_sync_safe.sh" | grep -v "检查硬编码Token" | grep -v "不泄露Token" | grep -v "#" | grep -v "echo"; then
    echo -e "${RED}❌ 发现硬编码Token (违反安全防线协议)${NC}"
    grep -r "ghp_" "$REPO_ROOT" --include="*.sh" --include="*.py" --include="*.php" --include="*.js" --include="*.json" 2>/dev/null | grep -v "sync_clean.sh" | grep -v "github_sync_safe.sh" | grep -v "检查硬编码Token" | grep -v "不泄露Token" | grep -v "#" | grep -v "echo"
    exit 1
fi
echo -e "${GREEN}✅ 无硬编码Token${NC}"

# 1.2 检查绝对路径泄露
echo "检查绝对路径泄露..."
# 检查绝对路径模式，排除合理的相对路径和文档中的示例路径
if grep -r "/home/luckyelite" "$REPO_ROOT" --include="*.sh" --include="*.py" --include="*.php" --include="*.js" 2>/dev/null | grep -v "#" | grep -v "echo" | grep -v "示例"; then
    echo -e "${RED}❌ 发现绝对路径泄露 (违反安全防线协议)${NC}"
    grep -r "/home/luckyelite" "$REPO_ROOT" --include="*.sh" --include="*.py" --include="*.php" --include="*.js" 2>/dev/null | grep -v "#" | grep -v "echo" | grep -v "示例"
    exit 1
fi
echo -e "${GREEN}✅ 无绝对路径泄露${NC}"

# 1.3 检查敏感文件
echo "检查敏感文件..."
SENSITIVE_FILES=(".env" "private_*.json" "config_*.json")
for pattern in "${SENSITIVE_FILES[@]}"; do
    if find "$REPO_ROOT" -name "$pattern" -type f -not -path "*/_PRIVATE_DATA/*" -not -path "*/.git/*" -not -path "*/amber-sentry-logs/*" 2>/dev/null | grep -q .; then
        echo -e "${RED}❌ 发现敏感文件: $pattern (违反安全防线协议)${NC}"
        find "$REPO_ROOT" -name "$pattern" -type f -not -path "*/_PRIVATE_DATA/*" -not -path "*/.git/*" -not -path "*/amber-sentry-logs/*" 2>/dev/null
        exit 1
    fi
done
echo -e "${GREEN}✅ 无敏感文件${NC}"

# 步骤2: 目录结构检查
echo -e "${YELLOW}[步骤2] 物理拓扑检查${NC}"

REQUIRED_DIRS=("web" "vaults" "docs/reports" "scripts" "database")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$REPO_ROOT/$dir" ]; then
        echo -e "${RED}❌ 缺少必需目录: $dir (违反物理拓扑准则)${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ 目录结构完整${NC}"

# 步骤3: Git操作
echo -e "${YELLOW}[步骤3] Git同步操作${NC}"

cd "$REPO_ROOT"

# 3.1 检查git状态
if ! git status &>/dev/null; then
    echo -e "${RED}❌ 不是Git仓库或Git未初始化${NC}"
    exit 1
fi

# 3.2 添加文件 (仅限法典允许的目录)
ALLOWED_PATHS=("web/" "vaults/" "docs/" "scripts/" "database/")
for path in "${ALLOWED_PATHS[@]}"; do
    if [ -d "$path" ] || [ -f "$path" ]; then
        echo "添加: $path"
        git add "$path"
    fi
done

# 3.3 提交
echo "提交更改..."
if git commit -m "$COMMIT_MSG" 2>/dev/null; then
    echo -e "${GREEN}✅ 提交成功${NC}"
else
    echo -e "${YELLOW}⚠️ 无更改可提交${NC}"
    exit 0
fi

# 3.4 推送
echo "推送到远程仓库..."
if git push origin main 2>/dev/null; then
    echo -e "${GREEN}✅ 推送成功${NC}"
else
    echo -e "${RED}❌ 推送失败${NC}"
    exit 1
fi

echo -e "${GREEN}=== GitHub同步完成 ===${NC}"
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "提交哈希: $(git rev-parse --short HEAD)"
echo ""

# 生成执行报告
REPORT_FILE="$REPO_ROOT/docs/reports/github-sync-$(date '+%Y%m%d_%H%M%S').md"
cat > "$REPORT_FILE" << EOF
# GitHub同步执行报告
**同步时间**: $(date '+%Y-%m-%d %H:%M:%S')
**提交信息**: $COMMIT_MSG
**提交哈希**: $(git rev-parse --short HEAD)
**执行脚本**: sync_clean.sh V1.0.0
**法典依据**: [2614-001]档案馆单体仓库同步法典 V3.1

## 安全检查结果
- ✅ 无硬编码Token
- ✅ 无绝对路径泄露  
- ✅ 无敏感文件
- ✅ 目录结构完整

## 同步内容
$(git log --oneline -1)

## 执行状态
✅ 同步成功完成

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**执行者**: 工程师 Cheese 🧀
EOF

echo -e "${GREEN}📄 执行报告已生成: $REPORT_FILE${NC}"