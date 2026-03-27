# GitHub同步Skill

## 描述
用于将琥珀引擎工作区的代码同步到GitHub仓库的Skill。支持自动提交、推送、拉取和状态检查。

## 激活条件
当用户提到以下关键词时激活：
- "github同步"
- "git同步"
- "推送到github"
- "同步代码"
- "备份到github"

## 配置要求
需要以下环境变量或配置：
1. **GITHUB_TOKEN**: GitHub个人访问令牌（通过环境变量设置）
2. **GITHUB_REPO**: GitHub仓库地址 (格式: username/repo，通过环境变量设置)
3. **GIT_USER_NAME**: Git用户名（可选，默认: "Cheese Intelligence Team"）
4. **GIT_USER_EMAIL**: Git用户邮箱（可选，默认: "cheese@cheese.ai"）

## 快速使用
```bash
# 设置环境变量
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPO="username/repository"

# 执行同步
./scripts/github_sync_safe.sh "提交信息"
```

## 工具脚本

### 1. 安全同步脚本 (`scripts/github_sync_safe.sh`)
```bash
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
```

### 2. 生成同步报告 (`scripts/generate_sync_report.sh`)
```bash
#!/bin/bash
# 生成GitHub同步报告

generate_sync_report() {
    local status="$1"
    local commit_msg="$2"
    local latest_commit="$3"
    
    REPORT_FILE="GITHUB_SYNC_REPORT_$(date '+%Y%m%d_%H%M%S').md"
    
    cat > "$REPORT_FILE" << EOF
# GitHub同步报告

## 同步信息
- **同步时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **同步状态**: $( [ "$status" = "success" ] && echo "✅ 成功" || echo "❌ 失败" )
- **目标仓库**: $GITHUB_REPO
- **工作目录**: $WORKSPACE_DIR

## 提交信息
- **提交消息**: $commit_msg
- **最新提交**: $latest_commit

## Git状态摘要
\`\`\`
$(git status --short)
\`\`\`

## 最近提交记录
\`\`\`
$(git log --oneline -5)
\`\`\`

## 文件变更统计
\`\`\`
$(git diff --stat HEAD~1 HEAD 2>/dev/null || echo "无变更或首次提交")
\`\`\`

## 系统信息
- **操作系统**: $(uname -s)
- **内核版本**: $(uname -r)
- **Git版本**: $(git --version | cut -d' ' -f3)

## 故障诊断
$(if [ "$status" = "failed" ]; then
    echo "### ❌ 同步失败原因"
    echo "请检查："
    echo "1. GitHub令牌是否有效"
    echo "2. 网络连接是否正常"
    echo "3. 仓库权限是否正确"
    echo "4. 本地Git配置是否完整"
fi)

---
**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**Skill版本**: 1.0.0
EOF
    
    echo "📋 同步报告已生成: $REPORT_FILE"
}
```

### 3. 检查GitHub连接 (`scripts/check_github_connection.sh`)
```bash
#!/bin/bash
# 检查GitHub连接状态

check_github_connection() {
    echo "🔗 检查GitHub连接..."
    
    # 检查网络连接
    if ping -c 1 github.com > /dev/null 2>&1; then
        echo "✅ GitHub网络连接正常"
    else
        echo "❌ 无法连接到GitHub"
        return 1
    fi
    
    # 检查API访问
    API_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/user)
    
    if echo "$API_RESPONSE" | grep -q "login"; then
        USERNAME=$(echo "$API_RESPONSE" | grep '"login"' | cut -d'"' -f4)
        echo "✅ GitHub令牌有效 (用户: $USERNAME)"
    else
        echo "❌ GitHub令牌无效"
        return 1
    fi
    
    # 检查仓库访问
    REPO_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/repos/$GITHUB_REPO)
    
    if echo "$REPO_RESPONSE" | grep -q "full_name"; then
        REPO_NAME=$(echo "$REPO_RESPONSE" | grep '"full_name"' | cut -d'"' -f4)
        echo "✅ 仓库访问正常: $REPO_NAME"
    else
        echo "❌ 无法访问仓库: $GITHUB_REPO"
        return 1
    fi
    
    echo "🎉 所有GitHub连接检查通过！"
    return 0
}
```

### 4. 自动同步脚本 (`scripts/auto_sync.sh`)
```bash
#!/bin/bash
# 自动同步脚本 - 可用于cron定时任务

# 导入配置
source "$(dirname "$0")/github_sync_config.sh"

# 日志文件
LOG_FILE="/tmp/github_sync_$(date '+%Y%m%d').log"

echo "🔄 开始自动同步 $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

# 检查连接
if ! check_github_connection >> "$LOG_FILE" 2>&1; then
    echo "❌ GitHub连接检查失败，跳过同步" >> "$LOG_FILE"
    exit 1
fi

# 执行同步
cd "$WORKSPACE_DIR"
COMMIT_MSG="Auto-sync: $(date '+%Y-%m-%d %H:%M:%S') - 定时同步"

if ./github_sync.sh "$COMMIT_MSG" >> "$LOG_FILE" 2>&1; then
    echo "✅ 自动同步完成 $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
else
    echo "❌ 自动同步失败 $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
    exit 1
fi
```

### 5. 配置脚本 (`scripts/github_sync_config.sh`)
```bash
#!/bin/bash
# GitHub同步配置

# 工作区目录
WORKSPACE_DIR="/home/luckyelite/.openclaw/workspace/amber-engine"

# 检查环境变量
if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "❌ 错误: 请设置GITHUB_TOKEN环境变量"
    echo "示例: export GITHUB_TOKEN=your_github_token"
    exit 1
fi

if [[ -z "$GITHUB_REPO" ]]; then
    echo "❌ 错误: 请设置GITHUB_REPO环境变量"
    echo "示例: export GITHUB_REPO=username/repository"
    exit 1
fi

# Git用户配置
export GIT_USER_NAME="${GIT_USER_NAME:-"Cheese Intelligence Team"}"
export GIT_USER_EMAIL="${GIT_USER_EMAIL:-"cheese@cheese.ai"}"

# 配置Git
git config --global user.name "$GIT_USER_NAME"
git config --global user.email "$GIT_USER_EMAIL"

echo "✅ GitHub同步配置完成"
echo "   仓库: $GITHUB_REPO"
echo "   用户: $GIT_USER_NAME"
```

## 使用示例

### 基本同步
```bash
./scripts/github_sync.sh "更新投资组合页面"
```

### 检查连接
```bash
./scripts/check_github_connection.sh
```

### 自动同步 (cron)
```bash
# 每小时同步一次
0 * * * * /home/luckyelite/.openclaw/workspace/amber-engine/scripts/auto_sync.sh
```

## 故障排除

### 常见问题
1. **令牌无效**: 更新GITHUB_TOKEN环境变量
2. **网络问题**: 检查网络连接和代理设置
3. **权限不足**: 确认令牌有仓库写入权限
4. **仓库不存在**: 检查GITHUB_REPO配置

### 调试模式
```bash
# 启用详细输出
set -x
./github_sync.sh
set +x
```

## 安全注意事项
1. **令牌安全**: GitHub令牌应妥善保管，不要硬编码在脚本中
2. **权限最小化**: 使用最小必要权限的令牌
3. **定期轮换**: 定期更新GitHub令牌
4. **访问日志**: 监控GitHub访问日志

## 版本历史
- **v1.0.0** (2026-03-28): 初始版本，包含基本同步功能
- **v1.1.0**: 添加连接检查、自动同步、报告生成

---
**Skill维护者**: 工程师 Cheese
**最后更新**: 2026-03-28
**适用场景**: 琥珀引擎代码同步与备份