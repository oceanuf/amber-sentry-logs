# ⚡ 生存线看板 (Survival)

## 📋 模组概述
**模组编号**: MOD-04  
**核心文件**: Codex_Prohibition.md  
**动态逻辑**: 注入 `database/risk_level.json` (实时风险等级)  
**状态**: 🟢 活跃

## 📁 文件清单

### 1. 法典禁令
- **文件**: `Codex_Prohibition.md`
- **类型**: 风险控制规则
- **版本**: V1.0.0
- **状态**: ✅ 强制执行

### 2. 风险矩阵
- **文件**: `Risk_Matrix.md`
- **类型**: 风险评估框架
- **版本**: V1.0.0
- **状态**: ✅ 生产环境运行

### 3. 应急预案
- **文件**: `Emergency_Protocol.md`
- **类型**: 应急处理流程
- **版本**: V1.0.0
- **状态**: ✅ 就绪状态

## 🔧 技术规范

### 风险数据注入
生存线看板支持实时风险数据注入：

```markdown
# 实时风险监控

## 🚨 当前风险等级
[[RISK_LEVEL_ZONE]]

## 📊 风险指标
- 系统风险: {{system_risk}}%
- 组合风险: {{portfolio_risk}}%
- 流动性风险: {{liquidity_risk}}%
```

### PHP风险数据注入
```php
// 风险数据注入逻辑
$risk_data = json_decode(file_get_contents('database/risk_level.json'), true);
$risk_html = generate_risk_dashboard($risk_data);
$markdown = str_replace('[[RISK_LEVEL_ZONE]]', $risk_html, $markdown);
```

## 📊 数据接口

### 1. 实时风险等级
- **文件**: `database/risk_level.json`
- **更新频率**: 15分钟
- **内容**: 系统实时风险评估

### 2. 风险历史数据
- **文件**: `database/risk_history.json`
- **更新频率**: 每日闭市后
- **内容**: 风险指标历史变化

### 3. 预警触发记录
- **文件**: `database/alerts_log.json`
- **更新频率**: 实时
- **内容**: 风险预警触发记录

## 🚨 风险等级标准

### 风险等级定义
| 等级 | 颜色 | 描述 | 应对措施 |
|------|------|------|----------|
| 低风险 | 🟢 绿色 | 系统正常 | 正常操作 |
| 中风险 | 🟡 黄色 | 需关注 | 加强监控 |
| 高风险 | 🟠 橙色 | 需干预 | 调整仓位 |
| 极高风险 | 🔴 红色 | 紧急状态 | 强制平仓 |

### 风险指标阈值
```json
{
  "system_risk": {
    "low": 30,
    "medium": 50,
    "high": 70,
    "critical": 85
  },
  "portfolio_risk": {
    "low": 20,
    "medium": 40,
    "high": 60,
    "critical": 80
  }
}
```

## 🚀 使用指南

### 查看风险状态
```markdown
查看实时风险: [[Codex_Prohibition.md#risk-monitor]]
```

### 查看风险矩阵
```markdown
查看风险框架: [[Risk_Matrix.md]]
```

### 查看应急预案
```markdown
查看应急流程: [[Emergency_Protocol.md]]
```

## 📈 维护记录

| 日期 | 版本 | 变更内容 | 负责人 |
|------|------|----------|--------|
| 2026-03-28 | V1.0.0 | 模组初始化 | Cheese |
| 2026-03-28 | V1.0.1 | 实现风险数据注入 | Cheese |

---

**最后更新**: 2026-03-28 16:08 GMT+8  
**维护团队**: Cheese Intelligence Team 🧀