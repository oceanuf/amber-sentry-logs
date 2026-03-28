# 🧮 核心算法库 (Formulas)

## 📋 模组概述
**模组编号**: MOD-01  
**核心文件**: Stellar_Gravity.md, Bronze_Codex.md  
**动态逻辑**: 引用 `database/formulas_perf.json` (收益回测)  
**状态**: 🟢 活跃

## 📁 文件清单

### 1. 星辰引力算法
- **文件**: `Stellar_Gravity.md`
- **类型**: 趋势跟踪算法
- **版本**: V1.1.1-ELITE
- **状态**: ✅ 生产环境运行

### 2. 青铜法典
- **文件**: `Bronze_Codex.md`
- **类型**: 交易规则引擎
- **版本**: V1.0.0
- **状态**: ✅ 生产环境运行

## 🔧 技术规范

### YAML配置标准
每个算法文件必须包含以下YAML配置块：

```yaml
---
ID: STELLAR-01
TYPE: Trend_Following
HOLD_PERIOD: 60D
STATUS: Active
---
```

### 性能数据挂载
算法性能数据通过JSON动态注入：
```php
// PHP注入示例
$performance_data = json_decode(file_get_contents('database/formulas_perf.json'), true);
```

## 📊 数据接口

### 1. 收益回测数据
- **文件**: `database/formulas_perf.json`
- **更新频率**: 每日闭市后
- **内容**: 各算法历史回测表现

### 2. 参数调优记录
- **文件**: `database/params_history.json`
- **更新频率**: 参数变更时
- **内容**: 算法参数调整历史

## 🚀 使用指南

### 算法调用
```markdown
引用算法: [[Stellar_Gravity.md#alpha-ladder]]
```

### 性能查看
```markdown
查看回测: [[database/formulas_perf.json#STELLAR-01]]
```

## 📈 维护记录

| 日期 | 版本 | 变更内容 | 负责人 |
|------|------|----------|--------|
| 2026-03-28 | V1.0.0 | 模组初始化 | Cheese |
| 2026-03-28 | V1.0.1 | 添加YAML配置标准 | Cheese |

---

**最后更新**: 2026-03-28 16:05 GMT+8  
**维护团队**: Cheese Intelligence Team 🧀