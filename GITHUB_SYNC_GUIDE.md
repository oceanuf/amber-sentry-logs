# 🚀 GitHub同步指南 - 琥珀引擎实战日志

## 📋 核心原则
**任务日志每次都同步到GitHub，千万别把token也写进去了。**

## 🔐 GitHub Token信息
- **仓库地址**: `https://github.com/oceanuf/amber-sentry-logs`
- **Token类型**: Personal Access Token (PAT)
- **权限范围**: 仓库读写权限
- **安全等级**: ⚠️ **绝密** - 严禁写入任何文件或日志

## 🔄 同步流程

### 1. 日常同步 (每次任务完成后)
```bash
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/

# 添加所有变更
git add .

# 提交变更 (使用规范格式)
git commit -m "[任务日志] $(date +'%Y-%m-%d %H:%M') - 任务描述"

# 推送到GitHub (使用环境变量或临时输入)
git push origin main
```

### 2. 自动化同步 (Crontab配置)
```bash
# 每晚20:00自动同步
0 20 * * * cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/ && git add . && git commit -m "DAILY_SYNC: $(date +'%Y-%m-%d')" && git push origin main >> /tmp/git_sync_$(date +\%Y\%m\%d).log 2>&1
```

### 3. 手动同步 (带Token安全)
```bash
# 方法1: 使用环境变量 (推荐)
export GITHUB_TOKEN=your_github_token_here
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/
git push https://${GITHUB_TOKEN}@github.com/oceanuf/amber-sentry-logs.git main

# 方法2: 使用Git Credential Helper
git config --global credential.helper store
# 第一次需要输入，之后自动保存
```

## 🚨 安全注意事项

### 严禁操作 (Token泄露风险)
1. ❌ **将Token写入任何文件** (包括配置文件、日志文件、脚本文件)
2. ❌ **在commit信息中包含Token**
3. ❌ **在命令行历史中保留Token**
4. ❌ **将Token分享给任何人**

### 安全检查清单 (每次同步前)
1. ✅ 确认`.git/config`中没有硬编码Token
2. ✅ 确认所有提交不包含敏感信息
3. ✅ 确认环境变量在使用后立即清除
4. ✅ 确认命令行历史已清理

### Token泄露应急响应
1. **立即撤销Token**: 访问GitHub Settings → Developer settings → Personal access tokens
2. **生成新Token**: 创建新的PAT并更新所有使用位置
3. **清理历史记录**: 从Git历史中移除泄露的Token
4. **安全审计**: 检查是否有其他位置泄露

## 📁 同步内容规范

### 必须同步的文件
1. **任务日志**: `trading_logs/` 目录下的所有日志
2. **投资组合**: `portfolio_v1.json` (实战账户状态)
3. **算法配置**: `amber_cmd.json` (系统配置)
4. **扫描报告**: `REPORT_Gist_00127.md` (市场数据)
5. **共同记忆**: `SYSTEM_MEMORY.md` (系统状态)

### 可选同步的文件
1. **归档数据**: `archive/` 目录下的历史数据
2. **脚本源码**: `scripts/` 目录下的Python脚本
3. **HTML页面**: 实时看板页面

### 禁止同步的内容
1. ❌ **敏感Token**: GitHub Token、API密钥、数据库密码
2. ❌ **个人身份信息**: 姓名、邮箱、电话号码
3. ❌ **系统配置文件**: `/etc/` 目录下的系统文件
4. ❌ **临时文件**: `*.log`, `*.tmp`, `__pycache__/`

## 🔧 技术配置

### 1. Git全局配置
```bash
# 设置用户信息
git config --global user.name "Cheese Intelligence Team"
git config --global user.email "engineering@cheese.ai"

# 设置安全配置
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'
```

### 2. 仓库特定配置
```bash
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/

# 设置远程仓库 (无Token版本)
git remote set-url origin https://github.com/oceanuf/amber-sentry-logs.git

# 设置忽略文件
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "*.pem" >> .gitignore
echo "credentials.json" >> .gitignore
```

### 3. 自动化脚本 (`scripts/github_sync.sh`)
```bash
#!/bin/bash
# 安全GitHub同步脚本

set -e  # 遇到错误立即退出

# 进入仓库目录
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/

# 安全检查: 确认没有Token泄露
if grep -r "ghp_" . --include="*.json" --include="*.md" --include="*.txt" --include="*.py" --include="*.sh"; then
    echo "❌ 安全检查失败: 发现可能的Token泄露"
    exit 1
fi

# 添加变更
git add .

# 检查是否有变更
if git diff --cached --quiet; then
    echo "📭 没有变更需要提交"
    exit 0
fi

# 提交变更
COMMIT_MSG="[AUTO_SYNC] $(date +'%Y-%m-%d %H:%M:%S') - 任务日志更新"
git commit -m "$COMMIT_MSG"

# 推送到GitHub (使用环境变量)
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️ GITHUB_TOKEN环境变量未设置，跳过推送"
    echo "提示: export GITHUB_TOKEN=your_token_here"
    exit 0
fi

# 安全推送
git push https://${GITHUB_TOKEN}@github.com/oceanuf/amber-sentry-logs.git main

echo "✅ GitHub同步完成: $(date)"
```

## 📊 同步状态监控

### 1. 同步日志
```bash
# 查看最近同步记录
tail -f /tmp/git_sync_$(date +%Y%m%d).log

# 检查同步状态
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/
git status
git log --oneline -5
```

### 2. GitHub仓库状态
- **地址**: https://github.com/oceanuf/amber-sentry-logs
- **分支**: main
- **最新提交**: 自动显示最后同步时间
- **提交历史**: 按时间倒序排列所有任务日志

### 3. 同步失败处理
1. **网络问题**: 等待重试，最多重试3次
2. **权限问题**: 检查Token是否有效，是否有仓库访问权限
3. **冲突问题**: 先拉取最新变更，解决冲突后再推送
4. **Token失效**: 生成新Token并更新配置

## 🎯 最佳实践

### 1. 提交信息规范
```
[类型] 日期 - 简要描述

[任务日志] 2026-03-27 19:45 - 50万实战账户第一笔交易执行
[AUTO_SYNC] 2026-03-27 20:00 - 每日自动同步
[BUG_FIX] 2026-03-27 21:30 - 修复权限配置错误
```

### 2. 同步频率
- **实时同步**: 每次重要任务完成后立即同步
- **定时同步**: 每小时自动同步一次 (可选)
- **每日归档**: 每晚20:00完整同步并归档

### 3. 版本管理
- **主分支**: `main` - 稳定版本，只接受经过测试的提交
- **开发分支**: `dev` - 开发中的功能 (可选)
- **功能分支**: `feature/*` - 特定功能开发 (可选)

## ⚠️ 安全警告

**GitHub Token是琥珀引擎的核心安全资产，泄露将导致:**

1. **仓库被篡改**: 攻击者可以修改代码、删除历史
2. **数据泄露**: 实战账户信息、交易策略可能被窃取
3. **系统瘫痪**: 攻击者可以破坏整个自动化系统
4. **声誉损失**: 团队技术能力受到质疑

**保护Token就是保护琥珀引擎的生命线！**

---

**指南版本**: V1.0  
**更新日期**: 2026-03-27  
**维护团队**: Cheese Intelligence Team  
**安全等级**: 🔴 绝密 - 仅限团队内部使用