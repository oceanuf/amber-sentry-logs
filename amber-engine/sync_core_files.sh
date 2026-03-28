#!/bin/bash
# 琥珀引擎核心文件同步脚本
# 基于[2613-182号]GitHub同步标准化规范

set -e

echo "🧀 琥珀引擎核心文件同步启动"
echo "======================================"
echo "同步时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

# 切换到工作目录
cd /home/luckyelite/.openclaw/workspace/amber-engine

# 1. 检查Git状态
echo "1. 检查Git状态..."
git status --short

# 2. 添加核心文件（排除日志和临时文件）
echo ""
echo "2. 添加核心文件..."
git add .gitignore
git add *.py
git add *.md
git add *.sh
git add *.json
git add *.html
git add scripts/
git add skills/
git add vaults/

# 3. 移除不应该跟踪的文件
echo ""
echo "3. 清理不应该跟踪的文件..."
git reset -- output/
git reset -- memory/
git reset -- logs/
git reset -- schedule/
git reset -- data/
git reset -- *.log
git reset -- *.db
git reset -- *.backup

# 4. 提交更改
echo ""
echo "4. 提交更改..."
if [[ -n $(git status --porcelain) ]]; then
    git commit -m "[SYNC]: 琥珀引擎核心文件同步

基于[2613-182号]GitHub同步标准化规范，同步核心文件：
- 核心Python脚本和工具
- 文档文件 (.md)
- 脚本目录 (scripts/)
- 技能目录 (skills/)
- 档案馆目录 (vaults/)
- 配置文件 (.json, .gitignore)

排除文件：
- 输出目录 (output/)
- 内存文件 (memory/)
- 日志目录 (logs/)
- 临时数据文件

同步时间: $(date '+%Y-%m-%d %H:%M:%S %Z')
Cheese Intelligence Team - 工程师 Cheese"
    
    echo "✅ 提交完成"
else
    echo "📭 没有需要提交的更改"
fi

# 5. 推送到远程仓库
echo ""
echo "5. 推送到远程仓库..."
if [[ -n $(git log origin/main..HEAD) ]]; then
    echo "使用GitHub令牌进行身份验证..."
    
    # 设置Git凭据
    GITHUB_TOKEN="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"
    git push https://${GITHUB_TOKEN}@github.com/oceanuf/amber-sentry-logs.git master
    
    if [ $? -eq 0 ]; then
        echo "✅ 核心文件同步成功！"
        echo "提交哈希: $(git rev-parse --short HEAD)"
        echo "同步时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    else
        echo "❌ 核心文件同步失败"
        exit 1
    fi
else
    echo "📭 没有需要推送的更改"
fi

echo ""
echo "======================================"
echo "🧀 琥珀引擎核心文件同步完成"
echo "基于[2613-001号]命令发布规范"
echo "执行人: 工程师 Cheese"
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"