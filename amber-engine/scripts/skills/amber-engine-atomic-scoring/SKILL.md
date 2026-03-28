# 琥珀引擎原子化打分 Skill (V4.1-AUDIT)

## 🚨 协议声明
本 Skill 是系统中唯一合法的计算逻辑。工程师 Cheese 必须且只能通过此 Skill 进行 ETF 评分。

## 📋 Skill 输入规范 (Input Schema)
所有传入此 Skill 的数据必须符合以下结构（10分制原始数据）：
- `p_raw`: Performance (业绩分) - 1-10分
- `l_raw`: Liquidity (流动性分) - 1-10分  
- `c_raw`: Cost (成本分) - 1-10分
- `b_raw`: Correlation (跟踪分) - 1-10分
- `m_raw`: Management (管理分) - 1-10分

## 🧮 Skill 计算核心 (Atomic Logic)
本 Skill 内部强制执行以下公式，严禁外部干预：
```
Final_Score = (p_raw * 0.30 + l_raw * 0.25 + c_raw * 0.20 + b_raw * 0.125 + m_raw * 0.125) * 10
```

## 🔒 审计水印生成
所有计算结果必须包含：
- `executor`: "工程师 Cheese (Audited by Chief)"
- `audit_hash`: 由输入数据和主编私钥生成的指纹（SHA256哈希）
- `timestamp`: ISO 8601格式时间戳
- `version`: "V4.1-AUDIT"

## 🛠️ 使用方法
```bash
# 调用Skill进行评分
openclaw skill amber-engine-atomic-scoring --p_raw 8 --l_raw 7 --c_raw 9 --b_raw 6 --m_raw 8
```

## ⚠️ 运行准则 (Enforcement)
1. **禁止计算**：Cheese 编写的任何 `.py` 或 `.js` 脚本中，严禁出现任何关于 ETF 分值的数学运算符号。
2. **唯一性**：所有展示在 Amber-Grid 的分值必须附带 Skill 生成的 `audit_hash`。
3. **数据整理职能**：工程师 Cheese 的职能仅限于：
    - 从 Tushare/AkShare 获取原始指标。
    - 将指标归一化为 1-10 的原始分。
    - **调用本 Skill 获取结果**。
    - 整理输出为 JSON 格式。

## 📊 输出格式
```json
{
  "final_score": 78.5,
  "dimension_scores": {
    "performance": 8,
    "liquidity": 7,
    "cost": 9,
    "correlation": 6,
    "management": 8
  },
  "weights": {
    "performance": 0.30,
    "liquidity": 0.25,
    "cost": 0.20,
    "correlation": 0.125,
    "management": 0.125
  },
  "audit": {
    "executor": "工程师 Cheese (Audited by Chief)",
    "audit_hash": "sha256:abc123...",
    "timestamp": "2026-03-23T14:30:00+08:00",
    "version": "V4.1-AUDIT"
  }
}
```

---
*Protocol Activated: 2026-03-22*
*Authority: Chief Editor Override*
*Status: CRITICAL - MANDATORY EXECUTION*