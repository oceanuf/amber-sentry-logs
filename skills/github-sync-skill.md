# 🏛️ GitHub同步Skill操作手册

## 概述
本Skill用于执行符合[2613-182号]规范的GitHub同步操作。包含安全扫描、健康检查、环境验证等自动化防御机制。

## 激活条件
当用户提到以下关键词时激活：
- "github同步"
- "git同步" 
- "推送到github"
- "同步代码"
- "备份到github"
- "执行健康检查"

## 环境配置

### 1. 永久环境变量配置
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_REPO="oceanuf/amber-sentry-logs"
```

### 2. 临时环境变量配置
```bash
# 当前会话有效
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_REPO="oceanuf/amber-sentry-logs"
```

## 使用方式

### 1. 标准同步流程
```bash
# 进入共同记忆目录
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs

# 执行健康检查
./scripts/github_health_check.sh

# 执行同步
./scripts/github_sync_safe.sh "[FEAT]: 任务描述 (Gist_XXXXX)"
```

### 2. 快速同步
```bash
# 一键同步（使用默认提交信息）
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs
./scripts/github_sync_safe.sh
```

### 3. 仅健康检查
```bash
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs
./scripts/github_health_check.sh
```

## 提交信息规范

### 格式要求
```
[类型]: 简要描述 (可选标识)
```

### 类型说明
| 类型 | 说明 | 示例 |
|------|------|------|
| **FEAT** | 新功能添加 | `[FEAT]: 添加ETF健康检查脚本` |
| **FIX** | 问题修复 | `[FIX]: 修复净值计算精度问题` |
| **DOCS** | 文档更新 | `[DOCS]: 更新SYSTEM_MEMORY.md V1.1.1` |
| **REFACTOR** | 代码重构 | `[REFACTOR]: 优化同步脚本性能` |
| **TEST** | 测试相关 | `[TEST]: 添加健康检查单元测试` |
| **CHORE** | 维护任务 | `[CHORE]: 清理日志文件` |

### Gist标识
- 可选添加Gist编号：`(Gist_00159)`
- 示例：`[FEAT]: 添加ETF筛选器 (Gist_00159)`

## 安全特性

### 1. 自毁式敏感信息扫描
- 自动检测硬编码的GitHub Token (`ghp_[A-Za-z0-9]{36}`)
- 检测到立即终止脚本执行
- 输出违规文件位置

### 2. 环境锚定验证
- 验证执行用户必须为 `luckyelite`
- 防止跨用户权限污染
- 确保操作环境一致性

### 3. 环境变量验证
- 必须设置 `GITHUB_TOKEN` 和 `GITHUB_REPO`
- 缺失时提供明确错误提示
- 防止因配置问题导致的失败

## 健康检查项目

### 1. API连通性检查
- GitHub用户API访问测试
- 仓库访问权限验证
- 网络连接状态检查

### 2. 系统状态检查
- 磁盘空间使用率
- Git配置完整性
- 脚本和目录权限

### 3. 日志监控
- 自动生成带时间戳的日志
- 30天日志保留
- 错误分类记录

## 错误处理

### 常见错误及解决方案

#### 1. 认证失败
```
❌ GitHub API连接失败 (HTTP 401)
```
**解决方案**:
- 检查GITHUB_TOKEN是否有效
- 确认令牌有仓库写入权限
- 更新令牌：`export GITHUB_TOKEN="new_token"`

#### 2. 仓库访问失败
```
❌ 仓库访问失败 (HTTP 404)
```
**解决方案**:
- 检查GITHUB_REPO格式：`username/repository`
- 确认仓库存在且有访问权限
- 验证仓库名称拼写

#### 3. 用户权限错误
```
❌ 非法用户权限，必须在 luckyelite 用户下执行
```
**解决方案**:
- 切换到正确用户：`sudo -u luckyelite bash`
- 确认当前用户：`whoami`

#### 4. 硬编码Token检测
```
🚨 检测到硬编码 GitHub Token，脚本自毁终止
```
**解决方案**:
- 移除代码中的硬编码Token
- 改用环境变量配置
- 重新提交干净的代码

#### 5. 磁盘空间不足
```
⚠️ 磁盘空间不足: 95% (超过90%)
```
**解决方案**:
- 清理日志文件：`rm -f logs/github_*.log`
- 清理临时文件
- 扩展磁盘空间

## 日志文件

### 日志位置
- 同步日志：`logs/github_sync_YYYYMMDD.log`
- 健康检查日志：`logs/github_health_YYYYMMDD.log`

### 日志格式
```
[2026-03-28 08:15:30] 🔍 检查Git状态...
[2026-03-28 08:15:31] ✅ 环境变量验证通过
```

### 日志保留
- 自动保留最近30天日志
- 按月归档：`logs/archive/2026-03/`
- 安全审计可追溯

## 自动化任务

### 1. 定时同步
```bash
# 每日凌晨2点自动同步
0 2 * * * cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs && ./scripts/github_sync_safe.sh "[CHORE]: 每日自动同步"
```

### 2. 定时健康检查
```bash
# 每小时执行健康检查
0 * * * * cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs && ./scripts/github_health_check.sh
```

### 3. 日志清理
```bash
# 每月1号清理30天前日志
0 0 1 * * find /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/logs -name "*.log" -mtime +30 -delete
```

## 团队协作

### 1. 共同记忆更新
- 每次成功同步自动更新SYSTEM_MEMORY.md
- 记录同步时间、任务描述、安全状态
- 保持团队记忆一致

### 2. 问题上报流程
1. 检查日志文件获取详细错误信息
2. 更新SYSTEM_MEMORY.md记录问题
3. 通知架构师进行技术审计
4. 根据指导进行修复

### 3. 变更管理
- 脚本变更需通过架构师审计
- 配置变更需记录到共同记忆
- 安全策略变更需主编批准

## 性能优化

### 1. 网络优化
- 使用GitHub API缓存
- 减少不必要的API调用
- 并行执行独立检查

### 2. 资源优化
- 日志文件轮转，防止过大
- 临时文件及时清理
- 内存使用监控

### 3. 错误恢复
- 网络中断自动重试
- 部分失败继续执行其他检查
- 失败状态持久化记录

## 版本历史

### V1.0.0 (2026-03-28)
- 初始版本，符合[2613-182号]规范
- 集成自毁式安全扫描
- 完整健康检查体系
- 自动化日志记录

### 未来版本规划
- V1.1.0: 添加性能监控面板
- V1.2.0: 支持多仓库同步
- V2.0.0: 集成CI/CD流水线

## 附录

### A. 快速参考命令
```bash
# 设置环境变量
export GITHUB_TOKEN="your_token"
export GITHUB_REPO="username/repo"

# 完整流程
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs
./scripts/github_health_check.sh
./scripts/github_sync_safe.sh "[FEAT]: 你的任务描述"
```

### B. 调试模式
```bash
# 启用详细输出
set -x
./scripts/github_sync_safe.sh "[TEST]: 调试同步"
set +x

# 查看详细日志
tail -f logs/github_sync_$(date +%Y%m%d).log
```

### C. 联系支持
- **技术问题**: 架构师 Gemini
- **流程问题**: 主编 Haiyang
- **执行问题**: 工程师 Cheese

---

**规范即效率，安全即尊严。**

*琥珀引擎GitHub同步Skill · 符合[2613-182号]规范V1.0.0*