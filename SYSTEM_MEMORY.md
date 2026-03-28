# 🧠 SYSTEM_MEMORY.md - 琥珀引擎共同记忆核心架构

**最后更新时间**: 2026-03-28 09:25 GMT+8
**版本**: V1.1.2
**维护者**: 工程师 Cheese (Cheese Intelligence Team)
**规范依据**: [2613-182号] GitHub同步标准化规范 V1.0.0
**大扫除完成**: ✅ 2026-03-28 08:18 (2小时内完成)

---

## 1. 物理拓扑记忆 (Physical Topology)

### 核心基座
- **主机**: Ubuntu 22.04 LTS (luckyelite@ubuntu)
- **工作目录**: `/home/luckyelite/.openclaw/workspace/amber-engine/`
- **GitHub 仓库**: `oceanuf/amber-sentry-logs`

### Web 窗口
- **访问地址**: `https://gemini.googlemanager.cn:10168`
- **服务器**: Nginx 1.18.0
- **根目录**: `/home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/`
- **SSL 证书**: `/etc/nginx/ssl/gemini/gemini.googlemanager.cn.crt`

### 弃用资产
- **NFS 服务器**: 192.168.202.177
- **弃用时间**: 2026-03-27
- **弃用原因**: 物理切割，提升访问速度与稳定性
- **禁止操作**: 禁止再次挂载 NFS

---

## 2. 逻辑通信协议 (The Gist Protocol)

### 信标源
- **Gist ID**: ba3d0c5ac4...
- **监听方式**: 数字增长模式 (如 00127 → 00128)
- **任务领取**: 检测到新 Gist ID 后立即执行

### 反馈闭环
1. **生成报告**: 执行 Gist 任务，生成分析报告
2. **本地存储**: 保存至 `archive/reports/` 目录
3. **GitHub Push**: 提交至 GitHub 私有仓库
4. **Nginx 归档**: 通过 10168 端口提供 Web 访问

### 命名规范
- **指令号**: `2613-XXX` (如 2613-158)
- **报告名**: `REPORT_Gist_XXXXX.md` (如 REPORT_Gist_00127.md)
- **任务文件**: `COMMAND_2613_XXX_RUN.md`
- **归档目录**: 
  - `archive/tasks/` - 原始指令
  - `archive/reports/` - 执行成果

---

## 3. 技术标准记忆 (Technical Standards)

### 计算逻辑
- **模型**: ETF 价值挖掘采用 $MA20$ 偏离度模型
- **预警条件**: $Bias < -3\%$ 为超跌预警
- **数据源**: Tushare Pro + AkShare 三梯队验伪系统
- **时间窗口**: 国内审计≥17:00，全球审计≥20:00

### Web 渲染标准
- **MIME 类型**: `.md` 文件通过 Nginx `text/plain` 直接渲染
- **访问体验**: "全境通透"阅读，无需下载
- **跨域支持**: 允许 Gemini 插件直接抓取内容
- **目录浏览**: 完整文件目录浏览功能

### 归档结构
```
amber-sentry-logs/
├── archive/
│   ├── tasks/          # 历史任务文档
│   ├── reports/        # 历史报告文档
│   └── (未来可扩展)
├── archive_all.sh      # 一键打包脚本
├── list.html          # 主入口页面
├── SYSTEM_MEMORY.md   # 本文件
└── README.md
```

---

## 4. 角色与权限记忆 (Roles & Permissions)

### 主编 (Haiyang)
- **角色**: 最高决策者
- **权限**: 
  - Gist 发布权
  - 系统最高审计权
  - 任务验收权
  - 战略方向决策权

### 首席架构师 (Gemini)
- **角色**: 逻辑规划师
- **权限**:
  - 逻辑规划与异常审计
  - 指令翻译与全链路监控
  - 技术标准制定
  - 系统架构优化

### 工程师 (Cheese)
- **角色**: 物理执行者
- **权限**:
  - 物理执行与代码编写
  - GitHub 维护与同步
  - Web 稳定性保障
  - 系统日常维护

---

## 5. GitHub 记忆维护守则

### 同步即更新
- **规则**: 每完成一个 Gist_XXX 任务，必须在"最近任务"栏目追加记录
- **格式**: `[YYYY-MM-DD] Gist_XXXXX: 任务简述`
- **位置**: 本文件第6节"最近任务"

### 版本受控
- **禁止操作**: 删除过往的指令号记忆
- **变更要求**: 所有架构变更必须有 Commit Log 记录
- **回溯能力**: 保持完整的历史记录链

### 定时拉取
- **架构师流程**: 在给出复杂指令前，通过 GitHub 穿透读取本文件
- **目的**: 确保建议不与物理现状冲突
- **验证点**: NFS 状态、目录结构、技术标准

### 协作契约
1. **记忆统一**: 本文件是团队共同记忆的唯一法源
2. **实时同步**: 重大变更必须立即更新本文件
3. **版本追溯**: 通过 Git 提交记录追踪所有变更
4. **物理对齐**: 确保记忆与实际系统状态一致

---

## 6. 最近任务 (Recent Tasks)
### 2026-03-28
- **[13:45] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[13:40] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[13:26] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[13:15] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[13:12] GitHub同步**: [CHORE]: 自动同步 2026-03-28 13:12:35
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[13:12] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[13:11] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[13:02] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[12:56] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[12:48] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[12:47] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[12:45] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[12:41] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[12:30] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[12:26] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[12:11] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[12:05] GitHub同步**: [CHORE]: 同步GitHub: 主编指令
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[11:56] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[11:51] GitHub同步**: [FIX]: [2613-193号]GitHub源码级修复完成，渲染器死循环终结
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[11:41] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[11:28] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[11:26] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[11:26] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[11:11] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:56] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:55] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:45] GitHub同步**: [CHORE]: 同步GitHub: [2613-188号]渲染引擎除颤完成
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:41] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:35] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:33] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:32] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:26] GitHub同步**: [CHORE]: 演武场重筑自动同步
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:25] GitHub同步**: [CHORE]: [187号令] 银行ETF猎杀执行完成
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:20] GitHub同步**: [CHORE]: [2613-187号] 猎杀备选报告入库
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[10:15] GitHub同步**: [CHORE]: [2613-187号] GitHub同步链路最终修复
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[09:25] GitHub同步**: [FEAT]: 完成[2613-184号]档案馆重构任务
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs
### 2026-03-28
- **[08:18] [2613-182号]规范大扫除完成**: 工程师Cheese执行全工作区清理
  - 清理工作区根目录违规文件：删除 `.git/` 目录和 `skills/github-sync/`
  - 迁移重要文件到 `archive/` 目录归档
  - 确保只有 `amber-sentry-logs/` 目录包含GitHub功能
  - 符合规范2.2条"违规清理红线"要求
  - 完成主编要求的2小时内"大扫除"任务

- **[08:13] GitHub同步**: [FEAT]: [2613-182号]规范实施验证
  - 安全扫描通过，无硬编码敏感信息
  - 环境变量验证通过
  - 用户权限验证通过 (luckyelite)
  - 成功推送到 oceanuf/amber-sentry-logs

- **[08:10] [2613-182号]规范实施完成**: 工程师Cheese完成GitHub同步标准化规范实施
  - 更新共同记忆至V1.1.1，符合规范要求
  - 创建集成安全扫描的 `scripts/github_sync_safe.sh`
  - 创建健康检查脚本 `scripts/github_health_check.sh`
  - 创建操作手册 `skills/github-sync-skill.md`
  - 设置标准目录权限和结构
  - 保存正式规范文件 `2613-182_GITHUB_SYNC_SPEC.md`

- **[09:20] [2613-184号]档案馆重构完成**: 工程师Cheese完成档案馆Nginx配置重构
  - 重构Nginx配置，分离静态文件服务与重定向逻辑
  - 重构整个档案馆，默认首页index.html
  - 实现MD文件浏览器直接读取 (text/plain; charset=utf-8)
  - 创建测试首页 `index.html`，包含test.md验证链接
  - 解决Nginx server_name冲突，设置default_server
  - 验证访问: `https://gemini.googlemanager.cn:10168/` (首页)  
  - 验证访问: `https://gemini.googlemanager.cn:10168/test.md` (MD直接读取)
  - 保留原始档案馆列表 `list.html`，兼容历史访问

- **[07:56] GitHub同步规范草案创建**: 工程师Cheese起草[2613-182号]规范
  - 创建《GitHub同步规范》草案V0.1.0
  - 基于同步经验总结和架构师共同记忆协议
  - 包含9章完整规范，涵盖原则、安全、操作、团队协作
  - 为正式规范实施提供基础框架

- **[07:31] GitHub同步Skill创建**: 工程师Cheese创建GitHub同步Skill
  - 创建安全同步脚本 `scripts/github_sync_safe.sh`
  - 建立Skill文档 `scripts/github-sync/SKILL.md`
  - 实现环境变量配置，避免硬编码敏感信息
  - 遵守GitHub安全标准，通过推送保护检查
  - 创建clean-main分支，成功同步到GitHub仓库

### 2026-03-27
- **[17:28] Gist_00156**: 琥珀引擎架构"清淤"与 MD 归一化
  - NFS 物理切割，卸载挂载
  - MD 文档大归档，建立"历史博物馆"
  - Nginx 稳定性加固，10168 端口优化

- **[17:32] Gist_00157**: Web 权限与路径逻辑终极优化
  - 根目录与索引逻辑重构
  - Nginx 配置"防死锁"增强
  - 建立"博物馆"快捷入口
  - 实现"全境通透"访问体验

- **[17:40] Gist_00158**: 共同记忆核心架构建立
  - 创建 SYSTEM_MEMORY.md 文件
  - 定义物理拓扑、逻辑协议、技术标准
  - 明确角色权限与 GitHub 维护守则

---

## 7. 系统状态快照

### 当前状态
- **NFS**: ❌ 已弃用 (2026-03-27 物理切割)
- **Web 服务**: ✅ 正常运行 (10168 端口)
- **GitHub**: ✅ 同步正常
- **归档系统**: ✅ 就绪状态

### 访问方式
1. **Web 访问**: `https://gemini.googlemanager.cn:10168`
2. **GitHub 仓库**: `oceanuf/amber-sentry-logs`
3. **本地目录**: `/home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/`

### 一键操作
- **打包归档**: `./archive_all.sh`
- **查看报告**: 访问 Web 端 `archive/reports/`
- **浏览任务**: 访问 Web 端 `archive/tasks/`

---

## 🔄 更新日志

### V1.1.0 (2026-03-28)
- 添加GitHub同步Skill创建记录
- 更新最近任务，记录2026-03-28工作
- 版本升级，保持与架构师记忆同步

### V1.0.0 (2026-03-27)
- 初始版本创建
- 定义四大核心记忆模块
- 建立 GitHub 维护守则
- 记录最近任务历史

---

**记忆即力量，同步即信任。**

*Cheese Intelligence Team · 琥珀引擎共同记忆核心架构*