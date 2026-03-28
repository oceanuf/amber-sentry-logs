# Cron作业配置参考

## 当前自动化配置

### 作业信息
- **作业ID**: `262b7a44-98f0-491c-a164-da680a91cf42`
- **作业名称**: 琥珀引擎数据更新
- **创建时间**: 2026-03-20
- **状态**: 启用

### 调度配置
```json
{
  "kind": "cron",
  "expr": "0 15 * * 1-5",
  "tz": "Asia/Shanghai"
}
```

**解释**:
- `0 15 * * 1-5`: 每周一至周五的15:00执行
- `tz: Asia/Shanghai`: 使用北京时间 (UTC+8)
- **实际执行时间**: 交易日15:00 CST (北京时间)

### 执行配置
```json
{
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "执行琥珀引擎数据更新任务。运行统一数据引擎更新所有数据：指数数据、ETF数据、宏观数据。完成后报告执行结果。",
    "model": "deepseek/deepseek-chat"
  },
  "delivery": {
    "mode": "none"
  }
}
```

**解释**:
- `sessionTarget: "isolated"`: 在独立会话中执行
- `payload.kind: "agentTurn"`: 使用Agent执行任务
- `delivery.mode: "none"`: 静默执行，不发送通知

## 管理命令

### 查看作业状态
```bash
# 查看所有Cron作业
openclaw cron list

# 查看特定作业详情
openclaw cron list --includeDisabled=true | grep "262b7a44"
```

### 手动触发执行
```bash
# 立即执行作业
openclaw cron run --jobId=262b7a44-98f0-491c-a164-da680a91cf42

# 强制执行（即使未到调度时间）
openclaw cron run --jobId=262b7a44-98f0-491c-a164-da680a91cf42 --runMode=force
```

### 查看执行历史
```bash
# 查看作业执行历史
openclaw cron runs --jobId=262b7a44-98f0-491c-a164-da680a91cf42
```

### 修改作业配置
```bash
# 禁用作业
openclaw cron update --jobId=262b7a44-98f0-491c-a164-da680a91cf42 --patch='{"enabled": false}'

# 启用作业
openclaw cron update --jobId=262b7a44-98f0-491c-a164-da680a91cf42 --patch='{"enabled": true}'

# 修改调度时间
openclaw cron update --jobId=262b7a44-98f0-491c-a164-da680a91cf42 --patch='{"schedule": {"expr": "0 16 * * 1-5"}}'
```

### 删除作业
```bash
# 删除作业
openclaw cron remove --jobId=262b7a44-98f0-491c-a164-da680a91cf42
```

## 创建新作业

### 基本作业创建
```bash
openclaw cron add --job='{
  "name": "琥珀引擎数据更新",
  "schedule": {
    "kind": "cron",
    "expr": "0 15 * * 1-5",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行琥珀引擎数据更新任务。运行统一数据引擎更新所有数据：指数数据、ETF数据、宏观数据。完成后报告执行结果。",
    "model": "deepseek/deepseek-chat"
  },
  "sessionTarget": "isolated",
  "enabled": true
}'
```

### 带通知的作业
```bash
openclaw cron add --job='{
  "name": "琥珀引擎数据更新（带通知）",
  "schedule": {
    "kind": "cron",
    "expr": "0 15 * * 1-5",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行琥珀引擎数据更新任务。运行统一数据引擎更新所有数据。完成后发送简短报告。",
    "model": "deepseek/deepseek-chat"
  },
  "delivery": {
    "mode": "announce",
    "channel": "webchat"
  },
  "sessionTarget": "isolated",
  "enabled": true
}'
```

## 调度表达式参考

### Cron表达式格式
```
* * * * *
│ │ │ │ │
│ │ │ │ └── 星期几 (0-6, 0=周日)
│ │ │ └──── 月份 (1-12)
│ │ └────── 日 (1-31)
│ └──────── 小时 (0-23)
└────────── 分钟 (0-59)
```

### 常用表达式
- `0 15 * * 1-5`: 周一至周五15:00
- `0 9,15 * * 1-5`: 周一至周五9:00和15:00
- `0 */2 * * *`: 每2小时
- `0 0 * * *`: 每天0:00
- `0 0 * * 1`: 每周一0:00

### 时区说明
- `Asia/Shanghai`: 北京时间 (UTC+8)
- `Asia/Hong_Kong`: 香港时间 (UTC+8)
- `UTC`: 协调世界时
- `America/New_York`: 纽约时间 (UTC-5/-4)

## 故障排查

### 作业未执行
1. **检查作业状态**
   ```bash
   openclaw cron list --includeDisabled=true
   ```

2. **检查作业是否启用**
   ```bash
   openclaw cron list --includeDisabled=true | grep -A5 "262b7a44"
   ```

3. **手动触发测试**
   ```bash
   openclaw cron run --jobId=262b7a44-98f0-491c-a164-da680a91cf42
   ```

4. **检查执行历史**
   ```bash
   openclaw cron runs --jobId=262b7a44-98f0-491c-a164-da680a91cf42
   ```

### 执行失败
1. **检查日志**
   ```bash
   # 查看OpenClaw日志
   journalctl -u openclaw-gateway --since "1 hour ago"
   ```

2. **检查权限**
   ```bash
   # 检查工作目录权限
   ls -la /home/luckyelite/.openclaw/workspace/amber-engine/
   ```

3. **检查Python环境**
   ```bash
   python3 --version
   pip3 list | grep tushare
   ```

### 时间不正确
1. **检查系统时区**
   ```bash
   timedatectl
   ```

2. **检查Cron时区配置**
   ```bash
   openclaw cron list | grep -A10 "262b7a44"
   ```

3. **验证执行时间**
   ```bash
   # 计算下次执行时间
   date -d "next Monday 15:00" "+%Y-%m-%d %H:%M:%S"
   ```

## 最佳实践

### 1. 备份配置
定期导出Cron作业配置：
```bash
openclaw cron list --includeDisabled=true > cron_backup_$(date +%Y%m%d).json
```

### 2. 监控告警
- 设置作业失败告警
- 监控执行频率
- 跟踪执行时长

### 3. 定期维护
- 每月检查作业配置
- 每季度验证调度时间
- 每年更新时区信息（如有需要）

### 4. 文档更新
- 记录所有作业变更
- 更新调度表达式说明
- 维护故障排查指南

## 联系信息

- **配置维护**: Cheese Intelligence Team
- **最后更新**: 2026-03-20
- **版本**: 1.0.0
- **适用系统**: OpenClaw Gateway