#!/bin/bash
# 🚀 琥珀引擎GitHub安全同步脚本
# 功能: 自动同步任务日志到GitHub，确保Token安全
# 使用: ./github_sync.sh "提交描述"

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 进入仓库目录
REPO_DIR="/home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs"
cd "$REPO_DIR" || {
    log_error "无法进入仓库目录: $REPO_DIR"
    exit 1
}

log_info "开始GitHub安全同步检查"

# ==================== 安全检查阶段 ====================

# 1. 检查Git配置中是否有硬编码Token
log_info "检查Git配置中的Token泄露..."
if grep -q "ghp_" .git/config; then
    log_error "发现Git配置中包含Token，正在修复..."
    sed -i 's|https://ghp_.*@github.com|https://github.com|g' .git/config
    log_success "Git配置已修复"
fi

# 2. 检查文件中的Token泄露 (排除指南文件和脚本文件中的示例)
log_info "扫描文件中的Token泄露..."
TOKEN_FOUND=false
for file in $(find . -type f \( -name "*.json" -o -name "*.md" -o -name "*.txt" -o -name "*.py" -o -name "*.sh" \) ! -path "./.git/*" ! -path "./GITHUB_SYNC_GUIDE.md" ! -path "./scripts/github_sync.sh"); do
    if grep -q "ghp_" "$file"; then
        log_error "发现Token泄露: $file"
        TOKEN_FOUND=true
        # 显示泄露内容但不包含完整Token
        grep -o "ghp_[a-zA-Z0-9]\{4\}" "$file" | head -1 | while read -r leak; do
            log_error "泄露片段: ${leak}..."
        done
    fi
done

if [ "$TOKEN_FOUND" = true ]; then
    log_error "❌ 安全检查失败: 发现Token泄露，请立即处理"
    exit 1
fi
log_success "文件Token检查通过"

# 3. 检查敏感文件是否在.gitignore中
log_info "检查.gitignore配置..."
SENSITIVE_FILES=(".env" "*.key" "*.pem" "credentials.json" "*.log" "__pycache__/" "venv/")
for file in "${SENSITIVE_FILES[@]}"; do
    if ! grep -q "^$file$" .gitignore 2>/dev/null; then
        log_warning ".gitignore中缺少: $file"
        echo "$file" >> .gitignore
    fi
done
log_success ".gitignore检查完成"

# ==================== Git操作阶段 ====================

# 1. 检查是否有变更
log_info "检查Git状态..."
if git status --porcelain | grep -q "."; then
    CHANGES_COUNT=$(git status --porcelain | wc -l)
    log_info "发现 $CHANGES_COUNT 个变更"
    
    # 显示变更摘要
    git status --short
else
    log_info "📭 没有变更需要提交"
    exit 0
fi

# 2. 添加变更
log_info "添加变更到暂存区..."
git add .
log_success "变更已添加到暂存区"

# 3. 生成提交信息
if [ $# -ge 1 ]; then
    COMMIT_MSG="$1"
else
    COMMIT_MSG="[任务日志] $(date +'%Y-%m-%d %H:%M:%S') - 自动同步"
fi

# 添加任务编号检测
if [[ "$COMMIT_MSG" =~ \[([0-9]{4}-[0-9]{3})\] ]]; then
    TASK_NUMBER="${BASH_REMATCH[1]}"
    log_info "检测到任务编号: $TASK_NUMBER"
fi

# 4. 提交变更
log_info "提交变更: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"
COMMIT_HASH=$(git rev-parse --short HEAD)
log_success "提交完成: $COMMIT_HASH"

# ==================== GitHub推送阶段 ====================

# 1. 检查GitHub Token
if [ -z "${GITHUB_TOKEN:-}" ]; then
    log_warning "GITHUB_TOKEN环境变量未设置"
    log_info "请设置环境变量: export GITHUB_TOKEN=your_token_here"
    log_info "或者使用: GITHUB_TOKEN=your_token_here ./github_sync.sh"
    log_info "本地提交已完成，等待手动推送"
    exit 0
fi

# 2. 安全推送
log_info "开始推送到GitHub..."
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if git push https://${GITHUB_TOKEN}@github.com/oceanuf/amber-sentry-logs.git main; then
        log_success "✅ GitHub推送成功"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            log_warning "推送失败，第 $RETRY_COUNT 次重试 (等待5秒)..."
            sleep 5
        else
            log_error "❌ GitHub推送失败，已达最大重试次数"
            exit 1
        fi
    fi
done

# ==================== 清理阶段 ====================

# 1. 清理环境变量 (安全考虑)
unset GITHUB_TOKEN

# 2. 清理命令行历史中的Token
if [ -n "$BASH" ]; then
    history -c
    history -w
fi

# 3. 生成同步报告
SYNC_LOG="/tmp/github_sync_$(date +%Y%m%d_%H%M%S).log"
{
    echo "=== GitHub同步报告 ==="
    echo "时间: $(date)"
    echo "仓库: $(git remote get-url origin | sed 's|https://.*@||')"
    echo "提交: $COMMIT_HASH"
    echo "信息: $COMMIT_MSG"
    echo "变更数量: $CHANGES_COUNT"
    echo "状态: 成功"
} > "$SYNC_LOG"

log_info "同步报告已保存: $SYNC_LOG"

# 4. 显示最终状态
log_success "🎉 GitHub同步完成"
echo ""
echo "📊 同步摘要:"
echo "   仓库: amber-sentry-logs"
echo "   分支: main"
echo "   提交: $COMMIT_HASH"
echo "   时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "   变更: $CHANGES_COUNT 个文件"
echo ""

# 显示最新提交
log_info "最新提交记录:"
git log --oneline -3

exit 0