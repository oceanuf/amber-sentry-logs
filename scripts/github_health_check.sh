#!/bin/bash
# 🏛️ GitHub健康检查脚本 (符合[2613-182号]规范V1.0.0)
# 第五章：健康检查与监控

set -e

LOG_FILE="logs/github_health_$(date +%Y%m%d).log"

log_message() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="$1"
    echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

log_message "🩺 开始GitHub健康检查"

# ==================== 环境变量检查 ====================
log_message "🔍 检查环境变量..."
REQUIRED_ENV_VARS=("GITHUB_TOKEN" "GITHUB_REPO")
all_passed=true

for var in "${REQUIRED_ENV_VARS[@]}"; do
    if [[ -z "${!var}" ]]; then
        log_message "❌ 缺失环境变量: $var"
        all_passed=false
    else
        log_message "✅ $var 已设置"
    fi
done

if [[ "$all_passed" != "true" ]]; then
    log_message "🚨 环境变量检查失败"
    exit 1
fi

# ==================== 5.1 API连通性检查 ====================
log_message "🌐 检查GitHub API连通性..."
API_RESPONSE=$(curl -s -w "%{http_code}" -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/user -o /tmp/github_api_response.json)

HTTP_CODE=$(echo "$API_RESPONSE" | tail -1)

if [[ "$HTTP_CODE" == "200" ]]; then
    USER_LOGIN=$(grep -o '"login":"[^"]*"' /tmp/github_api_response.json | head -1 | cut -d'"' -f4)
    log_message "✅ GitHub API连通正常 (用户: $USER_LOGIN)"
else
    log_message "❌ GitHub API连接失败 (HTTP $HTTP_CODE)"
    all_passed=false
fi

# ==================== 5.2 仓库状态检查 ====================
log_message "📦 检查仓库状态..."
REPO_RESPONSE=$(curl -s -w "%{http_code}" \
    https://api.github.com/repos/$GITHUB_REPO -o /tmp/github_repo_response.json)

REPO_HTTP_CODE=$(echo "$REPO_RESPONSE" | tail -1)

if [[ "$REPO_HTTP_CODE" == "200" ]]; then
    REPO_NAME=$(grep -o '"full_name":"[^"]*"' /tmp/github_repo_response.json | head -1 | cut -d'"' -f4)
    REPO_PRIVATE=$(grep -o '"private":[^,]*' /tmp/github_repo_response.json | head -1 | cut -d':' -f2)
    log_message "✅ 仓库访问正常: $REPO_NAME (私有: $REPO_PRIVATE)"
else
    log_message "❌ 仓库访问失败 (HTTP $REPO_HTTP_CODE)"
    all_passed=false
fi

# ==================== 网络连接检查 ====================
log_message "📡 检查网络连接..."
if ping -c 1 github.com > /dev/null 2>&1; then
    log_message "✅ GitHub网络连接正常"
else
    log_message "❌ 无法连接到GitHub"
    all_passed=false
fi

# ==================== 5.3 磁盘空间检查 ====================
log_message "💾 检查磁盘空间..."
DISK_USAGE=$(df /home --output=pcent | tail -1 | tr -d '% ')
if [[ "$DISK_USAGE" -gt 90 ]]; then
    log_message "⚠️  磁盘空间不足: ${DISK_USAGE}% (超过90%)"
    all_passed=false
elif [[ "$DISK_USAGE" -gt 80 ]]; then
    log_message "⚠️  磁盘空间警告: ${DISK_USAGE}% (超过80%)"
else
    log_message "✅ 磁盘空间正常: ${DISK_USAGE}%"
fi

# ==================== Git配置检查 ====================
log_message "🔧 检查Git配置..."
GIT_USER_NAME=$(git config --global user.name)
GIT_USER_EMAIL=$(git config --global user.email)

if [[ -n "$GIT_USER_NAME" && -n "$GIT_USER_EMAIL" ]]; then
    log_message "✅ Git配置正常: $GIT_USER_NAME <$GIT_USER_EMAIL>"
else
    log_message "⚠️  Git配置不完整"
    all_passed=false
fi

# ==================== 脚本权限检查 ====================
log_message "🔐 检查脚本权限..."
SCRIPTS=("github_sync_safe.sh" "github_health_check.sh")
for script in "${SCRIPTS[@]}"; do
    if [[ -f "scripts/$script" ]]; then
        PERMISSIONS=$(stat -c "%a" "scripts/$script")
        if [[ "$PERMISSIONS" == "755" ]]; then
            log_message "✅ $script 权限正确: $PERMISSIONS"
        else
            log_message "⚠️  $script 权限异常: $PERMISSIONS (应为755)"
            all_passed=false
        fi
    else
        log_message "❌ 脚本不存在: $script"
        all_passed=false
    fi
done

# ==================== 目录权限检查 ====================
log_message "📁 检查目录权限..."
DIRS=("scripts" "skills" "logs" "archive")
for dir in "${DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        OWNER=$(stat -c "%U:%G" "$dir")
        if [[ "$OWNER" == "luckyelite:www-data" || "$OWNER" == "luckyelite:luckyelite" ]]; then
            log_message "✅ $dir 所有者正确: $OWNER"
        else
            log_message "⚠️  $dir 所有者异常: $OWNER"
            all_passed=false
        fi
    else
        log_message "⚠️  目录不存在: $dir"
        all_passed=false
    fi
done

# ==================== 日志文件检查 ====================
log_message "📋 检查日志文件..."
LOG_DIR="logs"
if [[ -d "$LOG_DIR" ]]; then
    LOG_COUNT=$(find "$LOG_DIR" -name "github_*.log" -mtime -30 | wc -l)
    log_message "✅ 日志目录正常，最近30天日志文件: $LOG_COUNT"
else
    log_message "⚠️  日志目录不存在"
    all_passed=false
fi

# ==================== 最终检查结果 ====================
if [[ "$all_passed" == "true" ]]; then
    log_message "🎉 所有健康检查通过！系统状态正常"
    echo "✅ 健康检查通过 - 详细日志: $LOG_FILE"
    exit 0
else
    log_message "🚨 健康检查失败，请检查上述问题"
    echo "❌ 健康检查失败 - 详细日志: $LOG_FILE"
    exit 1
fi