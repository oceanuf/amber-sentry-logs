#!/bin/bash
# 安全的GitHub同步脚本（不包含硬编码令牌）

set -e

WORKSPACE_DIR="/home/luckyelite/.openclaw/workspace/amber-engine"
cd "$WORKSPACE_DIR"

# 检查环境变量
if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "❌ 错误: GITHUB_TOKEN环境变量未设置"
    echo "请设置环境变量: export GITHUB_TOKEN=your_token_here"
    exit 1
fi

if [[ -z "$GITHUB_REPO" ]]; then
    echo "❌ 错误: GITHUB_REPO环境变量未设置"
    echo "请设置环境变量: export GITHUB_REPO=username/repo"
    exit 1
fi

# 配置Git用户
git config --global user.name "Cheese Intelligence Team"
git config --global user.email "cheese@cheese.ai"

echo "🔍 检查Git状态..."
git status

# 如果有未提交的更改
if [[ -n $(git status --porcelain) ]]; then
    echo "📝 发现未提交的更改"
    
    COMMIT_MSG="${1:-"Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')"}"
    
    # 添加所有更改
    git add .
    
    # 提交
    git commit -m "$COMMIT_MSG"
    echo "✅ 提交完成: $COMMIT_MSG"
else
    echo "📭 没有需要提交的更改"
    COMMIT_MSG="No changes to commit"
fi

# 配置远程仓库
REMOTE_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git"
echo "🌐 配置远程仓库: ${GITHUB_REPO}"

# 检查远程仓库配置
if ! git remote | grep -q origin; then
    git remote add origin "$REMOTE_URL"
    echo "➕ 添加远程仓库"
else
    CURRENT_URL=$(git remote get-url origin)
    if [[ "$CURRENT_URL" != "$REMOTE_URL" ]]; then
        git remote set-url origin "$REMOTE_URL"
        echo "🔄 更新远程仓库URL"
    else
        echo "✅ 远程仓库URL已正确配置"
    fi
fi

# 推送到GitHub
echo "🚀 推送到GitHub..."
if git push -u origin master; then
    echo "✅ GitHub同步成功！"
    LATEST_COMMIT=$(git log --oneline -1)
    echo "📋 最新提交: $LATEST_COMMIT"
else
    echo "❌ GitHub推送失败"
    exit 1
fi