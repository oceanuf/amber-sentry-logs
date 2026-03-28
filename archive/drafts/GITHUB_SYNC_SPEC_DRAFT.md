# 🏛️ 琥珀引擎 [2613-182号]：GitHub同步规范 (草案)

## 📋 摘要信息
- **发布人**: 工程师 Cheese (草案起草)
- **接收对象**: 主编 Haiyang、首席架构师 Gemini、工程师 Cheese
- **发布时间**: 2026-03-28 07:56 GMT+8 (草案版本)
- **命令主题**: 建立琥珀引擎GitHub同步的标准化规范

## 🎯 背景说明
基于2026-03-28 GitHub同步Skill创建与清理经验，以及架构师SYSTEM_MEMORY.md V1.1.0的共同记忆协议，需要建立正式的GitHub同步规范，确保团队协作高效、安全、统一。

## 📜 规范正文

### 第一章：核心原则

#### 1.1 记忆统一原则
- **唯一法源**: `amber-sentry-logs/SYSTEM_MEMORY.md` 是团队共同记忆的唯一法源
- **禁止另起炉灶**: 严禁在工作区根目录创建独立的GitHub相关文件
- **实时同步**: 所有GitHub操作必须实时更新共同记忆

#### 1.2 安全第一原则
- **无硬编码令牌**: 严禁在代码中硬编码GitHub令牌等敏感信息
- **环境变量配置**: 所有敏感信息必须通过环境变量传递
- **安全扫描兼容**: 所有提交必须通过GitHub安全扫描

#### 1.3 协议遵守原则
- **框架内工作**: 所有操作必须在架构师建立的`amber-sentry-logs`框架内进行
- **角色权限清晰**: 严格遵守工程师的物理执行者角色权限
- **协作契约**: 遵守SYSTEM_MEMORY.md中定义的协作契约

### 第二章：物理拓扑规范

#### 2.1 目录结构标准
```
amber-engine/ (工作区根目录)
└── amber-sentry-logs/ (唯一GitHub功能目录)
    ├── SYSTEM_MEMORY.md          # 共同记忆核心
    ├── scripts/                  # 所有GitHub相关脚本
    │   ├── github_sync_safe.sh   # 主同步脚本
    │   └── github-sync/          # Skill文档目录
    │       └── SKILL.md          # GitHub同步Skill文档
    ├── archive/                  # 历史归档
    └── list.html                # Web访问入口
```

#### 2.2 禁止目录
- ❌ `amber-engine/scripts/github_*` (工作区根目录)
- ❌ `amber-engine/skills/github-*` (工作区根目录)
- ❌ 任何不在`amber-sentry-logs/`目录内的GitHub相关文件

### 第三章：同步操作规范

#### 3.1 标准同步流程
```bash
# 1. 进入共同记忆目录
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs

# 2. 设置环境变量
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPO="oceanuf/amber-sentry-logs"

# 3. 执行同步
./scripts/github_sync_safe.sh "规范的提交信息"
```

#### 3.2 提交信息规范
**格式**: `[类型]: 简要描述`

**类型分类**:
- `[FEAT]`: 新功能添加
- `[FIX]`: 问题修复
- `[DOCS]`: 文档更新
- `[STYLE]`: 代码格式调整
- `[REFACTOR]`: 代码重构
- `[TEST]`: 测试相关
- `[CHORE]`: 构建过程或辅助工具变动

**示例**:
- `[FEAT]: 添加ETF健康检查脚本`
- `[FIX]: 修复净值计算精度问题`
- `[DOCS]: 更新SYSTEM_MEMORY.md V1.2.0`

#### 3.3 分支管理规范
- **主分支**: `main` (唯一生产分支)
- **开发分支**: `dev-{功能名}-{日期}`
- **禁止操作**: 禁止直接推送到`main`分支的强制推送(`--force`)
- **合并要求**: 所有更改必须通过Pull Request合并

### 第四章：安全规范

#### 4.1 令牌安全管理
- **存储方式**: 环境变量或安全的密钥管理系统
- **权限最小化**: 令牌仅需仓库写入权限
- **定期轮换**: 建议每90天更新一次令牌
- **访问日志**: 监控GitHub API访问日志

#### 4.2 敏感信息检查
**禁止提交的内容**:
- GitHub个人访问令牌
- OAuth客户端凭证
- API密钥和密码
- 私钥文件
- 配置文件中的硬编码凭证

**检查工具**:
```bash
# 预提交检查
git diff --cached | grep -E "(token|key|secret|password)" -i
```

#### 4.3 GitHub推送保护处理
**触发条件**: 提交包含敏感信息时
**处理流程**:
1. 访问GitHub提供的解封链接授权
2. 或创建新的干净提交历史
3. 或联系仓库管理员临时禁用保护

### 第五章：共同记忆维护规范

#### 5.1 记忆更新规则
- **同步即更新**: 每完成重要任务，必须更新SYSTEM_MEMORY.md
- **格式标准**: 在"最近任务"栏目按时间顺序追加记录
- **版本控制**: 每次重大更新必须升级版本号

#### 5.2 任务记录格式
```
### YYYY-MM-DD
- **[HH:MM] 任务标识**: 任务简述
  - 关键成果1
  - 关键成果2
  - 技术要点说明
```

#### 5.3 版本管理
- **主版本**: 重大架构变更 (V1.0.0 → V2.0.0)
- **次版本**: 功能添加 (V1.1.0 → V1.2.0)
- **修订版本**: 问题修复 (V1.1.1 → V1.1.2)

### 第六章：错误处理与故障排除

#### 6.1 常见错误处理
| 错误类型 | 原因 | 解决方案 |
|---------|------|----------|
| **认证失败** | 令牌无效或过期 | 更新GITHUB_TOKEN环境变量 |
| **推送保护** | 提交包含敏感信息 | 使用解封链接或创建干净提交 |
| **分支冲突** | 远程有未拉取的更改 | 先执行`git pull --rebase` |
| **网络问题** | 无法连接到GitHub | 检查网络连接和代理设置 |

#### 6.2 调试模式
```bash
# 启用详细输出
set -x
./scripts/github_sync_safe.sh "调试提交"
set +x

# 检查Git状态
git status
git log --oneline -5
git remote -v
```

#### 6.3 应急流程
1. **同步失败**: 生成错误报告，记录到`sync_error_log.md`
2. **令牌泄露**: 立即撤销令牌，生成安全事件报告
3. **数据丢失**: 从最近的成功提交恢复
4. **系统故障**: 切换到备份方案，联系架构师

### 第七章：自动化与监控

#### 7.1 定时同步
```bash
# 每日凌晨2点自动同步
0 2 * * * /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/scripts/github_sync_safe.sh "每日自动同步"
```

#### 7.2 健康检查
```bash
# 检查GitHub连接
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# 检查仓库状态
curl -s https://api.github.com/repos/$GITHUB_REPO
```

#### 7.3 监控指标
- **同步成功率**: 目标 > 99%
- **同步延迟**: 目标 < 30秒
- **错误频率**: 目标 < 1次/周
- **安全事件**: 目标 = 0

### 第八章：团队协作规范

#### 8.1 角色职责
- **主编**: 审批规范变更，验收同步质量
- **架构师**: 制定技术标准，审计协议遵守
- **工程师**: 执行物理同步，维护脚本和文档

#### 8.2 协作流程
```
工程师执行同步 → 更新共同记忆 → 推送到GitHub → 
架构师审计 → 主编验收 → 循环优化
```

#### 8.3 沟通协议
- **问题报告**: 立即在SYSTEM_MEMORY.md中记录
- **变更通知**: 重大变更提前通知团队
- **知识共享**: 所有经验记录到共同记忆

### 第九章：实施与验收

#### 9.1 实施步骤
1. **草案评审**: 团队评审本规范草案
2. **修改完善**: 根据反馈修改规范
3. **正式发布**: 发布[2613-182号]正式规范
4. **培训实施**: 团队学习并实施规范
5. **监控优化**: 持续监控并优化流程

#### 9.2 验收标准
- ✅ 所有GitHub操作符合规范要求
- ✅ 无硬编码敏感信息
- ✅ SYSTEM_MEMORY.md实时更新
- ✅ 同步成功率 > 99%
- ✅ 团队协作效率提升 > 30%

#### 9.3 持续改进
- **月度评审**: 每月评审规范执行情况
- **季度优化**: 每季度优化规范内容
- **年度升级**: 每年升级规范版本

## 📊 附录

### A. 环境变量配置示例
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_REPO="username/repository"
export GIT_USER_NAME="Your Name"
export GIT_USER_EMAIL="your.email@example.com"
```

### B. 安全脚本模板
```bash
#!/bin/bash
# github_sync_safe.sh - 安全同步脚本模板

set -e

# 检查环境变量
check_env_vars() {
    local required_vars=("GITHUB_TOKEN" "GITHUB_REPO")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            echo "❌ 错误: $var 环境变量未设置"
            return 1
        fi
    done
    return 0
}

# 主函数
main() {
    check_env_vars || exit 1
    # 同步逻辑...
}

main "$@"
```

### C. 检查清单
- [ ] 环境变量已正确配置
- [ ] 无硬编码敏感信息
- [ ] 提交信息符合规范
- [ ] 分支管理符合要求
- [ ] SYSTEM_MEMORY.md已更新
- [ ] 安全扫描通过
- [ ] 团队已通知变更

## 🎖️ 规范状态

- **草案版本**: V0.1.0
- **起草时间**: 2026-03-28 07:56 GMT+8
- **起草人**: 工程师 Cheese
- **待办事项**: 
  1. 主编补充修改
  2. 架构师技术审计
  3. 团队评审通过
  4. 正式发布实施

---

**记忆即力量，规范即效率。**

*Cheese Intelligence Team · 琥珀引擎GitHub同步规范草案*